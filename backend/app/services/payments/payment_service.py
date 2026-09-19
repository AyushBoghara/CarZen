import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

import httpx
from sqlalchemy.orm import Session

from app.models.enums.OrderEnums import NotificationType, OrderStatus
from app.models.enums.TransactionEnums import GatewayPaymentStatus, PaymentStatus
from app.models.orders import Orders
from app.models.payments import Payments
from app.models.users import User
from app.services.notifications import notification_service
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

PAYABLE_ORDER_STATUSES = {OrderStatus.CONFIRMED, OrderStatus.PROCESSING}
RAZORPAY_ORDER_URL = "https://api.razorpay.com/v1/orders"
DEFAULT_RAZORPAY_MAX_ORDER_AMOUNT_PAISE = 5_000_000


class PaymentAmountLimitError(ValueError):
    """The order is above the transaction limit enabled for this account."""

def create_payment(db: Session, order_id: int, payment_method, buyer: User) -> Payments:
    order = _get_payable_order(db, order_id, buyer)
    
    existing = db.query(Payments).filter(
        Payments.order_id == order.id,
        Payments.status.in_([GatewayPaymentStatus.PENDING, GatewayPaymentStatus.PROCESSING, GatewayPaymentStatus.SUCCESS]),
    ).first()
    if existing:
        raise ValueError("A payment already exists for this order.")

    key_id, key_secret = _razorpay_credentials()
    amount_in_paise = _to_paise(order.amount)
    _validate_razorpay_order_amount(amount_in_paise)
    gateway_order = _create_razorpay_order(key_id, key_secret, amount_in_paise, order.id)
    payment = Payments(
        order_id=order.id,
        user_id=buyer.id,
        amount=order.amount,
        currency="INR",
        payment_method=payment_method,
        provider="razorpay",
        razorpay_order_id=gateway_order["id"],
        status=GatewayPaymentStatus.PENDING,
        provider_metadata={"gateway_amount": amount_in_paise},
    )
    db.add(payment)
    db.flush()
    notification_service.create_notification(
        db, buyer.id, NotificationType.PAYMENT, "Payment initiated",
        f"A payment was initiated for order #{order.id}.", payment.id, "payment",
    )
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_for_user(db: Session, payment_id: int, user: User) -> Payments:
    payment = db.get(Payments, payment_id)
    if not payment:
        raise LookupError("Payment not found.")
    if user.role.value != "admin" and payment.user_id != user.id:
        raise PermissionError("You do not have access to this payment.")
    return payment


def get_order_payment(db: Session, order_id: int, user: User) -> Payments:
    order = db.get(Orders, order_id)
    if not order:
        raise LookupError("Order not found.")
    if user.role.value != "admin" and user.id not in {order.buyer_id, order.seller_id}:
        raise PermissionError("You do not have access to this order.")
    payment = db.query(Payments).filter(Payments.order_id == order_id).order_by(Payments.id.desc()).first()
    if not payment:
        raise LookupError("Payment not found.")
    return payment


def verify_payment(db: Session, payment_id: int, values: dict, buyer: User) -> Payments:
    payment = get_payment_for_user(db, payment_id, buyer)
    if payment.status == GatewayPaymentStatus.SUCCESS:
        return payment
    if payment.status not in {GatewayPaymentStatus.PENDING, GatewayPaymentStatus.PROCESSING}:
        raise ValueError("This payment cannot be verified.")
    if values["razorpay_order_id"] != payment.razorpay_order_id:
        raise ValueError("Razorpay order does not match this payment.")
    _verify_payment_signature(values)
    duplicate = db.query(Payments).filter(
        Payments.razorpay_payment_id == values["razorpay_payment_id"],
        Payments.id != payment.id,
    ).first()
    if duplicate:
        raise ValueError("This Razorpay payment has already been processed.")
    _mark_success(db, payment, values["razorpay_payment_id"], values["razorpay_signature"])
    db.commit()
    db.refresh(payment)
    return payment


def process_webhook(db: Session, payload: bytes, signature: str | None) -> Payments | None:
    _verify_webhook_signature(payload, signature)
    event = json.loads(payload.decode("utf-8"))
    event_name = event.get("event")
    entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    if not razorpay_order_id:
        return None
    payment = db.query(Payments).filter(Payments.razorpay_order_id == razorpay_order_id).first()
    if not payment:
        return None
    if event_name == "payment.captured":
        if payment.status == GatewayPaymentStatus.SUCCESS:
            return payment
        if entity.get("status") != "captured":
            raise ValueError("Razorpay payment was not captured.")
        if entity.get("currency") != payment.currency or entity.get("amount") != _to_paise(payment.amount):
            raise ValueError("Razorpay payment amount or currency does not match the order.")
        _mark_success(db, payment, entity.get("id"), None)
    elif event_name == "payment.failed":
        if payment.status in {GatewayPaymentStatus.SUCCESS, GatewayPaymentStatus.FAILED}:
            return payment
        payment.status = GatewayPaymentStatus.FAILED
        notification_service.create_notification(
            db, payment.user_id, NotificationType.PAYMENT, "Payment failed",
            f"Payment for order #{payment.order_id} failed. You can try again.", payment.id, "payment",
        )
    else:
        return payment
    db.commit()
    db.refresh(payment)
    return payment


def _get_payable_order(db: Session, order_id: int, buyer: User) -> Orders:
    order = db.get(Orders, order_id)
    if not order:
        raise LookupError("Order not found.")
    if order.buyer_id != buyer.id:
        raise PermissionError("Only the buyer can pay for this order.")
    if order.status not in PAYABLE_ORDER_STATUSES:
        raise ValueError("Only confirmed or processing orders can be paid.")
    if order.payment_status == PaymentStatus.PAID:
        raise ValueError("This order has already been paid.")
    if order.listing.deleted_at is not None or order.car.deleted_at is not None:
        raise ValueError("This listing is no longer available for payment.")
    return order


def _mark_success(db: Session, payment: Payments, razorpay_payment_id: str | None, signature: str | None) -> None:
    
    if not razorpay_payment_id:
        raise ValueError("Razorpay payment id is missing.")
    
    processed_payment = db.query(Payments).filter(
        Payments.razorpay_payment_id == razorpay_payment_id,
        Payments.id != payment.id,
    ).first()
    
    if processed_payment:
        raise ValueError("This Razorpay payment has already been processed.")
    
    payment.status = GatewayPaymentStatus.SUCCESS
    payment.razorpay_payment_id = razorpay_payment_id
    payment.provider_transaction_id = razorpay_payment_id
    payment.razorpay_signature = signature
    payment.payment_date = datetime.now(timezone.utc)
    order = payment.order
    order.payment_status = PaymentStatus.PAID
    
    notification_service.create_notification(
        db, order.buyer_id, NotificationType.PAYMENT, "Payment successful",
        f"Payment for order #{order.id} was verified successfully.", payment.id, "payment",
    )
    notification_service.create_notification(
        db, order.seller_id, NotificationType.PAYMENT, "Buyer payment received",
        f"Payment for order #{order.id} was verified successfully.", payment.id, "payment",
    )
    
def _razorpay_credentials() -> tuple[str, str]:
    load_dotenv(BASE_DIR / ".env")
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not key_id or not key_secret:
        raise RuntimeError("Razorpay is not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")
    
    return key_id, key_secret


def _create_razorpay_order(
    key_id: str,
    key_secret: str,
    amount: int,
    order_id: int,
) -> dict:

    payload = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"carzen-order-{order_id}",
    }

    print("========== RAZORPAY REQUEST ==========")
    print("KEY ID:", key_id)
    print("SECRET EXISTS:", bool(key_secret))
    print("AMOUNT:", amount)
    print("PAYLOAD:", payload)
    print("URL:", RAZORPAY_ORDER_URL)
    print("=======================================")

    try:
        response = httpx.post(
            RAZORPAY_ORDER_URL,
            auth=(key_id, key_secret),
            json=payload,
            headers={
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )

    except httpx.RequestError as exc:
        print("RAZORPAY CONNECTION ERROR:", repr(exc))
        raise RuntimeError(
            f"Could not connect to Razorpay: {exc}"
        ) from exc

    print("========== RAZORPAY RESPONSE ==========")
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
    print("========================================")

    if response.status_code >= 400:
        try:
            error = response.json().get("error", {})
        except ValueError:
            error = {}
        if error.get("description") == "Amount exceeds maximum amount allowed.":
            raise PaymentAmountLimitError(
                "Razorpay rejected this order because it exceeds the payment "
                "limit enabled for the account. Request a higher account limit, "
                "then update RAZORPAY_MAX_ORDER_AMOUNT_PAISE to that approved limit."
            )
        raise RuntimeError(
            f"Razorpay API error {response.status_code}: "
            f"{response.text}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Razorpay returned invalid JSON: {response.text}"
        ) from exc

    if not data.get("id"):
        raise RuntimeError(
            f"Razorpay did not return order id: {data}"
        )

    return data

def _verify_payment_signature(values: dict) -> None:
    _, secret = _razorpay_credentials()
    content = f"{values['razorpay_order_id']}|{values['razorpay_payment_id']}".encode()
    
    expected = hmac.new(secret.encode(), content, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(expected, values["razorpay_signature"]):
        raise ValueError("Invalid Razorpay payment signature.")


def _verify_webhook_signature(payload: bytes, signature: str | None) -> None:
    if not signature:
        raise PermissionError("Missing Razorpay webhook signature.")
    
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    
    if not secret:
        raise RuntimeError("Razorpay webhooks are not configured. Set RAZORPAY_WEBHOOK_SECRET.")
    
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise PermissionError("Invalid Razorpay webhook signature.")


def _to_paise(amount: Decimal) -> int:
    return int((Decimal(amount) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _validate_razorpay_order_amount(amount_in_paise: int) -> None:
    """Reject values above the account's enabled Razorpay order limit.

    Razorpay limits vary by account and environment.  The default reflects the
    usual unraised test-account limit; production must set the environment
    variable to the limit approved for its Razorpay account.
    """
    configured_limit = os.getenv(
        "RAZORPAY_MAX_ORDER_AMOUNT_PAISE",
        str(DEFAULT_RAZORPAY_MAX_ORDER_AMOUNT_PAISE),
    )
    try:
        max_amount_in_paise = int(configured_limit)
    except ValueError as exc:
        raise RuntimeError(
            "RAZORPAY_MAX_ORDER_AMOUNT_PAISE must be a whole number of paise."
        ) from exc

    if max_amount_in_paise < 100:
        raise RuntimeError(
            "RAZORPAY_MAX_ORDER_AMOUNT_PAISE must be at least 100 paise."
        )
    if amount_in_paise > max_amount_in_paise:
        order_amount = Decimal(amount_in_paise) / 100
        limit_amount = Decimal(max_amount_in_paise) / 100
        raise PaymentAmountLimitError(
            f"Order amount ₹{order_amount:,.2f} exceeds the configured Razorpay "
            f"per-payment limit of ₹{limit_amount:,.2f}. Increase the account "
            "limit in Razorpay, then set RAZORPAY_MAX_ORDER_AMOUNT_PAISE to the "
            "approved limit."
        )

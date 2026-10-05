
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.cars import Cars
from app.models.enums.CarEnums import CarApprovalStatus
from app.models.enums.ListingEnums import ListingStatus
from app.models.enums.OrderEnums import NotificationType, OrderStatus
from app.models.enums.TransactionEnums import (
    GatewayPaymentStatus,
    PaymentMethod,
    PaymentStatus,
    TransactionStatus,
)
from app.models.enums.UserRoles import UserRoles
from app.models.listings import Listings
from app.models.orders import Orders
from app.models.payments import Payments
from app.models.transactions import Transactions
from app.models.users import User
from app.services.notifications import notification_service


BASE_DIR = Path(__file__).resolve().parents[2]

PAYABLE_ORDER_STATUSES = {
    OrderStatus.CONFIRMED,
    OrderStatus.PROCESSING,
}

RAZORPAY_ORDER_URL = "https://api.razorpay.com/v1/orders"
DEFAULT_RAZORPAY_MAX_ORDER_AMOUNT_PAISE = 5_000_000


class PaymentAmountLimitError(ValueError):
    """The order is above the transaction limit enabled for this account."""


def create_payment(
    db: Session,
    order_id: int,
    payment_method,
    buyer: User,
) -> Payments:
    """
    Create a Razorpay payment attempt using the trusted amount
    stored on the Order.

    The client must never supply the payment amount.
    """
    order = _get_payable_order(db, order_id, buyer)

    existing = (
        db.query(Payments)
        .filter(
            Payments.order_id == order.id,
            Payments.status.in_(
                [
                    GatewayPaymentStatus.PENDING,
                    GatewayPaymentStatus.PROCESSING,
                    GatewayPaymentStatus.SUCCESS,
                ]
            ),
        )
        .first()
    )

    if existing:
        raise ValueError("A payment already exists for this order.")

    is_cash = payment_method == PaymentMethod.CASH or (
        isinstance(payment_method, str) and payment_method.lower() == "cash"
    )

    if is_cash:
        payment = Payments(
            order_id=order.id,
            user_id=buyer.id,
            amount=order.amount,
            currency="INR",
            payment_method=PaymentMethod.CASH,
            provider="cash",
            razorpay_order_id=None,
            status=GatewayPaymentStatus.PENDING,
            provider_metadata={
                "type": "cash_payment",
                "notes": "Cash payment requested. Awaiting seller/admin confirmation.",
            },
        )
        db.add(payment)
        db.flush()

        notification_service.create_notification(
            db,
            buyer.id,
            NotificationType.PAYMENT,
            "Cash payment selected",
            f"You selected cash payment for order #{order.id}. Please pay the seller directly upon car handover.",
            payment.id,
            "payment",
        )
        notification_service.create_notification(
            db,
            order.seller_id,
            NotificationType.PAYMENT,
            "Cash payment requested by buyer",
            f"Buyer {buyer.first_name} selected cash payment for order #{order.id}. Confirm receipt in CarZen once cash is received.",
            payment.id,
            "payment",
        )

        db.commit()
        db.refresh(payment)
        return payment

    key_id, key_secret = _razorpay_credentials()

    # IMPORTANT:
    # Always use the server-side Order amount.
    amount_in_paise = _to_paise(order.amount)

    _validate_razorpay_order_amount(amount_in_paise)

    gateway_order = _create_razorpay_order(
        key_id=key_id,
        key_secret=key_secret,
        amount=amount_in_paise,
        order_id=order.id,
    )

    payment = Payments(
        order_id=order.id,
        user_id=buyer.id,
        amount=order.amount,
        currency="INR",
        payment_method=payment_method,
        provider="razorpay",
        razorpay_order_id=gateway_order["id"],
        status=GatewayPaymentStatus.PENDING,
        provider_metadata={
            "gateway_amount": amount_in_paise,
        },
    )

    db.add(payment)
    db.flush()

    notification_service.create_notification(
        db,
        buyer.id,
        NotificationType.PAYMENT,
        "Payment initiated",
        f"A payment was initiated for order #{order.id}.",
        payment.id,
        "payment",
    )

    db.commit()
    db.refresh(payment)

    return payment


def get_payment_for_user(
    db: Session,
    payment_id: int,
    user: User,
) -> Payments:
    payment = db.get(Payments, payment_id)

    if not payment:
        raise LookupError("Payment not found.")

    if user.role != UserRoles.ADMIN and payment.user_id != user.id:
        raise PermissionError(
            "You do not have access to this payment."
        )

    return payment


def get_order_payment(
    db: Session,
    order_id: int,
    user: User,
) -> Payments:
    order = db.get(Orders, order_id)

    if not order:
        raise LookupError("Order not found.")

    if (
        user.role != UserRoles.ADMIN
        and user.id not in {order.buyer_id, order.seller_id}
    ):
        raise PermissionError(
            "You do not have access to this order."
        )

    payment = (
        db.query(Payments)
        .filter(Payments.order_id == order_id)
        .order_by(Payments.id.desc())
        .first()
    )

    if not payment:
        raise LookupError("Payment not found.")

    return payment


def verify_payment(
    db: Session,
    payment_id: int,
    values: dict,
    buyer: User,
) -> Payments:
    """
    Verify a Razorpay payment from the client callback.

    The actual state-changing work is centralized in _mark_success()
    so webhook and client verification use the same idempotent path.
    """
    payment = get_payment_for_user(
        db,
        payment_id,
        buyer,
    )

    if payment.status == GatewayPaymentStatus.SUCCESS:
        return payment

    if payment.status not in {
        GatewayPaymentStatus.PENDING,
        GatewayPaymentStatus.PROCESSING,
    }:
        raise ValueError("This payment cannot be verified.")

    razorpay_order_id = (values.get("razorpay_order_id") or "").strip()
    razorpay_payment_id = (values.get("razorpay_payment_id") or "").strip()
    razorpay_signature = (values.get("razorpay_signature") or "").strip()

    if not razorpay_order_id:
        raise ValueError("Razorpay order id is required.")

    if not razorpay_payment_id:
        raise ValueError("Razorpay payment id is required.")

    if not razorpay_signature:
        raise ValueError("Razorpay signature is required.")

    if razorpay_order_id != (payment.razorpay_order_id or "").strip():
        raise ValueError(
            f"Razorpay order does not match this payment. Expected: '{payment.razorpay_order_id}', received: '{razorpay_order_id}'."
        )

    _verify_payment_signature({
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    })

    duplicate = (
        db.query(Payments)
        .filter(
            Payments.razorpay_payment_id == razorpay_payment_id,
            Payments.id != payment.id,
        )
        .first()
    )

    if duplicate:
        raise ValueError(
            "This Razorpay payment has already been processed."
        )

    _mark_success(
        db,
        payment,
        razorpay_payment_id,
        razorpay_signature,
    )

    db.commit()
    db.refresh(payment)

    return payment


def confirm_cash_payment(
    db: Session,
    payment_id: int,
    actor: User,
    notes: str | None = None,
) -> Payments:
    """
    Confirm receipt of a cash payment for an order.
    Can be performed by the order's seller or an admin.
    """
    payment = db.get(Payments, payment_id)
    if not payment:
        raise LookupError("Payment not found.")

    if payment.order_id is None:
        raise ValueError("This payment is not linked to a car order.")

    order = db.get(Orders, payment.order_id)
    if not order:
        raise LookupError("Payment order not found.")

    if actor.role != UserRoles.ADMIN and actor.id != order.seller_id:
        raise PermissionError(
            "Only the seller of this order or an admin can confirm cash receipt."
        )

    if payment.status == GatewayPaymentStatus.SUCCESS:
        return payment

    if payment.status != GatewayPaymentStatus.PENDING:
        raise ValueError(f"Cannot confirm cash payment in status: {payment.status}.")

    if payment.payment_method != PaymentMethod.CASH:
        raise ValueError("Only cash payments can be manually confirmed.")

    synthetic_ref = f"cash_order_{order.id}_pay_{payment.id}_{int(datetime.now(timezone.utc).timestamp())}"

    _mark_success(
        db,
        payment,
        razorpay_payment_id=synthetic_ref,
        signature=None,
    )

    if notes:
        existing_meta = dict(payment.provider_metadata or {})
        existing_meta["confirmation_notes"] = notes
        existing_meta["confirmed_by"] = actor.id
        payment.provider_metadata = existing_meta

    db.commit()
    db.refresh(payment)

    return payment


def process_webhook(
    db: Session,
    payload: bytes,
    signature: str | None,
) -> Payments | None:
    """
    Process Razorpay webhook events.

    payment.captured and payment.failed are handled here.
    payment.captured uses the same _mark_success() path as
    client-side verification to prevent duplicate transactions.
    """
    _verify_webhook_signature(payload, signature)

    try:
        event = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid Razorpay webhook payload.") from exc

    event_name = event.get("event")

    entity = (
        event.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    razorpay_order_id = entity.get("order_id")

    if not razorpay_order_id:
        return None

    payment = (
        db.query(Payments)
        .filter(
            Payments.razorpay_order_id == razorpay_order_id
        )
        .first()
    )

    if not payment:
        return None

    if event_name == "payment.captured":
        if payment.status == GatewayPaymentStatus.SUCCESS:
            return payment

        if entity.get("status") != "captured":
            raise ValueError(
                "Razorpay payment was not captured."
            )

        if (
            entity.get("currency") != payment.currency
            or entity.get("amount") != _to_paise(payment.amount)
        ):
            raise ValueError(
                "Razorpay payment amount or currency does not "
                "match the order."
            )

        _mark_success(
            db,
            payment,
            entity.get("id"),
            None,
        )

    elif event_name == "payment.failed":
        if payment.status in {
            GatewayPaymentStatus.SUCCESS,
            GatewayPaymentStatus.FAILED,
        }:
            return payment

        payment.status = GatewayPaymentStatus.FAILED

        notification_service.create_notification(
            db,
            payment.user_id,
            NotificationType.PAYMENT,
            "Payment failed",
            (
                f"Payment for order #{payment.order_id} failed. "
                "You can try again."
            ),
            payment.id,
            "payment",
        )

    else:
        return payment

    db.commit()
    db.refresh(payment)

    return payment


def _get_payable_order(
    db: Session,
    order_id: int,
    buyer: User,
) -> Orders:
    """
    Return an order that is currently eligible for payment.

    Payment is allowed only when:
    - the order exists
    - the buyer owns the order
    - the order is confirmed/processing
    - the order is not already paid
    - listing/car are not deleted
    - listing is RESERVED
    """
    order = (
        db.query(Orders)
        .filter(Orders.id == order_id)
        .first()
    )

    if not order:
        raise LookupError("Order not found.")

    if order.buyer_id != buyer.id:
        raise PermissionError(
            "Only the buyer can pay for this order."
        )

    if order.status not in PAYABLE_ORDER_STATUSES:
        raise ValueError(
            "Only confirmed or processing orders can be paid."
        )

    if order.payment_status == PaymentStatus.PAID:
        raise ValueError(
            "This order has already been paid."
        )

    if order.listing is None:
        raise LookupError(
            "Order listing was not found."
        )

    if order.car is None:
        raise LookupError(
            "Order car was not found."
        )

    if (
        order.listing.deleted_at is not None
        or order.car.deleted_at is not None
    ):
        raise ValueError(
            "This listing is no longer available for payment."
        )

    # Only a seller-reserved listing can be paid for.
    if order.listing.listing_status != ListingStatus.RESERVED:
        raise ValueError(
            "Only a reserved listing can be paid for."
        )

    return order


def _mark_success(
    db: Session,
    payment: Payments,
    razorpay_payment_id: str | None,
    signature: str | None,
) -> None:
    """
    Single source of truth for successful Razorpay payments.

    This function:
    1. Locks the payment.
    2. Locks the order.
    3. Verifies the trusted amount.
    4. Marks payment SUCCESS.
    5. Marks order PAID.
    6. Creates exactly one transaction per order.
    7. Links Payment -> Transaction.
    8. Locks listing and car.
    9. Marks Listing SOLD and Car SOLD.

    The caller is responsible for committing the DB transaction.
    """
    if not razorpay_payment_id:
        raise ValueError(
            "Razorpay payment id is missing."
        )

    # 1. Lock the payment row.
    locked_payment = (
        db.query(Payments)
        .filter(Payments.id == payment.id)
        .with_for_update()
        .first()
    )

    if locked_payment is None:
        raise LookupError("Payment not found.")

    payment = locked_payment


    # 2. Idempotency: same Razorpay payment cannot belong
    #    to another local payment record.
    processed_payment = (
        db.query(Payments)
        .filter(
            Payments.razorpay_payment_id
            == razorpay_payment_id,
            Payments.id != payment.id,
        )
        .first()
    )

    if processed_payment:
        raise ValueError(
            "This Razorpay payment has already been processed."
        )
    # 3. If already successful, stop safely.
    if payment.status == GatewayPaymentStatus.SUCCESS:
        return

    if payment.status not in {
        GatewayPaymentStatus.PENDING,
        GatewayPaymentStatus.PROCESSING,
    }:
        raise ValueError(
            "This payment cannot be marked successful."
        )

    # 4. Lock the order.
    order = (
        db.query(Orders)
        .filter(Orders.id == payment.order_id)
        .with_for_update()
        .first()
    )

    if order is None:
        raise LookupError(
            "Payment order not found."
        )

    # 5. Validate payment amount against trusted order amount.
    if payment.amount != order.amount:
        raise ValueError(
            "Payment amount does not match order amount."
        )

    # 6. Validate order/payment state.

    if order.payment_status == PaymentStatus.PAID:
        raise ValueError(
            "Order is already marked as paid."
        )

    if order.status not in PAYABLE_ORDER_STATUSES:
        raise ValueError(
            "Order is no longer payable."
        )


    # 7. Lock listing.
    
    listing = (
        db.query(Listings)
        .filter(Listings.id == order.listing_id)
        .with_for_update()
        .first()
    )

    if listing is None:
        raise LookupError("Listing not found.")

    if listing.deleted_at is not None:
        raise ValueError(
            "Listing has been deleted."
        )

    if listing.listing_status != ListingStatus.RESERVED:
        raise ValueError(
            "Listing is not reserved for this order."
        )

    
    # 8. Lock car.
    car = (
        db.query(Cars)
        .filter(Cars.id == order.car_id)
        .with_for_update()
        .first()
    )

    if car is None:
        raise LookupError("Car not found.")

    if car.deleted_at is not None:
        raise ValueError(
            "Car has been deleted."
        )
    # 9. Mark gateway payment successful.
    payment.status = GatewayPaymentStatus.SUCCESS
    payment.razorpay_payment_id = razorpay_payment_id
    payment.provider_transaction_id = razorpay_payment_id
    payment.razorpay_signature = signature
    payment.payment_date = datetime.now(timezone.utc)


    # 10. Mark order as paid.
    order.payment_status = PaymentStatus.PAID

    # 11. Find transaction directly by order_id.
    # Requires Transactions.order_id with UNIQUE constraint.
    transaction = (
        db.query(Transactions)
        .filter(
            Transactions.order_id == order.id
        )
        .with_for_update()
        .first()
    )

    
    # 12. Create exactly one transaction.
    if transaction is None:
        transaction = Transactions(
            order_id=order.id,
            listing_id=order.listing_id,
            car_id=order.car_id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            final_price=order.amount,
            transaction_date=datetime.now(timezone.utc),
            payment_method=payment.payment_method,
            payment_status=PaymentStatus.PAID,
            transaction_status=TransactionStatus.COMPLETED,
        )

        db.add(transaction)
        db.flush()

    
    # 13. Link Payment -> Transaction.
    payment.transaction_id = transaction.id

    
    # 14. Mark listing SOLD.
    listing.listing_status = ListingStatus.SOLD

    # 15. Mark car SOLD.
    car.approval_status = CarApprovalStatus.SOLD

    
    # 16. Notifications.
    notification_service.create_notification(
        db,
        order.buyer_id,
        NotificationType.PAYMENT,
        "Payment successful",
        (
            f"Payment for order #{order.id} "
            "was verified successfully."
        ),
        payment.id,
        "payment",
    )

    notification_service.create_notification(
        db,
        order.seller_id,
        NotificationType.PAYMENT,
        "Buyer payment received",
        (
            f"Payment for order #{order.id} "
            "was verified successfully."
        ),
        payment.id,
        "payment",
    )


def _razorpay_credentials() -> tuple[str, str]:
    load_dotenv(BASE_DIR / ".env")

    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        raise RuntimeError(
            "Razorpay is not configured. Set "
            "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET."
        )

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
        raise RuntimeError(
            f"Could not connect to Razorpay: {exc}"
        ) from exc

    if response.status_code >= 400:
        try:
            error = response.json().get("error", {})
        except ValueError:
            error = {}

        if (
            error.get("description")
            == "Amount exceeds maximum amount allowed."
        ):
            raise PaymentAmountLimitError(
                "Razorpay rejected this order because it exceeds "
                "the payment limit enabled for the account. "
                "Request a higher account limit, then update "
                "RAZORPAY_MAX_ORDER_AMOUNT_PAISE to that approved limit."
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
    try:
        razorpay_order_id = values["razorpay_order_id"]
        razorpay_payment_id = values["razorpay_payment_id"]
        razorpay_signature = values["razorpay_signature"]
    except KeyError as exc:
        raise ValueError(
            f"Missing Razorpay verification field: {exc.args[0]}"
        ) from exc

    _, secret = _razorpay_credentials()

    content = (
        f"{razorpay_order_id}|{razorpay_payment_id}"
    ).encode()

    expected = hmac.new(
        secret.encode(),
        content,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected,
        razorpay_signature,
    ):
        raise ValueError(
            "Invalid Razorpay payment signature."
        )


def _verify_webhook_signature(
    payload: bytes,
    signature: str | None,
) -> None:
    if not signature:
        raise PermissionError(
            "Missing Razorpay webhook signature."
        )

    load_dotenv(BASE_DIR / ".env")

    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

    if not secret:
        raise RuntimeError(
            "Razorpay webhooks are not configured. "
            "Set RAZORPAY_WEBHOOK_SECRET."
        )

    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected,
        signature,
    ):
        raise PermissionError(
            "Invalid Razorpay webhook signature."
        )


def _to_paise(amount: Decimal) -> int:
    return int(
        (
            Decimal(amount) * 100
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


def _validate_razorpay_order_amount(
    amount_in_paise: int,
) -> None:
    load_dotenv(BASE_DIR / ".env", override=True)
    configured_limit = os.getenv(
        "RAZORPAY_MAX_ORDER_AMOUNT_PAISE",
        str(DEFAULT_RAZORPAY_MAX_ORDER_AMOUNT_PAISE),
    )

    try:
        max_amount_in_paise = int(configured_limit)
    except ValueError as exc:
        raise RuntimeError(
            "RAZORPAY_MAX_ORDER_AMOUNT_PAISE must be a whole "
            "number of paise."
        ) from exc

    if max_amount_in_paise < 100:
        raise RuntimeError(
            "RAZORPAY_MAX_ORDER_AMOUNT_PAISE must be at least "
            "100 paise."
        )

    if amount_in_paise > max_amount_in_paise:
        order_amount = Decimal(amount_in_paise) / 100
        limit_amount = Decimal(max_amount_in_paise) / 100

        raise PaymentAmountLimitError(
            f"Order amount ₹{order_amount:,.2f} exceeds the "
            f"configured Razorpay per-payment limit of "
            f"₹{limit_amount:,.2f}. Increase the account limit "
            "in Razorpay, then set "
            "RAZORPAY_MAX_ORDER_AMOUNT_PAISE to the approved limit."
        )
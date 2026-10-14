from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session, selectinload

from app.models.cars import Cars
from app.models.enums.OrderEnums import NotificationType
from app.models.enums.ServiceEnums import ServiceCatalogStatus, ServiceRequestStatus, ServiceStatus
from app.models.enums.TransactionEnums import GatewayPaymentStatus, PaymentMethod, PaymentStatus
from app.models.payments import Payments
from app.models.service_items import ServiceItems
from app.models.service_records import ServiceRecords
from app.models.service_requests import ServiceRequests
from app.models.service_request_items import ServiceRequestItems
from app.models.services import Services
from app.models.users import User
from app.services.car.catalog_service import paginate
from app.services.notifications import notification_service
from app.services.payments import payment_service
from app.models.address import Address


def _request_query(db: Session):
    return (
        db.query(ServiceRequests)
        .options(
            selectinload(ServiceRequests.user),
            selectinload(ServiceRequests.car),
            selectinload(ServiceRequests.service),
            selectinload(ServiceRequests.service_record),
            selectinload(ServiceRequests.items),
        )
        .filter(ServiceRequests.deleted_at.is_(None))
    )


def _get_service_name(request: ServiceRequests) -> str:
    if request.items:
        return ", ".join(item.service_name for item in request.items)
    if request.service:
        return request.service.name
    return "Service"


def create_service_request(db: Session, user: User, data: dict) -> ServiceRequests:
    car_id = data["car_id"]
    scheduled_date = data["scheduled_date"]
    scheduled_time = data["scheduled_time"]

    # 1. Car validation: user can only book service for their own car
    car = db.query(Cars).filter(Cars.id == car_id, Cars.deleted_at.is_(None)).first()
    if not car:
        raise LookupError("Car not found.")
    if car.owner_id != user.id:
        raise PermissionError("You can only request service for your own car.")

    # 2. Extract and deduplicate requested service IDs (multi or single)
    raw_ids = data.get("service_ids") or ([data["service_id"]] if data.get("service_id") else [])
    service_ids = list(dict.fromkeys(raw_ids))
    if not service_ids:
        raise ValueError("At least one service must be selected.")

    # 3. Fetch all requested services from database (must be active)
    services = (
        db.query(Services)
        .filter(
            Services.id.in_(service_ids),
            Services.status == ServiceCatalogStatus.ACTIVE.value,
            Services.deleted_at.is_(None),
        )
        .all()
    )

    if len(services) != len(service_ids):
        found_ids = {s.id for s in services}
        missing = [sid for sid in service_ids if sid not in found_ids]
        raise LookupError(f"Selected services not found or inactive: {missing}")

    # 4. Time validation: cannot be in the past
    scheduled_dt = datetime.combine(scheduled_date, scheduled_time)
    if scheduled_dt < datetime.now():
        raise ValueError("Scheduled date and time cannot be in the past.")

    # 5. Calculate server-side trusted catalog total
    catalog_total = sum(s.price for s in services)

    # Validate address ONLY if provided by user
    address_id = data.get("address_id")
    if address_id is not None:
        address = (
            db.query(Address)
            .filter(
                Address.id == address_id,
                Address.user_id == user.id,
                Address.deleted_at.is_(None),
            )
            .first()
        )
        if not address:
            raise LookupError("Address not found or does not belong to the current user.")

    # 6. Create parent appointment request
    request = ServiceRequests(
        user_id=user.id,
        car_id=car.id,
        service_id=services[0].id if services else None,
        address_id=address_id,
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        notes=data.get("notes"),
        amount=catalog_total,          # The single primary bill amount
        base_amount=catalog_total,     # Transparent breakdown: Base service
        parts_cost=Decimal("0.00"),     # Transparent breakdown: Parts (₹0 at booking)
        labor_cost=Decimal("0.00"),     # Transparent breakdown: Labor (₹0 at booking)
        total_amount=catalog_total,    # Helper alias matching amount
        payment_status=PaymentStatus.UNPAID,
        status=ServiceRequestStatus.REQUESTED,
    )
    db.add(request)
    db.flush()

    # 7. Save each service as an item under this request
    for s in services:
        item = ServiceRequestItems(
            service_request_id=request.id,
            service_id=s.id,
            service_name=s.name,
            unit_price=s.price,
            duration_minutes=s.duration_minutes,
        )
        db.add(item)
    db.flush()

    service_names = ", ".join(s.name for s in services)
    notification_service.create_notification(
        db,
        user.id,
        NotificationType.SYSTEM,
        "Service Request Submitted",
        f"Your request for '{service_names}' on {scheduled_date} at {scheduled_time} has been submitted.",
        request.id,
        "service_request",
    )

    db.commit()
    db.refresh(request)
    return get_user_request(db, request.id, user)


def list_user_requests(
    db: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    status: ServiceRequestStatus | None = None,
):
    query = _request_query(db).filter(ServiceRequests.user_id == user.id)
    if status:
        query = query.filter(ServiceRequests.status == status)

    return paginate(query.order_by(ServiceRequests.created_at.desc(), ServiceRequests.id.desc()), page, limit)


def get_user_request(db: Session, request_id: int, user: User) -> ServiceRequests:
    request = _request_query(db).filter(ServiceRequests.id == request_id).first()
    if not request:
        raise LookupError("Service request not found.")
    if request.user_id != user.id:
        raise PermissionError("You do not have access to this service request.")
    return request


def cancel_user_request(
    db: Session,
    request_id: int,
    user: User,
    notes: str | None = None,
) -> ServiceRequests:
    request = get_user_request(db, request_id, user)

    allowed_states = {
        ServiceRequestStatus.REQUESTED,
        ServiceRequestStatus.ACCEPTED,
        ServiceRequestStatus.SCHEDULED,
    }
    if request.status not in allowed_states:
        raise ValueError(
            f"Cannot cancel service request in status '{request.status.value}'. "
            "Only requested, accepted, or scheduled requests can be cancelled."
        )

    request.status = ServiceRequestStatus.CANCELLED
    if notes:
        request.notes = f"{request.notes or ''}\nCancellation reason: {notes}".strip()
    request.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(request)
    return request


# --- Admin Service Request Management ---

def admin_list_requests(
    db: Session,
    page: int = 1,
    limit: int = 20,
    status: ServiceRequestStatus | None = None,
    user_id: int | None = None,
    car_id: int | None = None,
):
    query = _request_query(db)
    if status:
        query = query.filter(ServiceRequests.status == status)
    if user_id:
        query = query.filter(ServiceRequests.user_id == user_id)
    if car_id:
        query = query.filter(ServiceRequests.car_id == car_id)

    return paginate(query.order_by(ServiceRequests.created_at.desc(), ServiceRequests.id.desc()), page, limit)


def admin_get_request(db: Session, request_id: int) -> ServiceRequests:
    request = _request_query(db).filter(ServiceRequests.id == request_id).first()
    if not request:
        raise LookupError("Service request not found.")
    return request


def admin_accept_request(db: Session, request_id: int) -> ServiceRequests:
    request = admin_get_request(db, request_id)
    if request.status == ServiceRequestStatus.ACCEPTED:
        return request
    if request.status != ServiceRequestStatus.REQUESTED:
        raise ValueError(
            f"Cannot accept request in status '{request.status.value}'. Must be REQUESTED."
        )

    request.status = ServiceRequestStatus.ACCEPTED
    request.updated_at = datetime.utcnow()

    notification_service.create_notification(
        db,
        request.user_id,
        NotificationType.SYSTEM,
        "Service Request Accepted",
        f"Your service request for '{_get_service_name(request)}' has been accepted by CarZen.",
        request.id,
        "service_request",
    )

    db.commit()
    db.refresh(request)
    return request


def admin_reject_request(
    db: Session,
    request_id: int,
    reason: str,
) -> ServiceRequests:
    request = admin_get_request(db, request_id)
    if request.status not in {ServiceRequestStatus.REQUESTED, ServiceRequestStatus.ACCEPTED}:
        raise ValueError(
            f"Cannot reject request in status '{request.status.value}'. Must be REQUESTED or ACCEPTED."
        )

    request.status = ServiceRequestStatus.REJECTED
    request.admin_note = reason
    request.updated_at = datetime.utcnow()

    notification_service.create_notification(
        db,
        request.user_id,
        NotificationType.SYSTEM,
        "Service Request Rejected",
        f"Your service request for '{_get_service_name(request)}' was rejected: {reason}",
        request.id,
        "service_request",
    )

    db.commit()
    db.refresh(request)
    return request


def admin_schedule_request(
    db: Session,
    request_id: int,
    data: dict,
) -> ServiceRequests:
    request = admin_get_request(db, request_id)
    if request.status not in {
        ServiceRequestStatus.REQUESTED,
        ServiceRequestStatus.ACCEPTED,
        ServiceRequestStatus.SCHEDULED,
    }:
        raise ValueError(
            f"Cannot schedule request in status '{request.status.value}'. Must be REQUESTED, ACCEPTED, or SCHEDULED."
        )

    if data.get("scheduled_date"):
        request.scheduled_date = data["scheduled_date"]
    if data.get("scheduled_time"):
        request.scheduled_time = data["scheduled_time"]
    if data.get("admin_note"):
        request.admin_note = data["admin_note"]

    request.status = ServiceRequestStatus.SCHEDULED
    request.updated_at = datetime.utcnow()

    notification_service.create_notification(
        db,
        request.user_id,
        NotificationType.SYSTEM,
        "Service Scheduled",
        f"Your service for '{_get_service_name(request)}' is scheduled for {request.scheduled_date} at {request.scheduled_time}.",
        request.id,
        "service_request",
    )

    db.commit()
    db.refresh(request)
    return request


def admin_start_request(db: Session, request_id: int) -> ServiceRequests:
    request = admin_get_request(db, request_id)
    if request.status == ServiceRequestStatus.IN_PROGRESS:
        return request
    if request.status not in {ServiceRequestStatus.ACCEPTED, ServiceRequestStatus.SCHEDULED}:
        raise ValueError(
            f"Cannot start request in status '{request.status.value}'. Must be ACCEPTED or SCHEDULED."
        )

    request.status = ServiceRequestStatus.IN_PROGRESS
    request.updated_at = datetime.utcnow()

    notification_service.create_notification(
        db,
        request.user_id,
        NotificationType.SYSTEM,
        "Service In Progress",
        f"Work on your car for '{_get_service_name(request)}' has begun.",
        request.id,
        "service_request",
    )

    db.commit()
    db.refresh(request)
    return request


def admin_complete_request(
    db: Session,
    request_id: int,
    data: dict | None = None,
) -> ServiceRequests:
    request = admin_get_request(db, request_id)
    if request.status not in {
        ServiceRequestStatus.IN_PROGRESS,
        ServiceRequestStatus.SCHEDULED,
        ServiceRequestStatus.ACCEPTED,
    }:
        raise ValueError(
            f"Cannot complete request in status '{request.status.value}'. Must be IN_PROGRESS, SCHEDULED, or ACCEPTED."
        )

    data = data or {}
    request.status = ServiceRequestStatus.COMPLETED
    if data.get("admin_note"):
        request.admin_note = data["admin_note"]

    # 1. Extract parts & labor logged by the technician
    parts_cost = Decimal(str(data.get("parts_cost") or 0))
    labor_cost = Decimal(str(data.get("labor_cost") or 0))
    base_amount = request.base_amount if (request.base_amount is not None and request.base_amount > 0) else (request.amount or Decimal("0.00"))

    # 2. Automatically update user-side payable bill
    request.base_amount = base_amount
    request.parts_cost = parts_cost
    request.labor_cost = labor_cost
    request.total_amount = base_amount + parts_cost + labor_cost
    request.amount = request.total_amount
    request.updated_at = datetime.utcnow()

    # 3. Update vehicle mileage if odometer reading was logged
    odometer_reading = data.get("odometer_reading")
    if odometer_reading is not None and request.car:
        request.car.mileage_km = Decimal(str(odometer_reading))

    service_title = _get_service_name(request)

    # Automatically create permanent vehicle ServiceRecord entry
    record = ServiceRecords(
        car_id=request.car_id,
        service_type=service_title,
        service_date=request.scheduled_date,
        odometer_reading=odometer_reading,
        service_cost=request.base_amount,
        parts_cost=parts_cost,
        labor_cost=labor_cost,
        description=data.get("admin_note") or request.notes,
        next_service_date=data.get("next_service_date"),
        next_service_mileage=data.get("next_service_mileage"),
        status=ServiceStatus.COMPLETED,
    )
    db.add(record)
    db.flush()

    # Populate itemized service items in vehicle history
    for item in request.items:
        db.add(
            ServiceItems(
                service_record_id=record.id,
                item_name=item.service_name,
                quantity=1,
                unit_cost=item.unit_price,
                total_cost=item.unit_price,
            )
        )

    request.service_record_id = record.id

    notification_service.create_notification(
        db,
        request.user_id,
        NotificationType.SYSTEM,
        "Service Completed",
        f"Service for '{service_title}' on your car has been completed successfully.",
        request.id,
        "service_request",
    )

    db.commit()
    db.refresh(request)
    return request


def admin_cancel_request(
    db: Session,
    request_id: int,
    reason: str | None = None,
) -> ServiceRequests:
    request = admin_get_request(db, request_id)
    if request.status in {
        ServiceRequestStatus.COMPLETED,
        ServiceRequestStatus.CANCELLED,
        ServiceRequestStatus.REJECTED,
    }:
        raise ValueError(f"Cannot cancel request in status '{request.status.value}'.")

    request.status = ServiceRequestStatus.CANCELLED
    if reason:
        request.admin_note = reason
    request.updated_at = datetime.utcnow()

    service_title = _get_service_name(request)
    notification_service.create_notification(
        db,
        request.user_id,
        NotificationType.SYSTEM,
        "Service Request Cancelled",
        f"Your service request for '{service_title}' was cancelled by admin.",
        request.id,
        "service_request",
    )

    db.commit()
    db.refresh(request)
    return request


# --- Payments for Service Requests ---

def initiate_online_payment(db: Session, request_id: int, user: User) -> dict:
    request = get_user_request(db, request_id, user)

    if request.status in {ServiceRequestStatus.CANCELLED, ServiceRequestStatus.REJECTED}:
        raise ValueError(f"Cannot pay for a {request.status.value.lower()} service request.")
    if request.payment_status == "paid":
        raise ValueError("This service request has already been paid.")

    # Charge the recalculated final bill (base + parts + labor)
    amount = request.total_amount if (request.total_amount is not None and request.total_amount > 0) else request.amount
    key_id, key_secret = payment_service._razorpay_credentials()
    amount_in_paise = payment_service._to_paise(amount)
    payment_service._validate_razorpay_order_amount(amount_in_paise)

    gateway_order = payment_service._create_razorpay_order(
        key_id=key_id,
        key_secret=key_secret,
        amount=amount_in_paise,
        order_id=request.id,
    )

    payment = Payments(
        service_request_id=request.id,
        user_id=user.id,
        amount=amount,
        currency="INR",
        payment_method=PaymentMethod.UPI,
        provider="razorpay",
        razorpay_order_id=gateway_order["id"],
        status=GatewayPaymentStatus.PENDING,
        provider_metadata={"service_request_id": request.id, "gateway_amount": amount_in_paise},
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "request_id": request.id,
        "payment_id": payment.id,
        "amount": amount,
        "currency": "INR",
        "razorpay_order_id": gateway_order["id"],
        "razorpay_key_id": key_id,
    }


def select_payment_method(
    db: Session,
    request_id: int,
    user: User,
    payment_method: str,
    notes: str | None = None,
) -> ServiceRequests:
    """
    User chooses payment method ('online' or 'cash') directly.
    No prior admin approval is required.
    """
    request = get_user_request(db, request_id, user)

    if request.status in {ServiceRequestStatus.CANCELLED, ServiceRequestStatus.REJECTED}:
        raise ValueError(f"Cannot select payment method for a {request.status.value.lower()} service request.")
    if request.payment_status == "paid":
        raise ValueError("This service request has already been paid.")

    normalized = payment_method.strip().lower()
    if normalized not in {"cash", "online"}:
        raise ValueError("Invalid payment method. Allowed values are 'cash' or 'online'.")

    request.payment_method = normalized
    if notes:
        request.notes = f"{request.notes or ''}\nPayment Note: {notes}".strip()
    request.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(request)
    return request


def verify_online_payment(db: Session, request_id: int, user: User, values: dict) -> ServiceRequests:
    request = get_user_request(db, request_id, user)
    
    if request.payment_status == "paid":
        return request

    razorpay_order_id = values.get("razorpay_order_id")
    razorpay_payment_id = values.get("razorpay_payment_id")
    razorpay_signature = values.get("razorpay_signature")

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        raise ValueError("Missing required Razorpay verification fields.")

    payment = (
        db.query(Payments)
        .filter(
            Payments.service_request_id == request.id,
            Payments.razorpay_order_id == razorpay_order_id,
        )
        .first()
    )
    if not payment:
        raise LookupError("Payment record not found for this service request.")

    payment_service._verify_payment_signature(values)

    payment.status = GatewayPaymentStatus.SUCCESS
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.payment_date = datetime.now(timezone.utc)

    request.payment_status = "paid"
    request.payment_method = "online"
    request.updated_at = datetime.utcnow()

    final_amount = request.total_amount if (request.total_amount is not None and request.total_amount > 0) else request.amount
    
    notification_service.create_notification(
        db,
        user.id,
        NotificationType.PAYMENT,
        "Service Payment Successful",
        f"Online payment of INR {final_amount} for service request #{request.id} was verified.",
        payment.id,
        "service_payment",
    )

    db.commit()
    db.refresh(request)
    return request


def confirm_cash_payment(
    db: Session,
    request_id: int,
    admin: User,
    notes: str | None = None,
) -> ServiceRequests:
    """
    Workshop counter desk / admin settles cash payment collected physically upon car pickup.
    """
    request = admin_get_request(db, request_id)
    if request.status in {ServiceRequestStatus.CANCELLED, ServiceRequestStatus.REJECTED}:
        raise ValueError(f"Cannot collect cash for a {request.status.value.lower()} service request.")

    amount = request.total_amount if (request.total_amount is not None and request.total_amount > 0) else request.amount

    request.payment_status = "paid"
    request.payment_method = "cash"
    request.updated_at = datetime.utcnow()

    payment = Payments(
        service_request_id=request.id,
        user_id=request.user_id,
        amount=amount,
        currency="INR",
        payment_method=PaymentMethod.CASH,
        provider="cash",
        status=GatewayPaymentStatus.SUCCESS,
        payment_date=datetime.now(timezone.utc),
        provider_metadata={
            "type": "cash_payment",
            "confirmed_by": admin.id,
            "notes": notes or "Cash collected directly at CarZen service center",
        },
    )
    db.add(payment)

    notification_service.create_notification(
        db,
        request.user_id,
        NotificationType.PAYMENT,
        "Service Cash Payment Received",
        f"Cash payment of INR {amount} for service request #{request.id} was confirmed by {admin.first_name}.",
        payment.id,
        "service_payment",
    )

    db.commit()
    db.refresh(request)
    return request

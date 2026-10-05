from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date as DateType
from decimal import Decimal

from app.core.auth_dependencies import get_current_admin, get_current_user
from app.database.connection.conn import get_db
from app.models.cars import Cars
from app.models.car_variants import CarVariants
from app.models.enums.CarEnums import CarApprovalStatus, CarCondition, FuelType, TransmissionType
from app.models.enums.ServiceEnums import ServiceRequestStatus
from app.models.service_requests import ServiceRequests
from app.models.users import User
from app.schemas.cars_schema import CarResponse, PaginatedResponse
from app.schemas.payment_schema import PaymentVerify
from app.schemas.service_request_schema import (
    ServiceRequestAdminComplete,
    ServiceRequestCancel,
    ServiceRequestConfirmCash,
    ServiceRequestCreate,
    ServiceRequestPayOnlineResponse,
    ServiceRequestReject,
    ServiceRequestResponse,
    ServiceRequestSchedule,
    ServiceCarCreate
)
from app.services.services import service_request_service
from pydantic import BaseModel, Field

router = APIRouter()

def _raise(exc: Exception):
    code = (
        404 if isinstance(exc, LookupError)
        else 403 if isinstance(exc, PermissionError)
        else 400 if isinstance(exc, ValueError)
        else 500
    )
    raise HTTPException(status_code=code, detail=str(exc)) from exc


# ==========================================
# Service-purpose Car Endpoints — NO admin approval needed
# ==========================================

@router.post(
    "/service/my-cars",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Service Cars"],
    summary="Add your car for service (no admin approval needed)",
)
def add_service_car(
    payload: ServiceCarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a car for service booking purposes.
    Unlike the seller POST /cars endpoint, this car is immediately
    available (approval_status = APPROVED) without waiting for admin review.
    The car can only be used for service requests — not for marketplace listings.
    """
    try:
        # Validate variant exists
        variant = db.query(CarVariants).filter(CarVariants.id == payload.variant_id).first()
        if not variant:
            raise HTTPException(status_code=404, detail="Car variant not found.")

        # Check for duplicate registration number
        if payload.registration_number:
            existing = db.query(Cars).filter(
                Cars.registration_number == payload.registration_number,
                Cars.deleted_at.is_(None),
            ).first()
            if existing:
                raise HTTPException(status_code=409, detail="A car with this registration number already exists.")

        # Create car — auto-approved, no pending_approval queue
        car = Cars(
            owner_id=current_user.id,
            variant_id=payload.variant_id,
            registration_number=payload.registration_number,
            manufacturing_year=payload.manufacturing_year,
            fuel_type=payload.fuel_type,
            transmission=payload.transmission,
            mileage_km=payload.mileage_km,
            color=payload.color,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            # KEY DIFFERENCE: auto-approved — no admin review needed
            approval_status=CarApprovalStatus.APPROVED,
            is_verified=False,
            # Required DB fields with safe defaults
            condition=CarCondition.GOOD,
        )
        db.add(car)
        db.commit()
        db.refresh(car)
        return car

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.get(
    "/service/my-cars",
    response_model=list[CarResponse],
    tags=["Service Cars"],
    summary="List all your cars (for service booking car picker)",
)
def list_service_cars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all non-deleted cars owned by the current user.
    Used by the service booking UI to show the car picker dropdown.
    """
    cars = (
        db.query(Cars)
        .filter(
            Cars.owner_id == current_user.id,
            Cars.deleted_at.is_(None),
        )
        .order_by(Cars.id.desc())
        .all()
    )
    return cars


# ==========================================
# Slot Availability — no login required
# ==========================================

@router.get(
    "/service-slots",
    tags=["Service Requests"],
    summary="Get available time slots for a given date",
)
def get_available_slots(
    date: DateType | None = Query(default=None, description="Date to check. Format: YYYY-MM-DD. Defaults to today."),
    db: Session = Depends(get_db),
):
    """
    Returns all time slots for the given date with availability.
    Slots already booked (status not CANCELLED or REJECTED) are marked unavailable.
    """
    if date is None:
        date = DateType.today()

    ALL_SLOTS = [
        "09:00:00", "10:00:00", "11:00:00",
        "12:00:00", "13:00:00", "14:00:00",
        "15:00:00", "16:00:00", "17:00:00",
        "15:30:00", "16:30:00", "17:30:00"
    ]

    booked = (
        db.query(ServiceRequests.scheduled_time)
        .filter(
            ServiceRequests.scheduled_date == date,
            ServiceRequests.status.notin_([
                ServiceRequestStatus.CANCELLED,
                ServiceRequestStatus.REJECTED,
            ]),
            ServiceRequests.deleted_at.is_(None),
        )
        .all()
    )

    booked_times = {str(r.scheduled_time) for r in booked}

    slots = [
        {"time": slot, "available": slot not in booked_times}
        for slot in ALL_SLOTS
    ]

    return {"date": str(date), "slots": slots}


# ==========================================
# User Service Request Endpoints
# ==========================================

@router.post(
    "/service-requests",
    response_model=ServiceRequestResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Service Requests"],
    summary="Create a new service request for your car",
)
def create_service_request(
    payload: ServiceRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return service_request_service.create_service_request(db, user, payload.model_dump())
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.get(
    "/service-requests",
    response_model=PaginatedResponse[ServiceRequestResponse],
    tags=["Service Requests"],
    summary="List all service requests placed by the current user",
)
def list_user_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: ServiceRequestStatus | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        data, pagination = service_request_service.list_user_requests(db, user, page, limit, status)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/service-requests/{request_id}",
    response_model=ServiceRequestResponse,
    tags=["Service Requests"],
    summary="Get single service request details",
)
def get_user_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return service_request_service.get_user_request(db, request_id, user)
    except Exception as exc:
        _raise(exc)


@router.post(
    "/service-requests/{request_id}/cancel",
    response_model=ServiceRequestResponse,
    tags=["Service Requests"],
    summary="Cancel a service request (before it is in progress)",
)
def cancel_user_request(
    request_id: int,
    payload: ServiceRequestCancel = ServiceRequestCancel(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return service_request_service.cancel_user_request(db, request_id, user, payload.notes)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/service-requests/{request_id}/pay-online",
    response_model=ServiceRequestPayOnlineResponse,
    tags=["Service Requests"],
    summary="Initiate Razorpay online payment for a service request",
)
def pay_service_online(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return service_request_service.initiate_online_payment(db, request_id, user)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/service-requests/{request_id}/verify-online",
    response_model=ServiceRequestResponse,
    tags=["Service Requests"],
    summary="Verify Razorpay online payment signature for a service request",
)
def verify_service_online(
    request_id: int,
    payload: PaymentVerify,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return service_request_service.verify_online_payment(db, request_id, user, payload.model_dump())
    except Exception as exc:
        db.rollback()
        _raise(exc)


# ==========================================
# Admin Service Request Management Endpoints
# ==========================================

@router.get(
    "/admin/service-requests",
    response_model=PaginatedResponse[ServiceRequestResponse],
    tags=["Admin Service Requests"],
    summary="Admin list all service requests across users",
)
def admin_list_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: ServiceRequestStatus | None = Query(None, description="Filter by status"),
    user_id: int | None = Query(None, description="Filter by user ID"),
    car_id: int | None = Query(None, description="Filter by car ID"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        data, pagination = service_request_service.admin_list_requests(
            db, page, limit, status, user_id, car_id
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/admin/service-requests/{request_id}",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin get service request by ID",
)
def admin_get_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.admin_get_request(db, request_id)
    except Exception as exc:
        _raise(exc)


@router.post(
    "/admin/service-requests/{request_id}/accept",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin accept a requested service",
)
def admin_accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.admin_accept_request(db, request_id)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/service-requests/{request_id}/reject",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin reject a service request with a reason",
)
def admin_reject_request(
    request_id: int,
    payload: ServiceRequestReject,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.admin_reject_request(db, request_id, payload.admin_note)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/service-requests/{request_id}/schedule",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin confirm or reschedule service appointment",
)
def admin_schedule_request(
    request_id: int,
    payload: ServiceRequestSchedule,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.admin_schedule_request(db, request_id, payload.model_dump())
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/service-requests/{request_id}/start",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin start service (transitions to IN_PROGRESS)",
)
def admin_start_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.admin_start_request(db, request_id)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/service-requests/{request_id}/complete",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin complete service (transitions to COMPLETED and generates permanent vehicle ServiceRecord)",
)
def admin_complete_request(
    request_id: int,
    payload: ServiceRequestAdminComplete = ServiceRequestAdminComplete(),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.admin_complete_request(
            db, request_id, payload.model_dump(exclude_unset=True)
        )
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/service-requests/{request_id}/cancel",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin cancel a service request",
)
def admin_cancel_request(
    request_id: int,
    payload: ServiceRequestCancel = ServiceRequestCancel(),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.admin_cancel_request(db, request_id, payload.notes)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/service-requests/{request_id}/confirm-cash",
    response_model=ServiceRequestResponse,
    tags=["Admin Service Requests"],
    summary="Admin confirm cash payment collected for service request",
)
def admin_confirm_cash(
    request_id: int,
    payload: ServiceRequestConfirmCash = ServiceRequestConfirmCash(),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_request_service.confirm_cash_payment(db, request_id, admin, payload.notes)
    except Exception as exc:
        db.rollback()
        _raise(exc)

from datetime import date, datetime, time
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.ServiceEnums import ServiceRequestStatus
from app.schemas.service_catalog_schema import ServiceResponse
from app.models.enums.CarEnums import FuelType, TransmissionType


class ServiceRequestUserSummary(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    email: str
    phone_number: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRequestCarSummary(BaseModel):
    id: int
    registration_number: str | None = None
    manufacturing_year: int
    color: str | None = None
    fuel_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRequestItemResponse(BaseModel):
    id: int
    service_id: int | None = None
    service_name: str
    unit_price: Decimal
    duration_minutes: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRequestCreate(BaseModel):
    car_id: int = Field(..., gt=0, description="ID of the user's car")
    service_ids: list[int] | None = Field(
        default=None,
        description="List of service IDs from catalog for multi-service booking",
    )
    service_id: int | None = Field(
        default=None,
        gt=0,
        description="Single service ID from catalog (backward compatibility)",
    )
    address_id: int | None = Field(
        default=None,
        gt=0,
        description="ID of the user's saved address for pickup/service location",
    )
    scheduled_date: date = Field(..., description="Requested date for the service")
    scheduled_time: time = Field(..., description="Requested time slot for the service")
    notes: str | None = Field(default=None, max_length=5000, description="Customer instructions or issues to inspect")



class ServiceRequestSchedule(BaseModel):
    scheduled_date: date = Field(..., description="Confirmed or rescheduled service date")
    scheduled_time: time = Field(..., description="Confirmed or rescheduled service time")
    admin_note: str | None = Field(default=None, max_length=2000, description="Admin notes or instructions for the user")


class ServiceRequestReject(BaseModel):
    admin_note: str = Field(..., min_length=1, max_length=2000, description="Reason for rejecting the request")


class ServiceRequestCancel(BaseModel):
    notes: str | None = Field(default=None, max_length=2000, description="Reason for cancellation")


class ServiceRequestAdminComplete(BaseModel):
    admin_note: str | None = Field(default=None, max_length=2000, description="Work completion notes")
    odometer_reading: Decimal | None = Field(default=None, ge=0, description="Odometer reading at completion")
    parts_cost: Decimal | None = Field(default=None, ge=0, description="Cost of replacement parts")
    labor_cost: Decimal | None = Field(default=None, ge=0, description="Labor cost")
    next_service_date: date | None = Field(default=None, description="Recommended next service date")
    next_service_mileage: Decimal | None = Field(default=None, ge=0, description="Recommended next service mileage")


class ServiceRequestConfirmCash(BaseModel):
    notes: str | None = Field(default=None, max_length=500, description="Notes on cash payment collection")


class ServiceRequestPayOnlineResponse(BaseModel):
    request_id: int
    payment_id: int
    amount: Decimal
    currency: str = "INR"
    razorpay_order_id: str
    razorpay_key_id: str | None = None


class ServiceRequestResponse(BaseModel):
    id: int
    user_id: int
    car_id: int
    service_id: int | None = None
    address_id: int | None = None
    scheduled_date: date
    scheduled_time: time
    notes: str | None = None
    amount: Decimal
    payment_status: str
    payment_method: str | None = None
    status: ServiceRequestStatus
    admin_note: str | None = None
    service_record_id: int | None = None
    created_at: datetime
    updated_at: datetime
    user: ServiceRequestUserSummary | None = None
    car: ServiceRequestCarSummary | None = None
    service: ServiceResponse | None = None
    items: list[ServiceRequestItemResponse] = []

    model_config = ConfigDict(from_attributes=True)



class ServiceCarCreate(BaseModel):
    """
    A simplified schema for adding a car for service purposes.
    No expected_market_price, no ownership_type required.
    The car is auto-approved — no admin review needed.
    """
    variant_id: int = Field(..., gt=0, description="Car variant ID from catalog")
    registration_number: str | None = Field(default=None, max_length=30, description="Number plate, e.g. MH02AB1234")
    manufacturing_year: int = Field(..., ge=1886, le=2030, description="Year car was manufactured")
    fuel_type: FuelType = Field(..., description="petrol / diesel / cng / electric / hybrid")
    transmission: TransmissionType = Field(..., description="manual / automatic / amt / cvt / dct")
    mileage_km: Decimal = Field(..., ge=0, description="Current odometer reading in km")
    color: str | None = Field(default=None, max_length=50)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field(default="India", max_length=100)

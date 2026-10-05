from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.ServiceEnums import ServiceStatus


class ServiceRecordCarSummary(BaseModel):
    id: int
    registration_number: str | None = None
    manufacturing_year: int
    color: str | None = None
    fuel_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRecordCenterSummary(BaseModel):
    id: int
    name: str
    phone_number: str | None = None
    city: str | None = None
    state: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Backwards compatibility aliases
ServiceBookingCarSummary = ServiceRecordCarSummary
ServiceBookingCenterSummary = ServiceRecordCenterSummary


class ServiceItemResponse(BaseModel):
    id: int
    item_name: str
    quantity: int | None = None
    unit_price: Decimal | None = None
    total_price: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRecordResponse(BaseModel):
    id: int
    car_id: int
    service_center_id: int | None = None
    service_type: str
    service_date: date
    odometer_reading: Decimal | None = None
    service_cost: Decimal | None = None
    parts_cost: Decimal | None = None
    labor_cost: Decimal | None = None
    description: str | None = None
    next_service_date: date | None = None
    next_service_mileage: Decimal | None = None
    status: ServiceStatus | None = None
    created_at: datetime
    updated_at: datetime
    car: ServiceRecordCarSummary | None = None
    service_center: ServiceRecordCenterSummary | None = None
    items: list[ServiceItemResponse] = []

    model_config = ConfigDict(from_attributes=True)

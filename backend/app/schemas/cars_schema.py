from datetime import date, datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums.CarEnums import CarApprovalStatus, CarCondition, FuelType, MediaType, OwnershipType, TransmissionType

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta


class BrandSummary(BaseModel):
    id: int
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)


class ModelSummary(BaseModel):
    id: int
    brand_id: int
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)


class VariantSummary(BaseModel):
    id: int
    model_id: int
    variant_name: str
    fuel_type: FuelType
    transmission: TransmissionType
    model_config = ConfigDict(from_attributes=True)


class OwnerSummary(BaseModel):
    id: int
    first_name: str
    last_name: str | None
    username: str
    model_config = ConfigDict(from_attributes=True)


class CarMediaResponse(BaseModel):
    id: int
    media_type: MediaType
    media_url: str
    thumbnail_url: str | None
    file_name: str | None
    file_size: int | None
    sort_order: int
    is_primary: bool
    created_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CarMediaUpdate(BaseModel):
    sort_order: int | None = Field(default=None, ge=0)
    is_primary: bool | None = None
    thumbnail_url: str | None = Field(default=None, max_length=500)


class MediaOrderItem(BaseModel):
    id: int
    sort_order: int = Field(ge=0)


class CarMediaReorderRequest(BaseModel):
    media: list[MediaOrderItem] = Field(min_length=1)


class CarFeatureCreate(BaseModel):
    feature_name: str = Field(min_length=1, max_length=150)
    feature_value: str | None = Field(default=None, max_length=255)


class CarFeatureUpdate(BaseModel):
    feature_name: str | None = Field(default=None, min_length=1, max_length=150)
    feature_value: str | None = Field(default=None, max_length=255)


class CarFeatureResponse(BaseModel):
    id: int
    car_id: int
    feature_name: str
    feature_value: str | None
    created_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CarCreate(BaseModel):
    variant_id: int
    registration_number: str | None = Field(default=None, max_length=30)
    vin_number: str | None = Field(default=None, max_length=100)
    manufacturing_year: int = Field(ge=1886, le=9999)
    registration_year: int | None = Field(default=None, ge=1886, le=9999)
    fuel_type: FuelType
    transmission: TransmissionType
    engine_cc: Decimal | None = Field(default=None, ge=0)
    horsepower: Decimal | None = Field(default=None, ge=0)
    mileage_km: Decimal = Field(ge=0)
    color: str | None = Field(default=None, max_length=50)
    seating_capacity: int | None = Field(default=None, ge=1)
    owner_count: int | None = Field(default=None, ge=0)
    ownership_type: OwnershipType | None = None
    condition: CarCondition
    insurance_company: str | None = Field(default=None, max_length=150)
    insurance_type: str | None = Field(default=None, max_length=100)
    insurance_expiry: date | None = None
    rc_status: str | None = Field(default=None, max_length=50)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    country: str = Field(default="India", min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, max_length=10)
    description: str | None = None
    expected_market_price: Decimal | None = Field(default=None, ge=0)

    @field_validator("registration_year", mode="before")
    @classmethod
    def normalize_optional_year(cls, value):
        return None if value in ("", 0, "0") else value

    @field_validator("ownership_type", "insurance_expiry", mode="before")
    @classmethod
    def normalize_blank_optional_fields(cls, value):
        return None if value == "" else value

    @field_validator(
        "registration_number", "vin_number", "insurance_company", "insurance_type",
        "rc_status", "postal_code", "description", mode="before",
    )
    @classmethod
    def normalize_blank_optional_text(cls, value):
        return None if isinstance(value, str) and not value.strip() else value


class CarUpdate(BaseModel):
    variant_id: int | None = None
    registration_number: str | None = Field(default=None, max_length=30)
    vin_number: str | None = Field(default=None, max_length=100)
    manufacturing_year: int | None = Field(default=None, ge=1886, le=9999)
    registration_year: int | None = Field(default=None, ge=1886, le=9999)
    fuel_type: FuelType | None = None
    transmission: TransmissionType | None = None
    engine_cc: Decimal | None = Field(default=None, ge=0)
    horsepower: Decimal | None = Field(default=None, ge=0)
    mileage_km: Decimal | None = Field(default=None, ge=0)
    color: str | None = Field(default=None, max_length=50)
    seating_capacity: int | None = Field(default=None, ge=1)
    owner_count: int | None = Field(default=None, ge=1)
    ownership_type: OwnershipType | None = None
    condition: CarCondition | None = None
    insurance_company: str | None = Field(default=None, max_length=150)
    insurance_type: str | None = Field(default=None, max_length=100)
    insurance_expiry: date | None = None
    rc_status: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, max_length=10)
    description: str | None = None
    expected_market_price: Decimal | None = Field(default=None, ge=0)

    @field_validator("registration_year", mode="before")
    @classmethod
    def normalize_optional_year(cls, value):
        return None if value in ("", 0, "0") else value

    @field_validator("ownership_type", "insurance_expiry", mode="before")
    @classmethod
    def normalize_blank_optional_fields(cls, value):
        return None if value == "" else value

    @field_validator(
        "registration_number", "vin_number", "insurance_company", "insurance_type",
        "rc_status", "postal_code", "description", mode="before",
    )
    @classmethod
    def normalize_blank_optional_text(cls, value):
        return None if isinstance(value, str) and not value.strip() else value


class CarResponse(BaseModel):
    id: int
    variant_id: int
    owner_id: int
    registration_number: str | None
    vin_number: str | None
    manufacturing_year: int
    registration_year: int | None
    fuel_type: FuelType
    transmission: TransmissionType
    mileage_km: Decimal
    color: str | None
    condition: CarCondition
    city: str
    state: str
    expected_market_price: Decimal | None
    is_verified: bool
    approval_status: CarApprovalStatus
    created_at: datetime | None
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CarDetailResponse(CarResponse):
    engine_cc: Decimal | None
    horsepower: Decimal | None
    seating_capacity: int | None
    owner_count: int | None
    ownership_type: OwnershipType | None
    insurance_company: str | None
    insurance_type: str | None
    insurance_expiry: date | None
    rc_status: str | None
    country: str
    postal_code: str | None
    description: str | None
    rejection_reason: str | None
    verified_at: datetime | None
    brand: BrandSummary
    model: ModelSummary
    variant: VariantSummary
    owner: OwnerSummary
    media: list[CarMediaResponse]
    features: list[CarFeatureResponse]


class CarRejectionRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=2000)

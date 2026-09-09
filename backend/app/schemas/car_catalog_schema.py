from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.CarEnums import BodyType, FuelType, TransmissionType


class ActiveStatusUpdate(BaseModel):
    is_active: bool


class CarBrandCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    country: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=500)
    description: str | None = None
    is_active: bool = True


class CarBrandUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    country: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=500)
    description: str | None = None
    is_active: bool | None = None


class CarBrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    country: str | None
    logo_url: str | None
    description: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CarModelCreate(BaseModel):
    brand_id: int
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    body_type: BodyType | None = None
    seating_capacity: int | None = Field(default=None, ge=1)
    description: str | None = None
    is_active: bool = True


class CarModelUpdate(BaseModel):
    brand_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    body_type: BodyType | None = None
    seating_capacity: int | None = Field(default=None, ge=1)
    description: str | None = None
    is_active: bool | None = None


class CarModelResponse(BaseModel):
    id: int
    brand_id: int
    name: str
    slug: str
    body_type: BodyType | None
    seating_capacity: int | None
    description: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CarVariantCreate(BaseModel):
    model_id: int
    variant_name: str = Field(min_length=1, max_length=150)
    fuel_type: FuelType
    transmission: TransmissionType
    engine_cc: Decimal | None = Field(default=None, ge=0)
    horsepower: Decimal | None = Field(default=None, ge=0)
    seating_capacity: int | None = Field(default=None, ge=1)
    ex_showroom_price: Decimal | None = Field(default=None, ge=0)


class CarVariantUpdate(BaseModel):
    model_id: int | None = None
    variant_name: str | None = Field(default=None, min_length=1, max_length=150)
    fuel_type: FuelType | None = None
    transmission: TransmissionType | None = None
    engine_cc: Decimal | None = Field(default=None, ge=0)
    horsepower: Decimal | None = Field(default=None, ge=0)
    seating_capacity: int | None = Field(default=None, ge=1)
    ex_showroom_price: Decimal | None = Field(default=None, ge=0)


class CarVariantResponse(BaseModel):
    id: int
    model_id: int
    variant_name: str
    fuel_type: FuelType
    transmission: TransmissionType
    engine_cc: Decimal | None
    horsepower: Decimal | None
    seating_capacity: int | None
    ex_showroom_price: Decimal | None
    created_at: datetime | None
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)

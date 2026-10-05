from datetime import datetime
from decimal import Decimal

from pydantic import AliasPath, BaseModel, ConfigDict, Field

from app.models.enums.ListingEnums import ListingStatus, ListingType

from app.models.enums.CarEnums import (
    BodyType,
    CarCondition,
    FuelType,
    OwnershipType,
    TransmissionType,
)
class ListingCreate(BaseModel):
    listing_type: ListingType
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    asking_price: Decimal = Field(gt=0)
    negotiable: bool = True
    expiry_date: datetime | None = None


class ListingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    asking_price: Decimal | None = Field(default=None, gt=0)
    negotiable: bool | None = None
    expiry_date: datetime | None = None


class ListingResponse(BaseModel):
    id: int
    car_id: int
    seller_id: int
    listing_type: ListingType
    title: str
    description: str | None
    asking_price: Decimal
    negotiable: bool
    listing_status: ListingStatus
    listed_at: datetime | None
    expiry_date: datetime | None
    views_count: int | None
    created_at: datetime | None
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class ListingBrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ListingModelResponse(BaseModel):
    id: int
    name: str
    slug: str
    body_type: BodyType | None = None
    seating_capacity: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ListingVariantResponse(BaseModel):
    id: int
    variant_name: str
    fuel_type: FuelType
    transmission: TransmissionType
    engine_cc: Decimal | None = None
    horsepower: Decimal | None = None
    seating_capacity: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ListingMediaResponse(BaseModel):
    id: int
    media_type: str
    media_url: str
    thumbnail_url: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    sort_order: int
    is_primary: bool

    model_config = ConfigDict(from_attributes=True)


class ListingFeatureResponse(BaseModel):
    id: int
    feature_name: str
    feature_value: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ListingCarResponse(BaseModel):
    id: int

    brand: ListingBrandResponse = Field(
        validation_alias=AliasPath("variant", "model", "brand")
    )

    model: ListingModelResponse = Field(
        validation_alias=AliasPath("variant", "model")
    )

    variant: ListingVariantResponse

    registration_number: str | None = None
    vin_number: str | None = None

    manufacturing_year: int
    registration_year: int | None = None

    fuel_type: FuelType
    transmission: TransmissionType

    engine_cc: Decimal | None = None
    horsepower: Decimal | None = None

    mileage_km: Decimal

    color: str | None = None
    seating_capacity: int | None = None

    owner_count: int | None = None
    ownership_type: OwnershipType | None = None

    condition: CarCondition

    insurance_company: str | None = None
    insurance_type: str | None = None
    insurance_expiry: datetime | None = None

    rc_status: str | None = None

    city: str
    state: str
    country: str
    postal_code: str | None = None

    description: str | None = None
    expected_market_price: Decimal | None = None

    media: list[ListingMediaResponse] = Field(default_factory=list)
    features: list[ListingFeatureResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
class ListingResponseSecond(BaseModel):

    id: int
    car_id: int
    seller_id: int

    listing_type: ListingType

    title: str
    description: str | None = None

    asking_price: Decimal
    negotiable: bool

    listing_status: ListingStatus

    listed_at: datetime | None = None
    expiry_date: datetime | None = None

    views_count: int | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    car: ListingCarResponse

    model_config = ConfigDict(from_attributes=True)

class CarDetailResponse(BaseModel):
    id: int

    brand: ListingBrandResponse = Field(
        validation_alias=AliasPath("variant", "model", "brand")
    )

    model: ListingModelResponse = Field(
        validation_alias=AliasPath("variant", "model")
    )

    variant: ListingVariantResponse

    manufacturing_year: int

    fuel_type: FuelType
    transmission: TransmissionType

    engine_cc: Decimal | None = None
    horsepower: Decimal | None = None

    mileage_km: Decimal

    color: str | None = None
    seating_capacity: int | None = None

    condition: CarCondition

    city: str
    state: str
    country: str
    postal_code: str | None = None

    description: str | None = None
    expected_market_price: Decimal | None = None

    media: list[ListingMediaResponse] = Field(default_factory=list)
    features: list[ListingFeatureResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)    
    
class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    car_id: int
    created_at: datetime | None
    car: CarDetailResponse

    model_config = ConfigDict(from_attributes=True)
    
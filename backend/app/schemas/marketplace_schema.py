from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.ListingEnums import ListingStatus, ListingType


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


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    car_id: int
    created_at: datetime | None
    model_config = ConfigDict(from_attributes=True)

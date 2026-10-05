from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.buyer_schema import BuyerUserSummary
from app.schemas.transaction_schema import TransactionCarSummary


class ReviewCreate(BaseModel):
    car_id: int = Field(..., gt=0)
    transaction_id: int | None = Field(default=None, gt=0)
    rating: int = Field(..., ge=1, le=5)
    title: str | None = Field(default=None, max_length=255)
    review_text: str | None = Field(default=None, max_length=5000)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    title: str | None = Field(default=None, max_length=255)
    review_text: str | None = Field(default=None, max_length=5000)


class ReviewVisibilityUpdate(BaseModel):
    is_visible: bool


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    car_id: int | None = None
    listing_id: int | None = None
    transaction_id: int | None = None
    rating: int
    title: str | None = None
    review_text: str | None = None
    is_visible: bool
    created_at: datetime
    updated_at: datetime
    user: BuyerUserSummary | None = None
    car: TransactionCarSummary | None = None

    model_config = ConfigDict(from_attributes=True)

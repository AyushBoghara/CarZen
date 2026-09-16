from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.inquiries import InquiryStatus
from app.models.enums.TransactionEnums import PaymentMethod, PaymentStatus, TransactionStatus
from app.schemas.marketplace_schema import ListingResponse, ListingResponseSecond


class BuyerInquiryCreate(BaseModel):
    subject: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=1, max_length=5000)


class InquiryMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


class BuyerUserSummary(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str

    model_config = ConfigDict(from_attributes=True)


class InquiryMessageResponse(BaseModel):
    id: int
    inquiry_id: int
    sender_id: int
    message: str
    created_at: datetime
    sender: BuyerUserSummary

    model_config = ConfigDict(from_attributes=True)


class BuyerInquiryResponse(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    subject: str | None = None
    message: str
    status: InquiryStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None
    listing: ListingResponse
    seller: BuyerUserSummary

    model_config = ConfigDict(from_attributes=True)


class BuyerInquiryDetailResponse(BuyerInquiryResponse):
    messages: list[InquiryMessageResponse] = Field(default_factory=list)


class BuyerPurchaseResponse(BaseModel):
    id: int
    listing_id: int
    car_id: int
    buyer_id: int
    seller_id: int
    final_price: Decimal
    transaction_date: datetime | None = None
    payment_method: PaymentMethod | None = None
    payment_status: PaymentStatus
    transaction_status: TransactionStatus
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    listing: ListingResponse
    seller: BuyerUserSummary

    model_config = ConfigDict(from_attributes=True)


class RecentlyViewedListingResponse(BaseModel):
    id: int
    listing_id: int
    viewed_at: datetime
    listing: ListingResponseSecond

    model_config = ConfigDict(from_attributes=True)


class BuyerDashboardResponse(BaseModel):
    total_favorite_cars: int
    active_inquiries: int
    recently_viewed_cars: int
    purchase_history: int

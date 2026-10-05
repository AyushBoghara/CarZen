from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.inquiries import InquiryStatus
from app.schemas.buyer_schema import BuyerUserSummary, InquiryMessageResponse
from app.schemas.marketplace_schema import ListingResponse


class SellerInquiryStatusUpdate(BaseModel):
    status: InquiryStatus


class SellerInquiryResponse(BaseModel):
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
    buyer: BuyerUserSummary

    model_config = ConfigDict(from_attributes=True)


class SellerInquiryDetailResponse(SellerInquiryResponse):
    messages: list[InquiryMessageResponse] = Field(default_factory=list)

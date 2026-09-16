from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.OrderEnums import OrderStatus
from app.models.enums.TransactionEnums import PaymentStatus
from app.schemas.buyer_schema import BuyerUserSummary
from app.schemas.marketplace_schema import ListingCarResponse, ListingResponse


class OrderCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    notes: str | None = Field(default=None, max_length=5000)


class OrderCreateRequest(OrderCreate):
    listing_id: int = Field(gt=0)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    listing_id: int
    car_id: int
    buyer_id: int
    seller_id: int
    amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    buyer: BuyerUserSummary
    seller: BuyerUserSummary
    listing: ListingResponse
    car: ListingCarResponse

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.models.enums.TransactionEnums import PaymentMethod, PaymentStatus, TransactionStatus
from app.schemas.buyer_schema import BuyerUserSummary


class TransactionCarSummary(BaseModel):
    id: int
    registration_number: str | None = None
    manufacturing_year: int
    color: str | None = None
    fuel_type: str | None = None
    transmission: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TransactionListingSummary(BaseModel):
    id: int
    title: str
    asking_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    id: int
    listing_id: int
    order_id: int
    car_id: int
    buyer_id: int
    seller_id: int
    final_price: Decimal
    transaction_date: datetime | None = None
    payment_method: PaymentMethod | None = None
    payment_status: PaymentStatus
    transaction_status: TransactionStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    buyer: BuyerUserSummary | None = None
    seller: BuyerUserSummary | None = None
    car: TransactionCarSummary | None = None
    listing: TransactionListingSummary | None = None

    model_config = ConfigDict(from_attributes=True)

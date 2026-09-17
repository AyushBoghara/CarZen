from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.TransactionEnums import GatewayPaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    payment_method: PaymentMethod = PaymentMethod.CARD


class PaymentVerify(BaseModel):
    razorpay_order_id: str = Field(min_length=1, max_length=255)
    razorpay_payment_id: str = Field(min_length=1, max_length=255)
    razorpay_signature: str = Field(min_length=1, max_length=512)


class PaymentResponse(BaseModel):
    id: int
    order_id: int | None = None
    amount: Decimal
    currency: str
    payment_method: PaymentMethod | None = None
    razorpay_order_id: str | None = None
    razorpay_payment_id: str | None = None
    status: GatewayPaymentStatus
    payment_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentStatusResponse(PaymentResponse):
    razorpay_key_id: str | None = None

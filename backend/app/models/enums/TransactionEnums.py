from enum import Enum


class PaymentMethod(str, Enum):
    CASH = "cash"
    UPI = "upi"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    FINANCE = "finance"
    OTHER = "other"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class TransactionStatus(str, Enum):
    INITIATED = "initiated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
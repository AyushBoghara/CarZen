from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class NotificationType(str, Enum):
    ORDER = "order"
    PAYMENT = "payment"
    LISTING = "listing"
    INQUIRY = "inquiry"
    FAVORITE = "favorite"
    SYSTEM = "system"
    ADMIN = "admin"

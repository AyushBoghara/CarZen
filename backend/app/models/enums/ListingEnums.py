from enum import Enum


class ListingType(str, Enum):
    SALE = "sale"
    RESALE = "resale"


class ListingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RESERVED = "reserved"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REMOVED = "removed"
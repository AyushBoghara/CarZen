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


class ListingSort(str, Enum):
    NEWEST = "newest"
    PRICE_LOW_TO_HIGH = "price_low_to_high"
    PRICE_HIGH_TO_LOW = "price_high_to_low"
    YEAR_NEWEST = "year_newest"
    MILEAGE_LOW_TO_HIGH = "mileage_low_to_high"

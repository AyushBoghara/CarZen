from enum import Enum


class ReportReason(str, Enum):
    FAKE_LISTING = "fake_listing"
    WRONG_INFORMATION = "wrong_information"
    FRAUD = "fraud"
    DUPLICATE_LISTING = "duplicate_listing"
    SUSPICIOUS_SELLER = "suspicious_seller"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    OTHER = "other"


class ReportStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"

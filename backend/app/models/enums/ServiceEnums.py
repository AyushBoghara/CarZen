from enum import Enum


class ServiceStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val = value.lower()
            for member in cls:
                if member.value == val or member.name.lower() == val:
                    return member
        return None


class ServiceRequestStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val = value.lower()
            if val == "reject":
                return cls.REJECTED
            for member in cls:
                if member.value == val or member.name.lower() == val:
                    return member
        return None


class ServiceCatalogStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


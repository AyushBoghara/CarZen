from enum import Enum


class PredictionStatus(str, Enum):
    REQUESTED = "requested"
    COMPLETED = "completed"
    FAILED = "failed"


class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
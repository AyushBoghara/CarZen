from enum import Enum

class ContactVisibility(str, Enum):
    PUBLIC = "public"
    BUYERS_ONLY = "buyers_only"
    PRIVATE = "private"
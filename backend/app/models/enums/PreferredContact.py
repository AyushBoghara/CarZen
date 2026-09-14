from enum import Enum


class PreferredContactMethod(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
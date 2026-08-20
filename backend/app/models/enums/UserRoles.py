from enum import Enum


class UserRoles(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    RESELLER = "reseller"
    SERVICE_PROVIDER = "service_provider"
    USER = "user"
    ADMIN = "admin"
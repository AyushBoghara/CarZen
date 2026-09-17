from enum import Enum

class UserRoles(str, Enum):
    SELLER = "seller"
    # RESELLER = "reseller"
    SERVICE_PROVIDER = "service_provider"
    USER = "user"  # Buyer
    ADMIN = "admin"

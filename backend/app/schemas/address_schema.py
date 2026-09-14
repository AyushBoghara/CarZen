from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.enums.ListingEnums import ListingStatus, ListingType
from app.models.enums.PreferredContact import PreferredContactMethod
from app.models.enums.ContactVisibility import ContactVisibility
    
from typing import Optional

from pydantic import BaseModel, ConfigDict

class AddressCreate(BaseModel):
    address_line_1: str
    address_line_2: str | None = None
    landmark: str | None = None
    city: str
    state: str
    country: str = "India"
    postal_code: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_default: bool = False
    
class AddressUpdate(BaseModel):
    address_line_1: str
    address_line_2: Optional[str] = None
    landmark:Optional[str] =None
    city:str
    state:str
    country:str
    postal_code:str
    latitude:Optional[float] = None
    longitude:Optional[float] = None

    is_default:bool = True  
    
class AddressResponse(BaseModel):
    id: int
    address_line_1: str
    address_line_2: Optional[str] = None
    landmark:Optional[str] =None
    city:str
    state:str
    country:str
    postal_code:str
    latitude:Optional[float] = None
    longitude:Optional[float] = None

    is_default:bool  
    
    model_config = ConfigDict(
        from_attributes=True
    )

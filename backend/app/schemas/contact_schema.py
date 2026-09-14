from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums.PreferredContact import PreferredContactMethod
from app.models.enums.ContactVisibility import ContactVisibility
from app.schemas.address_schema import AddressResponse


class ContactCreate(BaseModel):
    address_id: int
    whatsapp_number: Optional[str] = None
    preferred_contact_method: PreferredContactMethod = (
        PreferredContactMethod.PHONE
    )
    contact_visibility: ContactVisibility = (
        ContactVisibility.BUYERS_ONLY
    )
    is_visible: bool = True


class ContactUpdate(BaseModel):
    address_id: Optional[int] = None

    whatsapp_number: Optional[str] = None

    preferred_contact_method: Optional[
        PreferredContactMethod
    ] = None

    contact_visibility: Optional[
        ContactVisibility
    ] = None

    is_visible: Optional[bool] = None


class ContactVisibilityUpdate(BaseModel):
    contact_visibility: ContactVisibility


class SellerContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    preferred_contact_method: PreferredContactMethod
    contact_visibility: ContactVisibility
    is_visible: bool
    address: Optional[AddressResponse] = None
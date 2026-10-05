import datetime

from sqlalchemy import (
    Column,
    Enum,
    String,
    BigInteger,
    Boolean,
    ForeignKey,    
    DateTime
)
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enums.PreferredContact import PreferredContactMethod
from app.models.enums.ContactVisibility import ContactVisibility

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(BigInteger,ForeignKey("users.id"),nullable=False,index=True)
    address_id = Column(BigInteger,ForeignKey("addresses.id"),nullable=False,index=True)
    
    whatsapp_number = Column(String(20), nullable=True)
    preferred_contact_method = Column(Enum(PreferredContactMethod,name="preferred_contact_method_enum",),nullable=False,default=PreferredContactMethod.PHONE)
    contact_visibility = Column(Enum(ContactVisibility,name="contact_visibility_enum"),nullable=False,default=ContactVisibility.BUYERS_ONLY)
    is_visible = Column(Boolean,nullable=False,default=True)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )

    deleted_at = Column(
        DateTime,
        nullable=True
    )
    
    # Relationships
    user = relationship("User", back_populates="contact", foreign_keys=[user_id])
    address = relationship("Address",back_populates="contacts",foreign_keys=[address_id])
    
    @property
    def email(self):
        return self.user.email if self.user else None

    @property
    def phone_number(self):
        return self.user.phone_number if self.user else None
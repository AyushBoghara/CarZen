import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Text,
    Enum,
    ForeignKey
)

from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

from app.database.connection import Base


class InquiryStatus(str, PyEnum):
    OPEN = "open"
    CONTACTED = "contacted"
    CLOSED = "closed"


class Inquiries(Base):
    __tablename__ = "inquiries"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    listing_id = Column(
        BigInteger,
        ForeignKey("listings.id"),
        nullable=False
    )

    buyer_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    seller_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    subject = Column(
        String(255),
        nullable=True
    )

    message = Column(
        Text,
        nullable=False
    )

    status = Column(
        Enum(InquiryStatus),
        default=InquiryStatus.OPEN
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )
    
    # Relationships
    listing = relationship("Listings", back_populates="inquiries", foreign_keys=[listing_id])
    buyer = relationship("User", back_populates="inquiries_made", foreign_keys=[buyer_id])
    seller = relationship("User", back_populates="inquiries_received", foreign_keys=[seller_id])

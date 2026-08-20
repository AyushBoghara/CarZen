import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Text,
    Integer,
    Numeric,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.ListingEnums import ListingType, ListingStatus


class Listings(Base):
    __tablename__ = "listings"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    car_id = Column(
        BigInteger,
        ForeignKey("cars.id"),
        nullable=False
    )

    seller_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    listing_type = Column(
        Enum(ListingType),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    asking_price = Column(
        Numeric(15, 2),
        nullable=False
    )

    negotiable = Column(
        Boolean,
        default=True
    )

    listing_status = Column(
        Enum(ListingStatus),
        default=ListingStatus.DRAFT
    )

    listed_at = Column(
        DateTime,
        nullable=True
    )

    expiry_date = Column(
        DateTime,
        nullable=True
    )

    views_count = Column(
        Integer,
        default=0
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

    deleted_at = Column(
        DateTime,
        nullable=True
    )
    
    # Relationships
    car = relationship("Cars", back_populates="listings", foreign_keys=[car_id])
    seller = relationship("User", back_populates="listings", foreign_keys=[seller_id])
 
    inquiries = relationship("Inquiries", back_populates="listing", foreign_keys="Inquiries.listing_id")
    transactions = relationship("Transactions", back_populates="listing", foreign_keys="Transactions.listing_id")
    reviews = relationship("Reviews", back_populates="listing", foreign_keys="Reviews.listing_id")
    reports = relationship("Reports", back_populates="listing", foreign_keys="Reports.listing_id")

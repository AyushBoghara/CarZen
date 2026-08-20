import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Numeric,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ServiceCenters(Base):
    __tablename__ = "service_centers"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    owner_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    contact_person = Column(
        String(150),
        nullable=True
    )

    email = Column(
        String(150),
        nullable=True
    )

    phone_number = Column(
        String(20),
        nullable=True
    )

    address_line_1 = Column(
        String(255),
        nullable=True
    )

    address_line_2 = Column(
        String(255),
        nullable=True
    )

    city = Column(
        String(100),
        nullable=True
    )

    state = Column(
        String(100),
        nullable=True
    )

    country = Column(
        String(100),
        default="India"
    )

    postal_code = Column(
        String(10),
        nullable=True
    )

    latitude = Column(
        Numeric(10, 7),
        nullable=True
    )

    longitude = Column(
        Numeric(10, 7),
        nullable=True
    )

    rating = Column(
        Numeric(3, 2),
        nullable=True
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    is_active = Column(
        Boolean,
        default=True
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
    owner = relationship("User", back_populates="service_centers", foreign_keys=[owner_id])
    service_records = relationship("ServiceRecords", back_populates="service_center", foreign_keys="ServiceRecords.service_center_id")
 

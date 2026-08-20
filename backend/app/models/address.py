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


class Addresses(Base):
    __tablename__ = "addresses"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    address_line_1 = Column(
        String(255),
        nullable=False
    )

    address_line_2 = Column(
        String(255),
        nullable=True
    )

    landmark = Column(
        String(255),
        nullable=True
    )

    city = Column(
        String(100),
        nullable=False
    )

    state = Column(
        String(100),
        nullable=False
    )

    country = Column(
        String(100),
        nullable=False,
        default="India"
    )

    postal_code = Column(
        String(10),
        nullable=False
    )

    latitude = Column(
        Numeric(10, 7),
        nullable=True
    )

    longitude = Column(
        Numeric(10, 7),
        nullable=True
    )

    is_default = Column(
        Boolean,
        default=False
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
    user = relationship("User", back_populates="addresses", foreign_keys=[user_id])
 

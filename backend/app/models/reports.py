import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base

class Reports(Base):
    __tablename__ = "reports"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    reporter_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    listing_id = Column(
        BigInteger,
        ForeignKey("listings.id"),
        nullable=True
    )

    car_id = Column(
        BigInteger,
        ForeignKey("cars.id"),
        nullable=True
    )

    reason = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )
    
    
    # Relationships
    reporter = relationship("User", back_populates="reports", foreign_keys=[reporter_id])
    listing = relationship("Listings", back_populates="reports", foreign_keys=[listing_id])
    car = relationship("Cars", back_populates="reports", foreign_keys=[car_id])
 

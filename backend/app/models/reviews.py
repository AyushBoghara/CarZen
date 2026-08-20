import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Text,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Reviews(Base):
    __tablename__ = "reviews"

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

    car_id = Column(
        BigInteger,
        ForeignKey("cars.id"),
        nullable=True
    )

    listing_id = Column(
        BigInteger,
        ForeignKey("listings.id"),
        nullable=True
    )

    rating = Column(
        Integer,
        nullable=False
    )

    title = Column(
        String(255),
        nullable=True
    )

    review_text = Column(
        Text,
        nullable=True
    )

    is_visible = Column(
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
    user = relationship("User", back_populates="reviews", foreign_keys=[user_id])
    car = relationship("Cars", back_populates="reviews", foreign_keys=[car_id])
    listing = relationship("Listings", back_populates="reviews", foreign_keys=[listing_id])
 

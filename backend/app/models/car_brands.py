import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Text
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class CarBrands(Base):
    __tablename__ = "car_brands"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    slug = Column(
        String(120),
        unique=True,
        nullable=False
    )

    country = Column(
        String(100),
        nullable=True
    )

    logo_url = Column(
        String(500),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
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
    models = relationship("CarModels", back_populates="brand", foreign_keys="CarModels.brand_id")
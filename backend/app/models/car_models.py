import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Text,
    Integer,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.CarEnums import BodyType


class CarModels(Base):
    __tablename__ = "car_models"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    brand_id = Column(
        BigInteger,
        ForeignKey("car_brands.id"),
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    slug = Column(
        String(120),
        unique=True,
        nullable=False
    )

    body_type = Column(
        Enum(BodyType),
        nullable=True
    )

    seating_capacity = Column(
        Integer,
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
    brand = relationship("CarBrands", back_populates="models", foreign_keys=[brand_id])
    variants = relationship("CarVariants", back_populates="model", foreign_keys="CarVariants.model_id")

import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Integer,
    Numeric,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.CarEnums import FuelType, TransmissionType


class CarVariants(Base):
    __tablename__ = "car_variants"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    model_id = Column(
        BigInteger,
        ForeignKey("car_models.id"),
        nullable=False
    )

    variant_name = Column(
        String(150),
        nullable=False
    )

    fuel_type = Column(
        Enum(FuelType),
        nullable=False
    )

    transmission = Column(
        Enum(TransmissionType),
        nullable=False
    )

    engine_cc = Column(
        Numeric(8, 2),
        nullable=True
    )

    horsepower = Column(
        Numeric(8, 2),
        nullable=True
    )

    seating_capacity = Column(
        Integer,
        nullable=True
    )

    ex_showroom_price = Column(
        Numeric(15, 2),
        nullable=True
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
    
    model = relationship("CarModels", back_populates="variants", foreign_keys=[model_id])
    cars = relationship("Cars", back_populates="variant", foreign_keys="Cars.variant_id")

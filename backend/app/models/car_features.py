import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class CarFeatures(Base):
    __tablename__ = "car_features"

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

    feature_name = Column(
        String(150),
        nullable=False
    )

    feature_value = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )
    
        # Relationships
    car = relationship("Cars", back_populates="features", foreign_keys=[car_id])

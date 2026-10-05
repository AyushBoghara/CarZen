import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Numeric,
    Enum,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.PredictionEnums import PredictionStatus


class PricePredictions(Base):
    __tablename__ = "price_predictions"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    car_id = Column(
        BigInteger,
        ForeignKey("cars.id"),
        nullable=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    prediction_status = Column(
        Enum(PredictionStatus),
        default=PredictionStatus.REQUESTED
    )

    predicted_price = Column(
        Numeric(15, 2),
        nullable=True
    )

    minimum_price = Column(
        Numeric(15, 2),
        nullable=True
    )

    maximum_price = Column(
        Numeric(15, 2),
        nullable=True
    )

    confidence_score = Column(
        Numeric(5, 2),
        nullable=True
    )

    model_name = Column(
        String(150),
        nullable=True
    )

    model_version = Column(
        String(100),
        nullable=True
    )

    prediction_input = Column(
        JSON,
        nullable=True
    )

    prediction_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )
    
    
    # Relationships
    car = relationship("Cars", back_populates="price_predictions", foreign_keys=[car_id])
    user = relationship("User", back_populates="price_predictions", foreign_keys=[user_id])
    features = relationship("PredictionFeatures", back_populates="prediction", foreign_keys="PredictionFeatures.prediction_id")
 

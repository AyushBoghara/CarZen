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


class PredictionFeatures(Base):
    __tablename__ = "prediction_features"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    prediction_id = Column(
        BigInteger,
        ForeignKey("price_predictions.id"),
        nullable=False
    )

    feature_name = Column(
        String(100),
        nullable=False
    )

    feature_value = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )
    
    
    # Relationships
    prediction = relationship("PricePredictions", back_populates="features", foreign_keys=[prediction_id])
 

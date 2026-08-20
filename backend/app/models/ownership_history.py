import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Date,
    Integer,
    Numeric,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.CarEnums import OwnershipType


class OwnershipHistory(Base):
    __tablename__ = "ownership_history"

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

    owner_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    ownership_number = Column(
        Integer,
        nullable=False
    )

    ownership_type = Column(
        Enum(OwnershipType),
        nullable=True
    )

    purchase_date = Column(
        Date,
        nullable=True
    )

    sale_date = Column(
        Date,
        nullable=True
    )

    purchase_price = Column(
        Numeric(15, 2),
        nullable=True
    )

    sale_price = Column(
        Numeric(15, 2),
        nullable=True
    )

    purchase_location = Column(
        String(150),
        nullable=True
    )

    sale_location = Column(
        String(150),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )
    
    # Relationships
    car = relationship("Cars", back_populates="ownership_history", foreign_keys=[car_id])
    owner = relationship("User", back_populates="ownership_history", foreign_keys=[owner_id])
 

import datetime

from sqlalchemy import (
    Column,
    BigInteger,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Favorites(Base):
    __tablename__ = "favorites"

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
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )
    
    __table_args__ = (
        UniqueConstraint("user_id", "car_id", name="uq_favorites_user_car"),
    )
 
    # Relationships
    user = relationship("User", back_populates="favorites", foreign_keys=[user_id])
    car = relationship("Cars", back_populates="favorites", foreign_keys=[car_id])


from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Float,
)
from sqlalchemy.orm import relationship

from app.database.connection.conn import Base


class CarPricePredict(Base):
    __tablename__ = "car_price_predict"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    km_driven = Column(BigInteger, nullable=False)
    fuel = Column(String(50), nullable=False)
    seller_type = Column(String(50), nullable=False)
    transmission = Column(String(50), nullable=False)
    owner = Column(String(50), nullable=False)

    mileage = Column(Float, nullable=False)
    engine = Column(Float, nullable=False)
    max_power = Column(Float, nullable=False)
    seats = Column(Integer, nullable=False)

    predicted_price = Column(BigInteger, nullable=False)

    user = relationship(
        "User",
        back_populates="car_price_predict",
        foreign_keys=[user_id],
    )

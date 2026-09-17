import datetime

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.OrderEnums import OrderStatus
from app.models.enums.TransactionEnums import PaymentStatus


class Orders(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    listing_id = Column(BigInteger, ForeignKey("listings.id"), nullable=False)
    car_id = Column(BigInteger, ForeignKey("cars.id"), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    seller_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)

    listing = relationship("Listings", back_populates="orders", foreign_keys=[listing_id])
    car = relationship("Cars", back_populates="orders", foreign_keys=[car_id])
    buyer = relationship("User", back_populates="orders_bought", foreign_keys=[buyer_id])
    seller = relationship("User", back_populates="orders_sold", foreign_keys=[seller_id])
    payments = relationship("Payments", back_populates="order", foreign_keys="Payments.order_id")

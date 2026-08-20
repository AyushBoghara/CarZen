import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Text,
    Numeric,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base

from app.models.enums.TransactionEnums import (
    PaymentMethod,
    PaymentStatus,
    TransactionStatus
)


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    listing_id = Column(
        BigInteger,
        ForeignKey("listings.id"),
        nullable=False
    )

    car_id = Column(
        BigInteger,
        ForeignKey("cars.id"),
        nullable=False
    )

    buyer_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    seller_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    final_price = Column(
        Numeric(15, 2),
        nullable=False
    )

    transaction_date = Column(
        DateTime,
        nullable=True
    )

    payment_method = Column(
        Enum(PaymentMethod),
        nullable=True
    )

    payment_status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING
    )

    transaction_status = Column(
        Enum(TransactionStatus),
        default=TransactionStatus.INITIATED
    )

    notes = Column(
        Text,
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
    
    
    # Relationships
    listing = relationship("Listings", back_populates="transactions", foreign_keys=[listing_id])
    car = relationship("Cars", back_populates="transactions", foreign_keys=[car_id])
    buyer = relationship("User", back_populates="transactions_bought", foreign_keys=[buyer_id])
    seller = relationship("User", back_populates="transactions_sold", foreign_keys=[seller_id])
 
    payments = relationship("Payments", back_populates="transaction", foreign_keys="Payments.transaction_id")

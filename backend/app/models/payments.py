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

from app.models.enums.TransactionEnums import (
    PaymentMethod,
    PaymentStatus
)


class Payments(Base):
    __tablename__ = "payments"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    transaction_id = Column(
        BigInteger,
        ForeignKey("transactions.id"),
        nullable=False
    )

    amount = Column(
        Numeric(15, 2),
        nullable=False
    )

    currency = Column(
        String(10),
        default="INR"
    )

    payment_method = Column(
        Enum(PaymentMethod),
        nullable=True
    )

    provider = Column(
        String(100),
        nullable=True
    )

    provider_transaction_id = Column(
        String(255),
        nullable=True
    )

    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING
    )

    payment_date = Column(
        DateTime,
        nullable=True
    )

    provider_metadata = Column(
        "metadata",
        JSON,
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
    transaction = relationship("Transactions", back_populates="payments", foreign_keys=[transaction_id])

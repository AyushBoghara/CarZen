import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Integer,
    Numeric,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ServiceItems(Base):
    __tablename__ = "service_items"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    service_record_id = Column(
        BigInteger,
        ForeignKey("service_records.id"),
        nullable=False
    )

    item_name = Column(
        String(150),
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1
    )

    unit_cost = Column(
        Numeric(15, 2),
        nullable=True
    )

    total_cost = Column(
        Numeric(15, 2),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )
    
        # Relationships
    service_record = relationship("ServiceRecords", back_populates="items", foreign_keys=[service_record_id])

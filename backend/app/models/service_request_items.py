import datetime
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.database.connection.conn import Base


class ServiceRequestItems(Base):
    __tablename__ = "service_request_items"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    service_request_id = Column(
        BigInteger,
        ForeignKey("service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    service_id = Column(
        BigInteger,
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    service_name = Column(
        String(150),
        nullable=False,
    )

    unit_price = Column(
        Numeric(15, 2),
        nullable=False,
    )

    duration_minutes = Column(
        Integer,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    # Relationships
    service_request = relationship(
        "ServiceRequests",
        back_populates="items",
        foreign_keys=[service_request_id],
    )
    service = relationship(
        "Services",
        foreign_keys=[service_id],
    )

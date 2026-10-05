import datetime
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from app.database.connection.conn import Base
from app.models.enums.ServiceEnums import ServiceRequestStatus


class ServiceRequests(Base):
    __tablename__ = "service_requests"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    car_id = Column(
        BigInteger,
        ForeignKey("cars.id"),
        nullable=False,
        index=True,
    )

    service_id = Column(
        BigInteger,
        ForeignKey("services.id"),
        nullable=True,
        index=True,
    )

    address_id = Column(
        BigInteger,
        ForeignKey("addresses.id"),
        nullable=True,
        index=True,
    )

    scheduled_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    scheduled_time = Column(
        Time,
        nullable=False,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    amount = Column(
        Numeric(15, 2),
        nullable=False,
    )

    payment_status = Column(
        String(50),
        nullable=False,
        default="unpaid",
        index=True,
    )

    payment_method = Column(
        String(50),
        nullable=True,
    )

    status = Column(
        Enum(
            ServiceRequestStatus,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=ServiceRequestStatus.REQUESTED,
        index=True,
    )

    admin_note = Column(
        Text,
        nullable=True,
    )

    service_record_id = Column(
        BigInteger,
        ForeignKey("service_records.id"),
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    deleted_at = Column(
        DateTime,
        nullable=True,
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="service_requests", foreign_keys=[user_id])
    car = relationship("Cars", back_populates="service_requests", foreign_keys=[car_id])
    service = relationship("Services", back_populates="requests", foreign_keys=[service_id])
    service_record = relationship("ServiceRecords", back_populates="service_request", foreign_keys=[service_record_id])
    payments = relationship("Payments", back_populates="service_request", foreign_keys="Payments.service_request_id")
    items = relationship("ServiceRequestItems", back_populates="service_request", cascade="all, delete-orphan", foreign_keys="ServiceRequestItems.service_request_id")
    address = relationship("Address", foreign_keys=[address_id])

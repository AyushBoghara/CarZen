import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Date,
    Text,
    Numeric,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.ServiceEnums import ServiceStatus

class ServiceRecords(Base):
    __tablename__ = "service_records"

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

    service_center_id = Column(
        BigInteger,
        nullable=True
    )

    service_type = Column(
        String(150),
        nullable=False
    )

    service_date = Column(
        Date,
        nullable=False
    )

    odometer_reading = Column(
        Numeric(12, 2),
        nullable=True
    )

    service_cost = Column(
        Numeric(15, 2),
        nullable=True
    )

    parts_cost = Column(
        Numeric(15, 2),
        nullable=True
    )

    labor_cost = Column(
        Numeric(15, 2),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    next_service_date = Column(
        Date,
        nullable=True
    )

    next_service_mileage = Column(
        Numeric(12, 2),
        nullable=True
    )

    status = Column(
        Enum(
            ServiceStatus,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        default=ServiceStatus.COMPLETED,
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
    car = relationship("Cars", back_populates="service_records", foreign_keys=[car_id])
    items = relationship("ServiceItems", back_populates="service_record", foreign_keys="ServiceItems.service_record_id")
    service_request = relationship("ServiceRequests", back_populates="service_record", uselist=False, foreign_keys="ServiceRequests.service_record_id")

 
    
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
        ForeignKey("service_centers.id"),
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
        Enum(ServiceStatus),
        default=ServiceStatus.COMPLETED
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
    service_center = relationship("ServiceCenters", back_populates="service_records", foreign_keys=[service_center_id])
    items = relationship("ServiceItems", back_populates="service_record", foreign_keys="ServiceItems.service_record_id")
 
    
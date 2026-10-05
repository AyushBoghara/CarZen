import datetime
from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database.connection.conn import Base


class Services(Base):
    __tablename__ = "services"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    price = Column(
        Numeric(15, 2),
        nullable=False,
    )

    duration_minutes = Column(
        Integer,
        nullable=True,
    )

    image_url = Column(
        String(500),
        nullable=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="active",
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
    requests = relationship("ServiceRequests", back_populates="service")

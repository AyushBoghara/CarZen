import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    Text,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.ReportEnums import ReportReason, ReportStatus

class Reports(Base):
    __tablename__ = "reports"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    reporter_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    listing_id = Column(
        BigInteger,
        ForeignKey("listings.id"),
        nullable=True
    )

    car_id = Column(
        BigInteger,
        ForeignKey("cars.id"),
        nullable=True
    )

    reason = Column(
        Enum(
            ReportReason,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        Enum(
            ReportStatus,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=ReportStatus.PENDING
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )

    resolved_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    admin_note = Column(Text, nullable=True)
    
    
    # Relationships
    reporter = relationship("User", back_populates="reports", foreign_keys=[reporter_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    listing = relationship("Listings", back_populates="reports", foreign_keys=[listing_id])
    car = relationship("Cars", back_populates="reports", foreign_keys=[car_id])
 

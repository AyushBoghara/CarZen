import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    notification_type = Column(
        String(100),
        nullable=True
    )

    reference_id = Column(
        BigInteger,
        nullable=True
    )

    reference_type = Column(
        String(100),
        nullable=True
    )

    is_read = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )
    
        # Relationships
    user = relationship("User", back_populates="notifications", foreign_keys=[user_id])
 

import datetime

from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.PredictionEnums import AdminRole


class Admins(Base):
    __tablename__ = "admins"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    role = Column(
        Enum(AdminRole),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
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
    user = relationship("User", back_populates="admin", foreign_keys=[user_id])

import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.enums.CarEnums import MediaType


class CarMedia(Base):
    __tablename__ = "car_media"

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

    media_type = Column(
        Enum(MediaType),
        nullable=False
    )

    media_url = Column(
        String(500),
        nullable=False
    )

    thumbnail_url = Column(
        String(500),
        nullable=True
    )

    file_name = Column(
        String(255),
        nullable=True
    )

    file_size = Column(
        BigInteger,
        nullable=True
    )

    sort_order = Column(
        Integer,
        default=0
    )

    is_primary = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    deleted_at = Column(
        DateTime,
        nullable=True
    )
    
    # Relationships
    car = relationship("Cars", back_populates="media", foreign_keys=[car_id])
 

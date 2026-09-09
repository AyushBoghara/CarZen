import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Date,
    Text,
    Integer,
    Numeric,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.connection import Base

from app.models.enums.CarEnums import (
    FuelType,
    TransmissionType,
    OwnershipType,
    CarCondition,
    CarApprovalStatus,
)


class Cars(Base):
    __tablename__ = "cars"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    variant_id = Column(
        BigInteger,
        ForeignKey("car_variants.id"),
        nullable=False
    )

    owner_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    registration_number = Column(
        String(30),
        unique=True,
        nullable=True
    )

    vin_number = Column(
        String(100),
        unique=True,
        nullable=True
    )

    manufacturing_year = Column(
        Integer,
        nullable=False
    )

    registration_year = Column(
        Integer,
        nullable=True
    )

    fuel_type = Column(
        Enum(FuelType),
        nullable=False
    )

    transmission = Column(
        Enum(TransmissionType),
        nullable=False
    )

    engine_cc = Column(
        Numeric(8, 2),
        nullable=True
    )

    horsepower = Column(
        Numeric(8, 2),
        nullable=True
    )

    mileage_km = Column(
        Numeric(12, 2),
        nullable=False
    )

    color = Column(
        String(50),
        nullable=True
    )

    seating_capacity = Column(
        Integer,
        nullable=True
    )

    owner_count = Column(
        Integer,
        default=1
    )

    ownership_type = Column(
        Enum(OwnershipType),
        nullable=True
    )

    condition = Column(
        Enum(CarCondition),
        nullable=True
    )

    insurance_company = Column(
        String(150),
        nullable=True
    )

    insurance_type = Column(
        String(100),
        nullable=True
    )

    insurance_expiry = Column(
        Date,
        nullable=True
    )

    rc_status = Column(
        String(50),
        nullable=True
    )

    city = Column(
        String(100),
        nullable=False
    )

    state = Column(
        String(100),
        nullable=False
    )

    country = Column(
        String(100),
        nullable=False,
        default="India"
    )

    postal_code = Column(
        String(10),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    expected_market_price = Column(
        Numeric(15, 2),
        nullable=True
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    approval_status = Column(
        Enum(
            CarApprovalStatus,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=CarApprovalStatus.PENDING_APPROVAL,
    )

    rejection_reason = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )

    deleted_at = Column(
        DateTime,
        nullable=True
    )
    
     # Relationships
    variant = relationship("CarVariants", back_populates="cars", foreign_keys=[variant_id])
    owner = relationship("User", back_populates="cars_owned", foreign_keys=[owner_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
 
    media = relationship("CarMedia", back_populates="car", foreign_keys="CarMedia.car_id")
    features = relationship("CarFeatures", back_populates="car", foreign_keys="CarFeatures.car_id")
    listings = relationship("Listings", back_populates="car", foreign_keys="Listings.car_id")
    ownership_history = relationship("OwnershipHistory", back_populates="car", foreign_keys="OwnershipHistory.car_id")
    service_records = relationship("ServiceRecords", back_populates="car", foreign_keys="ServiceRecords.car_id")
    favorites = relationship("Favorites", back_populates="car", foreign_keys="Favorites.car_id")
    transactions = relationship("Transactions", back_populates="car", foreign_keys="Transactions.car_id")
    price_predictions = relationship("PricePredictions", back_populates="car", foreign_keys="PricePredictions.car_id")
    reviews = relationship("Reviews", back_populates="car", foreign_keys="Reviews.car_id")
    reports = relationship("Reports", back_populates="car", foreign_keys="Reports.car_id")
 

from datetime import datetime, timezone 
from sqlalchemy import Column, String, BigInteger, Enum, DateTime 
from sqlalchemy.orm import relationship 
 
from app.database.connection.conn import Base 
from app.models.enums.UserStatus import UserStatus 
from app.models.enums.UserRoles import UserRoles 
 
class User(Base): 
    __tablename__ = "users" 
 
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True) 
    first_name = Column(String(100), nullable=False) 
    last_name = Column(String(100), nullable=True) 
    username = Column(String(100), unique=True, nullable=False, index=True) 
    email = Column(String(255), unique=True, nullable=False, index=True) 
    password = Column(String(255), nullable=False) 
    phone_number = Column(String(20), unique=True, nullable=True) 
    role = Column(Enum(UserRoles), nullable=False, default=UserRoles.USER) 
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE) 
    profile_image_url = Column(String(500), nullable=True) 
 
    # Use timezone-aware UTC default markers
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) 
    deleted_at = Column(DateTime, nullable=True) 
     
    # Relationships 
    addresses = relationship("Addresses", back_populates="user", foreign_keys="Addresses.user_id")
    cars_owned = relationship("Cars", back_populates="owner", foreign_keys="Cars.owner_id")
    listings = relationship("Listings", back_populates="seller", foreign_keys="Listings.seller_id")
    ownership_history = relationship("OwnershipHistory", back_populates="owner", foreign_keys="OwnershipHistory.owner_id")
    service_centers = relationship("ServiceCenters", back_populates="owner", foreign_keys="ServiceCenters.owner_id")
    favorites = relationship("Favorites", back_populates="user", foreign_keys="Favorites.user_id")
    notifications = relationship("Notifications", back_populates="user", foreign_keys="Notifications.user_id")
    reports = relationship("Reports", back_populates="reporter", foreign_keys="Reports.reporter_id")

    inquiries_made = relationship("Inquiries", back_populates="buyer", foreign_keys="Inquiries.buyer_id")
    inquiries_received = relationship("Inquiries", back_populates="seller", foreign_keys="Inquiries.seller_id")

    transactions_bought = relationship("Transactions", back_populates="buyer", foreign_keys="Transactions.buyer_id")
    transactions_sold = relationship("Transactions", back_populates="seller", foreign_keys="Transactions.seller_id")

    price_predictions = relationship("PricePredictions", back_populates="user", foreign_keys="PricePredictions.user_id")
    reviews = relationship("Reviews", back_populates="user", foreign_keys="Reviews.user_id")
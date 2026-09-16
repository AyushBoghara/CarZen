import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ListingViews(Base):
    __tablename__ = "listing_views"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    listing_id = Column(BigInteger, ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("listing_id", "buyer_id", name="uq_listing_views_listing_buyer"),
    )

    listing = relationship("Listings", back_populates="views", foreign_keys=[listing_id])
    buyer = relationship("User", back_populates="listing_views", foreign_keys=[buyer_id])

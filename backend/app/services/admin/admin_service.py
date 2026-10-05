from datetime import datetime
from sqlalchemy.orm import Session, selectinload

from app.models.enums.ListingEnums import ListingStatus
from app.models.listings import Listings
from app.services.car.catalog_service import paginate


def list_admin_listings(
    db: Session,
    page: int = 1,
    limit: int = 20,
    status: ListingStatus | None = None,
    seller_id: int | None = None,
    car_id: int | None = None,
):
    query = (
        db.query(Listings)
        .options(
            selectinload(Listings.car),
            selectinload(Listings.seller),
        )
        .filter(Listings.deleted_at.is_(None))
    )
    if status:
        query = query.filter(Listings.listing_status == status)
    if seller_id:
        query = query.filter(Listings.seller_id == seller_id)
    if car_id:
        query = query.filter(Listings.car_id == car_id)

    return paginate(query.order_by(Listings.created_at.desc(), Listings.id.desc()), page, limit)


def get_admin_listing(db: Session, listing_id: int) -> Listings:
    listing = (
        db.query(Listings)
        .options(
            selectinload(Listings.car),
            selectinload(Listings.seller),
        )
        .filter(Listings.id == listing_id, Listings.deleted_at.is_(None))
        .first()
    )
    if not listing:
        raise LookupError("Listing not found.")
    return listing


def approve_listing(db: Session, listing_id: int, reason: str | None = None) -> Listings:
    listing = get_admin_listing(db, listing_id)
    listing.listing_status = ListingStatus.APPROVED
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    return listing


def reject_listing(db: Session, listing_id: int, reason: str | None = None) -> Listings:
    listing = get_admin_listing(db, listing_id)
    listing.listing_status = ListingStatus.REJECTED
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    return listing


def suspend_listing(db: Session, listing_id: int, reason: str | None = None) -> Listings:
    listing = get_admin_listing(db, listing_id)
    listing.listing_status = ListingStatus.SUSPENDED
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    return listing


def delete_admin_listing(db: Session, listing_id: int) -> None:
    listing = get_admin_listing(db, listing_id)
    listing.deleted_at = datetime.utcnow()
    listing.listing_status = ListingStatus.REMOVED
    db.commit()

from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.models.enums.CarEnums import CarApprovalStatus
from app.models.enums.ListingEnums import ListingStatus
from app.models.cars import Cars
from app.models.favorites import Favorites
from app.models.listings import Listings
from app.models.users import User
from app.services.car import car_service
from app.services.car.catalog_service import paginate
from app.schemas.cars_schema import CarDetailResponse
from app.models.car_variants import CarVariants
from app.models.car_models import CarModels


def create_listing(db: Session, car_id: int, user: User, values: dict) -> Listings:
    car_service.get_owned_car(db, car_id, user)
    if db.query(Listings).filter(Listings.car_id == car_id, Listings.deleted_at.is_(None)).first():
        raise ValueError("An active listing already exists for this car.")
    listing = Listings(car_id=car_id, seller_id=user.id, listing_status=ListingStatus.DRAFT, **values)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def get_owned_listing(db: Session, car_id: int, user: User) -> Listings:
    listing = _get_listing_for_car(db, car_id)
    if listing.seller_id != user.id: raise PermissionError("You do not own this listing.")
    return listing


def get_listing(db: Session, listing_id: int, public_only: bool = True) -> Listings:
    query = db.query(Listings).filter(Listings.id == listing_id, Listings.deleted_at.is_(None))
    if public_only: 
        query = query.filter(Listings.listing_status == ListingStatus.ACTIVE)
    listing = query.first()
    if not listing: 
        raise LookupError("Listing not found.")
    return listing

# get all infomations for car
def get_listings(
    db: Session,
    listing_id: int,
    public_only: bool = True,
) -> Listings:

    query = (
        db.query(Listings)
        .options(
            selectinload(Listings.car)
            .selectinload(Cars.variant)
            .selectinload(CarVariants.model)
            .selectinload(CarModels.brand),

            selectinload(Listings.car)
            .selectinload(Cars.media),

            selectinload(Listings.car)
            .selectinload(Cars.features),
        )
        .filter(
            Listings.id == listing_id,
            Listings.deleted_at.is_(None),
        )
    )

    if public_only:
        query = query.filter(
            Listings.listing_status == ListingStatus.ACTIVE
        )

    listing = query.first()

    if not listing:
        raise LookupError("Listing not found.")

    return listing

def update_listing(db: Session, car_id: int, user: User, values: dict) -> Listings:
    listing = get_owned_listing(db, car_id, user)
    if not values: raise ValueError("Provide at least one field to update.")
    for field, value in values.items(): setattr(listing, field, value)
    listing.updated_at = datetime.now(timezone.utc); db.commit(); db.refresh(listing); return listing


def delete_listing(db: Session, car_id: int, user: User) -> None:
    listing = get_owned_listing(db, car_id, user); 
    listing.deleted_at = datetime.now(timezone.utc); 
    listing.listing_status = ListingStatus.REMOVED; 
    db.commit()


def publish_listing(db: Session, car_id: int, user: User, publish: bool) -> Listings:
    listing = get_owned_listing(db, car_id, user); car = car_service.get_owned_car(db, car_id, user)
    if publish:
        if not car.is_verified or car.approval_status not in {CarApprovalStatus.APPROVED, CarApprovalStatus.PUBLISHED}:
            raise ValueError("Only approved cars can be published.")
        listing.listing_status = ListingStatus.ACTIVE; listing.listed_at = datetime.now(timezone.utc); car.approval_status = CarApprovalStatus.PUBLISHED
    else:
        listing.listing_status = ListingStatus.DRAFT
    db.commit()
    db.refresh(listing); return listing


def list_public_listings(db: Session, page: int, limit: int, **filters):
    query = db.query(Listings).join(Listings.car).filter(Listings.deleted_at.is_(None), Listings.listing_status == ListingStatus.ACTIVE, Cars.is_verified.is_(True))
    car_query = car_service._filtered_query(db, **filters).with_entities(Cars.id)
    query = query.filter(Listings.car_id.in_(car_query))
    return paginate(query.order_by(Listings.listed_at.desc()), page, limit)


def add_favorite(db: Session, car_id: int, user: User) -> Favorites:
    car_service.get_car(db, car_id)
    favorite = db.query(Favorites).filter(Favorites.user_id == user.id, Favorites.car_id == car_id).first()
    if favorite:
        raise ValueError("Car is already in favorites.")
    favorite = Favorites(user_id=user.id, car_id=car_id); 
   
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, car_id: int, user: User) -> None:
    favorite = db.query(Favorites).filter(Favorites.user_id == user.id, Favorites.car_id == car_id).first()
    if not favorite: 
        raise LookupError("Favorite not found.")
    db.delete(favorite)
    db.commit()


def list_favorites(db: Session, user: User) -> list[Favorites]:
    return db.query(Favorites).filter(Favorites.user_id == user.id).order_by(Favorites.created_at.desc()).all()




def _get_listing_for_car(db: Session, car_id: int) -> Listings:
    listing = db.query(Listings).filter(Listings.car_id == car_id, Listings.deleted_at.is_(None)).first()
    if not listing: 
        raise LookupError("Listing not found.")
    return listing

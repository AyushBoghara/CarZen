from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.enums.CarEnums import CarCondition, FuelType, TransmissionType
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.marketplace_schema import FavoriteResponse, ListingCreate, ListingResponse, ListingUpdate,ListingResponseSecond
from app.schemas.users_schema import MessageResponse
from app.services.car import marketplace_service

router = APIRouter()


def _raise(exc):
    code = 404 if isinstance(exc, LookupError) else 403 if isinstance(exc, PermissionError) else 409 if isinstance(exc, ValueError) else 400
    raise HTTPException(code, str(exc)) from exc


@router.post("/cars/{car_id}/listing", response_model=ListingResponse, status_code=201, tags=["Listings"])
def create_listing(car_id: int, payload: ListingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return marketplace_service.create_listing(db, car_id, user, payload.model_dump())
    except Exception as exc: 
        _raise(exc)

@router.get("/cars/{car_id}/listing", response_model=ListingResponse, tags=["Listings"])
def get_owned_listing(car_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return marketplace_service.get_owned_listing(db, car_id, user)
    except Exception as exc: 
        _raise(exc)

@router.patch("/cars/{car_id}/listing", response_model=ListingResponse, tags=["Listings"])
def update_listing(car_id: int, payload: ListingUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try: 
        return marketplace_service.update_listing(db, car_id, user, payload.model_dump(exclude_unset=True))
    except Exception as exc: 
        _raise(exc)

@router.delete("/cars/{car_id}/listing", response_model=MessageResponse, tags=["Listings"])
def delete_listing(car_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try: 
        marketplace_service.delete_listing(db, car_id, user)
        return {"message": "Listing deleted successfully."}
    except Exception as exc:
        _raise(exc)

@router.post("/cars/{car_id}/listing/publish", response_model=ListingResponse, tags=["Listings"])
def publish_listing(car_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try: return marketplace_service.publish_listing(db, car_id, user, True)
    except Exception as exc: _raise(exc)

@router.post("/cars/{car_id}/listing/unpublish", response_model=ListingResponse, tags=["Listings"])
def unpublish_listing(car_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try: return marketplace_service.publish_listing(db, car_id, user, False)
    except Exception as exc: _raise(exc)

@router.get("/listings", response_model=PaginatedResponse[ListingResponse], tags=["Listings"])
def list_public_listings(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), brand_id: int | None = None, model_id: int | None = None, variant_id: int | None = None, fuel_type: FuelType | None = None, transmission: TransmissionType | None = None, city: str | None = None, state: str | None = None, min_price: Decimal | None = Query(None, ge=0), max_price: Decimal | None = Query(None, ge=0), min_year: int | None = Query(None, ge=1886), max_year: int | None = Query(None, ge=1886), min_mileage: Decimal | None = Query(None, ge=0), max_mileage: Decimal | None = Query(None, ge=0), condition: CarCondition | None = None, db: Session = Depends(get_db)):
    filters = dict(brand_id=brand_id, model_id=model_id, variant_id=variant_id, fuel_type=fuel_type, transmission=transmission, city=city, state=state, min_price=min_price, max_price=max_price, min_year=min_year, max_year=max_year, min_mileage=min_mileage, max_mileage=max_mileage, condition=condition)
    data, pagination = marketplace_service.list_public_listings(db, page, limit, **filters)
    return {"data": data, "pagination": pagination}

@router.get("/listings/{listing_id}", response_model=ListingResponseSecond, tags=["Listings"])
def get_public_listing(listing_id: int, db: Session = Depends(get_db)):
    try:
        listing = marketplace_service.get_listings(db, listing_id)
        
        listing.views_count = (listing.views_count or 0) + 1
        
        db.commit()
        db.refresh(listing)
        
        return listing
    except Exception as exc:
        _raise(exc)


@router.post("/cars/{car_id}/favorite", response_model=FavoriteResponse, status_code=201, tags=["Favorites"])
def add_favorite(car_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try: 
        return marketplace_service.add_favorite(db, car_id, user)
    except Exception as exc:
        _raise(exc)

@router.delete("/cars/{car_id}/favorite", response_model=MessageResponse, tags=["Favorites"])
def remove_favorite(car_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try: 
        marketplace_service.remove_favorite(db, car_id, user)
        return {"message": "Favorite removed successfully."}
    except Exception as exc: 
        _raise(exc)

@router.get("/users/me/favorites", response_model=list[FavoriteResponse], tags=["Favorites"])
def list_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return marketplace_service.list_favorites(db, user)

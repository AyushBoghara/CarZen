from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin, get_current_user
from app.database.connection.conn import get_db
from app.models.enums.CarEnums import CarApprovalStatus, FuelType, MediaType, TransmissionType
from app.models.enums.UserRoles import UserRoles
from app.models.users import User
from app.schemas.cars_schema import CarCreate, CarDetailResponse, CarFeatureCreate, CarFeatureResponse, CarFeatureUpdate, CarMediaReorderRequest, CarMediaResponse, CarMediaUpdate, CarRejectionRequest, CarResponse, CarUpdate, PaginatedResponse
from app.schemas.users_schema import MessageResponse
from app.services.car import car_service, feature_service, media_service

router = APIRouter()


def _raise(exc: Exception):
    if isinstance(exc, LookupError) and "not among the defined enum values" not in str(exc): code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, PermissionError): code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ValueError): code = status.HTTP_409_CONFLICT
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the car request.",
        ) from exc
    raise HTTPException(code, str(exc)) from exc


def _page_result(data, pagination): 
    return {"data": data, "pagination": pagination}

def _managed_car(db: Session, car_id: int, user: User):
    return car_service.get_owned_car(db, car_id, user, allow_admin=user.role == UserRoles.ADMIN)


@router.post("/cars", response_model=CarResponse, status_code=201, summary="Seller adds a new car or reseller adds a resale car", tags=["Cars"])
def create_car(payload: CarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        return car_service.create_car(db, current_user, payload.model_dump())
    except Exception as exc: 
        _raise(exc)


@router.get("/cars", response_model=PaginatedResponse[CarResponse], summary="List the current user's cars", tags=["Cars"])
def list_my_cars(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), search: str | None = None, verification_status: bool | None = None, approval_status: CarApprovalStatus | None = Query(None, alias="status"), brand_id: int | None = None, model_id: int | None = None, variant_id: int | None = None, fuel_type: FuelType | None = None, transmission: TransmissionType | None = None, city: str | None = None, state: str | None = None, min_price: Decimal | None = Query(None, ge=0), max_price: Decimal | None = Query(None, ge=0), min_year: int | None = Query(None, ge=1886), max_year: int | None = Query(None, ge=1886), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data, pagination = car_service.list_cars(db, page, limit, owner_id=current_user.id, search=search, verification_status=verification_status, approval_status=approval_status, brand_id=brand_id, model_id=model_id, variant_id=variant_id, fuel_type=fuel_type, transmission=transmission, city=city, state=state, min_price=min_price, max_price=max_price, min_year=min_year, max_year=max_year)
    return _page_result(data, pagination)


@router.get("/cars/{car_id}", response_model=CarDetailResponse, summary="Get one owned car with details", tags=["Cars"])
def get_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return car_service.detail_payload(_managed_car(db, car_id, current_user))
    except Exception as exc: 
        _raise(exc)


@router.patch("/cars/{car_id}", response_model=CarResponse, summary="Partially update an owned car", tags=["Cars"])
def update_car(car_id: int, payload: CarUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        return car_service.update_car(db, car_id, current_user, payload.model_dump(exclude_unset=True), allow_admin=current_user.role == UserRoles.ADMIN)
    except Exception as exc: 
        _raise(exc)


@router.delete("/cars/{car_id}", response_model=MessageResponse, summary="Soft-delete an owned car", tags=["Cars"])
def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        car_service.soft_delete_car(db, car_id, current_user, allow_admin=current_user.role == UserRoles.ADMIN); return {"message": "Car deleted successfully."}
    except Exception as exc:
        _raise(exc)


@router.get("/cars/{car_id}/media", response_model=list[CarMediaResponse], tags=["Car Media"])
def list_media(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: _managed_car(db, car_id, current_user); return media_service.list_media(db, car_id)
    except Exception as exc: _raise(exc)

@router.post("/cars/{car_id}/media", response_model=CarMediaResponse, status_code=201, tags=["Car Media"])
async def upload_media(car_id: int, file: UploadFile = File(...), media_type: MediaType = Form(...), sort_order: int = Form(0), is_primary: bool = Form(False), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        _managed_car(db, car_id, current_user)
        return media_service.create_media(db, car_id, media_type, file.filename or "", await file.read(), sort_order, is_primary)
    except Exception as exc: 
        _raise(exc)
    finally: 
        await file.close()

@router.patch("/cars/{car_id}/media/reorder", response_model=list[CarMediaResponse], tags=["Car Media"])
def reorder_media(car_id: int, payload: CarMediaReorderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        _managed_car(db, car_id, current_user)
        return media_service.reorder_media(db, car_id, [item.model_dump() for item in payload.media])
    except Exception as exc:
        _raise(exc)

@router.patch("/cars/{car_id}/media/{media_id}", response_model=CarMediaResponse, tags=["Car Media"])
def update_media(car_id: int, media_id: int, payload: CarMediaUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        _managed_car(db, car_id, current_user)
        return media_service.update_media(db, car_id, media_id, payload.model_dump(exclude_unset=True))
    except Exception as exc: 
        _raise(exc)

@router.delete("/cars/{car_id}/media/{media_id}", response_model=MessageResponse, tags=["Car Media"])
def delete_media(car_id: int, media_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        
        _managed_car(db, car_id, current_user); 
        
        media_service.delete_media(db, car_id, media_id); 
        
        return {"message":"Media deleted successfully."}
    
    except Exception as exc: 
        _raise(exc)

@router.patch("/cars/{car_id}/media/{media_id}/primary", response_model=CarMediaResponse, tags=["Car Media"])
def set_primary_media(car_id: int, media_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        _managed_car(db, car_id, current_user) 
        return media_service.set_primary(db, car_id, media_id)
    except Exception as exc: 
        _raise(exc)


@router.get("/cars/{car_id}/features", response_model=list[CarFeatureResponse], tags=["Car Features"])
def list_features(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        _managed_car(db, car_id, current_user)
        return feature_service.list_features(db, car_id)
    except Exception as exc: 
        _raise(exc)

@router.post("/cars/{car_id}/features", response_model=CarFeatureResponse, status_code=201, tags=["Car Features"])
def create_feature(car_id: int, payload: CarFeatureCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        _managed_car(db, car_id, current_user); return feature_service.create_feature(db, car_id, payload.model_dump())
    except Exception as exc:
        _raise(exc)

@router.patch("/cars/{car_id}/features/{feature_id}", response_model=CarFeatureResponse, tags=["Car Features"])
def update_feature(car_id: int, feature_id: int, payload: CarFeatureUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        _managed_car(db, car_id, current_user); 
        return feature_service.update_feature(db, car_id, feature_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        _raise(exc)

@router.delete("/cars/{car_id}/features/{feature_id}", response_model=MessageResponse, tags=["Car Features"])
def delete_feature(car_id: int, feature_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try: 
        _managed_car(db, car_id, current_user)
        feature_service.delete_feature(db, car_id, feature_id)
        return {"message": "Feature deleted successfully."}
    except Exception as exc: 
        _raise(exc)


@router.get("/admin/cars", response_model=PaginatedResponse[CarResponse], tags=["Admin Cars"])
def list_admin_cars(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), search: str | None = None, owner_id: int | None = None, brand_id: int | None = None, model_id: int | None = None, variant_id: int | None = None, city: str | None = None, state: str | None = None, fuel_type: FuelType | None = None, transmission: TransmissionType | None = None, verification_status: bool | None = None, approval_status: CarApprovalStatus | None = Query(None, alias="status"), db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    data, pagination = car_service.list_cars(db, page, limit, owner_id=owner_id, search=search, brand_id=brand_id, model_id=model_id, variant_id=variant_id, city=city, state=state, fuel_type=fuel_type, transmission=transmission, verification_status=verification_status, approval_status=approval_status)
    return _page_result(data, pagination)

@router.get("/admin/cars/{car_id}", response_model=CarDetailResponse, tags=["Admin Cars"])
def get_admin_car(car_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try:
        return car_service.detail_payload(car_service.get_car(db, car_id))
    except Exception as exc: 
        _raise(exc)

@router.post("/admin/cars/{car_id}/approve", response_model=CarDetailResponse, tags=["Admin Cars"])
def approve_car(car_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        car = car_service.approve_car(db, car_id, admin)
        return car_service.detail_payload(car)
    except Exception as exc:
        _raise(exc)

@router.post("/admin/cars/{car_id}/reject", response_model=CarDetailResponse, tags=["Admin Cars"])
def reject_car(car_id: int, payload: CarRejectionRequest, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        return car_service.detail_payload(car_service.reject_car(db, car_id, admin, payload.reason))
    except Exception as exc: 
        _raise(exc)

@router.post("/admin/cars/{car_id}/verify", response_model=CarDetailResponse, tags=["Admin Cars"])
def verify_car(car_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try: 
        return car_service.detail_payload(car_service.set_verification(db, car_id, admin, True))
    except Exception as exc: 
        _raise(exc)

@router.post("/admin/cars/{car_id}/unverify", response_model=CarDetailResponse, tags=["Admin Cars"])
def unverify_car(car_id: int, 
                 db: Session = Depends(get_db), 
                 admin: User = Depends(get_current_admin)
):
    try: 
        return car_service.detail_payload(car_service.set_verification(db, car_id, admin, False))
    except Exception as exc:
        _raise(exc)

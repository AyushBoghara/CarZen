from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin
from app.database.connection.conn import get_db
from app.models.enums.CarEnums import BodyType, FuelType, TransmissionType
from app.models.users import User
from app.schemas.car_catalog_schema import ActiveStatusUpdate, CarBrandCreate, CarBrandResponse, CarBrandUpdate, CarModelCreate, CarModelResponse, CarModelUpdate, CarVariantCreate, CarVariantResponse, CarVariantUpdate
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.users_schema import MessageResponse
from app.services.car import catalog_service

router = APIRouter()


def _page(page: int, limit: int): 
    return page, limit

def _result(data, pagination): 
    return {"data": data, "pagination": pagination}

def _error(exc):
    code = status.HTTP_404_NOT_FOUND if isinstance(exc, LookupError) else status.HTTP_409_CONFLICT if isinstance(exc, ValueError) else status.HTTP_400_BAD_REQUEST
    raise HTTPException(code, str(exc)) from exc

# ===================  brand ============================= 

@router.get("/car-brands", response_model=PaginatedResponse[CarBrandResponse], tags=["Car Brands"])
def list_brands(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), search: str | None = None, is_active: bool | None = None, db: Session = Depends(get_db)):
    return _result(*catalog_service.list_brands(db, page, limit, search, is_active))

@router.get("/car-brands/{brand_id}", response_model=CarBrandResponse, tags=["Car Brands"])
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    try: 
        return catalog_service.get_brand(db, brand_id)
    except Exception as exc:
        _error(exc)
        
# create a car brands 
@router.post("/admin/car-brands", response_model=CarBrandResponse, status_code=201, tags=["Car Brands"])
def create_brand(payload: CarBrandCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.create_brand(db, payload.model_dump())
    except Exception as exc: 
        _error(exc)

@router.patch("/admin/car-brands/{brand_id}", response_model=CarBrandResponse, tags=["Car Brands"])
def update_brand(brand_id: int, payload: CarBrandUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.update_brand(db, brand_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        _error(exc)

@router.delete("/admin/car-brands/{brand_id}", response_model=MessageResponse, tags=["Car Brands"])
def delete_brand(brand_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        catalog_service.delete_brand(db, brand_id)
        return {"message": "Car brand deleted successfully."}
    except Exception as exc: 
        _error(exc)

@router.patch("/admin/car-brands/{brand_id}/status", response_model=CarBrandResponse, tags=["Car Brands"])
def set_brand_status(brand_id: int, payload: ActiveStatusUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.update_brand(db, brand_id, payload.model_dump())
    except Exception as exc: 
        _error(exc)


# ===================  brand end ============================= 

@router.get("/car-models", response_model=PaginatedResponse[CarModelResponse], tags=["Car Models"])
def list_models(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), search: str | None = None, brand_id: int | None = None, body_type: BodyType | None = None, is_active: bool | None = None, db: Session = Depends(get_db)):
    return _result(*catalog_service.list_models(db, page, limit, search, brand_id, body_type, is_active))

@router.get("/car-models/{model_id}", response_model=CarModelResponse, tags=["Car Models"])
def get_model(model_id: int, db: Session = Depends(get_db)):
    try: 
        return catalog_service.get_model(db, model_id)
    except Exception as exc: 
        _error(exc)

@router.get("/car-brands/{brand_id}/models", response_model=PaginatedResponse[CarModelResponse], tags=["Car Models"])
def list_brand_models(brand_id: int, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    try: 
        catalog_service.get_brand(db, brand_id); 
        return _result(*catalog_service.list_models(db, page, limit, brand_id=brand_id))
    except Exception as exc:
        _error(exc)

@router.post("/admin/car-models", response_model=CarModelResponse, status_code=201, tags=["Car Models"])
def create_model(payload: CarModelCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.create_model(db, payload.model_dump())
    except Exception as exc:
        _error(exc)

@router.patch("/admin/car-models/{model_id}", response_model=CarModelResponse, tags=["Car Models"])
def update_model(model_id: int, payload: CarModelUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.update_model(db, model_id, payload.model_dump(exclude_unset=True))
    except Exception as exc: 
        _error(exc)

@router.delete("/admin/car-models/{model_id}", response_model=MessageResponse, tags=["Car Models"])
def delete_model(model_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        catalog_service.delete_model(db, model_id); 
        return {"message": "Car model deleted successfully."}
    except Exception as exc:
        _error(exc)

@router.patch("/admin/car-models/{model_id}/status", response_model=CarModelResponse, tags=["Car Models"])
def set_model_status(model_id: int, payload: ActiveStatusUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.update_model(db, model_id, payload.model_dump())
    except Exception as exc: 
        _error(exc)


@router.get("/car-variants", response_model=PaginatedResponse[CarVariantResponse], tags=["Car Variants"])
def list_variants(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), brand_id: int | None = None, model_id: int | None = None, fuel_type: FuelType | None = None, transmission: TransmissionType | None = None, db: Session = Depends(get_db)):
    return _result(*catalog_service.list_variants(db, page, limit, brand_id, model_id, fuel_type, transmission))

@router.get("/car-variants/{variant_id}", response_model=CarVariantResponse, tags=["Car Variants"])
def get_variant(variant_id: int, db: Session = Depends(get_db)):
    try: 
        return catalog_service.get_variant(db, variant_id)
    except Exception as exc:
        _error(exc)

@router.get("/car-models/{model_id}/variants", response_model=PaginatedResponse[CarVariantResponse], tags=["Car Variants"])
def list_model_variants(model_id: int, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    try: 
        catalog_service.get_model(db, model_id); 
        return _result(*catalog_service.list_variants(db, page, limit, model_id=model_id))
    except Exception as exc: 
        _error(exc)

@router.post("/admin/car-variants", response_model=CarVariantResponse, status_code=201, tags=["Car Variants"])
def create_variant(payload: CarVariantCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.create_variant(db, payload.model_dump())
    except Exception as exc: 
        _error(exc)

@router.patch("/admin/car-variants/{variant_id}", response_model=CarVariantResponse, tags=["Car Variants"])
def update_variant(variant_id: int, payload: CarVariantUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        return catalog_service.update_variant(db, variant_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        _error(exc)

@router.delete("/admin/car-variants/{variant_id}", response_model=MessageResponse, tags=["Car Variants"])
def delete_variant(variant_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try: 
        catalog_service.delete_variant(db, variant_id); 
        return {"message": "Car variant deleted successfully."}
    except Exception as exc:
        _error(exc)

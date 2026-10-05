from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.service_history_schema import ServiceRecordResponse
from app.services.services import service_history_service

router = APIRouter()

def _raise(exc: Exception):
    code = (
        404 if isinstance(exc, LookupError)
        else 403 if isinstance(exc, PermissionError)
        else 400 if isinstance(exc, ValueError)
        else 500
    )
    raise HTTPException(status_code=code, detail=str(exc)) from exc


# --- Service History ---

@router.get(
    "/services/history",
    response_model=PaginatedResponse[ServiceRecordResponse],
    tags=["Service History"],
    summary="View service history records",
)
def list_service_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        data, pagination = service_history_service.list_service_history(db, user, page, limit)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/services/history/{record_id}",
    response_model=ServiceRecordResponse,
    tags=["Service History"],
    summary="Get specific service record details",
)
def get_service_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return service_history_service.get_service_record(db, record_id, user)
    except Exception as exc:
        _raise(exc)


@router.get(
    "/cars/{car_id}/service-history",
    response_model=PaginatedResponse[ServiceRecordResponse],
    tags=["Service History"],
    summary="View service history for a specific car",
)
def get_car_service_history(
    car_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        data, pagination = service_history_service.get_car_service_history(
            db, car_id, user, page, limit
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)

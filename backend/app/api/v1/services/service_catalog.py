from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.service_catalog_schema import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.services import service_catalog_service

router = APIRouter()
def _raise(exc: Exception):
    code = (
        404 if isinstance(exc, LookupError)
        else 403 if isinstance(exc, PermissionError)
        else 400 if isinstance(exc, ValueError)
        else 500
    )
    raise HTTPException(status_code=code, detail=str(exc)) from exc


# ==========================================
# User Service Catalog Endpoints
# ==========================================

@router.get(
    "/services",
    response_model=PaginatedResponse[ServiceResponse],
    tags=["Service Catalog"],
    summary="Browse available active services",
)
def list_services(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Search services by name"),
    db: Session = Depends(get_db),
):
    try:
        data, pagination = service_catalog_service.list_active_services(db, page, limit, search)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/services/{service_id}",
    response_model=ServiceResponse,
    tags=["Service Catalog"],
    summary="Get single active service details",
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service_catalog_service.get_service(db, service_id)
    except Exception as exc:
        _raise(exc)


# ==========================================
# Admin Service Catalog Management Endpoints
# ==========================================

@router.post(
    "/admin/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin Service Catalog"],
    summary="Create a new service in the catalog",
)
def admin_create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_catalog_service.admin_create_service(db, payload.model_dump())
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.get(
    "/admin/services",
    response_model=PaginatedResponse[ServiceResponse],
    tags=["Admin Service Catalog"],
    summary="Admin list all services (active and inactive)",
)
def admin_list_services(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, description="Filter by status (active/inactive)"),
    search: str | None = Query(None, description="Search by name"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        data, pagination = service_catalog_service.admin_list_services(db, page, limit, status, search)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/admin/services/{service_id}",
    response_model=ServiceResponse,
    tags=["Admin Service Catalog"],
    summary="Admin get service by ID",
)
def admin_get_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_catalog_service.admin_get_service(db, service_id)
    except Exception as exc:
        _raise(exc)


@router.patch(
    "/admin/services/{service_id}",
    response_model=ServiceResponse,
    tags=["Admin Service Catalog"],
    summary="Update service attributes",
)
def admin_update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_catalog_service.admin_update_service(
            db, service_id, payload.model_dump(exclude_unset=True)
        )
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.delete(
    "/admin/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin Service Catalog"],
    summary="Soft-delete a service from catalog",
)
def admin_delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        service_catalog_service.admin_delete_service(db, service_id)
        return None
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/services/{service_id}/activate",
    response_model=ServiceResponse,
    tags=["Admin Service Catalog"],
    summary="Activate a service in catalog",
)
def admin_activate_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_catalog_service.admin_activate_service(db, service_id)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post(
    "/admin/services/{service_id}/deactivate",
    response_model=ServiceResponse,
    tags=["Admin Service Catalog"],
    summary="Deactivate a service in catalog",
)
def admin_deactivate_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return service_catalog_service.admin_deactivate_service(db, service_id)
    except Exception as exc:
        db.rollback()
        _raise(exc)

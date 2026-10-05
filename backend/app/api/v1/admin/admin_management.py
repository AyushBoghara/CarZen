from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin
from app.database.connection.conn import get_db
from app.models.enums.ListingEnums import ListingStatus
from app.models.users import User
from app.schemas.admin_listing_schema import AdminListingActionRequest
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.marketplace_schema import ListingResponse
from app.schemas.users_schema import MessageResponse
from app.services.admin import admin_service

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
# ADMIN LISTINGS
# ==========================================

@router.get(
    "/admin/listings",
    response_model=PaginatedResponse[ListingResponse],
    tags=["Admin Listings"],
    summary="Admin list all listings",
)
def admin_list_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: ListingStatus | None = Query(None),
    seller_id: int | None = Query(None),
    car_id: int | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        data, pagination = admin_service.list_admin_listings(
            db, page, limit, status, seller_id, car_id
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/admin/listings/{listing_id}",
    response_model=ListingResponse,
    tags=["Admin Listings"],
    summary="Admin get listing by ID",
)
def admin_get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return admin_service.get_admin_listing(db, listing_id)
    except Exception as exc:
        _raise(exc)


@router.patch(
    "/admin/listings/{listing_id}/approve",
    response_model=ListingResponse,
    tags=["Admin Listings"],
    summary="Admin approve listing",
)
def admin_approve_listing(
    listing_id: int,
    payload: AdminListingActionRequest | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        reason = payload.reason if payload else None
        return admin_service.approve_listing(db, listing_id, reason)
    except Exception as exc:
        _raise(exc)


@router.patch(
    "/admin/listings/{listing_id}/reject",
    response_model=ListingResponse,
    tags=["Admin Listings"],
    summary="Admin reject listing",
)
def admin_reject_listing(
    listing_id: int,
    payload: AdminListingActionRequest | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        reason = payload.reason if payload else None
        return admin_service.reject_listing(db, listing_id, reason)
    except Exception as exc:
        _raise(exc)


@router.patch(
    "/admin/listings/{listing_id}/suspend",
    response_model=ListingResponse,
    tags=["Admin Listings"],
    summary="Admin suspend listing",
)
def admin_suspend_listing(
    listing_id: int,
    payload: AdminListingActionRequest | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        reason = payload.reason if payload else None
        return admin_service.suspend_listing(db, listing_id, reason)
    except Exception as exc:
        _raise(exc)


@router.delete(
    "/admin/listings/{listing_id}",
    response_model=MessageResponse,
    tags=["Admin Listings"],
    summary="Admin delete listing",
)
def admin_delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        admin_service.delete_admin_listing(db, listing_id)
        return {"message": "Listing deleted successfully."}
    except Exception as exc:
        _raise(exc)

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin, get_current_user
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.review_schema import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
    ReviewVisibilityUpdate,
)
from app.schemas.users_schema import MessageResponse
from app.services.review import review_service

router = APIRouter()

def _raise(exc: Exception):
    msg = str(exc).lower()
    code = (
        404 if isinstance(exc, LookupError)
        else 403 if isinstance(exc, PermissionError)
        else 409 if isinstance(exc, ValueError) and ("already" in msg or "duplicate" in msg)
        else 400 if isinstance(exc, ValueError)
        else 500
    )
    raise HTTPException(status_code=code, detail=str(exc)) from exc


# --- User Reviews ---

@router.post(
    "/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Reviews"],
    summary="Submit a review for a purchased car",
)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return review_service.create_review(db, user, payload.model_dump())
    except Exception as exc:
        _raise(exc)


@router.get(
    "/reviews/my",
    response_model=PaginatedResponse[ReviewResponse],
    tags=["Reviews"],
    summary="List reviews submitted by current user",
)
def list_my_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        data, pagination = review_service.list_my_reviews(db, user, page, limit)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/cars/{car_id}/reviews",
    response_model=PaginatedResponse[ReviewResponse],
    tags=["Reviews"],
    summary="List public visible reviews for a car",
)
def list_car_reviews(
    car_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        data, pagination = review_service.list_car_reviews(db, car_id, page, limit)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
    tags=["Reviews"],
    summary="Update own review",
)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return review_service.update_own_review(
            db, review_id, user, payload.model_dump(exclude_unset=True)
        )
    except Exception as exc:
        _raise(exc)


@router.delete(
    "/reviews/{review_id}",
    response_model=MessageResponse,
    tags=["Reviews"],
    summary="Delete own review",
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        review_service.delete_own_review(db, review_id, user)
        return {"message": "Review deleted successfully."}
    except Exception as exc:
        _raise(exc)


# --- Admin Reviews ---

@router.get(
    "/admin/reviews",
    response_model=PaginatedResponse[ReviewResponse],
    tags=["Admin Reviews"],
    summary="Admin list all reviews",
)
def admin_list_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    is_visible: bool | None = Query(None),
    car_id: int | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        data, pagination = review_service.list_admin_reviews(db, page, limit, is_visible, car_id)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.patch(
    "/admin/reviews/{review_id}/visibility",
    response_model=ReviewResponse,
    tags=["Admin Reviews"],
    summary="Admin toggle review visibility",
)
def admin_set_visibility(
    review_id: int,
    payload: ReviewVisibilityUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return review_service.set_review_visibility(db, review_id, payload.is_visible)
    except Exception as exc:
        _raise(exc)


@router.delete(
    "/admin/reviews/{review_id}",
    response_model=MessageResponse,
    tags=["Admin Reviews"],
    summary="Admin delete a review",
)
def admin_delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        review_service.admin_delete_review(db, review_id)
        return {"message": "Review deleted by administrator."}
    except Exception as exc:
        _raise(exc)

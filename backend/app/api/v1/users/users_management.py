from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin, get_current_user
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.users_schema import (
    ChangePasswordRequest,
    MessageResponse,
    UserResponse,
    UserRoleStatusUpdate,
    UserUpdateProfile,
)
from app.services.users import user_service

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/users/update/me", response_model=UserResponse)
def update_user_profile(
    payload: UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return user_service.update_user_profile(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id( 
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return user_service.get_user_for_request(db, user_id, current_user)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e


@router.post("/users/me/change-password", response_model=MessageResponse)
def change_user_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        user_service.change_password(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return {"message": "Password updated successfully."}


@router.delete("/users/me", response_model=MessageResponse)
def delete_user_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.soft_delete_user(db, current_user)
    return {"message": "User account deleted successfully."}



@router.patch("/admin/update/me", response_model=UserResponse)
def update_admin_profile(
    payload: UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    try:
        return user_service.update_user_profile(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

@router.get("/admin/users", response_model=list[UserResponse])
def list_registered_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return user_service.list_users(db)


@router.get("/admin/users/{user_id}", response_model=UserResponse)
def get_admin_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        return user_service.get_user(db, user_id)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.patch("/admin/users/{user_id}/role-status", response_model=UserResponse)
def update_user_role_and_status(
    user_id: int,
    payload: UserRoleStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        return user_service.update_role_and_status(db, user_id, payload)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/admin/users/{user_id}", response_model=MessageResponse)
def delete_user_as_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        user = user_service.get_user(db, user_id)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    user_service.soft_delete_user(db, user)
    return {"message": "User account deleted successfully."}

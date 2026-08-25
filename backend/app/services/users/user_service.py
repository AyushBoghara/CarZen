from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.enums.UserRoles import UserRoles
from app.models.enums.UserStatus import UserStatus
from app.models.users import User
from app.schemas.users_schema import (
    ChangePasswordRequest,
    UserRoleStatusUpdate,
    UserUpdateProfile,
)
from app.services.auth.auth_service import is_password_valid


def list_users(db: Session) -> list[User]:
    return db.query(User).filter(User.deleted_at.is_(None)).order_by(User.id.asc()).all()


def get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise LookupError("User not found.")
    return user


def get_user_for_request(db: Session, user_id: int, current_user: User) -> User:
    if current_user.id != user_id and current_user.role != UserRoles.ADMIN:
        raise PermissionError("You are not allowed to access this user.")
    return get_user(db, user_id)


def update_user_profile(db: Session, current_user: User, payload: UserUpdateProfile) -> User:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return current_user

    _ensure_unique_profile_fields(db, current_user.id, updates)

    for field, value in updates.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(timezone.utc)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


def change_password(db: Session, current_user: User, payload: ChangePasswordRequest) -> None:
    if not verify_password(payload.current_password, current_user.password):
        raise ValueError("Current password is incorrect.")

    if payload.current_password == payload.new_password:
        raise ValueError("New password must be different from the current password.")

    is_password_valid(payload.new_password)

    current_user.password = hash_password(payload.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    db.add(current_user)
    db.commit()


def update_role_and_status(
    db: Session,
    user_id: int,
    payload: UserRoleStatusUpdate,
) -> User:
    user = get_user(db, user_id)
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise ValueError("Provide at least one field to update.")

    for field, value in updates.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(db: Session, user: User) -> None:
    user.deleted_at = datetime.now(timezone.utc)
    user.updated_at = user.deleted_at
    user.status = UserStatus.INACTIVE
    db.add(user)
    db.commit()


def _ensure_unique_profile_fields(
    db: Session,
    current_user_id: int,
    updates: dict,
) -> None:
    username = updates.get("username")
    email = str(updates["email"]) if updates.get("email") is not None else None
    phone_number = updates.get("phone_number")

    filters = []
    if username is not None:
        filters.append(User.username == username)
    if email is not None:
        filters.append(User.email == email)
    if phone_number is not None:
        filters.append(User.phone_number == phone_number)

    if not filters:
        return

    existing_user = (
        db.query(User)
        .filter(User.id != current_user_id)
        .filter(or_(*filters))
        .first()
    )
    if not existing_user:
        return

    if username is not None and existing_user.username == username:
        raise ValueError("Username is already in use.")
    if email is not None and existing_user.email == email:
        raise ValueError("Email is already in use.")
    if phone_number is not None and existing_user.phone_number == phone_number:
        raise ValueError("Phone number is already in use.")

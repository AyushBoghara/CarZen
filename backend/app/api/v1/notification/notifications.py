from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.notification_schema import NotificationResponse
from app.schemas.users_schema import MessageResponse
from app.services.notifications import notification_service

router = APIRouter()

def _raise(exc: Exception):
    code = 404 if isinstance(exc, LookupError) else 400
    raise HTTPException(code, str(exc)) from exc


@router.get("/notifications", response_model=PaginatedResponse[NotificationResponse], tags=["Notifications"])
def list_notifications(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data, pagination = notification_service.list_notifications(db, user, page, limit)
    return {"data": data, "pagination": pagination}


@router.get("/notifications/unread", response_model=PaginatedResponse[NotificationResponse], tags=["Notifications"])
def list_unread_notifications(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data, pagination = notification_service.list_notifications(db, user, page, limit, unread_only=True)
    return {"data": data, "pagination": pagination}


@router.patch("/notifications/read-all", response_model=MessageResponse, tags=["Notifications"])
def mark_all_as_read(db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    updated = notification_service.mark_all_as_read(db, user)
    return {"message": f"Marked {updated} notifications as read."}


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse, tags=["Notifications"])
def mark_as_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return notification_service.mark_as_read(db, notification_id, user)
    except Exception as exc:
        _raise(exc)


@router.delete("/notifications/{notification_id}", response_model=MessageResponse, tags=["Notifications"])
def delete_notification(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        notification_service.delete_notification(db, notification_id, user)
        return {"message": "Notification deleted successfully."}
    except Exception as exc:
        _raise(exc)

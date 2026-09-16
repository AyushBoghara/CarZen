from sqlalchemy.orm import Session

from app.models.enums.OrderEnums import NotificationType
from app.models.favorites import Favorites
from app.models.notifications import Notifications
from app.models.users import User
from app.services.car.catalog_service import paginate


def create_notification(
    db: Session,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    reference_id: int | None = None,
    reference_type: str | None = None,
) -> Notifications:
    
    notification = Notifications(
        user_id=user_id,
        notification_type=notification_type.value,
        title=title,
        message=message,
        reference_id=reference_id,
        reference_type=reference_type,
    )
    
    db.add(notification)
    return notification


def notify_favorite_users(
    db: Session,
    car_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    reference_id: int,
    reference_type: str,
) -> None:
    user_ids = db.query(Favorites.user_id).filter(Favorites.car_id == car_id).all()
    for (user_id,) in user_ids:
        create_notification(
            db,
            user_id,
            notification_type,
            title,
            message,
            reference_id,
            reference_type,
        )


def list_notifications(db: Session, user: User, page: int, limit: int, unread_only: bool = False):
    query = db.query(Notifications).filter(Notifications.user_id == user.id)
    if unread_only:
        query = query.filter(Notifications.is_read.is_(False))
    return paginate(query.order_by(Notifications.created_at.desc(), Notifications.id.desc()), page, limit)


def mark_as_read(db: Session, notification_id: int, user: User) -> Notifications:
    notification = _get_notification(db, notification_id, user)
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user: User) -> int:
    updated = (
        db.query(Notifications)
        .filter(Notifications.user_id == user.id, Notifications.is_read.is_(False))
        .update({Notifications.is_read: True}, synchronize_session=False)
    )
    db.commit()
    return updated


def delete_notification(db: Session, notification_id: int, user: User) -> None:
    notification = _get_notification(db, notification_id, user)
    db.delete(notification)
    db.commit()


def _get_notification(db: Session, notification_id: int, user: User) -> Notifications:
    notification = db.query(Notifications).filter(
        Notifications.id == notification_id,
        Notifications.user_id == user.id,
    ).first()
    if not notification:
        raise LookupError("Notification not found.")
    return notification

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.OrderEnums import NotificationType


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: NotificationType | None = None
    reference_id: int | None = None
    reference_type: str | None = None
    is_read: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

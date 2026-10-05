import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.car_media import CarMedia
from app.models.enums.CarEnums import MediaType

UPLOAD_ROOT = Path(os.getenv("CAR_MEDIA_UPLOAD_DIR", "uploads/cars"))
MAX_FILE_SIZE = int(os.getenv("CAR_MEDIA_MAX_BYTES", str(20 * 1024 * 1024)))
MAX_MEDIA_PER_CAR = int(os.getenv("CAR_MEDIA_MAX_COUNT", "20"))
ALLOWED_EXTENSIONS = {MediaType.IMAGE: {".jpg", ".jpeg", ".png", ".webp"}, MediaType.VIDEO: {".mp4", ".webm", ".mov"}}


def list_media(db: Session, car_id: int) -> list[CarMedia]:
    return db.query(CarMedia).filter(CarMedia.car_id == car_id, CarMedia.deleted_at.is_(None)).order_by(CarMedia.sort_order.asc(), CarMedia.id.asc()).all()


def create_media(db: Session, car_id: int, media_type: MediaType, filename: str, content: bytes, sort_order: int, is_primary: bool) -> CarMedia:
    extension = Path(filename or "").suffix.lower()
    if media_type not in ALLOWED_EXTENSIONS or extension not in ALLOWED_EXTENSIONS[media_type]:
        raise ValueError("Unsupported media file type.")
    if not content or len(content) > MAX_FILE_SIZE: raise ValueError("Media file is empty or exceeds the configured size limit.")
    if len(list_media(db, car_id)) >= MAX_MEDIA_PER_CAR: raise ValueError("Maximum media count reached for this car.")

    relative_dir = Path(str(car_id)); 
    destination_dir = UPLOAD_ROOT / relative_dir; destination_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{extension}"; 
    destination = destination_dir / stored_name
    destination.write_bytes(content)
    
    if is_primary: _clear_primary(db, car_id)
    media = CarMedia(car_id=car_id, media_type=media_type, media_url=f"/uploads/cars/{car_id}/{stored_name}", file_name=Path(filename).name, file_size=len(content), sort_order=sort_order, is_primary=is_primary)
    db.add(media); 
    db.commit(); 
    db.refresh(media);
    return media


def get_media(db: Session, car_id: int, media_id: int) -> CarMedia:
    media = db.query(CarMedia).filter(CarMedia.id == media_id, CarMedia.car_id == car_id, CarMedia.deleted_at.is_(None)).first()
    if not media: raise LookupError("Media does not belong to this car.")
    return media


def update_media(db: Session, car_id: int, media_id: int, values: dict) -> CarMedia:
    media = get_media(db, car_id, media_id)
    if not values: raise ValueError("Provide at least one field to update.")
    if values.get("is_primary"): _clear_primary(db, car_id)
    for field, value in values.items(): setattr(media, field, value)
    db.commit(); db.refresh(media); return media


def delete_media(db: Session, car_id: int, media_id: int) -> None:
    media = get_media(db, car_id, media_id)
    media.deleted_at = datetime.now(timezone.utc)
    db.commit()


def set_primary(db: Session, car_id: int, media_id: int) -> CarMedia:
    media = get_media(db, car_id, media_id); _clear_primary(db, car_id); media.is_primary = True; db.commit(); db.refresh(media); return media


def reorder_media(db: Session, car_id: int, orders: list[dict]) -> list[CarMedia]:
    items = {media.id: media for media in list_media(db, car_id)}
    requested_ids = [item["id"] for item in orders]
    if len(set(requested_ids)) != len(requested_ids) or any(media_id not in items for media_id in requested_ids):
        raise ValueError("Every media item must belong to the requested car and appear once.")
    for item in orders: items[item["id"]].sort_order = item["sort_order"]
    
    db.commit(); 
    return list_media(db, car_id)


def _clear_primary(db: Session, car_id: int) -> None:
    db.query(CarMedia).filter(CarMedia.car_id == car_id, CarMedia.deleted_at.is_(None)).update({CarMedia.is_primary: False}, synchronize_session=False)

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.enums.ServiceEnums import ServiceCatalogStatus
from app.models.services import Services
from app.services.car.catalog_service import paginate


def list_active_services(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
):
    query = (
        db.query(Services)
        .filter(
            Services.status == ServiceCatalogStatus.ACTIVE.value,
            Services.deleted_at.is_(None),
        )
    )
    if search:
        query = query.filter(Services.name.ilike(f"%{search.strip()}%"))

    return paginate(query.order_by(Services.price.asc(), Services.id.asc()), page, limit)


def get_service(db: Session, service_id: int) -> Services:
    service = (
        db.query(Services)
        .filter(
            Services.id == service_id,
            Services.status == ServiceCatalogStatus.ACTIVE.value,
            Services.deleted_at.is_(None),
        )
        .first()
    )
    if not service:
        raise LookupError("Service not found or is currently inactive.")
    return service


def admin_create_service(db: Session, data: dict) -> Services:
    service = Services(
        name=data["name"].strip(),
        description=data.get("description"),
        price=data["price"],
        duration_minutes=data.get("duration_minutes"),
        image_url=data.get("image_url"),
        status=ServiceCatalogStatus.ACTIVE.value,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    return service


def admin_list_services(
    db: Session,
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
    search: str | None = None,
):
    query = db.query(Services).filter(Services.deleted_at.is_(None))

    if status:
        query = query.filter(Services.status == status.lower())
    if search:
        query = query.filter(Services.name.ilike(f"%{search.strip()}%"))

    return paginate(query.order_by(Services.id.desc()), page, limit)


def admin_get_service(db: Session, service_id: int) -> Services:
    service = (
        db.query(Services)
        .filter(Services.id == service_id, Services.deleted_at.is_(None))
        .first()
    )
    if not service:
        raise LookupError("Service not found.")
    return service


def admin_update_service(db: Session, service_id: int, data: dict) -> Services:
    service = admin_get_service(db, service_id)

    for field, value in data.items():
        if value is not None and hasattr(service, field):
            if field == "status" and hasattr(value, "value"):
                setattr(service, field, value.value)
            elif field == "name":
                setattr(service, field, value.strip())
            else:
                setattr(service, field, value)

    service.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(service)
    return service


def admin_delete_service(db: Session, service_id: int) -> None:
    service = admin_get_service(db, service_id)
    service.deleted_at = datetime.utcnow()
    service.status = ServiceCatalogStatus.INACTIVE.value
    db.commit()


def admin_activate_service(db: Session, service_id: int) -> Services:
    service = admin_get_service(db, service_id)
    service.status = ServiceCatalogStatus.ACTIVE.value
    service.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(service)
    return service


def admin_deactivate_service(db: Session, service_id: int) -> Services:
    service = admin_get_service(db, service_id)
    service.status = ServiceCatalogStatus.INACTIVE.value
    service.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(service)
    return service

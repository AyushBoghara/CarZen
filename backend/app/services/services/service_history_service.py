from sqlalchemy.orm import Session, selectinload

from app.models.cars import Cars
from app.models.enums.UserRoles import UserRoles
from app.models.service_records import ServiceRecords
from app.models.users import User
from app.services.car.catalog_service import paginate


def list_service_history(db: Session, user: User, page: int = 1, limit: int = 20):
    query = db.query(ServiceRecords).options(
        selectinload(ServiceRecords.car),
        selectinload(ServiceRecords.items),
    )

    if user.role != UserRoles.ADMIN:
        user_car_ids = db.query(Cars.id).filter(Cars.owner_id == user.id, Cars.deleted_at.is_(None))
        query = query.filter(ServiceRecords.car_id.in_(user_car_ids))

    return paginate(
        query.order_by(ServiceRecords.service_date.desc(), ServiceRecords.id.desc()),
        page,
        limit,
    )


def get_service_record(db: Session, record_id: int, user: User) -> ServiceRecords:
    record = (
        db.query(ServiceRecords)
        .options(
            selectinload(ServiceRecords.car),
            selectinload(ServiceRecords.items),
        )
        .filter(ServiceRecords.id == record_id)
        .first()
    )
    if not record:
        raise LookupError("Service record not found.")

    if user.role != UserRoles.ADMIN:
        car = db.query(Cars).filter(Cars.id == record.car_id).first()
        if not car or car.owner_id != user.id:
            raise PermissionError("You do not have permission to view this service record.")

    return record


def get_car_service_history(
    db: Session,
    car_id: int,
    user: User,
    page: int = 1,
    limit: int = 20,
):
    car = db.query(Cars).filter(Cars.id == car_id, Cars.deleted_at.is_(None)).first()
    if not car:
        raise LookupError("Car not found.")

    if user.role != UserRoles.ADMIN and car.owner_id != user.id:
        raise PermissionError("You can only view service history for your own car.")

    query = (
        db.query(ServiceRecords)
        .options(
            selectinload(ServiceRecords.car),
            selectinload(ServiceRecords.items),
        )
        .filter(ServiceRecords.car_id == car_id)
    )

    return paginate(
        query.order_by(ServiceRecords.service_date.desc(), ServiceRecords.id.desc()),
        page,
        limit,
    )

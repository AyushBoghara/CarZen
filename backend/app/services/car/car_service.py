from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.car_brands import CarBrands
from app.models.car_features import CarFeatures
from app.models.car_media import CarMedia
from app.models.car_models import CarModels
from app.models.car_variants import CarVariants
from app.models.cars import Cars
from app.models.enums.CarEnums import CarApprovalStatus, CarCondition
from app.models.enums.UserRoles import UserRoles
from app.models.users import User
from app.services.car.catalog_service import get_variant, paginate


def create_car(db: Session, owner: User, values: dict) -> Cars:
    values = _normalize_optional_identifiers(values)
    _validate_creator_role(owner, values["condition"])
    
    _validate_years(values, None)
    
    _validate_resale_details(owner, values)
    _validate_variant(db, values["variant_id"])
    _ensure_unique_identifiers(db, values)
    car = Cars(owner_id=owner.id, approval_status=CarApprovalStatus.PENDING_APPROVAL, **values)
    db.add(car)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Registration number or VIN already exists.") from exc
    db.refresh(car)
    return car


def list_cars(db: Session, page: int, limit: int, owner_id: int | None = None, **filters):
    query = _filtered_query(db, **filters)
    if owner_id is not None: 
        query = query.filter(Cars.owner_id == owner_id)
    return paginate(query.order_by(Cars.id.desc()), page, limit)


def get_car(db: Session, car_id: int) -> Cars:
    car = _detail_query(db).filter(Cars.id == car_id, Cars.deleted_at.is_(None)).first()
    if not car: 
        raise LookupError("Car not found.")
    return car


def get_owned_car(db: Session, car_id: int, user: User, allow_admin: bool = False) -> Cars:
    car = get_car(db, car_id)
    if car.owner_id != user.id and not allow_admin:
        raise PermissionError("You do not own this car.")
    return car


def update_car(db: Session, car_id: int, user: User, values: dict, allow_admin: bool = False) -> Cars:
    car = get_owned_car(db, car_id, user, allow_admin)
    values = _normalize_optional_identifiers(values)
    if not values: raise ValueError("Provide at least one field to update.")
    _validate_years(values, car)
    if "variant_id" in values: _validate_variant(db, values["variant_id"])
    _ensure_unique_identifiers(db, values, car.id)
    important = {"variant_id", "registration_number", "vin_number", "manufacturing_year", "fuel_type", "transmission"}
    for field, value in values.items(): setattr(car, field, value)
    if important.intersection(values) and car.approval_status in {CarApprovalStatus.APPROVED, CarApprovalStatus.REJECTED}:
        car.approval_status = CarApprovalStatus.PENDING_APPROVAL
        car.is_verified = False
        car.rejection_reason = None
        car.verified_at = None
        car.verified_by_id = None
    car.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Registration number or VIN already exists.") from exc
    db.refresh(car)
    return car


def soft_delete_car(db: Session, car_id: int, user: User, allow_admin: bool = False) -> None:
    car = get_owned_car(db, car_id, user, allow_admin)
    car.deleted_at = datetime.now(timezone.utc)
    car.updated_at = car.deleted_at
    car.approval_status = CarApprovalStatus.INACTIVE
    db.commit()


def approve_car(db: Session, car_id: int, admin: User) -> Cars:
    car = get_car(db, car_id)
    
    _ensure_approvable(car)
    
    car.is_verified = True
    car.approval_status = CarApprovalStatus.APPROVED
    car.rejection_reason = None
    car.verified_at = datetime.now(timezone.utc)
    car.verified_by_id = admin.id
    car.updated_at = car.verified_at
    db.commit()
    db.refresh(car)
    
    return car


def reject_car(db: Session, car_id: int, admin: User, reason: str) -> Cars:
    car = get_car(db, car_id)
    car.is_verified = False
    car.approval_status = CarApprovalStatus.REJECTED
    car.rejection_reason = reason
    car.verified_at = datetime.now(timezone.utc)
    car.verified_by_id = admin.id
    car.updated_at = car.verified_at
    db.commit()
    return get_car(db, car_id)


def set_verification(db: Session, car_id: int, admin: User, is_verified: bool) -> Cars:
    car = get_car(db, car_id)
    if is_verified:
        return approve_car(db, car_id, admin)
    car.is_verified = False
    if car.approval_status == CarApprovalStatus.APPROVED: car.approval_status = CarApprovalStatus.PENDING_APPROVAL
    car.verified_at = datetime.now(timezone.utc); car.verified_by_id = admin.id; car.updated_at = car.verified_at
    db.commit(); return get_car(db, car_id)


def detail_payload(car: Cars) -> dict:
    variant = car.variant 
    model = variant.model
    brand = model.brand
    return {
        **{column.name: getattr(car, column.name) for column in Cars.__table__.columns if column.name != "deleted_at"},
        "brand": brand, "model": model, "variant": variant, "owner": car.owner,
        "media": sorted((item for item in car.media if item.deleted_at is None), key=lambda item: item.sort_order),
        "features": car.features,
    }


def _filtered_query(db: Session, search=None, verification_status=None, brand_id=None, model_id=None, variant_id=None, fuel_type=None, transmission=None, city=None, state=None, min_price=None, max_price=None, min_year=None, max_year=None, min_mileage=None, max_mileage=None, condition=None, approval_status=None):
    query = db.query(Cars).join(CarVariants).join(CarModels).join(CarBrands).filter(Cars.deleted_at.is_(None))
    if search:
        query = query.filter(or_(Cars.registration_number.ilike(f"%{search}%"), Cars.vin_number.ilike(f"%{search}%"), CarModels.name.ilike(f"%{search}%"), CarBrands.name.ilike(f"%{search}%")))
    if verification_status is not None:
        query = query.filter(Cars.is_verified.is_(verification_status))
    if approval_status: 
        query = query.filter(Cars.approval_status == approval_status)
    if brand_id: 
        query = query.filter(CarModels.brand_id == brand_id)
    if model_id:
        query = query.filter(CarVariants.model_id == model_id)
    if variant_id:
        query = query.filter(Cars.variant_id == variant_id)
    if fuel_type: 
        query = query.filter(Cars.fuel_type == fuel_type)
    if transmission: 
        query = query.filter(Cars.transmission == transmission)
    if city: 
        query = query.filter(Cars.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Cars.state.ilike(f"%{state}%"))
    if min_price is not None: 
        query = query.filter(Cars.expected_market_price >= min_price)
    if max_price is not None:
        query = query.filter(Cars.expected_market_price <= max_price)
    if min_year is not None: 
        query = query.filter(Cars.manufacturing_year >= min_year)
    if max_year is not None: 
        query = query.filter(Cars.manufacturing_year <= max_year)
    if min_mileage is not None:
        query = query.filter(Cars.mileage_km >= min_mileage)
    if max_mileage is not None:
        query = query.filter(Cars.mileage_km <= max_mileage)
    if condition:
        query = query.filter(Cars.condition == condition)
    return query


def _detail_query(db: Session):
    return db.query(Cars).options(selectinload(Cars.variant).selectinload(CarVariants.model).selectinload(CarModels.brand), selectinload(Cars.owner), selectinload(Cars.media), selectinload(Cars.features))


def _validate_variant(db: Session, variant_id: int) -> None:
    variant = get_variant(db, variant_id, active_only=True)
    if variant.model.deleted_at is not None or variant.model.brand.deleted_at is not None:
        raise LookupError("Car variant catalog hierarchy is not active.")


def _validate_years(values: dict, car: Cars | None) -> None:
    manufacturing = values.get("manufacturing_year", car.manufacturing_year if car else None)
    registration = values.get("registration_year", car.registration_year if car else None)
    if registration is not None and registration < manufacturing:
        raise ValueError("Registration year cannot be earlier than manufacturing year.")


def _ensure_unique_identifiers(db: Session, values: dict, car_id: int | None = None) -> None:
    filters = []
    if values.get("registration_number"):
        filters.append(Cars.registration_number == values["registration_number"])
    
    if values.get("vin_number"):
        filters.append(Cars.vin_number == values["vin_number"])
    
    if not filters:
        return
    query = db.query(Cars).filter(or_(*filters))
    if car_id is not None:
        query = query.filter(Cars.id != car_id)
    existing = query.first()
    if not existing: 
        return
    if values.get("registration_number") == existing.registration_number:
        raise ValueError("Registration number already exists.")
    raise ValueError("VIN already exists.")


def _normalize_optional_identifiers(values: dict) -> dict:
    normalized = values.copy()
    for field in ("registration_number", "vin_number"):
        value = normalized.get(field)
        if isinstance(value, str) and not value.strip():
            normalized[field] = None
    return normalized


def _ensure_approvable(car: Cars) -> None:
    missing_fields = []

    if car.condition == CarCondition.OLD:
        if not car.registration_number:
            missing_fields.append("registration_number")

        if not car.vin_number:
            missing_fields.append("vin_number")

    # Required for both new and used
    if car.manufacturing_year is None:
        missing_fields.append("manufacturing_year")

    if missing_fields:
        raise ValueError(
            "Car is missing required vehicle information: "
            + ", ".join(missing_fields)
        )
        
def _validate_creator_role(owner: User, condition: CarCondition) -> None:
    if owner.role == UserRoles.USER:
        if condition != CarCondition.NEW:
            raise PermissionError("Sellers can add only new cars. Set condition to 'new'.")
        return
    if owner.role == UserRoles.RESELLER:
        if condition != CarCondition.OLD:
            raise PermissionError("Resellers can add only resale cars. Set condition to 'oldCar'.")
        return
    raise PermissionError("Only seller and reseller accounts can add cars.")


def _validate_resale_details(owner: User, values: dict) -> None:
    if owner.role != UserRoles.RESELLER:
        return
    required = ["registration_number", "vin_number", "registration_year", "ownership_type"]
    missing = [field for field in required if values.get(field) is None]
    if missing:
        raise ValueError(f"Resale cars require: {', '.join(missing)}.")

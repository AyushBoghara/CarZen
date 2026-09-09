from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.car_brands import CarBrands
from app.models.car_models import CarModels
from app.models.car_variants import CarVariants


def paginate(query, page: int, limit: int):
    total = query.count()
    data = query.offset((page - 1) * limit).limit(limit).all()
    return data, {"page": page, "limit": limit, "total": total, "total_pages": max(1, (total + limit - 1) // limit)}


def get_brand(db: Session, brand_id: int, active_only: bool = False) -> CarBrands:
    query = db.query(CarBrands).filter(CarBrands.id == brand_id, CarBrands.deleted_at.is_(None))
    if active_only:
        query = query.filter(CarBrands.is_active.is_(True))
        
    brand = query.first()
    if not brand:
        raise LookupError("Car brand not found.")
    return brand


def list_brands(db: Session, page: int, limit: int, search: str | None, is_active: bool | None):
    query = db.query(CarBrands).filter(CarBrands.deleted_at.is_(None))
    if search:
        query = query.filter(CarBrands.name.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.filter(CarBrands.is_active.is_(is_active))
    return paginate(query.order_by(CarBrands.name.asc()), page, limit)


def create_brand(db: Session, values: dict) -> CarBrands:
    _ensure_brand_unique(db, values)
    brand = CarBrands(**values)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def update_brand(db: Session, brand_id: int, values: dict) -> CarBrands:
    brand = get_brand(db, brand_id)
    if not values:
        raise ValueError("Provide at least one field to update.")
    _ensure_brand_unique(db, values, brand_id)
    for field, value in values.items(): setattr(brand, field, value)
    brand.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(brand)
    return brand


def delete_brand(db: Session, brand_id: int) -> None:
    brand = get_brand(db, brand_id)
    brand.deleted_at = datetime.now(timezone.utc); brand.is_active = False
    db.commit()


def get_model(db: Session, model_id: int, active_only: bool = False) -> CarModels:
    query = db.query(CarModels).filter(CarModels.id == model_id, CarModels.deleted_at.is_(None))
    if active_only:
        query = query.filter(CarModels.is_active.is_(True))
    model = query.first()
    if not model:
        raise LookupError("Car model not found.")
    return model


def list_models(db: Session, page: int, limit: int, search=None, brand_id=None, body_type=None, is_active=None):
    query = db.query(CarModels).filter(CarModels.deleted_at.is_(None))
    if search: query = query.filter(CarModels.name.ilike(f"%{search}%"))
    if brand_id: query = query.filter(CarModels.brand_id == brand_id)
    if body_type: query = query.filter(CarModels.body_type == body_type)
    if is_active is not None: query = query.filter(CarModels.is_active.is_(is_active))
    return paginate(query.order_by(CarModels.name.asc()), page, limit)


def create_model(db: Session, values: dict) -> CarModels:
    get_brand(db, values["brand_id"], active_only=True)
    _ensure_model_slug_unique(db, values.get("slug"))
    model = CarModels(**values); 
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update_model(db: Session, model_id: int, values: dict) -> CarModels:
    model = get_model(db, model_id)
    if not values: 
        raise ValueError("Provide at least one field to update.")
    
    if "brand_id" in values: 
        get_brand(db, values["brand_id"], active_only=True)
        
    _ensure_model_slug_unique(db, values.get("slug"), model_id)
    
    for field, value in values.items():
        setattr(model, field, value)
        
    model.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(model)
    return model


def delete_model(db: Session, model_id: int) -> None:
    model = get_model(db, model_id); model.deleted_at = datetime.now(timezone.utc); model.is_active = False; db.commit()


def get_variant(db: Session, variant_id: int, active_only: bool = False) -> CarVariants:
    query = db.query(CarVariants).filter(CarVariants.id == variant_id, CarVariants.deleted_at.is_(None))
    if active_only: query = query.join(CarModels).join(CarBrands).filter(CarModels.deleted_at.is_(None), CarModels.is_active.is_(True), CarBrands.deleted_at.is_(None), CarBrands.is_active.is_(True))
    variant = query.first()
    if not variant:
        raise LookupError("Car variant not found.")
    return variant


def list_variants(db: Session, page: int, limit: int, brand_id=None, model_id=None, fuel_type=None, transmission=None):
    query = db.query(CarVariants).join(CarModels).join(CarBrands).filter(CarVariants.deleted_at.is_(None), CarModels.deleted_at.is_(None), CarModels.is_active.is_(True), CarBrands.deleted_at.is_(None), CarBrands.is_active.is_(True))
    if brand_id:
        query = query.filter(CarModels.brand_id == brand_id)
    if model_id: 
        query = query.filter(CarVariants.model_id == model_id)
    if fuel_type:
        query = query.filter(CarVariants.fuel_type == fuel_type)
    if transmission: 
        query = query.filter(CarVariants.transmission == transmission)
    return paginate(query.order_by(CarVariants.variant_name.asc()), page, limit)


def create_variant(db: Session, values: dict) -> CarVariants:
    model = get_model(db, values["model_id"], active_only=True)
    get_brand(db, model.brand_id, active_only=True)
    variant = CarVariants(**values)
    db.add(variant)
    db.commit() 
    db.refresh(variant)
    return variant


def update_variant(db: Session, variant_id: int, values: dict) -> CarVariants:
    variant = get_variant(db, variant_id)
    if not values: raise ValueError("Provide at least one field to update.")
    if "model_id" in values:
        model = get_model(db, values["model_id"], active_only=True); get_brand(db, model.brand_id, active_only=True)
    
    for field, value in values.items():
        setattr(variant, field, value)
    variant.updated_at = datetime.now(timezone.utc); 
    db.commit()
    db.refresh(variant)
    return variant


def delete_variant(db: Session, variant_id: int) -> None:
    variant = get_variant(db, variant_id)
    variant.deleted_at = datetime.now(timezone.utc)
    db.commit()


def _ensure_brand_unique(db: Session, values: dict, brand_id: int | None = None) -> None:
    filters = [CarBrands.name == values["name"]] if values.get("name") else []
    if values.get("slug"):
        filters.append(CarBrands.slug == values["slug"])
    if not filters: 
        return
    query = db.query(CarBrands).filter(or_(*filters))
    if brand_id: 
        query = query.filter(CarBrands.id != brand_id)
    if query.first():
        raise ValueError("Car brand name or slug already exists.")


def _ensure_model_slug_unique(db: Session, slug: str | None, model_id: int | None = None) -> None:
    if not slug: return
    query = db.query(CarModels).filter(CarModels.slug == slug)
    if model_id:
        query = query.filter(CarModels.id != model_id)
    if query.first(): 
        raise ValueError("Car model slug already exists.")

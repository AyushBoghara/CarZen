from sqlalchemy.orm import Session

from app.models.car_features import CarFeatures


def list_features(db: Session, car_id: int) -> list[CarFeatures]:
    return db.query(CarFeatures).filter(CarFeatures.car_id == car_id).order_by(CarFeatures.id.asc()).all()


def create_feature(db: Session, car_id: int, values: dict) -> CarFeatures:
    name = values["feature_name"].strip()
    if db.query(CarFeatures).filter(CarFeatures.car_id == car_id, CarFeatures.feature_name.ilike(name)).first():
        raise ValueError("This feature already exists for the car.")
    feature = CarFeatures(car_id=car_id, feature_name=name, feature_value=values.get("feature_value"))
    db.add(feature); 
    db.commit();
    db.refresh(feature); 
    return feature


def update_feature(db: Session, car_id: int, feature_id: int, values: dict) -> CarFeatures:
    feature = get_feature(db, car_id, feature_id)
    if not values: 
        raise ValueError("Provide at least one field to update.")
    
    if "feature_name" in values: 
        values["feature_name"] = values["feature_name"].strip()
        
    for field, value in values.items(): 
        setattr(feature, field, value)
        
    db.commit();
    db.refresh(feature); 
    return feature


def delete_feature(db: Session, car_id: int, feature_id: int) -> None:
    feature = get_feature(db, car_id, feature_id); db.delete(feature); 
    db.commit()


def get_feature(db: Session, car_id: int, feature_id: int) -> CarFeatures:
    feature = db.query(CarFeatures).filter(CarFeatures.id == feature_id, CarFeatures.car_id == car_id).first()
    if not feature: 
        raise LookupError("Feature does not belong to this car.")
    return feature

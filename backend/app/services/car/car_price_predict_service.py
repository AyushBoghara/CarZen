from pathlib import Path

import pandas as pd
import joblib
from sqlalchemy.orm import Session
from app.models.car_price_predict import CarPricePredict
from app.models.users import User
from app.services.car.catalog_service import paginate

# Load saved files

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "model"

model = joblib.load(MODEL_DIR / "car_price_model.pkl")
feature_columns = joblib.load(MODEL_DIR / "feature_columns.pkl")


# model = joblib.load("backend/model/car_price_model.pkl")
# feature_columns = joblib.load("backend/model/feature_columns.pkl")

def predict_car_price(db: Session,user:User, name,year,km_driven,fuel,seller_type,transmission,owner,mileage,engine,max_power,seats)-> CarPricePredict:
    print("calling the function")
    # Create input DataFrame
    car = pd.DataFrame([{
        "name": name,
        "year": year,
        "km_driven": km_driven,
        "fuel": fuel,
        "seller_type": seller_type,
        "transmission": transmission,
        "owner": owner,
        "mileage(km/ltr/kg)": mileage,
        "engine": engine,
        "max_power": max_power,
        "seats": seats
    }])

    # Convert numeric columns
    numeric_cols = [
        "year", "km_driven", "mileage(km/ltr/kg)",
        "engine", "max_power", "seats"
    ]

    for col in numeric_cols:
        car[col] = pd.to_numeric(car[col], errors="coerce")

    # Calculate car age using the same reference year
    car["age"] = 2026 - car["year"]

    # Ordinal Encoding and One-hot encode categorical columns
    car = pd.get_dummies(
        car,
        columns=[
            "name", "fuel", "seller_type",
            "transmission", "owner"
        ]
    )

    # Match training features and their exact order
    car = car.reindex(
        columns=feature_columns,
        fill_value=0
    )

    # Reject invalid numeric input
    if car.isna().any().any():
        raise ValueError("Please enter valid numeric values.")

    # Predict selling price
    predicted_price = model.predict(car)
    
    #  Output the result
    # print(f"Predicted Car Price: INR {predicted_price[0]:,.2f}")

    car_ = {
        "name": name,
        "year": int(year),
        "km_driven": int(km_driven),
        "fuel": fuel,
        "seller_type": seller_type,
        "transmission": transmission,
        "owner": owner,
        "mileage": float(mileage),
        "engine": float(engine),
        "max_power": float(max_power),
        "seats": int(seats),
        "predicted_price": float(predicted_price[0]),
    }
    
    carData = CarPricePredict(
        user_id=user.id,
        name=car_['name'],
        year=car_['year'],
        km_driven=car_['km_driven'],
        fuel=car_['fuel'],
        seller_type=car_['seller_type'],
        transmission=car_['transmission'],
        owner=car_['owner'],
        mileage=car_['mileage'],
        engine=car_['engine'],
        max_power=car_['max_power'],
        seats=car_['seats'],
        predicted_price=car_['predicted_price'],
    ); 
    try:
        db.add(carData)
        db.commit()
        db.refresh(carData)
        return carData
    except Exception as e:
        db.rollback()
        raise("Error : ",e)

def get_predict_car_price(db: Session, page: int, limit: int, owner_id: int):
    query = (
        db.query(CarPricePredict)
        .filter(CarPricePredict.user_id == owner_id)
        .order_by(CarPricePredict.id.desc())
    )
    
    if not query:
        raise LookupError("Predicted Car Price not found.")
    
    return paginate(query, page, limit)

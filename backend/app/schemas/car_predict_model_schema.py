
from pydantic import BaseModel, ConfigDict, Field


class CarPricePredictCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1980, le=2026)
    km_driven: int = Field(ge=0)
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: float = Field(gt=0)
    engine: float = Field(gt=0)
    max_power: float = Field(gt=0)
    seats: int = Field(gt=0, le=20)


class CarPricePredictResponse(BaseModel):
    id: int
    user_id: int
    name: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: float | None
    engine: float | None
    max_power: float | None
    seats: int | None
    predicted_price: int

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums.ServiceEnums import ServiceCatalogStatus


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150, description="Name of the service (e.g., Full Servicing)")
    description: str | None = Field(default=None, max_length=5000, description="Detailed explanation of what the service includes")
    price: Decimal = Field(..., gt=0, description="Cost of the service in INR")
    duration_minutes: int | None = Field(default=None, gt=0, description="Estimated duration to complete the service in minutes")
    image_url: str | None = Field(default=None, max_length=500, description="Optional image illustration URL")


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(default=None, gt=0)
    duration_minutes: int | None = Field(default=None, gt=0)
    image_url: str | None = Field(default=None, max_length=500)
    status: ServiceCatalogStatus | None = None


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    duration_minutes: int | None = None
    image_url: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

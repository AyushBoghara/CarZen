from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums.ReportEnums import ReportReason, ReportStatus


class ReportCreate(BaseModel):
    listing_id: int | None = Field(default=None, gt=0)
    car_id: int | None = Field(default=None, gt=0)
    reason: ReportReason
    description: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def validate_target(self):
        if self.listing_id is None and self.car_id is None:
            raise ValueError("Either listing_id or car_id is required.")
        return self


class ReportStatusUpdate(BaseModel):
    status: ReportStatus
    admin_note: str | None = Field(default=None, max_length=5000)


class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    listing_id: int | None = None
    car_id: int | None = None
    reason: ReportReason
    description: str | None = None
    status: ReportStatus
    created_at: datetime
    resolved_at: datetime | None = None
    resolved_by_id: int | None = None
    admin_note: str | None = None

    model_config = ConfigDict(from_attributes=True)

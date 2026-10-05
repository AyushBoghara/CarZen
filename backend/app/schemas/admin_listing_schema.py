from pydantic import BaseModel, ConfigDict, Field


class AdminListingActionRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(from_attributes=True)

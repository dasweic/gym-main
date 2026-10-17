
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GymSettingsUpdate(BaseModel):
    gym_name: str = Field(min_length=1, max_length=150)
    slogan: str | None = Field(default=None, max_length=255)
    upi_id: str | None = Field(default=None, max_length=150)
    upi_qr_path: str | None = Field(default=None, max_length=255)
    hero_image_path: str | None = Field(default=None, max_length=255)
    male_opening_hours: str | None = Field(default=None, max_length=100)
    female_opening_hours: str | None = Field(default=None, max_length=100)


class GymSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gym_name: str
    slogan: str | None
    upi_id: str | None
    upi_qr_path: str | None
    hero_image_path: str | None
    male_opening_hours: str | None
    female_opening_hours: str | None
    updated_at: datetime

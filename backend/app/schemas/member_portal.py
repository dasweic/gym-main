
from pydantic import BaseModel, ConfigDict, Field


class MemberProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=120)
    age: int | None = Field(default=None, ge=1, le=120)
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    photo_path: str | None = None
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=500)


from pydantic import BaseModel, ConfigDict, Field


class TrainerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    specialization: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    photo_path: str | None = Field(default=None, max_length=255)
    bio: str | None = None


class TrainerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    specialization: str
    phone: str
    photo_path: str | None
    bio: str | None
    is_active: bool

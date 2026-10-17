
from pydantic import BaseModel, ConfigDict, Field


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    duration_days: int = Field(gt=0, le=3650)
    price: float = Field(ge=0, le=99999999.99)


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    duration_days: int
    price: float
    is_active: bool

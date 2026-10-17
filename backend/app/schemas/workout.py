
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkoutCreate(BaseModel):
    member_id: int = Field(gt=0)
    workout_date: date = Field(default_factory=date.today)
    body_part: str = Field(
        pattern="^(chest|triceps|back|biceps|legs|shoulders|abs)$",
    )
    notes: str | None = None


class WorkoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    workout_date: date
    body_part: str
    notes: str | None
    created_at: datetime

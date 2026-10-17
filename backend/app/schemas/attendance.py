
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AttendanceCreate(BaseModel):
    member_id: int = Field(gt=0)
    workout_focus: str | None = Field(
        default=None,
        pattern="^(chest|triceps|back|biceps|legs|shoulders|abs)$",
    )


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    attendance_date: date
    check_in_time: datetime
    workout_focus: str | None
    status: str


from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionCreate(BaseModel):
    member_id: int = Field(gt=0)
    plan_id: int = Field(gt=0)
    start_date: date


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    plan_id: int
    start_date: date
    end_date: date
    status: str

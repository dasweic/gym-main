
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    member_id: int = Field(gt=0)
    plan_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, le=99999999.99)
    payment_method: str = Field(default="UPI", min_length=1, max_length=30)
    transaction_id: str | None = Field(default=None, max_length=100)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    plan_id: int
    amount: Decimal
    payment_method: str
    status: str
    transaction_id: str | None
    created_at: datetime

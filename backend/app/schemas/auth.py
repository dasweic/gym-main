
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MemberLinkRequest(BaseModel):
    member_id: int = Field(gt=0)

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    member_id: int | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str | None = None
    phone: str | None = None
    password: str
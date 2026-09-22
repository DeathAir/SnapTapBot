from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    telegram_id: int = Field(..., description="Telegram user id")
    username: str = Field(..., min_length=5, max_length=55)
    phone: str = Field(..., min_length=10, max_length=20)


class UserCreate(UserBase):
    role: str = Field(default="user", max_length=50)
    club_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    role: str
    club_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    club_id: Optional[int] = None
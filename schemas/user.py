from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    telegram_id: int = Field(..., description="Telegram user id")
    username: str = Field(..., min_length=5, max_length=55, description="User's username")
    phone: str = Field(..., min_length=12, max_length=12, description="Phone number")

class UserCreate(UserBase):
    role: str = Field(default='user', max_length=50, description="Роль: user / admin / superadmin")
    club_id: int

class UserResponse(UserCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    config = ConfigDict(from_attributes=True)

class UserUpdate(UserCreate):
    pass

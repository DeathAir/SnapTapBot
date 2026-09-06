from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ClubBase(BaseModel):
    name: str = Field(..., description="Название клуба")
    address: str = Field(..., max_length=100, description="Адресс клуба")
    phone: str = Field(..., min_length=12, max_length=12, description="Номер телефона клуба")

class ClubCreate(ClubBase):
    pass

class ClubResponse(ClubBase):
    id: int = Field(...)
    is_active: bool = Field(...)
    subscription_start: datetime = Field(...)
    subscription_end: datetime = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    config = ConfigDict(from_attributes=True)


class ClubUpdate(ClubCreate):
    pass

class ClubDelete(ClubResponse):
    pass
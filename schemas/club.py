from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ClubBase(BaseModel):
    """Базовая схема клуба"""
    name: str = Field(..., description="Название клуба")
    address: str = Field(..., max_length=100, description="Адрес клуба")
    phone: str = Field(..., min_length=10, max_length=20, description="Телефон")
    is_active: bool = Field(default=True, description="Активен ли клуб")


class ClubCreate(ClubBase):
    """Схема для создания клуба"""
    pass


class ClubResponse(ClubBase):
    """Схема для ответа с данными клуба"""
    id: int
    subscription_start: datetime
    subscription_end: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClubUpdate(BaseModel):
    """Схема для обновления клуба (все поля опциональны)"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_end: Optional[datetime] = None
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class RaffleBase(BaseModel):
    title: str
    description: str
    prize: str
    start_date: datetime
    end_date: datetime


class RaffleCreate(RaffleBase):
    club_id: int


class RaffleResponse(RaffleBase):
    id: int
    club_id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RaffleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prize: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class RaffleListResponse(BaseModel):
    raffles: list[RaffleResponse]
    total: int

class WinnerInfo(BaseModel):
    place: int
    prize: str
    ticket_number: int
    username: str
    telegram_id: Optional[int] = None

class RaffleDrawResponse(BaseModel):
    raffle_id: int
    title: str
    winners: list[WinnerInfo]
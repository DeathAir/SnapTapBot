from pydantic import BaseModel, Field
from typing import List, Optional

from schemas import TicketResponse
from schemas.user import UserResponse


class AdminStats(BaseModel):
    total_ticket: int
    remaining_ticket: int
    free_ticket: int
    progress_percent: float

class AdminClubStats(AdminStats):
    club_id: int
    club_name: str
    total_ticket: int

class AdminUserList(BaseModel):
    users: List[UserResponse]
    total: int
    page: int = Field(default=1)
    per_page: int = Field(default=20)
    filter: Optional[str] = Field(None, description="all / free / used")

class AdminTicketList(BaseModel):
    """Список билетов для админа"""
    tickets: List[TicketResponse]
    total: int
    page: int = Field(default=1)
    per_page: int = Field(default=20)
    filter: Optional[str] = Field(None, description="all / free / used")

class AdminGenerateRequest(BaseModel):
    club_id: int
    count: int = Field(..., ge=1, le=10000, description="quantity tickets")

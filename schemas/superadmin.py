from typing import List

from pydantic import BaseModel, Field

from schemas.admin import AdminClubStats
from schemas.club import ClubResponse


class SuperAdminStats(BaseModel):
    total_clubs: int
    total_tickets: int
    total_registered: int
    total_users: int
    active_clubs: int
    unactive_clubs: int
    overall_progress: float

class SuperAdminClubList(BaseModel):
    clubs: List[ClubResponse]
    total: int
    page: int = Field(default=1)
    per_page: int = Field(default=20)

class SuperAdminClubDetail(BaseModel):
    club: ClubResponse
    stats: AdminClubStats


from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from schemas import ClubCreate, ClubResponse, SuperAdminStats, UserResponse
from services.club_service import ClubService
from services.ticket_service import TicketService
from services.user_service import UserService

router = APIRouter(prefix="/superadmin", tags=["superadmin"])




@router.get("/clubs", response_model=List[ClubResponse])
async def clubs(db: AsyncSession = Depends(get_db)):
    club_service = ClubService(db)
    clubs = await club_service.get_all_clubs()
    return clubs

@router.post("/clubs", response_model=ClubResponse)
async def create_club(data: ClubCreate, db: AsyncSession = Depends(get_db)):
    club_service = ClubService(db)
    club = await club_service.create_club(data)
    return club

@router.delete("/clubs/{club_id}")
async def delete_club(club_id: int, db: AsyncSession = Depends(get_db)):
    club_service = ClubService(db)
    club = await club_service.delete_club(club_id)
    return {
        "message": "Club deleted",
    }

@router.get("/stats", response_model=SuperAdminStats)
async def stats(db: AsyncSession = Depends(get_db)):
    club_service = ClubService(db)
    user_service = UserService(db)
    ticket_service = TicketService(db, user_service)

    clubs = await club_service.get_all_clubs()

    total_clubs = len(clubs)
    active_clubs = len([c for c in clubs if c.is_active])
    inactive_clubs = total_clubs - active_clubs

    total_users = await user_service.get_total_users_count()

    total_tickets = 0
    total_registered = 0
    for club in clubs:
        stats = await ticket_service.get_tickets_stats(club.id)
        total_tickets += stats["total"]
        total_registered += stats["registered"]

    overall_progress = (total_registered / total_tickets * 100) if total_tickets > 0 else 0

    return SuperAdminStats(
        total_clubs=total_clubs,
        active_clubs=active_clubs,
        unactive_clubs=inactive_clubs,
        total_users=total_users,
        total_tickets=total_tickets,
        total_registered=total_registered,
        overall_progress=round(overall_progress, 2)
    )

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    users = await user_service.get_all_users()
    return users
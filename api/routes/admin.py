from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from schemas import UserResponse, AdminStats, AdminGenerateRequest, RaffleCreate, RaffleResponse
from services.raffle_service import RaffleService
from services.report_service import ReportService
from services.ticket_service import TicketService
from services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats", response_model=AdminStats)
async def admin_stats(club_id: int, db: AsyncSession  = Depends(get_db)):
    ticket_service = TicketService(db, UserService(db))
    stats = await ticket_service.get_tickets_stats(club_id)
    return AdminStats(
       total_tickets=stats["total"],
       registered_tickets=stats["registered"],
       free_tickets=stats["free"],
       progress_percent=stats["progress_percent"]
   )

@router.get("/users")
async def admin_users(club_id: int, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    users = await user_service.get_users_by_club(club_id)
    return users

@router.get("/tickets")
async def admin_tickets(club_id: int, db: AsyncSession = Depends(get_db)):
    ticket_service = TicketService(db, UserService(db))
    tickets = await ticket_service.get_tickets_by_club(club_id)
    return tickets

@router.post("/tickets/generate")
async def generate_ticket(data: AdminGenerateRequest, db: AsyncSession = Depends(get_db)):
    ticket_service = TicketService(db, UserService(db))
    tickets = await ticket_service.generate_tickets(data.club_id, data.count)
    return {"message": f"Создано {data.count} билетов"}

@router.get("/report")
async def admin_report(club_id: int, db: AsyncSession = Depends(get_db)):
    report_service = ReportService(db)
    report = await report_service.generate_full_report(club_id)
    return report

@router.get("/raffles")
async def raffles_club(club_id: int, db: AsyncSession = Depends(get_db)):
    raffle_service = RaffleService(db)
    raffles = await raffle_service.get_raffles_by_club(club_id)
    return raffles

@router.post("/raffles", response_model=RaffleResponse)
async def create_raffles(data: RaffleCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    raffle_service = RaffleService(db)
    raffle = await raffle_service.create_raffle(data, user_id)
    return raffle



from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response
from api.dependencies import get_db
from schemas import AdminStats, AdminGenerateRequest, RaffleCreate, RaffleResponse
from services.qr_service import QRService
from services.raffle_service import RaffleService
from services.report_service import ReportService
from services.ticket_service import TicketService
from services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
async def admin_stats(club_id: int, db: AsyncSession = Depends(get_db)):
    ticket_service = TicketService(db, UserService(db))
    stats = await ticket_service.get_tickets_stats(club_id)

    # Обрати внимание на названия аргументов — они должны совпадать со схемой!
    return AdminStats(
        total_ticket=stats["total"],
        remaining_ticket=stats["registered"],  # Или stats["remaining"], смотри что там в словаре
        free_ticket=stats["free"],
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
    tickets = await ticket_service.generate_tickets(data.club_id, data.raffle_id, data.count)

    qr_service = QRService(db)
    qr_paths = await qr_service.generate_qr_for_club(data.club_id)

    return {
        "message": f"Создано {len(tickets)} билетов и {len(qr_paths)} QR-кодов",
        "tickets_count": len(tickets),
        "qr_count": len(qr_paths)
    }


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
    user_service = UserService(db)
    user = await user_service.get_user_by_telegram_id(user_id)

    raffle_service = RaffleService(db)
    raffle = await raffle_service.create_raffle(data, user.id)

    return raffle

@router.post("/raffles/{raffle_id}/activate", response_model=RaffleResponse)
async def raffle_activate(raffle_id: int, db: AsyncSession = Depends(get_db)):
    raffle_service = RaffleService(db)
    raffle = await raffle_service.activate_raffle(raffle_id)
    return raffle


@router.post("/raffles/{raffle_id}/deactivate", response_model=RaffleResponse)
async def raffle_deactivate(raffle_id: int, db: AsyncSession = Depends(get_db)):
    raffle_service = RaffleService(db)
    raffle = await raffle_service.deactivate_raffle(raffle_id)
    return raffle


@router.post("/raffles/{raffle_id}/draw")
async def raffle_draw(raffle_id: int, db: AsyncSession = Depends(get_db)):
    raffle_service = RaffleService(db)
    winner = await raffle_service.draw_winner(raffle_id)
    return winner


@router.get("/raffles/{raffle_id}/results")
async def raffle_results(raffle_id: int, db: AsyncSession = Depends(get_db)):
    raffle_service = RaffleService(db)
    results = await raffle_service.get_raffle_results(raffle_id)
    return results


@router.post("/tickets/deactivate")
async def deactivate_club_tickets(club_id: int, db: AsyncSession = Depends(get_db)):
    ticket_service = TicketService(db, UserService(db))
    result = await ticket_service.deactivate_club_tickets(club_id)
    return result


@router.delete("/tickets")
async def delete_tickets_club(club_id: int, db: AsyncSession = Depends(get_db)):
    ticket_service = TicketService(db, UserService(db))
    result = await ticket_service.delete_club_tickets(club_id)
    return result

@router.get("/tickets/zip")
async def get_tickets_zip(club_id: int, db: AsyncSession = Depends(get_db)):
    qr_service = QRService(db)
    zip_bytes = await qr_service.generate_qr_zip(club_id)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=tickets_{club_id}.zip"}
    )
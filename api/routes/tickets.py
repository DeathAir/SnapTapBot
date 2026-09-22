from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, result

from schemas import TicketVerify, StandardResponse, TicketListResponse
from api.dependencies import get_db
from services import ticket_service
from services.ticket_service import TicketService
from services.user_service import UserService

router = APIRouter(prefix="/tickets", tags=["tickets"])
@router.post("/verify", response_model=StandardResponse)
async def verify(data: TicketVerify, db: AsyncSession  = Depends(get_db)):
    user_service = UserService(db)
    ticket_service = TicketService(db, user_service)
    result = await ticket_service.verify_ticket(data)
    if not result["success"]:
        return StandardResponse(
            status="error",
            message=result["message"]
        )

    return StandardResponse(
        status="success",
        message=result["message"]
    )

@router.get("/my", response_model=TicketListResponse)
async def get_my_tickets(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    ticket_service = TicketService(db, user_service)
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tickets = await ticket_service.get_tickets_by_user(user.id)
    return TicketListResponse(
        tickets=tickets,
        total=len(tickets)
    )

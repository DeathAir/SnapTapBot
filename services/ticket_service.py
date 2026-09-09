from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select

from database import AsyncSessionLocal
from models import Ticket
from schemas import TicketVerify
from services.user_service import UserService


class TicketService:
    def __init__(self, db: AsyncSessionLocal, user_service: UserService):
        self.db = db
        self.user_service = user_service

    async def get_ticket_by_number(self, number: int, club_id: int) -> Optional[Ticket]:
        existing = await self.db.execute(select(Ticket).where(Ticket.number == number,
                                                              Ticket.club_id == club_id))
        result = existing.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return result

    async def get_ticket_by_id(self, ticket_id: int) -> Ticket:
        existing = await self.db.execute(select(Ticket).where(Ticket.id == ticket_id))
        result = existing.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return result

    async def get_tickets_by_club(self, club_id: int) -> List[Ticket]:
        existing = await self.db.execute(select(Ticket).where(Ticket.club_id == club_id))
        result = existing.scalars().all()
        return result

    async def get_tickets_by_user(self, user_id: int) -> List[Ticket]:
        existing = await self.db.execute(select(Ticket).where(Ticket.user_id == user_id))
        result = existing.scalars().all()
        return result

    async def get_registered_tickets(self, club_id: int) -> List[Ticket]:
        existing = await self.db.execute(select(Ticket).where(Ticket.is_registered == True,
                                                              Ticket.club_id == club_id))
        result = existing.scalars().all()
        return result

    async def get_free_tickets(self, club_id: int) -> List[Ticket]:
        existing = await self.db.execute(select(Ticket).where(Ticket.is_registered == False,
                                                              Ticket.club_id == club_id))
        result = existing.scalars().all()
        return result

    async def get_ticket_status(self, number: int, club_id: int) -> dict:
        existing = await self.db.execute(select(Ticket).where(Ticket.number == number, Ticket.club_id == club_id))
        result = existing.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return {"number": result.number, "is_registered": result.is_registered}

    async def verify_ticket(self, ticket_data: TicketVerify) -> dict:
        user = await self.user_service.get_user_by_telegram_id(ticket_data.telegram_id)
        if user is None:
            return {
                "success": False,
                "message": "User not found, First, write /start.",
            }
        if not user.club_id:
            return {
                "success": False,
                "message": "Вы не привязаны к клубу. Отсканируйте QR-код в клубе.",
            }
        tickets = await self.get_ticket_by_number(ticket_data.number, user.club_id)
        if tickets is None:
            return {
                "success": False,
                "message": f"Билет №{ticket_data.number} не найден"
            }
        if ticket_data.secret_hash != tickets.secret_hash:
            return {
                "success": False,
                "message": "Неверный хеш. Билет поддельный!"
            }
        if tickets.is_registered:
            return {
                "success": False,
                "message": f"Билет №{ticket_data.number} уже зарегистрирован"
            }
        tickets.is_registered = True
        tickets.user_id = user.id
        tickets.registered_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(tickets)

        return {
            "success": True,
            "message": f"✅ Билет №{tickets.number} успешно зарегистрирован!"
        }

    async def check_ticket_exists(self, number: int, club_id: int) -> bool:
        result = await self.db.execute(select(Ticket).where(Ticket.number == number,
                                                                     Ticket.club_id == club_id))
        return result.scalar_one_or_none() is not None

    async def check_ticket_available(self, number, club_id) -> bool:
        result = await self.db.execute(select(Ticket).where(Ticket.number == number,
                                                            Ticket.club_id == club_id,
                                                            Ticket.is_registered == False))
        return result.scalar_one_or_none() is not None

    async def register_ticket(self, ticket_id: int, user_id: int) -> Optional[Ticket]:
        ticket = await self.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Билет не найден")
        if ticket.is_registered:
            raise HTTPException(status_code=409, detail="Билет уже зарегистрирован")
        ticket.is_registered = True
        ticket.user_id = user_id
        ticket.registered_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def unregister_ticket(self, ticket_id):
        ticket = await self.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Билет не найден")
        if not ticket.is_registered:
            raise HTTPException(status_code=409, detail="Билет уже свободен")

        ticket_number = ticket.number

        ticket.is_registered = False
        ticket.user_id = None
        ticket.registered_at = None

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket







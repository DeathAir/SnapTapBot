import hashlib
import secrets
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select, func

from database import AsyncSessionLocal
from models import Ticket, User
from schemas import TicketVerify
from services.user_service import UserService


class TicketService:
    def __init__(self, db: AsyncSessionLocal, user_service: UserService):
        self.db = db
        self.user_service = user_service

    async def get_ticket_by_number(self, number: int, club_id: int) -> Optional[Ticket]:
        existing = await self.db.execute(
            select(Ticket).where(
                Ticket.number == number,
                Ticket.club_id == club_id
            )
        )
        return existing.scalar_one_or_none()

    async def get_ticket_by_id(self, ticket_id: int) -> Ticket:
        existing = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        result = existing.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return result

    async def get_tickets_by_club(self, club_id: int) -> List[Ticket]:
        existing = await self.db.execute(
            select(Ticket).where(Ticket.club_id == club_id)
        )
        return existing.scalars().all()

    async def get_tickets_by_user(self, user_id: int) -> List[Ticket]:
        existing = await self.db.execute(
            select(Ticket).where(
                Ticket.user_id == user_id,
                Ticket.is_active == True
            )
        )
        return existing.scalars().all()

    async def get_registered_tickets(self, club_id: int) -> List[Ticket]:
        existing = await self.db.execute(
            select(Ticket).where(
                Ticket.is_registered == True,
                Ticket.club_id == club_id
            )
        )
        return existing.scalars().all()

    async def get_free_tickets(self, club_id: int) -> List[Ticket]:
        existing = await self.db.execute(
            select(Ticket).where(
                Ticket.is_registered == False,
                Ticket.club_id == club_id
            )
        )
        return existing.scalars().all()

    async def get_ticket_status(self, number: int, club_id: int) -> dict:
        existing = await self.db.execute(
            select(Ticket).where(
                Ticket.number == number,
                Ticket.club_id == club_id
            )
        )
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


        ticket = await self.get_ticket_by_number(ticket_data.number, ticket_data.club_id)

        if ticket is None:
            return {
                "success": False,
                "message": f"Билет №{ticket_data.number} не найден в клубе {ticket_data.club_id}"
            }

        if not ticket.is_active:
            return {
                "success": False,
                "message": f"Билет №{ticket_data.number} деактивирован"
            }
        if ticket_data.secret_hash != ticket.secret_hash:
            return {
                "success": False,
                "message": "Неверный хеш. Билет поддельный!"
            }
        if ticket.is_registered:
            return {
                "success": False,
                "message": f"Билет №{ticket_data.number} уже зарегистрирован"
            }


        ticket.is_registered = True
        ticket.user_id = user.id
        ticket.registered_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(ticket)

        return {
            "success": True,
            "message": f"✅ Билет №{ticket.number} успешно зарегистрирован!"
        }

    async def check_ticket_exists(self, number: int, club_id: int) -> bool:
        result = await self.db.execute(
            select(Ticket).where(
                Ticket.number == number,
                Ticket.club_id == club_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def check_ticket_available(self, number: int, club_id: int) -> bool:
        result = await self.db.execute(
            select(Ticket).where(
                Ticket.number == number,
                Ticket.club_id == club_id,
                Ticket.is_registered == False
            )
        )
        return result.scalar_one_or_none() is not None

    async def register_ticket(self, ticket_id: int, user_id: int) -> Optional[Ticket]:
        ticket = await self.get_ticket_by_id(ticket_id)
        if ticket.is_registered:
            raise HTTPException(status_code=409, detail="Билет уже зарегистрирован")
        ticket.is_registered = True
        ticket.user_id = user_id
        ticket.registered_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def unregister_ticket(self, ticket_id: int) -> Ticket:
        ticket = await self.get_ticket_by_id(ticket_id)
        if not ticket.is_registered:
            raise HTTPException(status_code=409, detail="Билет уже свободен")

        ticket.is_registered = False
        ticket.user_id = None
        ticket.registered_at = None

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    def generate_ticket_hash(self, ticket_number: int) -> str:
        salt = secrets.token_hex(16)
        data = f"{ticket_number}{salt}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def generate_tickets(self, club_id: int, raffle_id: int, count: int) -> List[Ticket]:
        tickets = []

        for i in range(1, count + 1):
            secret_hash = self.generate_ticket_hash(i)
            ticket = Ticket(
                number=i,
                club_id=club_id,
                raffle_id=raffle_id,
                secret_hash=secret_hash,
                is_registered=False,
                is_active=True
            )
            tickets.append(ticket)

        self.db.add_all(tickets)
        await self.db.commit()

        for ticket in tickets:
            await self.db.refresh(ticket)

        return tickets

    async def deactivate_club_tickets(self, club_id: int) -> dict:
        result = await self.db.execute(
            select(Ticket).where(Ticket.club_id == club_id)
        )
        tickets = result.scalars().all()
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found")

        count = 0
        for ticket in tickets:
            if ticket.is_active:
                ticket.is_active = False
                count += 1

        await self.db.commit()
        return {"message": f"Деактивировано {count} билетов"}

    async def delete_club_tickets(self, club_id: int) -> dict:
        result = await self.db.execute(
            select(Ticket).where(Ticket.club_id == club_id)
        )
        tickets = result.scalars().all()
        if not tickets:
            raise HTTPException(status_code=404, detail="No tickets found")

        count = len(tickets)
        for ticket in tickets:
            await self.db.delete(ticket)

        await self.db.commit()
        return {"message": f"Удалено {count} билетов"}

    async def get_tickets_stats(self, club_id: int) -> dict:
        total_result = await self.db.execute(
            select(func.count()).where(Ticket.club_id == club_id)
        )
        total = total_result.scalar() or 0

        registered_result = await self.db.execute(
            select(func.count()).where(
                Ticket.club_id == club_id,
                Ticket.is_registered == True
            )
        )
        registered = registered_result.scalar() or 0

        free = total - registered
        progress = (registered / total * 100) if total > 0 else 0

        return {
            "total": total,
            "registered": registered,
            "free": free,
            "progress_percent": round(progress, 2)
        }

    async def get_club_stats(self, club_id: int) -> dict:
        tickets_stats = await self.get_tickets_stats(club_id)

        users_result = await self.db.execute(
            select(func.count()).where(User.club_id == club_id)
        )
        users_count = users_result.scalar() or 0

        return {
            "tickets": tickets_stats,
            "users_count": users_count
        }

    async def get_registration_progress(self, club_id: int) -> float:
        stats = await self.get_tickets_stats(club_id)
        return stats["progress_percent"]
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func, update

from database import AsyncSessionLocal
from models import Raffle, Ticket, User
from schemas import RaffleCreate, RaffleUpdate


class RaffleService:
    def __init__(self, db: AsyncSessionLocal):
        self.db = db

    async def get_raffle_by_id(self, raffle_id: int) -> Raffle:
        existing = await self.db.execute(
            select(Raffle).where(Raffle.id == raffle_id)
        )
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        return raffle

    async def get_raffles_by_club(self, club_id: int) -> List[Raffle]:
        existing = await self.db.execute(
            select(Raffle).where(Raffle.club_id == club_id)
        )
        return existing.scalars().all()

    async def get_active_raffles(self, club_id: int) -> List[Raffle]:
        existing = await self.db.execute(
            select(Raffle).where(
                Raffle.club_id == club_id,
                Raffle.is_active == True
            )
        )
        return existing.scalars().all()

    async def get_raffles_by_user(self, user_id: int) -> List[Raffle]:
        existing = await self.db.execute(
            select(Raffle).where(Raffle.created_by == user_id)
        )
        return existing.scalars().all()

    async def get_all_raffles(self) -> List[Raffle]:
        existing = await self.db.execute(select(Raffle))
        return existing.scalars().all()

    async def create_raffle(self, data: RaffleCreate, user_id: int) -> Raffle:
        raffle = Raffle(
            title=data.title,
            description=data.description,
            prize=data.prize,
            club_id=data.club_id,
            created_by=user_id,
            start_date=data.start_date,
            end_date=data.end_date,
            is_active=True
        )

        self.db.add(raffle)
        await self.db.commit()
        await self.db.refresh(raffle)
        return raffle

    async def update_raffle(self, raffle_id: int, data: RaffleUpdate) -> Raffle:
        raffle = await self.get_raffle_by_id(raffle_id)

        if data.title is not None:
            raffle.title = data.title
        if data.description is not None:
            raffle.description = data.description
        if data.prize is not None:
            raffle.prize = data.prize
        if data.start_date is not None:
            raffle.start_date = data.start_date
        if data.end_date is not None:
            raffle.end_date = data.end_date
        if data.is_active is not None:
            raffle.is_active = data.is_active

        await self.db.commit()
        await self.db.refresh(raffle)
        return raffle

    async def delete_raffle(self, raffle_id: int) -> dict:
        raffle = await self.get_raffle_by_id(raffle_id)
        await self.db.delete(raffle)
        await self.db.commit()
        return {"message": "Raffle deleted"}

    async def activate_raffle(self, raffle_id: int) -> Raffle:
        raffle = await self.get_raffle_by_id(raffle_id)
        raffle.is_active = True
        await self.db.commit()
        await self.db.refresh(raffle)
        return raffle

    async def deactivate_raffle(self, raffle_id: int) -> Raffle:
        raffle = await self.get_raffle_by_id(raffle_id)
        raffle.is_active = False
        await self.db.commit()
        await self.db.refresh(raffle)
        return raffle

    async def check_raffle_active(self, raffle_id: int) -> bool:
        raffle = await self.get_raffle_by_id(raffle_id)
        if raffle.is_active and raffle.end_date > datetime.now():
            return True
        return False

    async def is_raffle_expired(self, raffle_id: int) -> bool:
        raffle = await self.get_raffle_by_id(raffle_id)
        return raffle.end_date < datetime.now()

    async def draw_winner(self, raffle_id: int) -> dict:
        import random

        raffle = await self.get_raffle_by_id(raffle_id)

        result = await self.db.execute(
            select(Ticket).where(
                Ticket.raffle_id == raffle_id,
                Ticket.is_registered == True
            )
        )
        tickets = result.scalars().all()

        if not tickets:
            raise HTTPException(status_code=404, detail="No registered tickets")

        winner_ticket = random.choice(tickets)
        winner = await self.db.get(User, winner_ticket.user_id)

        raffle.is_active = False


        stmt = update(Ticket).where(Ticket.raffle_id == raffle_id).values(is_active=False)
        await self.db.execute(stmt)


        await self.db.commit()


        return {
            "raffle_id": raffle.id,
            "title": raffle.title,
            "prize": raffle.prize,
            "winner_ticket": winner_ticket.number,
            "winner_username": winner.username if winner else None,
            "winner_telegram_id": winner.telegram_id if winner else None
        }

    async def get_raffle_results(self, raffle_id: int) -> dict:
        raffle = await self.get_raffle_by_id(raffle_id)

        result = await self.db.execute(
            select(Ticket).where(
                Ticket.raffle_id == raffle_id,
                Ticket.is_registered == True
            )
        )
        tickets = result.scalars().all()

        participants = []
        for ticket in tickets:
            user = await self.db.get(User, ticket.user_id)
            if user:
                participants.append({
                    "ticket_number": ticket.number,
                    "username": user.username,
                    "telegram_id": user.telegram_id,
                    "registered_at": ticket.registered_at.isoformat() if ticket.registered_at else None
                })

        return {
            "raffle_id": raffle.id,
            "title": raffle.title,
            "prize": raffle.prize,
            "total_participants": len(participants),
            "participants": participants
        }

    async def get_raffle_stats(self, raffle_id: int) -> dict:
        raffle = await self.get_raffle_by_id(raffle_id)

        total_result = await self.db.execute(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.raffle_id == raffle_id)
        )
        total = total_result.scalar() or 0

        registered_result = await self.db.execute(
            select(func.count())
            .select_from(Ticket)
            .where(
                Ticket.raffle_id == raffle_id,
                Ticket.is_registered == True
            )
        )
        registered = registered_result.scalar() or 0

        free = total - registered

        users_result = await self.db.execute(
            select(func.count())
            .select_from(User)
            .where(User.club_id == raffle.club_id)
        )
        users_count = users_result.scalar() or 0

        return {
            "raffle_id": raffle.id,
            "title": raffle.title,
            "total_tickets": total,
            "registered": registered,
            "free": free,
            "participants": users_count,
            "is_active": raffle.is_active
        }
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func

from database import AsyncSessionLocal
from models import Raffle, Ticket, User
from schemas import RaffleCreate, RaffleUpdate


class RaffleService():
    def __init__(self, db: AsyncSessionLocal):
        self.db = db

    async def get_raffle_by_id(self, raffle_id: int) -> Raffle:
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        return raffle

    async def get_raffles_by_club(self, club_id: int) -> List[Raffle]:
        existing = await self.db.execute(select(Raffle).where(Raffle.club_id == club_id))
        raffles = existing.scalars().all()
        return raffles

    async def get_active_raffles(self, club_id: int) -> List[Raffle]:
        existing = await self.db.execute(select(Raffle).where(Raffle.club_id == club_id).where(Raffle.is_active  == True))
        raffles = existing.scalars().all()
        return raffles

    async def get_raffles_by_user(self, user_id: int) -> List[Raffle]:
        existing = await self.db.execute(select(Raffle).where(Raffle.created_by == user_id))
        raffles = existing.scalars().all()
        return raffles

    async def get_all_raffles(self) -> List[Raffle]:
        existing = await self.db.execute(select(Raffle))
        raffles = existing.scalars().all()
        return raffles

    async def create_raffle(self, data: RaffleCreate, user_id: int) -> Raffle:
        raffle = Raffle(
            title = data.title,
            description = data.description,
            prize = data.prize,
            club_id = data.club_id,
            created_by = user_id,
            start_date=data.start_date,
            end_date=data.end_date,
            is_active=True
        )

        self.db.add(raffle)
        await self.db.commit()
        await self.db.refresh(raffle)
        return raffle

    async def update_raffle(self, raffle_id: int, data: RaffleUpdate) -> Raffle:
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
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
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        self.db.delete(raffle)
        await self.db.commit()
        return {
            "message": "Raffle deleted"
        }

    async def activate_raffle(self, raffle_id: int) -> Raffle:
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        raffle.is_active = True
        await self.db.commit()
        await self.db.refresh(raffle)
        return raffle

    async def deactivate_raffle(self, raffle_id: int) -> Raffle:
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        raffle.is_active = False
        await self.db.commit()
        await self.db.refresh(raffle)
        return raffle

    async def check_raffle_active(self, raffle_id: int) -> bool:
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        if raffle.is_active and raffle.end_date > datetime.now():
            return True
        return False

    async def is_raffle_expired(self, raffle_id: int) -> bool:
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        if raffle.end_date < datetime.now():
            return True
        return False

    async def get_raffle_stats(self, raffle_id:int) -> dict:
        existing = await self.db.execute(select(Raffle).where(Raffle.id == raffle_id))
        raffle = existing.scalar_one_or_none()
        if not raffle:
            raise HTTPException(status_code=404, detail="Raffle not found")
        total_result = await self.db.execute(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.club_id == raffle.club_id)
        )

        total = total_result.scalar() or 0

        registered_ticket = await self.db.execute(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.club_id == raffle.club_id)
            .where(Ticket.is_registered == True)
        )

        registered = registered_ticket.scalar() or 0

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






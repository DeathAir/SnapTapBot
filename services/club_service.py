from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func

from database import AsyncSessionLocal
from models import Clubs, User, Ticket
from schemas import ClubResponse, ClubCreate, ClubUpdate


class ClubService:
    def __init__(self, db: AsyncSessionLocal):
        self.db = db


    async def get_club_by_id(self, club_id: int) -> Clubs:
        existing_club = await self.db.execute(select(Clubs).where(Clubs.id == club_id))
        result = existing_club.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="Club not found")
        return result

    async def get_club_by_name(self, name: str) -> ClubResponse:
        existing_club = await self.db.execute(select(Clubs).where(Clubs.name == name))
        result = existing_club.scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="Club not found")
        return result

    async def get_all_clubs(self) -> List[Clubs]:
        exiting_club = await self.db.execute(select(Clubs).order_by(Clubs.name.desc()))
        result = exiting_club.scalars().all()
        return result

    async def get_active_clubs(self) -> List[Clubs]:
        existing_ative_club = await self.db.execute(select(Clubs).where(Clubs.is_active == True))
        result = existing_ative_club.scalars().all()
        return result

    async def create_club(self, club_data: ClubCreate) -> Clubs:
        result = await self.db.execute(
            select(Clubs).where(Clubs.name == club_data.name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Club already exists")

        new_club = Clubs(
            name=club_data.name,
            address=club_data.address,
            phone=club_data.phone,
        )
        await self.db.add(new_club)
        await self.db.commit()
        await self.db.refresh(new_club)
        return new_club

    async def update_club(self, club_id: int, club_data: ClubUpdate) -> Clubs:
        existing_club = await self.get_club_by_id(club_id)

        if club_data.name is not None:
            existing_club.name = club_data.name
        if club_data.address is not None:
            existing_club.address = club_data.address
        if club_data.phone is not None:
            existing_club.phone = club_data.phone
        if club_data.is_active is not None:
            existing_club.is_active = club_data.is_active
        if club_data.subscription_end is not None:
            existing_club.subscription_end = club_data.subscription_end

        await self.db.commit()
        await self.db.refresh(existing_club)
        return existing_club

    async def activate_club(self, club_id: int) -> Clubs:
        existing_club = await self.get_club_by_id(club_id)

        existing_club.is_active = True

        await self.db.commit()
        await self.db.refresh(existing_club)

        return existing_club

    async def deactivate_club(self, club_id: int) -> Clubs:
        existing_club = await self.get_club_by_id(club_id)

        existing_club.is_active = False

        await self.db.commit()
        await self.db.refresh(existing_club)

        return existing_club

    async def check_subscription(self, club_id: int) -> bool:
        existing_club = await self.get_club_by_id(club_id)
        if not existing_club.subscription_end:
            return False
        return existing_club.subscription_end > datetime.now()

    async def renew_subscription(self, club_id: int, days: int = 30) -> Clubs:
        """Продлить подписку на N дней"""
        club = await self.get_club_by_id(club_id)
        from datetime import timedelta
        club.subscription_end = datetime.now() + timedelta(days=days)
        await self.db.commit()
        await self.db.refresh(club)
        return club

    async def get_club_stats(self, club_id: int) -> dict:

        club = await self.get_club_by_id(club_id)

        users_result = await self.db.execute(
            select(func.count()).where(User.club_id == club_id)
        )
        users_count = users_result.scalar() or 0

        tickets_result = await self.db.execute(
            select(func.count()).where(Ticket.club_id == club_id)
        )
        tickets_count = tickets_result.scalar() or 0

        return {
            "club_id": club.id,
            "name": club.name,
            "users_count": users_count,
            "tickets_count": tickets_count,
            "is_active": club.is_active,

        }

    async def delete_club(self, club_id: int):
        club = await self.get_club_by_id(club_id)
        if club is None:
            raise HTTPException(status_code=404, detail="Club not found")
        await self.db.delete(club)
        await self.db.commit()
        return {"message": "Club deleted"}





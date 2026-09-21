from typing import Optional

from sqlalchemy import select

from database import AsyncSessionLocal
from models import User


class AuthService:
    def __init__(self, db: AsyncSessionLocal):
        self.db = db

    async def is_admin(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False

        return user.role == 'admin'

    async def is_superadmin(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        return user.role == 'superadmin'

    async def is_user(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return False
        return user.role == 'user'

    async def has_role(self, user_id: int, role: str) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        return user.role == role

    async def check_club_access(self, user_id: int, club_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        if user.role == "superadmin":
            return True
        if user.club_id == club_id:
            return True
        return False

    async def get_user_club(self, user_id: int) -> Optional[int]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return None
        return user.club_id

    async def check_admin_club(self, user_id: int, club_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        if user.role != "admin":
            return False
        if user.club_id != club_id:
            return False
        return True

    async def can_manage_tickets(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        return user.role in ["admin", "superadmin"]

    async def can_view_stats(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        return user.role in ["admin", "superadmin"]

    async def can_manage_clubs(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        return user.role == "superadmin"

    async def can_generate_tickets(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        return user.role in ["admin", "superadmin"]

    async def can_view_reports(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return False
        return user.role in ["admin", "superadmin"]






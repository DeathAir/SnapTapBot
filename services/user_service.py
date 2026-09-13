from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func

from database import AsyncSessionLocal
from models import User
from schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSessionLocal):
        self.db = db

    async def get_or_create_user(self,
                                 user: UserCreate) -> User:
        existing = await self.db.execute(select(User).where(User.telegram_id == user.telegram_id))
        result = existing.scalar()
        if result is None:
            New_User = User(
                telegram_id=user.telegram_id,
                username=user.username,
                phone=user.phone,
                role=user.role,
                club_id=user.club_id
            )
            new_user = New_User
            await self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        else:
            return result

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        existing = await self.db.execute(select(User).where(User.telegram_id == telegram_id))
        result = existing.scalar()
        if result is None:
            raise HTTPException(status_code=404,
                                detail="User not found"
                                )
        return result

    async def get_user_by_id(self, user_id: int) -> User:
        existing = await self.db.execute(select(User).where(User.id == user_id))
        result = existing.scalar()
        if result is None:
            raise HTTPException(status_code=404,
                                detail="User not found"
            )
        return result

    async def get_user_by_username(self, username: str) -> User:
        existing = await self.db.execute(select(User).where(User.username == username))
        result = existing.scalar()
        if result is None:
            raise HTTPException(status_code=404,
                                detail="User not found"
            )
        return result

    async def get_user_by_club(self, club_id: int) -> User:
        existing = await self.db.execute(
            select(User).where(User.club_id == club_id)
        )
        return existing.scalars().all()

    async def get_all_users(self) -> List[User]:
        existing = await self.db.execute(select(User))
        result = existing.scalars().all()
        return result

    async def get_user_club(self, club_id: int) -> User:
        existing = await self.db.execute(select(User).where(User.club_id == club_id))
        result = existing.scalar().all()
        return result

    async def create_user(self, user_data: UserCreate) -> User:
        new_user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            phone=user_data.phone,
            role=user_data.role,
        )
        await self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = await self.get_user_by_id(user_id)
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.phone is not None:
            user.phone = user_data.phone
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_activity(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.last_activity = datetime.now()
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def set_user_club(self, user_id: int, club_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.club_id = club_id
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_role(self, user_id: int, role: str):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if role not in ["user", "admin", "superadmin"]:
            raise ValueError(f"Недопустимая роль: {role}")

        user.role = role
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_role(self, user_id: int):
        user_role = await self.db.execute(select(User.role).where(User.id == user_id))
        result = user_role.scalars().one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        return result

    async def make_admin(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.role = 'admin'
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def make_superadmin(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.role = 'superadmin'
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def remove_admin(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.role = 'user'
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def deactivate_user(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def is_user_active(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_active:
            return True
        return False

    async def get_active_users(self, user_id: int) -> List[User]:
        result = await self.db.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()

    async def get_total_users_count(self) -> int:
        existing = await self.db.execute(
        select(func.count()).select_from(User)
    )
        result = existing.scalars().one_or_none()
        return result

    async def get_total_clubs_count(self) -> int:
        existing = await self.db.execute(
        select(func.count(func.distinct(User.club_id)))
    )
        result = existing.scalars().one_or_none()
        return result

    async def delete_user(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        await self.db.delete(user)
        await self.db.commit()
        return {"message": "User deleted"}






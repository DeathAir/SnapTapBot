from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select, func, delete

from database import AsyncSessionLocal
from models import Logs
from schemas import LogCreate


class LogService:
    def __init__(self, db: AsyncSessionLocal):
        self.db = db

    async def create_log(
        self,
        user_id: int,
        action: str,
        ticket_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None
    ) -> Logs:
        new_log = Logs(
            user_id=user_id,
            action=action,
            ticket_id=ticket_id,
            ip_address=ip_address,
            details=details
        )
        self.db.add(new_log)
        await self.db.commit()
        await self.db.refresh(new_log)
        return new_log

    async def create_ticket_log(
        self,
        user_id: int,
        ticket_id: int,
        action: str
    ) -> Logs:
        return await self.create_log(
            user_id=user_id,
            action=action,
            ticket_id=ticket_id
        )

    async def create_user_log(
        self,
        user_id: int,
        action: str
    ) -> Logs:
        return await self.create_log(
            user_id=user_id,
            action=action
        )

    async def get_log_by_id(self, log_id: int) -> Logs:
        result = await self.db.execute(
            select(Logs).where(Logs.id == log_id)
        )
        log = result.scalar_one_or_none()
        if log is None:
            raise HTTPException(status_code=404, detail="Log not found")
        return log

    async def get_user_logs(self, user_id: int) -> List[Logs]:
        result = await self.db.execute(
            select(Logs)
            .where(Logs.user_id == user_id)
            .order_by(Logs.created_at.desc())
        )
        return result.scalars().all()

    async def get_ticket_logs(self, ticket_id: int) -> List[Logs]:
        result = await self.db.execute(
            select(Logs)
            .where(Logs.ticket_id == ticket_id)
            .order_by(Logs.created_at.desc())
        )
        return result.scalars().all()

    async def get_logs_by_action(self, action: str) -> List[Logs]:
        result = await self.db.execute(
            select(Logs)
            .where(Logs.action == action)
            .order_by(Logs.created_at.desc())
        )
        return result.scalars().all()

    async def get_logs_by_date_range(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> List[Logs]:
        result = await self.db.execute(
            select(Logs)
            .where(Logs.created_at >= date_from)
            .where(Logs.created_at <= date_to)
            .order_by(Logs.created_at.desc())
        )
        return result.scalars().all()

    async def get_all_logs(self) -> List[Logs]:
        result = await self.db.execute(
            select(Logs).order_by(Logs.created_at.desc())
        )
        return result.scalars().all()

    async def get_logs_stats(self) -> dict:
        total_result = await self.db.execute(
            select(func.count()).select_from(Logs)
        )
        total = total_result.scalar() or 0

        today = datetime.now().replace(hour=0, minute=0, second=0)
        today_result = await self.db.execute(
            select(func.count()).where(Logs.created_at >= today)
        )
        today_count = today_result.scalar() or 0

        week_ago = datetime.now() - timedelta(days=7)
        week_result = await self.db.execute(
            select(func.count()).where(Logs.created_at >= week_ago)
        )
        week_count = week_result.scalar() or 0

        return {
            "total": total,
            "today": today_count,
            "week": week_count
        }

    async def get_actions_count(self) -> dict:
        result = await self.db.execute(
            select(Logs.action, func.count(Logs.id))
            .group_by(Logs.action)
        )
        return {action: count for action, count in result.all()}

    async def get_user_activity(self, user_id: int) -> dict:
        total_result = await self.db.execute(
            select(func.count()).where(Logs.user_id == user_id)
        )
        total = total_result.scalar() or 0

        last_result = await self.db.execute(
            select(Logs)
            .where(Logs.user_id == user_id)
            .order_by(Logs.created_at.desc())
            .limit(1)
        )
        last_log = last_result.scalar_one_or_none()

        return {
            "user_id": user_id,
            "total_actions": total,
            "last_action": last_log.action if last_log else None,
            "last_activity": last_log.created_at if last_log else None
        }

    async def delete_old_logs(self, days: int = 30) -> int:
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await self.db.execute(
            delete(Logs).where(Logs.created_at < cutoff_date)
        )
        await self.db.commit()
        return result.rowcount

    async def delete_user_logs(self, user_id: int) -> int:
        result = await self.db.execute(
            delete(Logs).where(Logs.user_id == user_id)
        )
        await self.db.commit()
        return result.rowcount

    async def clear_logs(self) -> dict:
        result = await self.db.execute(delete(Logs))
        await self.db.commit()
        return {"message": "All logs cleared", "deleted": result.rowcount}
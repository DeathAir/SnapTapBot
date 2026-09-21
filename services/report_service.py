import csv
import json
import os
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func

from database import AsyncSessionLocal
from models import Ticket, User, Clubs


class ReportService:
    def __init__(self, db: AsyncSessionLocal):
        self.db = db

    async def generate_tickets_report(self, club_id: int) -> List[dict]:
        existing = await self.db.execute(
            select(Ticket).where(Ticket.club_id == club_id)
        )
        tickets = existing.scalars().all()
        report = []

        for ticket in tickets:
            row = {
                "ticket_number": ticket.number,  # ← исправлено
                "is_registered": ticket.is_registered,
                "registered_by": None,
                "registered_at": None
            }

            if ticket.is_registered and ticket.user_id:
                user = await self.db.get(User, ticket.user_id)
                if user:
                    row["registered_by"] = user.username
                    row["registered_at"] = (
                        ticket.registered_at.isoformat()
                        if ticket.registered_at
                        else None
                    )

            report.append(row)

        return report

    async def generate_users_report(self, club_id: int) -> List[dict]:
        existing = await self.db.execute(
            select(User).where(User.club_id == club_id)
        )
        users = existing.scalars().all()
        report = []

        for user in users:
            count_result = await self.db.execute(
                select(func.count())
                .select_from(Ticket)
                .where(Ticket.user_id == user.id)
            )
            count = count_result.scalar() or 0

            row = {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "role": user.role,
                "tickets_count": count,
            }
            report.append(row)

        return report

    async def generate_club_report(self, club_id: int) -> dict:
        club_result = await self.db.execute(
            select(Clubs).where(Clubs.id == club_id)
        )
        club = club_result.scalar_one_or_none()
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")

        total_result = await self.db.execute(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.club_id == club_id)
        )
        total = total_result.scalar() or 0

        registered_result = await self.db.execute(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.club_id == club_id)
            .where(Ticket.is_registered == True)
        )
        registered = registered_result.scalar() or 0

        users_result = await self.db.execute(
            select(func.count())
            .select_from(User)
            .where(User.club_id == club_id)
        )
        users_count = users_result.scalar() or 0

        return {
            "club_id": club.id,
            "name": club.name,
            "total_tickets": total,
            "registered": registered,
            "free": total - registered,
            "users_count": users_count
        }

    async def generate_csv_report(self, club_id: int) -> str:
        data = await self.generate_tickets_report(club_id)
        if not data:
            raise HTTPException(status_code=404, detail="Club not found")
        folder = "reports"
        os.makedirs(folder, exist_ok=True)
        file_path = f"{folder}/club_{club_id}_tickets.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return file_path

    async def generate_json_report(self, club_id: int) ->dict:
        data = await self.generate_tickets_report(club_id)
        return {
            "club_id": club_id,
            "generated_at": datetime.now().isoformat(),
            "tickets": data
        }

    async def generate_full_report(self, club_id: int) -> dict:
        club = await self.generate_club_report(club_id)
        tickets = await self.generate_tickets_report(club_id)
        users = await self.generate_users_report(club_id)
        return {
            "club": club,
            "tickets": tickets,
            "users": users
        }



from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportFilter(BaseModel):
    club_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    registered_only: bool = Field(default=False)


class ReportRow(BaseModel):
    """Строка отчёта"""
    ticket_number: int
    club_name: str
    is_registered: bool
    registered_by: Optional[str] = None
    registered_at: Optional[datetime] = None

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    action: str
    ip_adress:str
    details:dict
    user_id: int
    club_id: int
    ticket_id: int

class LogCreate(LogBase):
    pass


class LogResponse(LogBase):
    id: int
    created_at: datetime

    config = ConfigDict(from_attributes=True)

class LogListResponse(BaseModel):
    """Список логов"""
    logs: list[LogResponse]
    total: int
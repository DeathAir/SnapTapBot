from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class TicketBase(BaseModel):
    number: int
    secret_hash: str
    club_id: int

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: int
    is_registered: bool
    created_at: datetime
    updated_at:datetime
    registered_at: datetime
    user_id: int

class TicketVerify(BaseModel):
    ticket_number: int = Field(..., alias="ticketNumber", description="Ticket number from QR code")
    secret_hash: str = Field(..., alias="secretHash", description="Secret Hash from QR code")
    telegram_id: int = Field(..., alias="telegramId", description="Telegram Id Users")

class TicketVerifyResponse(BaseModel):
    status: str = Field(..., alias="status", description="success / error")
    message: str = Field(..., alias="message", description="Сообщение")
    ticket_number: int = Field(..., alias="ticketNumber", description="Ticket number")
    club_name: str = Field(..., alias="clubName", description="Club name")

    config = ConfigDict(from_attributes=True)

class TicketStatusResponse(BaseModel):
    """Ответ при проверке статуса билета"""
    ticket_number: int
    is_registered: bool
    registered_by: Optional[str] = Field(None, description="Кто зарегистрировал")
    registered_at: Optional[datetime] = None

class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int

class TicketGenerateRequest(BaseModel):
    club_id: int = Field(..., alias="clubId", description="Club Id")
    count: int = Field(..., min_length=1, max_length=1000, description="Count of tickets")
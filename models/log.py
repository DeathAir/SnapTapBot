from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, JSON, func, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database import Base


class Logs(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    ticket_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)

    club = relationship("Club", back_populates="logs")
    user = relationship("User", back_populates="logs")
    ticket = relationship("Ticket", back_populates="logs")

    def __repr__(self):
        return f"<Logs(id={self.id}, action={self.action}, ip_address={self.ip_address})>"
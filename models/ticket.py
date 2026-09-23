from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, DateTime, func, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    secret_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    registered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    raffle_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("raffles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    club_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    raffle = relationship("Raffle", back_populates="tickets")
    club = relationship("Club", back_populates="tickets")
    user = relationship("User", back_populates="tickets")
    logs = relationship("Logs", back_populates="ticket")

    __table_args__ = (
        UniqueConstraint("number", "club_id", "raffle_id", name="unique_ticket_per_raffle"),
    )

    def __repr__(self):
        return f"<Ticket(id={self.id}, number={self.number}, club_id={self.club_id}, is_registered={self.is_registered})>"
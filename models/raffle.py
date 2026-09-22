from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Raffle(Base):
    __tablename__ = "raffles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(125), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    prize: Mapped[str] = mapped_column(String(500), nullable=False)

    club_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )

    club = relationship("Club", back_populates="raffles")
    creator = relationship("User", back_populates="raffles")
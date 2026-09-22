import enum

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, func, TIMESTAMP, BigInteger, Boolean


class UserRole(enum.Enum):
    user = 'user'
    admin = 'admin'
    superadmin = 'superadmin'

user_role_pg_enum = ENUM(
    UserRole,
    name='user_role_enum',
    create_type=True,
    vilidate_string=True
)


import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    BigInteger, String, Boolean, DateTime,
    ForeignKey, func, Text
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserRole(enum.Enum):
    user = 'user'
    admin = 'admin'
    superadmin = 'superadmin'


user_role_pg_enum = ENUM(
    UserRole,
    name='user_role_enum',
    create_type=True,
    validate_strings=True
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(125), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(
        user_role_pg_enum,
        nullable=False,
        default=UserRole.user,
        server_default="user"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    club_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    club = relationship("Club", back_populates="users")
    tickets = relationship("Ticket", back_populates="user")
    logs = relationship("Log", back_populates="user")
    raffles = relationship("Raffle", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

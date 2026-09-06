import enum

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, func, TIMESTAMP, BigInteger

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


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[String] = mapped_column(String(125), nullable=False, unique=True)
    phone: Mapped[String] = mapped_column(String(12), nullable=False, unique=True)
    role: Mapped[String] = mapped_column(
        user_role_pg_enum,
        nullable=False,
        default=UserRole.user,
        server_default="user"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role.value})>"

    club_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    club = relationship("Club", back_populates="users")
    ticket = relationship("Ticket", back_populates="users")
    logs = relationship("Log", back_populates="users")

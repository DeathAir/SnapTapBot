from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import  declarative_base

from config import settings




async_engine = create_async_engine(settings.database_url,
                                   echo=False,
                                   poll_size=10,
                                   max_overflow=20,
                                   pool_pre_ping=True,
                                   pool_recycle=3600,
                                   pool_timeout=30,)

AsyncSessionLocal = async_sessionmaker(bind=async_engine,
                             autocommit=False,
                             autoflush=False,
                             expire_on_commit=False,
                             class_=AsyncSession,)

Base = declarative_base()

async def get_session():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
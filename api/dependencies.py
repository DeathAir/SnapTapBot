import secrets

from fastapi import Header, HTTPException, status

from config import settings
from database import get_session


async def get_db():
    async for session in get_session():
        yield session


async def verify_api_key(x_api_key: str = Header(default="")) -> None:

    expected = settings.api_key


    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_KEY is not configured on server",
        )


    if not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
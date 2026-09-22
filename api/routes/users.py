from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from schemas import UserResponse, UserCreate, UserUpdate
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(data: UserCreate, db: AsyncSession  = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_or_create_user(data)
    return user

@router.get("/me", response_model=UserResponse)
async def me(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserResponse)
async def update_user(telegram_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await user_service.update_user(user.id, user_data) # type: ignore
    return updated_user

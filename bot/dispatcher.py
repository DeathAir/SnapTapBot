from aiogram import Dispatcher
from aiogram.utils import keyboard

from bot.api_client import ApiClient
from bot.handlers import user, admin, superadmin
from config import settings



def setup_dispatcher() -> tuple[Dispatcher, ApiClient]:
    api_client: ApiClient = ApiClient(
        base_url=settings.base_url,
        api_key=settings.api_key,
    )

    dp = Dispatcher()

    dp.workflow_data["api_client"] = api_client
    dp.workflow_data["settings"] = settings
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(superadmin.router)

    return dp, api_client

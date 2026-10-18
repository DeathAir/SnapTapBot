import asyncio
import logging

from aiogram import Bot

from bot.dispatcher import setup_dispatcher
from config import settings


logging.basicConfig(level=logging.INFO)


async def main() -> None:

    bot = Bot(token=settings.bot_token)
    dp, api_client = setup_dispatcher()
    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
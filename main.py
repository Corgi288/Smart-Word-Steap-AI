import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import TOKEN_TG
from app.hendllers import router
from app.database.models import async_main


async def main():
    await async_main()
    bot = Bot(TOKEN_TG)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


logging.basicConfig(level=logging.INFO)
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot of")
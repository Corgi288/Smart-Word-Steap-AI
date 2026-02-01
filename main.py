"""
This file is the entry point for the Telegram bot.
It initializes the database, configures the bot, and starts polling for updates.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import TOKEN_TG
from app.hendllers import router
from app.database.models import async_main


async def main():
    """
    Main entry point for the bot.
    Initializes the database, sets up the dispatcher, and starts polling.

    Returns:
        None
    """
    await async_main()
    bot = Bot(token=TOKEN_TG)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


logging.basicConfig(level=logging.INFO)
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot of")
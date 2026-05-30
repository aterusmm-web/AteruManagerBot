import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db
import handler_start
import handler_chat_menu
import handler_messages
import handler_moderation
import handler_pinning
import handler_reactions
import handler_settings
import handler_poll
import handler_broadcast
import handler_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


async def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не задан! Укажите его в переменных окружения.")
        sys.exit(1)

    await init_db()
    logger.info("База данных инициализирована")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(handler_start.router)
    dp.include_router(handler_chat_menu.router)
    dp.include_router(handler_messages.router)
    dp.include_router(handler_moderation.router)
    dp.include_router(handler_pinning.router)
    dp.include_router(handler_reactions.router)
    dp.include_router(handler_settings.router)
    dp.include_router(handler_poll.router)
    dp.include_router(handler_broadcast.router)
    dp.include_router(handler_commands.router)

    bot_info = await bot.get_me()
    logger.info(f"Запуск бота @{bot_info.username} (ID: {bot_info.id})")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())

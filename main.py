import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

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
import handler_my_chat_member

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    """Регистрация подсказок команд при вводе /"""

    # Команды в личных сообщениях
    private_commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="help", description="Помощь и список функций"),
    ]

    # Команды в группах и каналах
    group_commands = [
        BotCommand(command="menu", description="Меню управления ботом"),
        BotCommand(command="link", description="Привязать этот чат к боту"),
        BotCommand(command="pin", description="Закрепить сообщение (ответом)"),
        BotCommand(command="unpin", description="Открепить сообщение"),
        BotCommand(command="ban", description="Забанить пользователя (ответом)"),
        BotCommand(command="mute", description="Замутить пользователя (ответом)"),
        BotCommand(command="warn", description="Предупреждение пользователю (ответом)"),
        BotCommand(command="id", description="Узнать ID пользователя или чата"),
        BotCommand(command="help", description="Список команд"),
    ]

    await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())
    logger.info("Команды бота зарегистрированы")


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

    # Подключаем все роутеры
    dp.include_router(handler_my_chat_member.router)  # первым — важно для событий вступления
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

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    # Указываем allowed_updates включая my_chat_member
    await dp.start_polling(
        bot,
        allowed_updates=["message", "callback_query", "my_chat_member", "chat_member"]
    )


if __name__ == "__main__":
    asyncio.run(main())

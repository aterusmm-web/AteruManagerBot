"""
Обработчик событий изменения статуса бота в чатах.
Срабатывает когда бот добавляется/удаляется из группы или канала.
"""
from aiogram import Router, F
from aiogram.types import (
    ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, Message
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION

router = Router()


def chat_added_inline_kb(bot_username: str, chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🤖 Управлять ботом в ЛС",
        url=f"https://t.me/{bot_username}?start=manage"
    ))
    builder.row(InlineKeyboardButton(
        text="➕ Привязать этот чат к боту",
        url=f"https://t.me/{bot_username}?start=link_{chat_id}"
    ))
    return builder.as_markup()


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_added_to_chat(event: ChatMemberUpdated):
    """Срабатывает когда бот добавлен в группу или канал."""
    chat = event.chat
    added_by = event.from_user
    bot_info = await event.bot.get_me()

    chat_title = chat.title or str(chat.id)
    chat_type_ru = {
        "group": "группа",
        "supergroup": "супергруппа",
        "channel": "канал"
    }.get(chat.type, chat.type)

    chat_kb = chat_added_inline_kb(bot_info.username, chat.id)

    # 1. Приветственное сообщение в чате
    try:
        await event.bot.send_message(
            chat.id,
            f"👋 Привет! Я бот-администратор для управления этим чатом.\n\n"
            f"Чтобы привязать <b>{chat_title}</b> к своему аккаунту и управлять им через ЛС — нажмите кнопку ниже.\n\n"
            f"📋 Доступные команды: /help",
            parse_mode="HTML",
            reply_markup=chat_kb
        )
    except Exception:
        pass

    # 2. Уведомление в ЛС тому, кто добавил бота
    try:
        await event.bot.send_message(
            added_by.id,
            f"✅ <b>Бот добавлен в чат!</b>\n\n"
            f"📌 Чат: <b>{chat_title}</b>\n"
            f"📂 Тип: {chat_type_ru}\n"
            f"🆔 ID чата: <code>{chat.id}</code>\n\n"
            f"Теперь привяжите этот чат к своему аккаунту, чтобы управлять им через меня. "
            f"Для этого нажмите кнопку ниже или отправьте ID чата через меню «Добавить чат».",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="➕ Привязать чат к аккаунту",
                    callback_data=f"add_method2"
                )
            ]])
        )
    except Exception:
        # Пользователь не начал диалог с ботом — нельзя отправить ЛС
        pass

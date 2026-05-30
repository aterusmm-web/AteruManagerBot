"""Команды, работающие прямо в чате (бот должен быть администратором)."""
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import (
    Message, ChatPermissions,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import Command

from database import add_chat, add_warning, log_event

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup", "channel"}))


def chat_control_reply_kb() -> ReplyKeyboardMarkup:
    """Постоянная клавиатура в чате для быстрых действий."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📋 Команды бота"),
        KeyboardButton(text="🆔 Мой ID")
    )
    builder.row(
        KeyboardButton(text="📌 Закрепить"),
        KeyboardButton(text="📍 Открепить")
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def chat_control_inline_kb(bot_username: str, chat_id: int) -> InlineKeyboardMarkup:
    """Inline-кнопки для управления ботом из чата."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🤖 Управление в ЛС",
        url=f"https://t.me/{bot_username}?start=manage"
    ))
    builder.row(InlineKeyboardButton(
        text="➕ Добавить этот чат к боту",
        url=f"https://t.me/{bot_username}?start=link_{chat_id}"
    ))
    return builder.as_markup()


@router.message(Command("start"))
async def cmd_start_chat(message: Message):
    """Стартовая команда в чате — показывает клавиатуру и меню."""
    bot_info = await message.bot.get_me()
    await message.reply(
        f"👋 <b>Бот-администратор готов к работе!</b>\n\n"
        f"Используйте кнопки ниже или напишите /help для списка команд.\n"
        f"Для полного управления — откройте ЛС с ботом @{bot_info.username}",
        parse_mode="HTML",
        reply_markup=chat_control_reply_kb()
    )


@router.message(Command("help"))
async def cmd_help_chat(message: Message):
    """Список команд в чате."""
    bot_info = await message.bot.get_me()
    await message.reply(
        "📋 <b>Команды в чате:</b>\n\n"
        "/link — привязать чат к боту\n"
        "/pin — закрепить сообщение (ответом)\n"
        "/unpin — открепить сообщение\n"
        "/ban — забанить пользователя (ответом)\n"
        "/mute [минуты] — замутить пользователя (ответом)\n"
        "/warn [причина] — предупреждение (3 = автобан)\n"
        "/id — узнать свой или чужой ID\n"
        "/menu — показать меню управления\n\n"
        f"Полное управление через ЛС: @{bot_info.username}",
        parse_mode="HTML",
        reply_markup=chat_control_reply_kb()
    )


@router.message(Command("menu"))
async def cmd_menu_chat(message: Message):
    """Показать inline-меню управления в чате."""
    bot_info = await message.bot.get_me()
    await message.reply(
        "🎛 <b>Меню управления</b>\n\nВыберите действие или откройте ЛС для полного управления:",
        parse_mode="HTML",
        reply_markup=chat_control_inline_kb(bot_info.username, message.chat.id)
    )


@router.message(F.text == "📋 Команды бота")
async def btn_commands(message: Message):
    bot_info = await message.bot.get_me()
    await message.reply(
        "📋 <b>Доступные команды:</b>\n\n"
        "/link — привязать чат\n"
        "/pin — закрепить (ответом)\n"
        "/unpin — открепить\n"
        "/ban — бан (ответом)\n"
        "/mute [мин] — мут (ответом)\n"
        "/warn [причина] — предупреждение\n"
        "/id — узнать ID\n"
        "/menu — меню управления\n\n"
        f"Полное управление: @{bot_info.username}",
        parse_mode="HTML"
    )


@router.message(F.text == "🆔 Мой ID")
async def btn_my_id(message: Message):
    await message.reply(
        f"👤 <b>{message.from_user.full_name}</b>\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"💬 ID чата: <code>{message.chat.id}</code>",
        parse_mode="HTML"
    )


@router.message(F.text == "📌 Закрепить")
async def btn_pin(message: Message):
    await message.reply(
        "📌 Ответьте на нужное сообщение командой /pin\n"
        "<i>Пример: ответьте на сообщение и напишите /pin</i>",
        parse_mode="HTML"
    )


@router.message(F.text == "📍 Открепить")
async def btn_unpin(message: Message):
    try:
        await message.bot.unpin_chat_message(message.chat.id)
        await message.reply("📍 Последнее закреплённое сообщение откреплено!")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("link"))
async def cmd_link(message: Message):
    chat = message.chat
    user = message.from_user
    try:
        member = await message.bot.get_chat_member(chat.id, user.id)
        if member.status not in ("creator", "administrator"):
            await message.reply("❌ Только для администраторов.")
            return
        await add_chat(user.id, chat.id, chat.title, chat.type, chat.username)
        bot_info = await message.bot.get_me()

        # Уведомление в чате
        await message.reply(
            f"✅ Чат <b>{chat.title}</b> привязан к аккаунту {user.full_name}!\n"
            f"Управляйте через ЛС: @{bot_info.username}",
            parse_mode="HTML"
        )
        # Уведомление в ЛС
        try:
            await message.bot.send_message(
                user.id,
                f"✅ <b>Чат успешно привязан!</b>\n\n"
                f"📌 Название: <b>{chat.title}</b>\n"
                f"🆔 ID: <code>{chat.id}</code>\n\n"
                f"Используйте меню для управления чатом.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="📋 Перейти к управлению", callback_data=f"chat:{chat.id}")
                ]])
            )
        except Exception:
            pass
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("pin"))
async def cmd_pin(message: Message):
    if not message.reply_to_message:
        await message.reply("❌ Используйте командой-ответом на сообщение.")
        return
    try:
        await message.bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        await log_event(message.chat.id, "pin", performed_by=message.from_user.id,
                        details=f"msg_id:{message.reply_to_message.message_id}")
        await message.reply("📌 Закреплено!")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("unpin"))
async def cmd_unpin(message: Message):
    try:
        if message.reply_to_message:
            await message.bot.unpin_chat_message(message.chat.id,
                                                  message_id=message.reply_to_message.message_id)
        else:
            await message.bot.unpin_chat_message(message.chat.id)
        await message.reply("📍 Откреплено!")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not message.reply_to_message:
        await message.reply("❌ Используйте как ответ на сообщение пользователя.")
        return
    try:
        target = message.reply_to_message.from_user
        await message.bot.ban_chat_member(message.chat.id, target.id)
        await log_event(message.chat.id, "ban", target_user_id=target.id,
                        performed_by=message.from_user.id)
        await message.reply(f"🚫 {target.full_name} забанен.")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("mute"))
async def cmd_mute(message: Message):
    if not message.reply_to_message:
        await message.reply("❌ Используйте как ответ на сообщение пользователя.")
        return
    parts = message.text.split()
    minutes = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
    try:
        target = message.reply_to_message.from_user
        until = datetime.now() + timedelta(minutes=minutes)
        await message.bot.restrict_chat_member(
            message.chat.id, target.id,
            permissions=ChatPermissions(can_send_messages=False), until_date=until
        )
        await log_event(message.chat.id, "mute", target_user_id=target.id,
                        performed_by=message.from_user.id, details=f"{minutes} мин.")
        await message.reply(f"🔇 {target.full_name} замучен на {minutes} мин.")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("warn"))
async def cmd_warn(message: Message):
    if not message.reply_to_message:
        await message.reply("❌ Используйте как ответ на сообщение пользователя.")
        return
    target = message.reply_to_message.from_user
    parts = message.text.split(maxsplit=1)
    reason = parts[1] if len(parts) > 1 else "без причины"
    total = await add_warning(message.chat.id, target.id, reason, message.from_user.id)
    await log_event(message.chat.id, "warn", target_user_id=target.id,
                    performed_by=message.from_user.id, details=reason)
    await message.reply(f"⚠️ {target.full_name} — предупреждение {total}/3!\nПричина: {reason}")
    if total >= 3:
        try:
            await message.bot.ban_chat_member(message.chat.id, target.id)
            await message.reply(f"🚫 {target.full_name} забанен за 3 предупреждения.")
        except Exception:
            pass


@router.message(Command("id"))
async def cmd_id(message: Message):
    if message.reply_to_message:
        u = message.reply_to_message.from_user
        await message.reply(f"👤 <b>{u.full_name}</b>\n🆔 <code>{u.id}</code>", parse_mode="HTML")
    else:
        await message.reply(
            f"👤 <b>{message.from_user.full_name}</b>\n"
            f"🆔 ID: <code>{message.from_user.id}</code>\n"
            f"💬 Чат ID: <code>{message.chat.id}</code>",
            parse_mode="HTML"
        )

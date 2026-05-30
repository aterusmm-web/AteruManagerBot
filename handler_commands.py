"""Команды, работающие прямо в чате (бот должен быть администратором)."""
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command

from database import add_chat, add_warning, log_event

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup", "channel"}))


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
        await message.reply(
            f"✅ Чат <b>{chat.title}</b> привязан к вашему аккаунту!\n"
            "Управляйте им в ЛС с ботом.",
            parse_mode="HTML"
        )
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

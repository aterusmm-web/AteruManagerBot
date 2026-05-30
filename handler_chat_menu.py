from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_chat, is_chat_owner, remove_chat, get_events
from keyboards import (
    chat_menu_kb, messages_menu_kb, members_menu_kb, pin_menu_kb,
    settings_menu_kb, reactions_menu_kb, confirm_kb, back_kb
)

router = Router()


@router.callback_query(F.data.startswith("chat:"))
async def cb_chat_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    chat = await get_chat(chat_id)
    if not chat:
        await call.answer("❌ Чат не найден", show_alert=True)
        return
    title = chat.get("chat_title") or str(chat_id)
    icon = "📢" if chat.get("chat_type") == "channel" else "👥"
    await call.message.edit_text(
        f"{icon} <b>{title}</b>\n🆔 ID: <code>{chat_id}</code>\n\nВыберите раздел управления:",
        reply_markup=chat_menu_kb(chat_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("msg:"))
async def cb_messages_menu(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await call.message.edit_text(
        "✉️ <b>Управление сообщениями</b>\n\nВыберите действие:",
        reply_markup=messages_menu_kb(chat_id), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("members:"))
async def cb_members_menu(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await call.message.edit_text(
        "👥 <b>Управление участниками</b>\n\nВыберите действие:",
        reply_markup=members_menu_kb(chat_id), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("pin:"))
async def cb_pin_menu(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await call.message.edit_text(
        "📌 <b>Закрепление сообщений</b>\n\nВыберите действие:",
        reply_markup=pin_menu_kb(chat_id), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("react:"))
async def cb_react_menu(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await call.message.edit_text(
        "❤️ <b>Реакции</b>\n\nВыберите действие:",
        reply_markup=reactions_menu_kb(chat_id), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("settings:"))
async def cb_settings_menu(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await call.message.edit_text(
        "⚙️ <b>Настройки чата/канала</b>\n\nВыберите действие:",
        reply_markup=settings_menu_kb(chat_id), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("stats:"))
async def cb_stats(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        chat = await call.bot.get_chat(chat_id)
        members_count = await call.bot.get_chat_member_count(chat_id)
        title = chat.title or str(chat_id)
        username_str = f"@{chat.username}" if chat.username else "Нет"
        invite_link = chat.invite_link or "Нет"
        await call.message.edit_text(
            f"📊 <b>Статистика: {title}</b>\n\n"
            f"👥 Участников: <b>{members_count}</b>\n"
            f"📂 Тип: {chat.type}\n"
            f"🔗 Username: {username_str}\n"
            f"🔗 Ссылка: {invite_link}",
            reply_markup=back_kb(f"chat:{chat_id}"), parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(
            f"❌ Ошибка: <code>{e}</code>",
            reply_markup=back_kb(f"chat:{chat_id}"), parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("events:"))
async def cb_events(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    events = await get_events(chat_id, limit=15)
    if not events:
        await call.message.edit_text(
            "📜 <b>Журнал событий</b>\n\nПока нет записей.",
            reply_markup=back_kb(f"chat:{chat_id}"), parse_mode="HTML"
        )
        return
    type_icons = {
        "ban": "🚫", "unban": "✅", "mute": "🔇", "unmute": "🔊",
        "warn": "⚠️", "promote": "👑", "demote": "👤", "pin": "📌",
        "unpin": "📍", "delete_msg": "🗑", "send_msg": "✉️",
        "set_title": "✏️", "set_desc": "📝"
    }
    lines = ["📜 <b>Журнал событий (последние 15):</b>\n"]
    for e in events:
        icon = type_icons.get(e["event_type"], "📌")
        target = f"User {e['target_user_id']}" if e.get("target_user_id") else ""
        details = f": {e['details']}" if e.get("details") else ""
        lines.append(f"{icon} <b>{e['event_type']}</b> {target}{details}")
    await call.message.edit_text(
        "\n".join(lines), reply_markup=back_kb(f"chat:{chat_id}"), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("unlink_confirm:"))
async def cb_unlink_confirm(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    chat = await get_chat(chat_id)
    title = chat.get("chat_title") if chat else str(chat_id)
    await call.message.edit_text(
        f"⚠️ <b>Подтвердите отвязку</b>\n\nВы уверены, что хотите отвязать <b>{title}</b>?",
        reply_markup=confirm_kb(f"unlink_do:{chat_id}", f"chat:{chat_id}"), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("unlink_do:"))
async def cb_unlink_do(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await remove_chat(call.from_user.id, chat_id)
    await call.message.edit_text(
        "✅ Чат успешно отвязан.", reply_markup=back_kb("my_chats"), parse_mode="HTML"
    )

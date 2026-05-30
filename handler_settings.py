from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, ChatPermissions
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database import is_chat_owner, log_event
from keyboards import back_kb, slow_mode_kb
from states import SettingsStates

router = Router()


@router.callback_query(F.data.startswith("set_title:"))
async def cb_set_title(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(SettingsStates.waiting_title)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("✏️ Введите новое <b>название</b> чата/канала:",
                                  reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")


@router.message(SettingsStates.waiting_title)
async def process_set_title(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        await message.bot.set_chat_title(chat_id, message.text.strip())
        await log_event(chat_id, "set_title", performed_by=message.from_user.id, details=message.text.strip())
        await state.clear()
        await message.answer(f"✅ Название изменено: <b>{message.text.strip()}</b>",
                             reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("set_desc:"))
async def cb_set_desc(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(SettingsStates.waiting_description)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("📝 Введите новое <b>описание</b> (или «-» чтобы очистить):",
                                  reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")


@router.message(SettingsStates.waiting_description)
async def process_set_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    desc = "" if message.text.strip() == "-" else message.text.strip()
    try:
        await message.bot.set_chat_description(chat_id, desc)
        await log_event(chat_id, "set_desc", performed_by=message.from_user.id)
        await state.clear()
        await message.answer("✅ Описание обновлено!", reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("set_photo:"))
async def cb_set_photo(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(SettingsStates.waiting_photo)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🖼 Отправьте фото для нового аватара:",
                                  reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")


@router.message(SettingsStates.waiting_photo, F.photo)
async def process_set_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        from aiogram.types import BufferedInputFile
        file = await message.bot.get_file(message.photo[-1].file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        content = file_bytes.read() if hasattr(file_bytes, 'read') else bytes(file_bytes)
        await message.bot.set_chat_photo(chat_id, BufferedInputFile(content, filename="avatar.jpg"))
        await log_event(chat_id, "set_photo", performed_by=message.from_user.id)
        await state.clear()
        await message.answer("✅ Аватар обновлён!", reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("inv_link:"))
async def cb_inv_link(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        link = await call.bot.create_chat_invite_link(chat_id)
        await call.message.edit_text(
            f"🔗 <b>Новая ссылка-приглашение:</b>\n\n<code>{link.invite_link}</code>",
            reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка: <code>{e}</code>",
                                     reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")


@router.callback_query(F.data.startswith("slow_mode:"))
async def cb_slow_mode(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await call.message.edit_text("🐌 Выберите интервал медленного режима:",
                                  reply_markup=slow_mode_kb(chat_id), parse_mode="HTML")


@router.callback_query(F.data.startswith("slow_set:"))
async def cb_slow_set(call: CallbackQuery):
    parts = call.data.split(":")
    chat_id, seconds = int(parts[1]), int(parts[2])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        await call.bot.set_chat_slow_mode_delay(chat_id, seconds)
        label = "выключен" if seconds == 0 else f"{seconds} сек."
        await call.message.edit_text(f"✅ Медленный режим: <b>{label}</b>",
                                     reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка: <code>{e}</code>",
                                     reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")


@router.callback_query(F.data.startswith("restrict_chat:"))
async def cb_restrict_chat(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔒 Только админы", callback_data=f"rchat_lock:{chat_id}"),
        InlineKeyboardButton(text="🔓 Все могут писать", callback_data=f"rchat_open:{chat_id}")
    )
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"settings:{chat_id}"))
    await call.message.edit_text("🔒 Выберите режим чата:", reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("rchat_lock:"))
async def cb_rchat_lock(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    try:
        await call.bot.set_chat_permissions(chat_id, ChatPermissions(can_send_messages=False))
        await call.message.edit_text("🔒 Чат закрыт — писать могут только администраторы.",
                                     reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка: <code>{e}</code>",
                                     reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")


@router.callback_query(F.data.startswith("rchat_open:"))
async def cb_rchat_open(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    try:
        await call.bot.set_chat_permissions(chat_id, ChatPermissions(
            can_send_messages=True, can_send_other_messages=True,
            can_add_web_page_previews=True, can_send_polls=True
        ))
        await call.message.edit_text("🔓 Чат открыт — все участники могут писать.",
                                     reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка: <code>{e}</code>",
                                     reply_markup=back_kb(f"settings:{chat_id}"), parse_mode="HTML")

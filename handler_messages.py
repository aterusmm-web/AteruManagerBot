from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database import is_chat_owner, save_bot_message, get_bot_messages, delete_bot_message_record, log_event
from keyboards import back_kb, messages_menu_kb, confirm_kb
from states import SendMessageStates

router = Router()


async def _check(call: CallbackQuery, chat_id: int) -> bool:
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return False
    return True


@router.callback_query(F.data.startswith("send_text:"))
async def cb_send_text(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_text)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text(
        "📝 Введите текст сообщения (поддерживается HTML):\n\n"
        "<i>Пример: &lt;b&gt;жирный&lt;/b&gt;, &lt;i&gt;курсив&lt;/i&gt;, &lt;code&gt;код&lt;/code&gt;</i>",
        reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML"
    )


@router.message(SendMessageStates.waiting_text)
async def process_send_text(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        sent = await message.bot.send_message(chat_id, message.text, parse_mode="HTML")
        await save_bot_message(chat_id, sent.message_id)
        await log_event(chat_id, "send_msg", performed_by=message.from_user.id, details="text")
        await state.clear()
        await message.answer(f"✅ Сообщение отправлено! (ID: <code>{sent.message_id}</code>)",
                             reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("send_photo:"))
async def cb_send_photo(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_photo)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🖼 Отправьте фото (можно с подписью):",
                                  reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_photo, F.photo)
async def process_send_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        sent = await message.bot.send_photo(chat_id, message.photo[-1].file_id, caption=message.caption)
        await save_bot_message(chat_id, sent.message_id)
        await log_event(chat_id, "send_msg", performed_by=message.from_user.id, details="photo")
        await state.clear()
        await message.answer("✅ Фото отправлено!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("send_video:"))
async def cb_send_video(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_video)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🎥 Отправьте видео:", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_video, F.video)
async def process_send_video(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        sent = await message.bot.send_video(chat_id, message.video.file_id, caption=message.caption)
        await save_bot_message(chat_id, sent.message_id)
        await state.clear()
        await message.answer("✅ Видео отправлено!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("send_doc:"))
async def cb_send_doc(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_doc)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("📄 Отправьте документ:", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_doc, F.document)
async def process_send_doc(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        sent = await message.bot.send_document(chat_id, message.document.file_id, caption=message.caption)
        await save_bot_message(chat_id, sent.message_id)
        await state.clear()
        await message.answer("✅ Документ отправлен!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("send_audio:"))
async def cb_send_audio(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_audio)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🎵 Отправьте аудио или голосовое сообщение:",
                                  reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_audio, F.audio | F.voice)
async def process_send_audio(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        if message.voice:
            sent = await message.bot.send_voice(chat_id, message.voice.file_id)
        else:
            sent = await message.bot.send_audio(chat_id, message.audio.file_id, caption=message.caption)
        await save_bot_message(chat_id, sent.message_id)
        await state.clear()
        await message.answer("✅ Аудио отправлено!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("edit_msg:"))
async def cb_edit_msg(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_msg_id_edit)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("✏️ Введите <b>ID сообщения</b> для редактирования:",
                                  reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_msg_id_edit)
async def process_edit_msg_id(message: Message, state: FSMContext):
    try:
        msg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой ID")
        return
    await state.update_data(edit_msg_id=msg_id)
    await state.set_state(SendMessageStates.waiting_new_text)
    await message.answer("✏️ Введите <b>новый текст</b> сообщения:", parse_mode="HTML")


@router.message(SendMessageStates.waiting_new_text)
async def process_edit_new_text(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id, msg_id = data["chat_id"], data["edit_msg_id"]
    try:
        await message.bot.edit_message_text(message.text, chat_id=chat_id, message_id=msg_id, parse_mode="HTML")
        await log_event(chat_id, "edit_msg", performed_by=message.from_user.id, details=f"msg_id:{msg_id}")
        await state.clear()
        await message.answer("✅ Сообщение отредактировано!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("delete_msg:"))
async def cb_delete_msg(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_msg_id_delete)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🗑 Введите <b>ID сообщения</b> для удаления:",
                                  reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_msg_id_delete)
async def process_delete_msg_id(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        msg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой ID")
        return
    await state.clear()
    try:
        await message.bot.delete_message(chat_id, msg_id)
        await delete_bot_message_record(chat_id, msg_id)
        await log_event(chat_id, "delete_msg", performed_by=message.from_user.id, details=f"msg_id:{msg_id}")
        await message.answer("✅ Сообщение удалено!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.callback_query(F.data.startswith("reply_msg:"))
async def cb_reply_msg(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_reply_msg_id)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("↩️ Введите <b>ID сообщения</b> на которое нужно ответить:",
                                  reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_reply_msg_id)
async def process_reply_msg_id(message: Message, state: FSMContext):
    try:
        msg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой ID")
        return
    await state.update_data(reply_to_msg_id=msg_id)
    await state.set_state(SendMessageStates.waiting_reply_text)
    await message.answer("↩️ Введите <b>текст ответа</b>:", parse_mode="HTML")


@router.message(SendMessageStates.waiting_reply_text)
async def process_reply_text(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id, reply_to = data["chat_id"], data["reply_to_msg_id"]
    try:
        from aiogram.types import ReplyParameters
        sent = await message.bot.send_message(
            chat_id, message.text,
            reply_parameters=ReplyParameters(message_id=reply_to), parse_mode="HTML"
        )
        await save_bot_message(chat_id, sent.message_id)
        await state.clear()
        await message.answer("✅ Ответ отправлен!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("forward_msg:"))
async def cb_forward_msg(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(SendMessageStates.waiting_forward_from)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("↪️ Введите <b>ID исходного чата</b>:",
                                  reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(SendMessageStates.waiting_forward_from)
async def process_forward_from(message: Message, state: FSMContext):
    try:
        from_chat_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой ID")
        return
    await state.update_data(forward_from_chat=from_chat_id)
    await state.set_state(SendMessageStates.waiting_forward_msg_id)
    await message.answer("↪️ Введите <b>ID сообщения</b> для пересылки:", parse_mode="HTML")


@router.message(SendMessageStates.waiting_forward_msg_id)
async def process_forward_msg_id(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id, from_chat = data["chat_id"], data["forward_from_chat"]
    try:
        msg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой ID")
        return
    try:
        await message.bot.forward_message(chat_id, from_chat, msg_id)
        await state.clear()
        await message.answer("✅ Сообщение переслано!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("clear_mine:"))
async def cb_clear_mine(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await call.message.edit_text(
        "🗑 Будут удалены последние 50 сообщений бота в этом чате. Продолжить?",
        reply_markup=confirm_kb(f"clear_mine_do:{chat_id}", f"chat:{chat_id}"), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("clear_mine_do:"))
async def cb_clear_mine_do(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    msg_ids = await get_bot_messages(chat_id, limit=50)
    deleted = 0
    for mid in msg_ids:
        try:
            await call.bot.delete_message(chat_id, mid)
            await delete_bot_message_record(chat_id, mid)
            deleted += 1
        except Exception:
            pass
    await call.message.edit_text(
        f"✅ Удалено <b>{deleted}</b> сообщений бота.",
        reply_markup=back_kb(f"chat:{chat_id}"), parse_mode="HTML"
    )

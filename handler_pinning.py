from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database import is_chat_owner, log_event
from keyboards import back_kb
from states import PinStates

router = Router()


@router.callback_query(F.data.startswith("pin_msg:"))
async def cb_pin_msg(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(PinStates.waiting_msg_id_pin)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text(
        "📌 Введите <b>ID сообщения</b> для закрепления:\n\n"
        "<i>Узнать ID: перешлите сообщение боту @getidsbot</i>",
        reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML"
    )


@router.message(PinStates.waiting_msg_id_pin)
async def process_pin(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        msg_id = int(message.text.strip())
        await message.bot.pin_chat_message(chat_id, msg_id, disable_notification=False)
        await log_event(chat_id, "pin", performed_by=message.from_user.id, details=f"msg_id:{msg_id}")
        await state.clear()
        await message.answer(f"📌 Сообщение <code>{msg_id}</code> закреплено!",
                             reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("unpin_msg:"))
async def cb_unpin_msg(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(PinStates.waiting_msg_id_unpin)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text(
        "📍 Введите <b>ID сообщения</b> для открепления (или 0 — открепить последнее):",
        reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML"
    )


@router.message(PinStates.waiting_msg_id_unpin)
async def process_unpin(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        msg_id = int(message.text.strip())
        if msg_id == 0:
            await message.bot.unpin_chat_message(chat_id)
        else:
            await message.bot.unpin_chat_message(chat_id, message_id=msg_id)
        await log_event(chat_id, "unpin", performed_by=message.from_user.id, details=f"msg_id:{msg_id}")
        await state.clear()
        await message.answer("📍 Сообщение откреплено!", reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("list_pins:"))
async def cb_list_pins(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        chat = await call.bot.get_chat(chat_id)
        pinned = chat.pinned_message
        if pinned:
            preview = (pinned.text or pinned.caption or "[медиа]")[:100]
            await call.message.edit_text(
                f"📌 <b>Закреплённое сообщение:</b>\n\n🆔 ID: <code>{pinned.message_id}</code>\n📝 {preview}",
                reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML"
            )
        else:
            await call.message.edit_text("📋 Нет закреплённых сообщений.",
                                         reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка: <code>{e}</code>",
                                     reply_markup=back_kb(f"pin:{chat_id}"), parse_mode="HTML")

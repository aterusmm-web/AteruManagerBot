from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database import get_user_chats, is_chat_owner
from keyboards import broadcast_kb, back_kb, confirm_kb
from states import BroadcastStates

router = Router()


@router.callback_query(F.data == "broadcast")
async def cb_broadcast(call: CallbackQuery):
    chats = await get_user_chats(call.from_user.id)
    if not chats:
        await call.message.edit_text("📭 У вас нет привязанных чатов для рассылки.",
                                     reply_markup=back_kb("main_menu"), parse_mode="HTML")
        return
    await call.message.edit_text(
        "📢 <b>Рассылка</b>\n\nВыберите чат или разошлите во все сразу:",
        reply_markup=broadcast_kb(chats), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("bc_chat:"))
async def cb_bc_chat(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(BroadcastStates.waiting_message)
    await state.update_data(target_chat_ids=[chat_id])
    await call.message.edit_text("📤 Отправьте сообщение для рассылки:",
                                  reply_markup=back_kb("broadcast"), parse_mode="HTML")


@router.callback_query(F.data == "bc_all")
async def cb_bc_all(call: CallbackQuery, state: FSMContext):
    chats = await get_user_chats(call.from_user.id)
    chat_ids = [c["chat_id"] for c in chats]
    await state.set_state(BroadcastStates.waiting_message)
    await state.update_data(target_chat_ids=chat_ids)
    await call.message.edit_text(f"📤 <b>Рассылка во все чаты ({len(chat_ids)})</b>\n\nОтправьте сообщение:",
                                  reply_markup=back_kb("broadcast"), parse_mode="HTML")


@router.message(BroadcastStates.waiting_message)
async def process_bc_message(message: Message, state: FSMContext):
    data = await state.get_data()
    target_ids = data["target_chat_ids"]
    await state.update_data(bc_from_chat=message.chat.id, bc_msg_id=message.message_id)
    await state.set_state(BroadcastStates.confirm)
    await message.answer(
        f"📢 Сообщение будет отправлено в <b>{len(target_ids)}</b> чат(ов). Подтвердить?",
        reply_markup=confirm_kb("bc_confirm", "broadcast"), parse_mode="HTML"
    )


@router.callback_query(F.data == "bc_confirm")
async def cb_bc_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_ids = data["target_chat_ids"]
    from_chat, msg_id = data["bc_from_chat"], data["bc_msg_id"]
    await state.clear()
    success = failed = 0
    for chat_id in target_ids:
        try:
            await call.bot.forward_message(chat_id, from_chat, msg_id)
            success += 1
        except Exception:
            failed += 1
    await call.message.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\nУспешно: {success}\nОшибок: {failed}",
        reply_markup=back_kb("main_menu"), parse_mode="HTML"
    )

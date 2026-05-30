from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReactionTypeEmoji
from aiogram.fsm.context import FSMContext

from database import is_chat_owner
from keyboards import back_kb, reactions_emoji_kb
from states import ReactStates

router = Router()


@router.callback_query(F.data.startswith("add_react:"))
async def cb_add_react(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(ReactStates.waiting_msg_id)
    await state.update_data(chat_id=chat_id, mode="add")
    await call.message.edit_text("❤️ Введите <b>ID сообщения</b>:",
                                  reply_markup=back_kb(f"react:{chat_id}"), parse_mode="HTML")


@router.callback_query(F.data.startswith("del_react:"))
async def cb_del_react(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(ReactStates.waiting_msg_id)
    await state.update_data(chat_id=chat_id, mode="del")
    await call.message.edit_text("❌ Введите <b>ID сообщения</b> для удаления реакции:",
                                  reply_markup=back_kb(f"react:{chat_id}"), parse_mode="HTML")


@router.message(ReactStates.waiting_msg_id)
async def process_react_msg_id(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id, mode = data["chat_id"], data["mode"]
    try:
        msg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой ID")
        return
    if mode == "del":
        try:
            await message.bot.set_message_reaction(chat_id, msg_id, reaction=[])
            await state.clear()
            await message.answer("✅ Реакция убрана!", reply_markup=back_kb(f"react:{chat_id}"), parse_mode="HTML")
        except Exception as e:
            await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"react:{chat_id}"), parse_mode="HTML")
            await state.clear()
        return
    await state.clear()
    await message.answer("❤️ Выберите реакцию:", reply_markup=reactions_emoji_kb(chat_id, msg_id))


@router.callback_query(F.data.startswith("react_set:"))
async def cb_react_set(call: CallbackQuery):
    parts = call.data.split(":")
    chat_id, msg_id, emoji = int(parts[1]), int(parts[2]), parts[3]
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        await call.bot.set_message_reaction(chat_id, msg_id, reaction=[ReactionTypeEmoji(emoji=emoji)])
        await call.message.edit_text(
            f"✅ Реакция {emoji} поставлена на сообщение <code>{msg_id}</code>!",
            reply_markup=back_kb(f"react:{chat_id}"), parse_mode="HTML"
        )
    except Exception as e:
        await call.message.edit_text(
            f"❌ Ошибка: <code>{e}</code>\n<i>Реакции доступны в супергруппах с включёнными реакциями.</i>",
            reply_markup=back_kb(f"react:{chat_id}"), parse_mode="HTML"
        )

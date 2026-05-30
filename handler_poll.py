from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database import is_chat_owner, save_bot_message
from keyboards import back_kb, confirm_kb
from states import PollStates

router = Router()


@router.callback_query(F.data.startswith("send_poll:"))
async def cb_send_poll(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    await state.set_state(PollStates.waiting_question)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("📊 Шаг 1/2: Введите <b>вопрос</b> для опроса:",
                                  reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")


@router.message(PollStates.waiting_question)
async def process_poll_question(message: Message, state: FSMContext):
    await state.update_data(poll_question=message.text.strip())
    await state.set_state(PollStates.waiting_options)
    await message.answer(
        "📊 Шаг 2/2: Введите варианты ответов — каждый с новой строки (мин. 2, макс. 10):\n\n"
        "<i>Пример:\nДа\nНет\nНе знаю</i>",
        parse_mode="HTML"
    )


@router.message(PollStates.waiting_options)
async def process_poll_options(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    options = [o.strip() for o in message.text.strip().split("\n") if o.strip()]
    if len(options) < 2:
        await message.answer("❌ Нужно минимум 2 варианта:")
        return
    if len(options) > 10:
        await message.answer("❌ Максимум 10 вариантов:")
        return
    await state.update_data(poll_options=options)
    await state.set_state(PollStates.waiting_confirm)
    preview = "\n".join([f"  {i+1}. {o}" for i, o in enumerate(options)])
    await message.answer(
        f"📊 <b>Предпросмотр:</b>\n\n❓ <b>{data['poll_question']}</b>\n\n{preview}\n\nОтправить?",
        reply_markup=confirm_kb(f"poll_send:{chat_id}", f"msg:{chat_id}"), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("poll_send:"))
async def cb_poll_send(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    data = await state.get_data()
    question, options = data.get("poll_question"), data.get("poll_options", [])
    await state.clear()
    try:
        sent = await call.bot.send_poll(chat_id, question=question, options=options, is_anonymous=True)
        await save_bot_message(chat_id, sent.message_id)
        await call.message.edit_text("✅ Опрос опубликован!", reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка: <code>{e}</code>",
                                     reply_markup=back_kb(f"msg:{chat_id}"), parse_mode="HTML")

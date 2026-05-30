from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import get_user_chats, add_chat, is_chat_owner
from keyboards import main_menu_kb, chats_list_kb, add_chat_kb, back_kb
from states import AddChatStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привет, <b>{message.from_user.full_name}</b>!\n\n"
        "Я многофункциональный бот для управления вашими чатами и каналами.\n\n"
        "Всё управление происходит здесь — в личных сообщениях, через удобные кнопки. "
        "Добавьте меня администратором в ваш чат или канал и привяжите его ниже.",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "🏠 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "my_chats")
async def cb_my_chats(call: CallbackQuery):
    chats = await get_user_chats(call.from_user.id)
    if not chats:
        await call.message.edit_text(
            "📭 У вас пока нет привязанных чатов/каналов.\n\n"
            "Нажмите <b>«Добавить»</b>, чтобы привязать первый.",
            reply_markup=add_chat_kb(),
            parse_mode="HTML"
        )
    else:
        await call.message.edit_text(
            f"📋 <b>Ваши чаты и каналы</b> ({len(chats)}):\n\nВыберите для управления:",
            reply_markup=chats_list_kb(chats),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "add_chat")
async def cb_add_chat(call: CallbackQuery):
    await call.message.edit_text(
        "➕ <b>Добавить чат/канал</b>\n\nВыберите способ привязки:",
        reply_markup=add_chat_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "add_method1")
async def cb_add_method1(call: CallbackQuery):
    bot_info = await call.bot.get_me()
    username = bot_info.username
    text = (
        "📖 <b>Способ 1 — Ручное добавление</b>\n\n"
        "1. Откройте ваш чат или канал\n"
        "2. Перейдите в <b>Настройки → Администраторы → Добавить администратора</b>\n"
        f"3. Найдите и добавьте <b>@{username}</b>\n"
        "4. Выдайте права:\n"
        "   • Закрепление сообщений\n"
        "   • Удаление сообщений\n"
        "   • Блокировка участников\n"
        "   • Назначение администраторов (опционально)\n"
        "   • Изменение информации (опционально)\n"
        "   • Приглашение через ссылки\n\n"
        "5. После добавления используйте <b>Способ 2</b> для привязки по ID или напишите "
        "в чат команду <code>/link</code> — бот автоматически зарегистрирует чат."
    )
    await call.message.edit_text(text, reply_markup=back_kb("add_chat"), parse_mode="HTML")


@router.callback_query(F.data == "add_method2")
async def cb_add_method2(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddChatStates.waiting_for_id)
    text = (
        "🔢 <b>Способ 2 — По ID чата/канала</b>\n\n"
        "Чтобы узнать ID:\n"
        "• Добавьте @userinfobot в чат и напишите любое сообщение — он покажет ID\n"
        "• Или перешлите любое сообщение из нужного чата боту @getidsbot\n"
        "• Для каналов: ID обычно начинается с <code>-100</code>\n\n"
        "📩 <b>Отправьте ID чата/канала:</b>"
    )
    await call.message.edit_text(text, reply_markup=back_kb("add_chat"), parse_mode="HTML")


@router.message(AddChatStates.waiting_for_id)
async def process_chat_id(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        chat_id = int(text)
    except ValueError:
        await message.answer(
            "❌ Неверный формат. ID должен быть числом (например: <code>-1001234567890</code>)",
            parse_mode="HTML"
        )
        return

    try:
        chat = await message.bot.get_chat(chat_id)
    except Exception as e:
        await message.answer(
            f"❌ Не удалось получить информацию о чате.\n\n"
            f"Убедитесь, что:\n"
            f"• Бот добавлен в этот чат/канал как администратор\n"
            f"• ID верный\n\n"
            f"Ошибка: <code>{str(e)}</code>",
            reply_markup=back_kb("add_chat"),
            parse_mode="HTML"
        )
        return

    try:
        test_msg = await message.bot.send_message(chat_id, "✅ Чат успешно привязан к боту!")
        await test_msg.delete()
    except Exception as e:
        await message.answer(
            f"❌ Бот не может писать в этот чат.\n\n"
            f"Убедитесь, что бот добавлен как администратор с правом отправки сообщений.\n\n"
            f"Ошибка: <code>{str(e)}</code>",
            reply_markup=back_kb("add_chat"),
            parse_mode="HTML"
        )
        return

    chat_title = chat.title or chat.full_name or str(chat_id)
    chat_type = chat.type
    username = chat.username

    await add_chat(message.from_user.id, chat_id, chat_title, chat_type, username)
    await state.clear()

    await message.answer(
        f"✅ <b>Чат успешно привязан!</b>\n\n"
        f"📌 Название: <b>{chat_title}</b>\n"
        f"🆔 ID: <code>{chat_id}</code>\n"
        f"📂 Тип: {chat_type}\n\n"
        f"Теперь вы можете управлять им из главного меню.",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "help")
async def cb_help(call: CallbackQuery):
    text = (
        "ℹ️ <b>Как пользоваться ботом</b>\n\n"
        "<b>1. Добавьте бота в чат/канал</b> как администратора\n"
        "<b>2. Привяжите чат</b> через «Мои чаты → Добавить»\n"
        "<b>3. Управляйте</b> — выбирайте чат и нужное действие\n\n"
        "<b>Доступные функции:</b>\n"
        "• ✉️ Отправка всех типов сообщений\n"
        "• 🗑 Удаление и редактирование сообщений\n"
        "• 📌 Закрепление/открепление\n"
        "• ❤️ Реакции на сообщения\n"
        "• 🚫 Бан/мут участников\n"
        "• ⚠️ Система предупреждений\n"
        "• 👑 Управление администраторами\n"
        "• ⚙️ Настройки чата/канала\n"
        "• 📊 Статистика и журнал\n"
        "• 📢 Рассылка в несколько чатов\n\n"
        "<b>Команды в чате:</b>\n"
        "/pin — закрепить сообщение (ответом)\n"
        "/unpin — открепить сообщение\n"
        "/ban — забанить пользователя\n"
        "/mute — замутить пользователя\n"
        "/warn — предупреждение\n"
        "/id — узнать ID пользователя\n"
        "/link — привязать чат к боту"
    )
    await call.message.edit_text(text, reply_markup=back_kb("main_menu"), parse_mode="HTML")

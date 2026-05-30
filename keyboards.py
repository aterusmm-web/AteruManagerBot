from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📋 Мои чаты/каналы", callback_data="my_chats"))
    builder.row(InlineKeyboardButton(text="➕ Добавить чат/канал", callback_data="add_chat"))
    builder.row(InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast"))
    builder.row(InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"))
    return builder.as_markup()


def chats_list_kb(chats: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for chat in chats:
        title = chat.get("chat_title") or str(chat["chat_id"])
        builder.row(InlineKeyboardButton(
            text=f"{'📢' if chat['chat_type'] == 'channel' else '👥'} {title}",
            callback_data=f"chat:{chat['chat_id']}"
        ))
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data="add_chat"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return builder.as_markup()


def chat_menu_kb(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✉️ Сообщения", callback_data=f"msg:{chat_id}"),
        InlineKeyboardButton(text="👥 Участники", callback_data=f"members:{chat_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📌 Закрепление", callback_data=f"pin:{chat_id}"),
        InlineKeyboardButton(text="❤️ Реакции", callback_data=f"react:{chat_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки чата", callback_data=f"settings:{chat_id}"),
        InlineKeyboardButton(text="📊 Статистика", callback_data=f"stats:{chat_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Очистить мои сообщения", callback_data=f"clear_mine:{chat_id}"),
        InlineKeyboardButton(text="📜 Журнал событий", callback_data=f"events:{chat_id}")
    )
    builder.row(InlineKeyboardButton(text="❌ Отвязать чат", callback_data=f"unlink_confirm:{chat_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="my_chats"))
    return builder.as_markup()


def messages_menu_kb(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Отправить текст", callback_data=f"send_text:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🖼 Отправить фото", callback_data=f"send_photo:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🎥 Отправить видео", callback_data=f"send_video:{chat_id}"))
    builder.row(InlineKeyboardButton(text="📄 Отправить документ", callback_data=f"send_doc:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🎵 Отправить аудио/голос", callback_data=f"send_audio:{chat_id}"))
    builder.row(InlineKeyboardButton(text="📊 Создать опрос", callback_data=f"send_poll:{chat_id}"))
    builder.row(InlineKeyboardButton(text="✏️ Редактировать сообщение", callback_data=f"edit_msg:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🗑 Удалить сообщение", callback_data=f"delete_msg:{chat_id}"))
    builder.row(InlineKeyboardButton(text="↩️ Ответить на сообщение", callback_data=f"reply_msg:{chat_id}"))
    builder.row(InlineKeyboardButton(text="↪️ Переслать сообщение", callback_data=f"forward_msg:{chat_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"chat:{chat_id}"))
    return builder.as_markup()


def members_menu_kb(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚫 Забанить", callback_data=f"ban:{chat_id}"))
    builder.row(InlineKeyboardButton(text="✅ Разбанить", callback_data=f"unban:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🔇 Замутить", callback_data=f"mute:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🔊 Размутить", callback_data=f"unmute:{chat_id}"))
    builder.row(InlineKeyboardButton(text="⚠️ Выдать предупреждение", callback_data=f"warn:{chat_id}"))
    builder.row(InlineKeyboardButton(text="👑 Назначить администратора", callback_data=f"promote:{chat_id}"))
    builder.row(InlineKeyboardButton(text="👤 Снять администратора", callback_data=f"demote:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🔍 Узнать ID пользователя", callback_data=f"get_id:{chat_id}"))
    builder.row(InlineKeyboardButton(text="📋 Список участников", callback_data=f"list_members:{chat_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"chat:{chat_id}"))
    return builder.as_markup()


def pin_menu_kb(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📌 Закрепить сообщение", callback_data=f"pin_msg:{chat_id}"))
    builder.row(InlineKeyboardButton(text="📍 Открепить сообщение", callback_data=f"unpin_msg:{chat_id}"))
    builder.row(InlineKeyboardButton(text="📋 Список закреплённых", callback_data=f"list_pins:{chat_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"chat:{chat_id}"))
    return builder.as_markup()


def settings_menu_kb(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"set_title:{chat_id}"))
    builder.row(InlineKeyboardButton(text="📝 Изменить описание", callback_data=f"set_desc:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🖼 Изменить аватар", callback_data=f"set_photo:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🔗 Ссылка-приглашение", callback_data=f"inv_link:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🐌 Медленный режим", callback_data=f"slow_mode:{chat_id}"))
    builder.row(InlineKeyboardButton(text="🔒 Только администраторы пишут", callback_data=f"restrict_chat:{chat_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"chat:{chat_id}"))
    return builder.as_markup()


def reactions_menu_kb(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❤️ Поставить реакцию", callback_data=f"add_react:{chat_id}"))
    builder.row(InlineKeyboardButton(text="❌ Убрать реакцию", callback_data=f"del_react:{chat_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"chat:{chat_id}"))
    return builder.as_markup()


def add_chat_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📖 Способ 1: Инструкция", callback_data="add_method1"))
    builder.row(InlineKeyboardButton(text="🔢 Способ 2: По ID", callback_data="add_method2"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"))
    return builder.as_markup()


def confirm_kb(yes_data: str, no_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да, подтвердить", callback_data=yes_data),
        InlineKeyboardButton(text="❌ Отмена", callback_data=no_data)
    )
    return builder.as_markup()


def back_kb(callback_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data))
    return builder.as_markup()


def slow_mode_kb(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    options = [("Выкл", 0), ("10 сек", 10), ("30 сек", 30), ("1 мин", 60), ("5 мин", 300), ("15 мин", 900), ("1 час", 3600)]
    for label, val in options:
        builder.button(text=label, callback_data=f"slow_set:{chat_id}:{val}")
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"settings:{chat_id}"))
    return builder.as_markup()


def reactions_emoji_kb(chat_id: int, msg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    emojis = ["👍", "❤️", "🔥", "🎉", "😁", "😮", "😢", "👎", "💯", "🏆", "⚡", "🤩"]
    for e in emojis:
        builder.button(text=e, callback_data=f"react_set:{chat_id}:{msg_id}:{e}")
    builder.adjust(4)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"react:{chat_id}"))
    return builder.as_markup()


def broadcast_kb(chats: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for chat in chats:
        title = chat.get("chat_title") or str(chat["chat_id"])
        builder.row(InlineKeyboardButton(
            text=f"{'📢' if chat['chat_type'] == 'channel' else '👥'} {title}",
            callback_data=f"bc_chat:{chat['chat_id']}"
        ))
    builder.row(InlineKeyboardButton(text="📤 Разослать во все", callback_data="bc_all"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"))
    return builder.as_markup()

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ChatPermissions
from aiogram.fsm.context import FSMContext

from database import is_chat_owner, add_warning, log_event
from keyboards import back_kb
from states import ModerationStates

router = Router()


async def _check(call: CallbackQuery, chat_id: int) -> bool:
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return False
    return True


@router.callback_query(F.data.startswith("ban:"))
async def cb_ban(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_ban)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🚫 Введите <b>ID</b> или <b>@username</b> пользователя для бана:",
                                  reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.message(ModerationStates.waiting_user_id_ban)
async def process_ban(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    user_input = message.text.strip()
    try:
        user_id = int(user_input) if not user_input.startswith("@") else user_input
        await message.bot.ban_chat_member(chat_id, user_id)
        await log_event(chat_id, "ban", target_user_id=user_id if isinstance(user_id, int) else None,
                        performed_by=message.from_user.id, details=str(user_input))
        await state.clear()
        await message.answer(f"✅ Пользователь <code>{user_input}</code> забанен.",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("unban:"))
async def cb_unban(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_unban)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("✅ Введите <b>ID пользователя</b> для разбана:",
                                  reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.message(ModerationStates.waiting_user_id_unban)
async def process_unban(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        user_id = int(message.text.strip())
        await message.bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
        await log_event(chat_id, "unban", target_user_id=user_id, performed_by=message.from_user.id)
        await state.clear()
        await message.answer(f"✅ Пользователь <code>{user_id}</code> разбанен.",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("mute:"))
async def cb_mute(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_mute)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🔇 Введите <b>ID пользователя</b> для мута:",
                                  reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.message(ModerationStates.waiting_user_id_mute)
async def process_mute_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        await state.update_data(mute_user_id=user_id)
        await state.set_state(ModerationStates.waiting_mute_duration)
        await message.answer("⏱ На сколько минут замутить? (0 = навсегда):")
    except ValueError:
        await message.answer("❌ Введите числовой ID")


@router.message(ModerationStates.waiting_mute_duration)
async def process_mute_duration(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id, user_id = data["chat_id"], data["mute_user_id"]
    try:
        minutes = int(message.text.strip())
        until = datetime.now() + timedelta(minutes=minutes) if minutes > 0 else None
        perms = ChatPermissions(can_send_messages=False, can_send_other_messages=False,
                                can_add_web_page_previews=False)
        await message.bot.restrict_chat_member(chat_id, user_id, permissions=perms, until_date=until)
        duration_str = f"{minutes} мин." if minutes > 0 else "навсегда"
        await log_event(chat_id, "mute", target_user_id=user_id, performed_by=message.from_user.id, details=duration_str)
        await state.clear()
        await message.answer(f"✅ Пользователь <code>{user_id}</code> замучен на {duration_str}.",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("unmute:"))
async def cb_unmute(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_unmute)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("🔊 Введите <b>ID пользователя</b> для размута:",
                                  reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.message(ModerationStates.waiting_user_id_unmute)
async def process_unmute(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        user_id = int(message.text.strip())
        perms = ChatPermissions(can_send_messages=True, can_send_other_messages=True,
                                can_add_web_page_previews=True, can_send_polls=True)
        await message.bot.restrict_chat_member(chat_id, user_id, permissions=perms)
        await log_event(chat_id, "unmute", target_user_id=user_id, performed_by=message.from_user.id)
        await state.clear()
        await message.answer(f"✅ Мут снят с <code>{user_id}</code>.",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("warn:"))
async def cb_warn(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_warn)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("⚠️ Введите <b>ID пользователя</b> для предупреждения:",
                                  reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.message(ModerationStates.waiting_user_id_warn)
async def process_warn_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        await state.update_data(warn_user_id=user_id)
        await state.set_state(ModerationStates.waiting_warn_reason)
        await message.answer("📝 Введите <b>причину</b>:", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Введите числовой ID")


@router.message(ModerationStates.waiting_warn_reason)
async def process_warn_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id, user_id = data["chat_id"], data["warn_user_id"]
    reason = message.text.strip()
    total = await add_warning(chat_id, user_id, reason, message.from_user.id)
    await log_event(chat_id, "warn", target_user_id=user_id, performed_by=message.from_user.id, details=reason)
    await state.clear()
    await message.bot.send_message(
        chat_id,
        f"⚠️ Пользователю <code>{user_id}</code> выдано предупреждение!\n"
        f"Причина: {reason}\nВсего: {total}/3",
        parse_mode="HTML"
    )
    if total >= 3:
        try:
            await message.bot.ban_chat_member(chat_id, user_id)
            await message.bot.send_message(chat_id, f"🚫 Пользователь <code>{user_id}</code> забанен за 3 предупреждения.", parse_mode="HTML")
        except Exception:
            pass
    await message.answer(f"✅ Предупреждение выдано. Всего: {total}",
                         reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.callback_query(F.data.startswith("promote:"))
async def cb_promote(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_promote)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("👑 Введите <b>ID пользователя</b> для назначения администратором:",
                                  reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.message(ModerationStates.waiting_user_id_promote)
async def process_promote(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        user_id = int(message.text.strip())
        await message.bot.promote_chat_member(
            chat_id, user_id,
            can_pin_messages=True, can_delete_messages=True,
            can_restrict_members=True, can_change_info=True, can_invite_users=True
        )
        await log_event(chat_id, "promote", target_user_id=user_id, performed_by=message.from_user.id)
        await state.clear()
        await message.answer(f"✅ Пользователь <code>{user_id}</code> назначен администратором.",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("demote:"))
async def cb_demote(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_demote)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("👤 Введите <b>ID пользователя</b> для снятия прав:",
                                  reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.message(ModerationStates.waiting_user_id_demote)
async def process_demote(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    try:
        user_id = int(message.text.strip())
        await message.bot.promote_chat_member(
            chat_id, user_id,
            can_pin_messages=False, can_delete_messages=False,
            can_restrict_members=False, can_change_info=False,
            can_invite_users=False, can_promote_members=False
        )
        await log_event(chat_id, "demote", target_user_id=user_id, performed_by=message.from_user.id)
        await state.clear()
        await message.answer(f"✅ Права администратора сняты с <code>{user_id}</code>.",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>", reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
        await state.clear()


@router.callback_query(F.data.startswith("get_id:"))
async def cb_get_id(call: CallbackQuery, state: FSMContext):
    chat_id = int(call.data.split(":")[1])
    if not await _check(call, chat_id): return
    await state.set_state(ModerationStates.waiting_user_id_info)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text(
        "🔍 Введите <b>@username</b> или перешлите сообщение от нужного пользователя:",
        reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML"
    )


@router.message(ModerationStates.waiting_user_id_info)
async def process_get_id(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data["chat_id"]
    await state.clear()
    if message.forward_from:
        u = message.forward_from
        uname = f"\n🔗 @{u.username}" if u.username else ""
        await message.answer(f"👤 <b>Пользователь:</b>\n🆔 <code>{u.id}</code>\n📛 {u.full_name}{uname}",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
        return
    username = message.text.strip().lstrip("@")
    try:
        user = await message.bot.get_chat(f"@{username}")
        await message.answer(
            f"👤 <b>Информация:</b>\n🆔 <code>{user.id}</code>\n📛 {user.full_name or user.title}",
            reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Не найден: <code>{e}</code>",
                             reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")


@router.callback_query(F.data.startswith("list_members:"))
async def cb_list_members(call: CallbackQuery):
    chat_id = int(call.data.split(":")[1])
    if not await is_chat_owner(call.from_user.id, chat_id):
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        admins = await call.bot.get_chat_administrators(chat_id)
        lines = ["👑 <b>Администраторы чата:</b>\n"]
        for a in admins:
            u = a.user
            status = "👑 Создатель" if a.status == "creator" else "⭐ Админ"
            uname = f" (@{u.username})" if u.username else ""
            lines.append(f"{status}: {u.full_name}{uname} — <code>{u.id}</code>")
        await call.message.edit_text("\n".join(lines),
                                     reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка: <code>{e}</code>",
                                     reply_markup=back_kb(f"members:{chat_id}"), parse_mode="HTML")

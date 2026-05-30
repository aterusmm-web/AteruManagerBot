from aiogram.fsm.state import State, StatesGroup


class AddChatStates(StatesGroup):
    waiting_for_id = State()


class SendMessageStates(StatesGroup):
    choosing_chat = State()
    waiting_text = State()
    waiting_photo = State()
    waiting_video = State()
    waiting_doc = State()
    waiting_audio = State()
    waiting_msg_id_edit = State()
    waiting_new_text = State()
    waiting_msg_id_delete = State()
    waiting_reply_msg_id = State()
    waiting_reply_text = State()
    waiting_forward_from = State()
    waiting_forward_msg_id = State()


class PollStates(StatesGroup):
    waiting_question = State()
    waiting_options = State()
    waiting_confirm = State()


class ModerationStates(StatesGroup):
    waiting_user_id_ban = State()
    waiting_user_id_unban = State()
    waiting_user_id_mute = State()
    waiting_mute_duration = State()
    waiting_user_id_unmute = State()
    waiting_user_id_warn = State()
    waiting_warn_reason = State()
    waiting_user_id_promote = State()
    waiting_user_id_demote = State()
    waiting_user_id_info = State()


class PinStates(StatesGroup):
    waiting_msg_id_pin = State()
    waiting_msg_id_unpin = State()


class ReactStates(StatesGroup):
    waiting_msg_id = State()


class SettingsStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_photo = State()


class BroadcastStates(StatesGroup):
    waiting_message = State()
    confirm = State()

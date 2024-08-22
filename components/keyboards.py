from aiogram.types import (
    ParseMode,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


def go_to_menu_keyboard():
    ReplyKeyboardRemove()
    next_button = InlineKeyboardButton("Перейти к меню", callback_data="next")
    keyboard = InlineKeyboardMarkup().add(next_button)
    return keyboard


def contact_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    contact_button = KeyboardButton("📞 Отправить контакт", request_contact=True)
    keyboard.add(contact_button)
    return keyboard


def create_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    add_token_button = InlineKeyboardButton(
        "🔑 Добавить API ключ", callback_data="add_api"
    )
    add_howto_button = InlineKeyboardButton(
        "❓ Где взять API ключ?", callback_data="howto"
    )
    add_options_button = InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
    keyboard.add(add_token_button, add_howto_button, add_options_button)
    return keyboard


def next_keyboard():
    keyboard = InlineKeyboardMarkup()
    next_button = InlineKeyboardButton("▶️ Далее", callback_data="next_button")
    keyboard.add(next_button)
    return keyboard


def prev_keyboard():
    keyboard = InlineKeyboardMarkup()
    prev_button = InlineKeyboardButton("◀️ Назад", callback_data="prev_button")
    keyboard.add(prev_button)
    return keyboard


def review_answer_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    skip_button = InlineKeyboardButton("Пропустить", callback_data="skip")
    reply_button = InlineKeyboardButton("Ответить", callback_data="reply")
    keyboard.add(skip_button, reply_button)
    return keyboard

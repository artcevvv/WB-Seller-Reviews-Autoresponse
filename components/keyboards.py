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
    next_button = InlineKeyboardButton("▶️ Перейти к меню", callback_data="next")
    keyboard = InlineKeyboardMarkup().add(next_button)
    return keyboard

def contact_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    contact_button = KeyboardButton("📞 Отправить контакт", request_contact=True)
    keyboard.add(contact_button)
    return keyboard

def create_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    add_gotoanswering_button = InlineKeyboardButton(
        "▶️ Приступить к ответам", callback_data="answer"
    )
    add_token_button = InlineKeyboardButton(
        "🔑 Добавить API ключ", callback_data="add_api"
    )
    add_options_button = InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
    add_buy_button = InlineKeyboardButton("💰 Купить токены", callback_data="buy")
    add_info_button = InlineKeyboardButton("ℹ Информация", callback_data="info")
    keyboard.add(
        add_gotoanswering_button,
        add_token_button,
        add_options_button,
        add_buy_button,
        add_info_button,
    )
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
    skip_button = InlineKeyboardButton("⏩️ Пропустить", callback_data="skip")
    reply_button = InlineKeyboardButton("💬 Ответить", callback_data="reply")
    keyboard.add(reply_button, skip_button)
    return keyboard

def tokens_kb_layout():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buy_button = InlineKeyboardButton("🏪 Купить токены", callback_data="buy")
    keyboard.add(buy_button)
    return keyboard

def go_to_menu_main():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button = KeyboardButton("/menu")
    keyboard.add(menu_button)
    return keyboard

def info_kb_layout():
    keyboard = InlineKeyboardMarkup(row_width=1)
    howto_button = InlineKeyboardButton("❓ Где взять API ключ?", callback_data="howto")
    what_is_tokens_button = InlineKeyboardButton(
        "❓ Что такое токены?", callback_data="what_is"
    )
    how_to_use_button = InlineKeyboardButton(
        "❓ Как пользоваться ботом?", callback_data="howto_bot"
    )
    prev_button = InlineKeyboardButton("◀️ Назад", callback_data="prev_button")
    keyboard.add(howto_button, what_is_tokens_button, how_to_use_button, prev_button)
    return keyboard

def settings_kb():
    keyboard = InlineKeyboardMarkup(row_width=2);
    delete_token_button  = InlineKeyboardButton("🗑 Удалить API-токен", callback_data="delete_token")
    delete_user_button = InlineKeyboardButton("🗑 Удалить аккаунт", callback_data="delete_account")
    prev_button = InlineKeyboardButton("◀️ Назад", callback_data="prev_button")
    
    keyboard.add(delete_token_button, delete_user_button, prev_button)
    return keyboard
          
def yesno_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    yes_btn = InlineKeyboardButton("✅ Да", callback_data="confirm_btn")
    no_btn = InlineKeyboardButton("❌ Нет", callback_data="prev_button")
    
    kb.add(no_btn, yes_btn)
    return kb
from aiogram import types

from components.config import *
from components.keyboards import *

@dp.callback_query_handler(lambda c: c.data == "info")
async def info_button_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    
    keyboard = info_kb_layout()
    
    await bot.edit_message_text(
        text="Что вы хотите узнать?",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard
    )
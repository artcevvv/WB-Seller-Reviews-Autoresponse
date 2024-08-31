from aiogram import types

from components.keyboards import *
from components.config import *
from components.database import *


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message):
    contact = message.contact
    user_id = message.chat.id
    # original_message_id = message.message_id
    keyboard = go_to_menu_keyboard()

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()
        if user and user.phone_number:
            await message.reply(
                "❌ Вы уже добавили свой номер телефона!", reply_markup=keyboard
            )
        else:
            user.phone_number = contact.phone_number
            session.commit()
            await message.reply(
                "✅ Спасибо! Ваш номер телефона сохранен.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer("⬇️ Выберите действие:", reply_markup=keyboard)
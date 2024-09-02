from aiogram import types
from aiogram.dispatcher import FSMContext


import logging

from components.database import *
from components.keyboards import *
from components.fetch import fetch_reviews
from components.config import *

from components.bot_components.options import *
from components.bot_handlers.buy_tokens_handler import *
from components.bot_handlers.contact_handler import *
from components.bot_handlers.API_tokens_handler import *
from components.bot_handlers.main_menu_handlers import *
from components.bot_handlers.info_handlers import *
from components.bot_handlers.respond_handlers import *

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.chat.id
    active_users.add(user_id)

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()

        if user:
            await message.reply(
                "Для вызова главного меню введите или выберите команду '/menu'",
                reply_markup = go_to_menu_main()
            )
        else:
            contact_layout = contact_keyboard()
            user = User(telegram_user_id=user_id, points=10)
            session.add(user)
            session.commit()
            await message.reply(
                "Привет!👋 Я помогу тебе упростить ответы на отзывы Wildberries.\n"
                "Пожалуйста, отправь мне свой контакт, чтобы я мог тебя зарегистрировать.\n"
                f"У тебя {user.points}",
                reply_markup=contact_layout,
            )

@dp.message_handler(commands=["menu"])
async def menu_command(message: types.Message):
    user_id = message.chat.id #Same thing as chat id tbf
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()
        
        if user:
            menu_layout = create_menu_keyboard()
            await message.reply(
                f"🎟 У вас осталось {user.points} токенов\n"
                "⬇️ Выберите действие\n",
                reply_markup=menu_layout,
            )
        else:
            await message.reply(
                "Вы не зарегистрированы! Введите команду '/start' для регистрации в сервисе!"
            )


@dp.callback_query_handler(lambda c: c.data == "next")
async def next_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    keyboard = create_menu_keyboard()

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        text="⬇️ Выберите действие",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )

@dp.callback_query_handler(lambda c: c.data == "prev_button")
async def prev_button_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = create_menu_keyboard()
    await bot.edit_message_text(
        text="⬇️ Выберите действие",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Сообщение {update} вызвало ошибку {exception}")
    return True

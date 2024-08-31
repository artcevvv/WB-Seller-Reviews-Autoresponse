from aiogram import types
from aiogram.dispatcher import FSMContext


import logging

from components.database import *
from components.keyboards import *
from components.fetch import fetch_reviews
from components.config import *
from components.messages import *

from components.bot_components.options import *
from components.bot_handlers.buy_tokens_handler import *
from components.bot_handlers.contact_handler import *
from components.bot_handlers.API_tokens_handler import *


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.chat.id
    active_users.add(user_id)

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()

        if user:
            menu_layout = create_menu_keyboard()
            await message.reply(
                "⬇️ Выберите действие" f"У тебя {user.points}\n",
                reply_markup=menu_layout,
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


@dp.callback_query_handler(lambda c: c.data == "answer")
async def answer_command(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    kb_layout = review_answer_keyboard()
    try:
        logging.info(f"Handling callback query for user: {user_id}")
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_user_id == user_id).first()

            if user.points <= 0:
                await bot.send_message(
                    user_id,
                    "❌ У вас недостаточно токенов для ответа. Пожалуйста, пополните баланс.",
                )
                return
            await fetch_reviews(user_id, kb_layout)
    except Exception as e:
        logging.info({e})


@dp.callback_query_handler(lambda c: c.data == "reply")
async def reply_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)
    review_id = message_to_review_map.get(
        original_message_id, "Review ID is not stored!"
    )
    await bot.send_message(callback_query.from_user.id, f"{review_id}")


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


@dp.callback_query_handler(lambda c: c.data == "howto")
async def howto_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = prev_keyboard()
    text = "📃 Для авторизации в сервисе требуется токен Wildberries, который действует 180 дней после его создания.\n\n Для создания токена:\n1. В личном кабинете нажмите на имя профиля и выберите <a href='https://seller.wildberries.ru/supplier-settings/access-to-api'>Настройки → Доступ к API.</a>\n2. Выберите категорию 'Вопросы и отзывы'\n3. Нажмите <b>Создать токен</b>\n4. Скопируйте и отправьте токен боту, выбрав в меню опцию 'Добавить API ключ'."
    await bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


@dp.callback_query_handler(lambda c: c.data == "settings")
async def setting_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = prev_keyboard()
    # text= ""
    await bot.edit_message_text(
        text="❌ Функция еще не готова!",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Сообщение {update} вызвало ошибку {exception}")
    return True

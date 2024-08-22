from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
import os
import logging

from components.database import *
from components.keyboards import *

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
active_users = set()
sent_reviews_ids = set()
message_to_review_map = {}

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.chat.id
    active_users.add(user_id)
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()

        if user:
            menu_layout = create_menu_keyboard()
            await message.reply(
                "Выбери действие", reply_markup=menu_layout
            )  # Добавить меню
        else:
            contact_layout = contact_keyboard()
            user = User(telegram_user_id=user_id)
            session.add(user)
            session.commit()
            await message.reply(
                "Привет!👋 Я помогу тебе упростить ответы на отзывы Wildberries.\n"
                "Пожалуйста, отправь мне свой контакт, чтобы я мог тебя зарегистрировать.",
                reply_markup=contact_layout,
            )

    # TODO Добавить возможность подключения к нескольким аккаунтам по API-ключу/ам, отправленному пользователем

    # await fetch_reviews(user_id, kb_layout)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message):
    contact = message.contact
    user_id = message.chat.id
    keyboard = go_to_menu_keyboard()
    
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()
        if user and user.phone_number:
            await message.reply("❌ Вы уже добавили свой номер телефона!", reply_markup=keyboard)
        else:
            user.phone_number = contact.phone_number
            session.commit()
            await message.reply(
                "✅ Спасибо! Ваш номер телефона сохранен.",
                reply_markup=ReplyKeyboardRemove(),
            )


@dp.callback_query_handler(lambda c: c.data == "next")
async def next_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    keyboard = create_menu_keyboard()

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        text="Выберите действие",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "reply")
async def reply_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)
    review_id = message_to_review_map.get(
        original_message_id, "Review ID is not stored!"
    )
    await bot.send_message(callback_query.from_user.id, f"{review_id}")


@dp.callback_query_handler(lambda c: c.data == "add_api")
async def add_api_handler(callback_query: types.CallbackQuery):
    keyboard = prev_keyboard()
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    await bot.edit_message_text(
        text="Функция еще не готова!",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "prev_button")
async def prev_button_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = create_menu_keyboard()
    # text= ""
    await bot.edit_message_text(
        text="Выбери действие",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "howto")
async def howto_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = prev_keyboard()
    # text= ""
    await bot.edit_message_text(
        text="Функция еще не готова!",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "settings")
async def setting_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = prev_keyboard()
    # text= ""
    await bot.edit_message_text(
        text="Функция еще не готова!",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Update {update} caused error {exception}")
    return True
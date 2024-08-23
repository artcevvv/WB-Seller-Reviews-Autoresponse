from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging

from components.database import *
from components.keyboards import *
from components.fetch import fetch_reviews
from components.config import *





class APIKeyForm(StatesGroup):
    waiting_for_api_key = State()


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.chat.id
    active_users.add(user_id)

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()

        if user:
            menu_layout = create_menu_keyboard()
            await message.reply("⬇️ Выберите действие", reply_markup=menu_layout)
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


@dp.callback_query_handler(lambda c: c.data == "add_api")
async def add_api_handler(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_user_id = callback_query.message.chat.id
    contact = callback_query.message.contact
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = contact_keyboard()
    
    # print(contact)

    with SessionLocal() as session:
        user = (
            session.query(User)
            .filter(
                User.telegram_user_id == telegram_user_id
            )
            .first()
        )

        if not user.phone_number:
            await callback_query.message.reply(
                "❌ Вы не зарегистрированы! Отправьте мне свой контакт, что бы зарегестрироваться.",
                reply_markup=keyboard,
            )
            # await state.finish()
            return

        else:
            await bot.edit_message_text(
                text="Введите свой API-ключ продавца",
                chat_id=chat_id,
                message_id=original_message_id,
                reply_markup=None,
            )

    await state.set_state(APIKeyForm.waiting_for_api_key.state) # Не робит


@dp.message_handler(state=APIKeyForm.waiting_for_api_key)
async def store_key(message: types.Message, state: FSMContext):
    telegram_user_id = message.chat.id
    api_key = message.text
    
    if len(api_key) < 300:
        await message.answer("❌ API ключ должен содержать не менее 300 символов. Пожалуйста, отправьте корректный API ключ.")
        return

    # keyboard = contact_keyboard()

    with SessionLocal() as session:
        user = (
            session.query(User)
            .filter(User.telegram_user_id == telegram_user_id)
            .first()
        )
        token = Token(user_id=user.id, wb_token=api_key)
        token.wb_token = api_key
        session.add(token)
        session.commit()

        await message.reply("✅ API ключ успешно сохранен!")
        await message.delete()

    await state.finish()


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
        text="Функция еще не готова!",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message):
    contact = message.contact
    user_id = message.chat.id
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
            await bot.edit_message_text(
                "⬇️ Выберите действие:"
            )

@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Update {update} caused error {exception}")
    return True



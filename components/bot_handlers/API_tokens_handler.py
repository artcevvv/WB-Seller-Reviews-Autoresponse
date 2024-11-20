from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from components.config import *
from components.keyboards import *
from components.database import *


class APIKeyForm(StatesGroup):
    waiting_for_api_key = State()

@dp.callback_query_handler(lambda c: c.data == "add_api")
async def add_api_handler(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    
    keyboard = contact_keyboard()

    with SessionLocal() as session:
        user = (
            session.query(User)
            .filter(User.telegram_user_id == chat_id)
            .first()
        )

        if not user or not user.phone_number:
            await callback_query.message.reply(
                "❌ Вы не зарегистрированы! Отправьте мне свой контакт, чтобы зарегистрироваться.",
                reply_markup=keyboard,
            )
            return
        else:
            await bot.edit_message_text(
                text="✒️ Введите свой API-ключ продавца.\nДля отмены введите команду '/cancel'",
                chat_id=chat_id,
                message_id=original_message_id,
                reply_markup=None,
            )

    # Set the state to waiting for API key
    await state.set_state(APIKeyForm.waiting_for_api_key.state)
    logger.info(
        f"State set to APIKeyForm.waiting_for_api_key for user {chat_id}"
    )


@dp.message_handler(commands="cancel", state="*")
async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.reply("❓ Нечего отменять.")

    await state.finish()
    await message.reply("✅ Операция успешно отменена.")


@dp.message_handler(state=APIKeyForm.waiting_for_api_key)
async def store_key(message: types.Message, state: FSMContext):
    telegram_user_id = message.chat.id
    api_key = message.text

    with SessionLocal() as session:
        if len(api_key) < 300:
            await message.answer(
                "❌ API ключ должен содержать не менее 300 символов. Пожалуйста, отправьте корректный API ключ."
            )
            return
        user = (
            session.query(User)
            .filter(User.telegram_user_id == telegram_user_id)
            .first()
        )
        token = Token(user_id=user.id, wb_token=api_key, telegram_user_id = telegram_user_id)
        session.add(token)
        session.commit()

        await message.reply("✅ API ключ успешно сохранен!")
        await message.delete()

    await state.finish()
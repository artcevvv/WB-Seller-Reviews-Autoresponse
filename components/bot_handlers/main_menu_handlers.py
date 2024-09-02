from aiogram import types

from components.config import *
from components.database import *
from components.bot import *
from components.keyboards import *
from components.fetch import *


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
        logging.info(f"Error handling answer command: {e}")


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

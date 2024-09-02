from aiogram import *

from components.config import *
from components.database import *
from components.bot_handlers.response_functions.reply import *
from components.fetch import *


@dp.callback_query_handler(lambda c: c.data == "reply")
async def reply_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)

    # Get the review and response data from the stored dictionary
    review_data = message_to_review_and_response_map.get(original_message_id)
    if not review_data:
        await bot.send_message(
            callback_query.from_user.id, "Review data is not stored!"
        )
        return

    review_id = review_data["review_id"]
    chatgpt_response = review_data["chatgpt_response"]
    token = review_data["token"]

    # Send the reply through Wildberries API
    success = await send_reply_to_review(review_id, chatgpt_response, token)

    if success:
        await bot.send_message(
            callback_query.from_user.id, "✅ Ответ на отзыв успешно отправлен!"
        )
    else:
        await bot.send_message(
            callback_query.from_user.id, "❌ Не удалось отправить ответ на отзыв."
        )


@dp.callback_query_handler(lambda c: c.data == "skip")
async def skip_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)

    # Получаем ID отзыва, связанный с сообщением
    review_id = message_to_review_map.get(original_message_id)

    # Проверяем, есть ли связанный отзыв
    if not review_id:
        await bot.send_message(
            callback_query.from_user.id, "❌ Review ID is not stored for this message!"
        )
        return

    # Получаем ID пользователя Telegram
    user_id = callback_query.from_user.id

    # Добавляем пропущенный отзыв в список пропущенных для этого пользователя
    if user_id not in processed_reviews:
        processed_reviews[user_id] = set()

    processed_reviews[user_id].add(review_id)

    # Удаляем сообщение о пропущенном отзыве из словаря сообщений к отзывам
    message_to_review_map.pop(original_message_id, None)

    await bot.send_message(user_id, "🟢 Отзыв пропущен и больше не будет показан.")

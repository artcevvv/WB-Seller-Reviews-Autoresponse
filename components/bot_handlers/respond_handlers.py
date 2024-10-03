from aiogram import *

from components.config import *
from components.database import *
from components.bot_handlers.response_functions.reply import *
from components.fetch import *


@dp.callback_query_handler(lambda c: c.data == "reply")
async def reply_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)

    with SessionLocal() as session:
        # Get the review data from the ReviewResponse table using message_id
        review_response = session.query(ReviewResponse).filter_by(message_id=original_message_id).first()

        if not review_response:
            await bot.send_message(callback_query.from_user.id, "Review data is not stored!")
            return

        # Retrieve the user from the review response and their tokens
        user = session.query(User).filter_by(id=review_response.user_id).first()

        if not user or not user.tokens:
            await bot.send_message(callback_query.from_user.id, "User tokens not found!")
            return

        # Extract the token that was originally used for this review
        token = user.tokens[0].wb_token  # Assuming you use the first token, adjust if necessary

        # Get review and response data
        review_id = review_response.review_id
        chatgpt_response = review_response.chatgpt_response

        # Send the reply through Wildberries API using the fetched token
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

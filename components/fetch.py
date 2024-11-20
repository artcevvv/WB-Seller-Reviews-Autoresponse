import logging
import requests
import os
from dotenv import load_dotenv
from aiogram.types import ParseMode
import asyncio

from components.chatGPTresp import *
from components.database import *
from components.config import *
from components.keyboards import *

load_dotenv()

WILDBERRIES_API_ENDPOINT = os.getenv("WILDBERRIES_API_ENDPOINT")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store message IDs and their corresponding review and response data
message_to_review_and_response_map = {}

async def fetch_reviews(user_id, kb_layout):
    processed_reviews_set = set()  # Множество для хранения обработанных отзывов
    while True:  # Бесконечный цикл
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.telegram_user_id == user_id).first()
                menu_layout = go_to_menu_keyboard()

                if not user or not user.tokens:
                    logging.info(f"No user or tokens found for user ID: {user_id}")
                    await bot.send_message(
                        user_id,
                        "❌ Необходимо добавить хотя бы один API токен!",
                        parse_mode=ParseMode.HTML
                    )
                    return

                # Retrieve processed review IDs from the user model
                processed_reviews_set.update(user.review_ids or [])

                if user.tokens:
                    for token in user.tokens:
                        headers = {
                            "Authorization": token.wb_token,
                            "Content-Type": "application/json",
                        }

                        params = {
                            "isAnswered": "false",
                            "take": 10,
                            "skip": 0,
                        }

                        try:
                            response = requests.get(
                                WILDBERRIES_API_ENDPOINT, headers=headers, params=params
                            )

                            if response.status_code == 200:
                                data = response.json()
                                feedbacks = data.get("data", {}).get("feedbacks", [])

                                if not feedbacks:
                                    await asyncio.sleep(10)  # Ждем 10 секунд перед следующим запросом
                                    continue

                                # Обработка отзывов
                                for feedback in feedbacks:
                                    review_id = feedback.get("id")

                                    # Пропускаем уже обработанные отзывы
                                    if review_id in processed_reviews_set:
                                        continue

                                    # Извлечение данных отзыва
                                    review_rating = feedback.get("productValuation", "Рейтинг не указан")
                                    review_username = feedback.get("userName", "Имя не указано")
                                    review_text = feedback.get("text", "Нет отзыва")
                                    product_details = feedback.get("productDetails", {})
                                    
                                    review_item = product_details.get("productName") or "Unknown item"
                                    review_supplier = product_details.get("supplierName", "Unknown supplier")

                                    chatgpt_response = await get_chatgpt_response(
                                        review_supplier, review_item, review_rating, review_text
                                    )

                                    if user.points <= 0:
                                        await bot.send_message(
                                            user_id,
                                            "❌ У вас недостаточно токенов для ответа. Пожалуйста, пополните баланс."
                                        )
                                        return

                                    # Отправка сообщения и сохранение его ID
                                    sent_message = await bot.send_message(
                                        user_id,
                                        f"<b>Новый отзыв:</b>\n\nМагазин: <b>{review_supplier}</b>\nИмя: {review_username}\nТовар: {review_item}\nОценка: {review_rating}\nТекст отзыва: {review_text}\nОтвет от ИИ: {chatgpt_response}\n<b>Осталось токенов: {user.points}</b>",
                                        parse_mode=ParseMode.HTML,
                                        reply_markup=kb_layout,
                                    )

                                    # Сохранение ответа в базе данных
                                    review_response = ReviewResponse(
                                        user_id=user.id,
                                        review_id=review_id,
                                        chatgpt_response=chatgpt_response,
                                        message_id=sent_message.message_id,
                                        product_name=review_item
                                    )
                                    session.add(review_response)
                                    session.commit()

                                    user.points -= 1
                                    session.commit()

                                    processed_reviews_set.add(review_id)
                                    user.review_ids = list(processed_reviews_set)
                                    session.commit()

                            else:
                                logging.error(f"Failed to fetch reviews: {response.status_code}")
                        except requests.RequestException as e:
                            logging.error(f"Error fetching reviews: {e}")

            await asyncio.sleep(10)  # Ждем 10 секунд перед следующим циклом
        except Exception as e:
            logging.error(f"Error in review fetching loop: {e}")
            await asyncio.sleep(10)  # Ждем 10 секунд перед повторной попыткой



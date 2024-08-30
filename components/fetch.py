import logging
import requests
import os
from dotenv import load_dotenv
from aiogram.types import ParseMode

from components.chatGPTresp import *
from components.database import *
from components.config import *
from components.keyboards import *

load_dotenv()

WILDBERRIES_API_ENDPOINT = os.getenv("WILDBERRIES_API_ENDPOINT")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_reviews(user_id, kb_layout):
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()
        menu_layout = go_to_menu_keyboard()
        
        if not user or not user.tokens:
            logger.info(f"No user or tokens found for user ID: {user_id}")
            await bot.send_message(
                user_id,
                "❌ Необходимо добавить хотя бы один API токен!",
                parse_mode = ParseMode.HTML
            )
            return
        
        if user and user.tokens:
            for token in user.tokens:
                headers = {
                    "Authorization": token.wb_token,
                    "Content-Type": "application/json",
                }

                params = {
                    "isAnswered": "true",
                    "take": 10,
                    "skip": 0,
                }  # Изменить isAnswered на false
                try:
                    response = requests.get(
                        WILDBERRIES_API_ENDPOINT, headers=headers, params=params
                    )

                    if response.status_code == 200:
                        data = response.json()
                        # print(data)
                        feedbacks = data.get("data", {}).get("feedbacks", [])

                        # print(feedbacks)

                        if not feedbacks:
                            logger.info("No feedbacks available.")
                            return

                        for feedback in feedbacks:
                            # Поверхностная хня
                            review_rating = feedback.get(
                                "productValuation", "Рейтинг не указан"
                            )
                            review_username = feedback.get("userName", "Имя не указано")
                            review_text = feedback.get("text", "Нет отзыва")
                            # Детали
                            product_details = feedback.get("productDetails", {})
                            review_item = product_details.get(
                                "productName", "Unknown item"
                            )
                            review_supplier = product_details.get(
                                "supplierName", "Unknown supplier"
                            )
                            review_id = feedback.get("id")

                            print(feedback)

                            chatgpt_response = await get_chatgpt_response(
                                review_supplier, review_item, review_rating, review_text
                            )

                            # print(
                            #     f"Текст отзыва: {review_text}, Товар: {review_item}, Поставщик: {review_supplier}, Рейтинг: {review_rating}, Имя:{review_username}"
                            # )
                            # {chatgpt_response}
                            
                            if user.points <= 0:
                                await bot.send_message(
                                user_id,
                                "❌ У вас недостаточно токенов для ответа. Пожалуйста, пополните баланс."
                                )
                                return

                            sent_message = await bot.send_message(
                                user_id,
                                f"<b>Новый отзыв:</b>\n\nМагазин: <b>{review_supplier}</b>\nИмя:{review_username}\nТовар: {review_item}\nОценка: {review_rating}\nТекст отзыва: {review_text}\nОтвет от ИИ: {chatgpt_response}\n<b>Осталось токенов:{user.points}</b>",
                                parse_mode=ParseMode.HTML,
                                reply_markup=kb_layout,
                                
                            )
                            
                            user.points -= 1
                            session.commit()

                            message_to_review_map[sent_message.message_id] = review_id
                    else:
                        logger.error(f"Failed to fetch reviews: {response.status_code}")
                        return []
                except requests.RequestException as e:
                    logger.error(f"Error fetching reviews: {e}")
                    return None
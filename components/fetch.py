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

# Dictionary to store message IDs and their corresponding review and response data
message_to_review_and_response_map = {}

async def fetch_reviews(user_id, kb_layout):
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
            processed_reviews_set = set(user.review_ids or [])

            if user.tokens:
                for token in user.tokens:
                    headers = {
                        "Authorization": token.wb_token,
                        "Content-Type": "application/json",
                    }

                    params = {
                        "isAnswered": "true",
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
                                logging.info("No feedbacks available.")
                                continue

                            # Flag to track if a "Нет новых отзывов!" message has been sent
                            no_new_reviews_sent = False

                            for feedback in feedbacks:
                                review_id = feedback.get("id")

                                # Skip if the review was already processed
                                if review_id in processed_reviews_set:
                                    if not no_new_reviews_sent:
                                        await bot.send_message(
                                            text="Нет новых отзывов!",
                                            chat_id=user_id
                                        )
                                        no_new_reviews_sent = True  # Set flag to True after sending the message
                                    continue

                                # Extract review data
                                review_rating = feedback.get("productValuation", "Рейтинг не указан")
                                review_username = feedback.get("userName", "Имя не указано")
                                review_text = feedback.get("text", "Нет отзыва")
                                product_details = feedback.get("productDetails", {})
                                
                                # Safely get product details with fallback values
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

                                # Send the message and store its ID
                                sent_message = await bot.send_message(
                                    user_id,
                                    f"<b>Новый отзыв:</b>\n\nМагазин: <b>{review_supplier}</b>\nИмя: {review_username}\nТовар: {review_item}\nОценка: {review_rating}\nТекст отзыва: {review_text}\nОтвет от ИИ: {chatgpt_response}\n<b>Осталось токенов: {user.points}</b>",
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=kb_layout,
                                )

                                # Create a new entry in ReviewResponse with the message_id and product_name
                                review_response = ReviewResponse(
                                    user_id=user.id,
                                    review_id=review_id,
                                    chatgpt_response=chatgpt_response,
                                    message_id=sent_message.message_id,  # Store the message ID
                                    product_name=review_item  # Store the product name with a default value
                                )
                                session.add(review_response)
                                session.commit()

                                # Decrease user points and save it
                                user.points -= 1
                                session.commit()

                                # Add the review ID to the processed set
                                processed_reviews_set.add(review_id)
                                user.review_ids = list(processed_reviews_set)
                                session.commit()

                        else:
                            logging.error(f"Failed to fetch reviews: {response.status_code}")
                    except requests.RequestException as e:
                        logging.error(f"Error fetching reviews: {e}")
    except Exception as e:
        logging.error(f"Error in review fetching loop: {e}")



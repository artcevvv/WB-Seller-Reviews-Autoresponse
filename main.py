from dotenv import load_dotenv
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ParseMode,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils import executor
import requests
import openai
import asyncio


load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WILDBERRIES_API_TOKEN = os.getenv("WILDBERRIES_API_TOKEN")
WILDBERRIES_API_ENDPOINT = os.getenv("WILDBERRIES_API_ENDPOINT")
GPT_API_TOKEN = os.getenv("GPT_API_TOKEN")

openai.api_key = GPT_API_TOKEN
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
publish_inline_button = InlineKeyboardButton("Опубликовать", callback_data="button1")
inline_keyboard = InlineKeyboardMarkup().add(publish_inline_button)
active_users = set()
sent_reviews_ids = set()
start_button = KeyboardButton("/start")
kb_menu_layout = ReplyKeyboardMarkup(resize_keyboard=True).add(start_button)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


messages = [{"role": "system", "content": "feedback_rating"}]


def create_rev_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    skip_button = InlineKeyboardButton("Пропустить", callback_data="skip")
    reply_button = InlineKeyboardButton("Ответить", callback_data="reply")
    keyboard.add(skip_button, reply_button)
    return keyboard


async def fetch_reviews(user_id, kb_layout):
    headers = {
        "Authorization": WILDBERRIES_API_TOKEN,
        "Content-Type": "application/json",
    }

    params = {
        "isAnswered": "true",
        "take": 4,
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

            print(feedbacks)

            if not feedbacks:
                logger.info("No feedbacks available.")
                return

            for feedback in feedbacks:
                # Поверхностная хня
                review_rating = feedback.get("productValuation", "Рейтинг не указан")
                review_username = feedback.get("userName", "Имя не указано")
                review_text = feedback.get("text", "Нет отзыва")
                # Детали
                product_details = feedback.get("productDetails", {})
                review_item = product_details.get("productName", "Unknown item")
                review_supplier = product_details.get(
                    "supplierName", "Unknown supplier"
                )

                print(
                    f"Текст отзыва: {review_text}, Товар: {review_item}, Поставщик: {review_supplier}, Рейтинг: {review_rating}, Имя:{review_username}"
                )

                await bot.send_message(
                    user_id,
                    f"<b>Новый отзыв:</b>\n\nМагазин: <b>{review_supplier}</b>\nИмя:{review_username}Товар: {review_item}\nОценка: {review_rating}\nТекст отзыва: {review_text}\n",
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb_layout,
                )
        else:
            logger.error(f"Failed to fetch reviews: {response.status_code}")
            return []
    except requests.RequestException as e:
        logger.error(f"Error fetching reviews: {e}")
        return None


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.chat.id
    active_users.add(user_id)

    kb_layout = create_rev_keyboard()

    await message.reply(
        "Hello! I will send you new reviews from Wildberries automatically.",
        reply_markup=kb_menu_layout,
    )

    await fetch_reviews(user_id, kb_layout)


@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Update {update} caused error {exception}")
    return True


if __name__ == "__main__":
    # asyncio.get_event_loop().run_forever()
    executor.start_polling(dp, skip_updates=True)

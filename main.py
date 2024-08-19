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
kb_layout = ReplyKeyboardMarkup(resize_keyboard=True).add(start_button)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


messages = [{"role": "system", "content": "feedback_rating"}]




def fetch_reviews():
    headers = {
        "Authorization": WILDBERRIES_API_TOKEN,
        "Content-Type": "application/json",
    }

    params = {"isAnswered": "false", "take": 1, "skip": 0}
    try:
        response = requests.get(
            WILDBERRIES_API_ENDPOINT, headers=headers, params=params
        )

        if response.status_code == 200:
            data = response.json()
            feedbacks = data.get("data", {}).get("feedbacks", [])
            feedbacks_answered_status = feedbacks[0].get("answer")
            # print(feedbacks[0])

            if feedbacks_answered_status == None:
                review_text = feedbacks[0].get("text", "No review_text available")
                review_item = feedbacks[0].get("productDetails").get("productName")
                review_supplier = feedbacks[0].get("productDetails").get("supplierName")
                review_rating = feedbacks[0].get("productValuation")
                review_username = feedbacks[0].get("userName")
                return (
                    review_text,
                    review_item,
                    review_username,
                    review_supplier,
                    review_rating,
                )
            else:
                logger.info("No feedbacks available.")
                return None
        else:
            logger.error(f"Failed to fetch reviews: {response.status_code}")
            return []
    except requests.RequestException as e:
        logger.error(f"Error fetching reviews: {e}")
        return None


# async def send_new_revs_periodically():
# while True:
# feedbacks = fetch_reviews()
# for user_id in active_users:
#     await bot.send_message(
#         user_id,
#         f"<b>New Review:</b>\n{feedbacks}",
#         parse_mode=ParseMode.HTML,
#     )

# await asyncio.sleep(30)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.chat.id
    active_users.add(user_id)
    (
        feedback_review,
        feedback_item,
        feedback_username,
        feedback_supplier,
        feedback_rating,
    ) = fetch_reviews()

    await message.reply(
        "Hello! I will send you new reviews from Wildberries automatically.",
        reply_markup=kb_layout,
    )

    await bot.send_message(
        user_id,
        f"<b>Новый отзыв:</b>\n\nМагазин: <b>{feedback_supplier}</b>\nТовар: {feedback_item}\nОценка: {feedback_rating} \nТекст отзыва: {feedback_review}\n",
        parse_mode=ParseMode.HTML,
    )


# @dp.message_handler(commands=["get_reviews"])
# async def get_revs_command(message: types.Message):
#     reviews = fetch_reviews()

#     if WILDBERRIES_API_TOKEN == "":
#         await message.reply("Command currently does not work")

#     if not reviews:
#         await message.reply("No reviews")

#     for review in reviews:
#         review_text = review.get()


@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Update {update} caused error {exception}")
    return True


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.create_task(send_new_revs_periodically())
    # send_new_revs_periodically()
    executor.start_polling(dp, skip_updates=True)

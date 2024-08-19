from dotenv import load_dotenv
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import requests
import logging

load_dotenv()

WILDBERRIES_API_TOKEN = os.getenv("WILDBERRIES_API_TOKEN")
WILDBERRIES_API_ENDPOINT = os.getenv("WILDBERRIES_API_ENDPOINT")

logger = logging.getLogger(__name__)


def fetch_reviews():
    headers = {
        "Authorization": WILDBERRIES_API_TOKEN,
        "Content-Type": "application/json",
    }

    params = {"isAnswered": "false", "take": 5000, "skip": 0}
    try:
        response = requests.get(
            WILDBERRIES_API_ENDPOINT, headers=headers, params=params
        )

        if response.status_code == 200:
            data = response.json()
            feedbacks = data.get("data", {}).get("feedbacks", [])
            
            # print(data)

            print(feedbacks[0].get('productDetails').get('productName'))

            if feedbacks:
                review_text = feedbacks[0].get("text", "No review_text available")
                # print(review_text)
                return review_text
            else:
                logger.info("No feedbacks available.")
                return None
        else:
            logger.error(f"Failed to fetch reviews: {response.status_code}")
            return []
    except requests.RequestException as e:
        logger.error(f"Error fetching reviews: {e}")
        return None


async def send_new_revs_periodically():
    feedbacks = fetch_reviews()

    for feedback in feedbacks:
        review_id = feedback[0].get("id")

        print(review_id)

        # if review_id not in sent_reviews_ids:
        # review_text = feedback.get("text", "No review text available.")

        # for user_id in active_users:
        # await bot.send_message(
        # user_id,
        # f"<b>New Review:</b>\n{review_text}",
        # parse_mode=ParseMode.HTML,
        # )
        # sent_reviews_ids.add(review_id)

    # await asyncio.sleep(30)


fetch_reviews()

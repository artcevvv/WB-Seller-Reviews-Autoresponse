from dotenv import load_dotenv
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import requests


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WILDBERRIES_API_TOKEN = os.getenv("WILDBERRIES_API_TOKEN")
WILDBERRIES_API_ENDPOINT = os.getenv("WILDBERRIES_API_ENDPOINT")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_reviews():
    headers = {
        "Authorization": f"Bearer {WILDBERRIES_API_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.get(WILDBERRIES_API_ENDPOINT, headers=headers)

    if response.status_code == 200:
        reviews = response.json()
        return reviews
    else:
        logger.error(f"Failed to fetch reviews: {response.status_code}")
        return []


fetch_reviews()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Hi! I'm auto-responder to the WildBerries reviews.")

@dp.message_handler(commands=['get_reviews'])
async def get_revs_command(message: types.Message):
    reviews = fetch_reviews()

    if WILDBERRIES_API_TOKEN == '':
        await message.reply("Command currently does not work")

    # if not reviews:
    #     await message.reply("No reviews")


@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Update {update} caused error {exception}")
    return True

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
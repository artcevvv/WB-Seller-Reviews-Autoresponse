import os
from dotenv import load_dotenv
from openai import OpenAI
import openai
import logging

load_dotenv()

OPENAI_API_KEY = os.getenv("GPT_API_TOKEN")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_chatgpt_response(
    review_supplier, review_item, review_rating, review_text
):
    messages = [
        {
            "role": "system",
            "content": "Ты продавец на wildberries, и тебе нужно отвечать на отзывы клиентов.",
        },
        {
            "role": "user",
            "content": (
                f"Представь, что ты продавец на wildberries. На твой товар оставили отзыв. Название магазина: {review_supplier}"
                f"Товар называется {review_item}. Оценка отзыва {review_rating}. "
                "Обязательно подтверди отзыв клиента и вырази благодарность за оставленный отзыв, независимо от того, положительный он или отрицательный. "
                "Если пользователь указал о какой-то проблеме, то дай ему ответ на эту проблему и покажи серьёзную озабоченность данной проблемой. "
                "В зависимости от тона отзыва поддержи отзыв клиента сочувствием или позитивом. "
                "Покажи клиенту, что ты понимаешь его точку зрения и предложи альтернативные варианты для устранения любой проблемы, которые он мог упомянуть в отзыве. "
                f"Отзыв клиента следующий: {review_text}. Если отзыв не указан- основывайся на оценке."
            ),
        },
    ]

    try:
        # Call the GPT API
        response = OpenAI().chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error calling GPT API: {e}")
        return "Произошла ошибка при обработке отзыва."

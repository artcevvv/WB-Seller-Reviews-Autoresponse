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
                f"Ты — продавец магазина на Wildberries, и на твой товар оставлен отзыв. Название магазина: {review_supplier}. "
                f"Товар: {review_item}. Оценка: {review_rating}. "
                "Составь вежливый и профессиональный ответ на этот отзыв. В начале поблагодари клиента за отзыв. "
                "Если отзыв положительный, вырази благодарность и подчеркни положительные моменты. "
                "Если отзыв содержит жалобу или проблему, вырази сочувствие, покажи, что ты понимаешь озабоченность клиента, и предложи возможные решения или альтернативы. "
                "Обращайся к клиенту уважительно и поддерживающе, показывая готовность помочь и улучшить его опыт. "
                f'Отзыв клиента: "{review_text}". Если текст отзыва отсутствует, ориентируйся только на оценку.'
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

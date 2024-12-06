import requests
from dotenv import load_dotenv

from components.bot import *
from components.config import *

WILDBERRIES_API_ENDPOINT = os.getenv("WILDBERRIES_API_ENDPOINT")

async def send_reply_to_review(review_id, reply_text, token):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    
    data = {
        "id": review_id,
        "text": reply_text
    }

    try:
        response = requests.patch(
            f"{WILDBERRIES_API_ENDPOINT}",  # Обратите внимание на конечную точку API для ответа на отзыв
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            return True  # Успешно отправлено
        else:
            logger.error(f"Failed to send reply: {response.status_code} - {response.text}")
            return False  # Не удалось отправить

    except requests.RequestException as e:
        logger.error(f"Error sending reply to review: {e}")
        return False

import requests
from config import Config


def send_telegram_message(chat_id: str, text: str):
    token = Config.TELEGRAM_BOT_TOKEN

    if not token:
        return {
            "ok": False,
            "error": "telegram_not_configured"
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
        },
        timeout=15,
    )

    return response.json()
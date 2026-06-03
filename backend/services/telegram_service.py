import requests
from config import Config


def send_telegram_message(chat_id: str, text: str):
    token = Config.TELEGRAM_BOT_TOKEN

    if not token:
        return {
            "ok": False,
            "error": "telegram_not_configured"
        }

    if not chat_id:
        return {
            "ok": False,
            "error": "telegram_chat_id_missing"
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        return {
            "ok": False,
            "error": "telegram_request_failed",
            "message": str(exc),
        }

    try:
        payload = response.json()
    except ValueError:
        return {
            "ok": False,
            "error": "telegram_invalid_response",
            "status_code": response.status_code,
        }

    if response.status_code >= 400 and "ok" not in payload:
        payload["ok"] = False

    return payload

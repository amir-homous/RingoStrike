from flask import Blueprint, jsonify
from services.telegram_service import send_telegram_message
from config import Config

telegram_bp = Blueprint(
    "telegram",
    __name__,
)

@telegram_bp.route(
    "/api/telegram/test-reminder",
    methods=["POST"],
)
def telegram_test_reminder():

    result = send_telegram_message(
        Config.TELEGRAM_TEST_CHAT_ID,
        "🔥 RingoStrike test reminder"
    )

    return jsonify(result)
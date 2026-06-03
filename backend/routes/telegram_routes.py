from flask import Blueprint, jsonify,request
from services.telegram_service import send_telegram_message
from config import Config
from services.reminder_service import send_unchecked_test_reminder

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

@telegram_bp.route(
    "/api/telegram/remind-unchecked-test",
    methods=["POST"],
)
def remind_unchecked_test():
    token = request.headers.get("X-Reminder-Token")

    if not Config.REMINDER_ADMIN_TOKEN or token != Config.REMINDER_ADMIN_TOKEN:
        return jsonify({
            "ok": False,
            "error": "unauthorized"
        }), 401

    result = send_unchecked_test_reminder()
    return jsonify(result)
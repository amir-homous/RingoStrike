from flask import Blueprint, jsonify, request

from auth import require_auth
from services.telegram_service import send_telegram_message
from config import Config
from services.reminder_service import (
    build_mission_reminder_diagnostics,
    send_due_mission_telegram_reminders,
    send_unchecked_test_reminder,
)
from services.telegram_connection_service import (
    connect_telegram_code,
    create_connect_code,
    disconnect_telegram,
    get_telegram_settings,
    update_telegram_settings,
)
from utils.api_response import service_response
from utils.validation_utils import parse_json_object_payload

telegram_bp = Blueprint(
    "telegram",
    __name__,
)


def _service_response(payload: dict, code: int):
    return service_response(
        payload,
        code,
        fallback_error="telegram_error",
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


@telegram_bp.post("/api/telegram/remind-due-missions")
def remind_due_missions():
    token = request.headers.get("X-Reminder-Token")

    if not Config.REMINDER_ADMIN_TOKEN or token != Config.REMINDER_ADMIN_TOKEN:
        return jsonify({
            "ok": False,
            "error": "unauthorized",
        }), 401

    payload, payload_error = parse_json_object_payload(request)

    if payload_error:
        return _service_response(
            {
                "ok": False,
                "error": payload_error,
            },
            400,
        )

    result = send_due_mission_telegram_reminders(
        dry_run=bool(payload.get("dry_run", False)),
        limit=payload.get("limit"),
    )
    return jsonify(result)


@telegram_bp.get("/api/telegram/reminder-diagnostics")
def reminder_diagnostics():
    token = request.headers.get("X-Reminder-Token")

    if not Config.REMINDER_ADMIN_TOKEN or token != Config.REMINDER_ADMIN_TOKEN:
        return jsonify({
            "ok": False,
            "error": "unauthorized",
        }), 401

    payload = build_mission_reminder_diagnostics(
        recent_limit=request.args.get("recent_limit", 20),
    )
    return jsonify(payload)


@telegram_bp.get("/api/me/telegram/settings")
@require_auth()
def get_my_telegram_settings(claims):
    payload, code = get_telegram_settings(claims["user_id"])
    return _service_response(payload, code)


@telegram_bp.post("/api/me/telegram/connect-code")
@require_auth()
def create_my_telegram_connect_code(claims):
    payload, code = create_connect_code(claims["user_id"])
    return _service_response(payload, code)


@telegram_bp.patch("/api/me/telegram/settings")
@require_auth()
def update_my_telegram_settings(claims):
    payload, payload_error = parse_json_object_payload(request)

    if payload_error:
        return _service_response(
            {
                "ok": False,
                "error": payload_error,
            },
            400,
        )

    response, code = update_telegram_settings(
        claims["user_id"],
        payload,
    )

    return _service_response(response, code)


@telegram_bp.post("/api/me/telegram/disconnect")
@require_auth()
def disconnect_my_telegram(claims):
    payload, code = disconnect_telegram(claims["user_id"])
    return _service_response(payload, code)


@telegram_bp.post("/api/telegram/connect")
def connect_telegram_chat():
    token = request.headers.get("X-Reminder-Token")

    if not Config.REMINDER_ADMIN_TOKEN or token != Config.REMINDER_ADMIN_TOKEN:
        return jsonify({
            "ok": False,
            "error": "unauthorized",
        }), 401

    payload, payload_error = parse_json_object_payload(request)

    if payload_error:
        return _service_response(
            {
                "ok": False,
                "error": payload_error,
            },
            400,
        )

    response, code = connect_telegram_code(
        payload.get("code"),
        payload.get("telegram_chat_id") or payload.get("chat_id"),
        payload.get("telegram_username") or payload.get("username"),
    )

    return _service_response(response, code)

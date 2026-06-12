from flask import Blueprint, request

from auth import require_auth
from services.mission_service import (
    get_today_missions,
    mark_mission_done,
    remind_mission_later,
    skip_mission,
)
from services.ringo_brain_service import get_today_ringo_guidance
from utils.api_response import error_response, service_response
from utils.validation_utils import parse_json_object_payload

mission_bp = Blueprint("mission_bp", __name__)


@mission_bp.get("/me/today-missions")
@require_auth()
def today_missions_route(claims):
    payload, code = get_today_missions(int(claims["user_id"]))
    return service_response(payload, code)


@mission_bp.get("/me/ringo/today")
@require_auth()
def today_ringo_guidance_route(claims):
    payload, code = get_today_ringo_guidance(int(claims["user_id"]))
    return service_response(payload, code)


@mission_bp.post("/me/missions/<int:mission_id>/done")
@require_auth()
def mission_done_route(claims, mission_id):
    payload, code = mark_mission_done(int(claims["user_id"]), mission_id)
    return service_response(payload, code)


@mission_bp.post("/me/missions/<int:mission_id>/remind-later")
@require_auth()
def mission_remind_later_route(claims, mission_id):
    body, payload_error = parse_json_object_payload(request)

    if payload_error:
        return error_response(payload_error, 400)

    reminder_at = body.get("reminder_at")
    payload, code = remind_mission_later(
        int(claims["user_id"]),
        mission_id,
        reminder_at,
    )
    return service_response(payload, code)


@mission_bp.post("/me/missions/<int:mission_id>/skip")
@require_auth()
def mission_skip_route(claims, mission_id):
    body, payload_error = parse_json_object_payload(request)

    if payload_error:
        return error_response(payload_error, 400)

    payload, code = skip_mission(
        int(claims["user_id"]),
        mission_id,
        reason=body.get("reason"),
    )
    return service_response(payload, code)

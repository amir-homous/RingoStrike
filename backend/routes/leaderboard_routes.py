from flask import Blueprint

from auth import require_auth
from services.leaderboard_service import enrollment_leaderboard
from utils.api_response import error_response, ok_response


leaderboard_bp = Blueprint("leaderboard_bp", __name__)


@leaderboard_bp.get("/me/enrollments/<int:enrollment_id>/leaderboard")
@require_auth()
def enrollment_leaderboard_route(claims, enrollment_id):
    payload, code = enrollment_leaderboard(enrollment_id)

    if not payload.get("ok"):
        return error_response(
            payload.get("error", "leaderboard_error"),
            code,
        )

    clean_payload = {
        key: value
        for key, value in payload.items()
        if key != "ok"
    }

    return ok_response(clean_payload, code)
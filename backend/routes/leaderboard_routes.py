from flask import Blueprint

from auth import require_auth
from services.leaderboard_service import enrollment_leaderboard
from utils.api_response import service_response


leaderboard_bp = Blueprint("leaderboard_bp", __name__)


@leaderboard_bp.get("/me/enrollments/<int:enrollment_id>/leaderboard")
@require_auth()
def enrollment_leaderboard_route(claims, enrollment_id):
    payload, code = enrollment_leaderboard(
        enrollment_id,
        int(claims["user_id"]),
    )

    return service_response(
        payload,
        code,
        fallback_error="leaderboard_error",
    )

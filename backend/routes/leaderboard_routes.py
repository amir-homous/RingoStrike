from flask import Blueprint, jsonify
from auth import require_auth
from services.leaderboard_service import enrollment_leaderboard

leaderboard_bp = Blueprint('leaderboard_bp', __name__)

@leaderboard_bp.get('/me/enrollments/<int:enrollment_id>/leaderboard')
@require_auth()
def enrollment_leaderboard_route(claims, enrollment_id):
    payload, code = enrollment_leaderboard(enrollment_id)
    return jsonify(payload), code
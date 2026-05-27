from flask import Blueprint, jsonify
from auth import require_auth
from services.enrollment_service import checkin

enrollment_bp = Blueprint('enrollment_bp', __name__)

@enrollment_bp.post('/me/challenges/<int:enrollment_id>/checkin')
@require_auth()
def checkin_route(claims, enrollment_id):
    payload, code = checkin(int(claims['user_id']), enrollment_id)
    return jsonify(payload), code
from flask import Blueprint, jsonify, request
from auth import require_auth
from services.history_service import enrollment_history

history_bp = Blueprint('history_bp', __name__)

@history_bp.get('/me/challenges/<int:enrollment_id>/history')
@require_auth()
def enrollment_history_route(claims, enrollment_id):
    payload, code = enrollment_history(int(claims['user_id']), enrollment_id, request.args.get('days'))
    return jsonify(payload), code
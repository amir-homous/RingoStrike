from flask import Blueprint, jsonify
from auth import require_auth
from services.dashboard_service import get_me, get_dashboard, get_stats
from services.activity_service import get_activity_feed

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.get('/me')
@require_auth()
def me(claims):
    payload, code = get_me(claims)
    return jsonify(payload), code

@dashboard_bp.get('/me/challenges')
@require_auth()
def me_dashboard(claims):
    payload, code = get_dashboard(int(claims['user_id']))
    return jsonify(payload), code

@dashboard_bp.get('/me/stats')
@require_auth()
def me_stats(claims):
    payload, code = get_stats(int(claims['user_id']))
    return jsonify(payload), code

@dashboard_bp.get('/me/activity')
@require_auth()
def me_activity(claims):
    payload, code = get_activity_feed(int(claims['user_id']))
    return jsonify(payload), code

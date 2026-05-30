from flask import Blueprint, jsonify
from auth import require_auth
from services.dashboard_service import get_me, get_dashboard
from services.activity_service import get_activity_feed
from services.achievement_service import get_user_achievements
from services.profile_service import get_profile
from services.consistency_service import get_consistency

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


@dashboard_bp.get('/me/activity')
@require_auth()
def me_activity(claims):
    payload, code = get_activity_feed(int(claims['user_id']))
    return jsonify(payload), code

@dashboard_bp.get('/me/achievements')
@require_auth()
def me_achievements(claims):
    payload, code = get_user_achievements(int(claims['user_id']))
    return jsonify(payload), code

@dashboard_bp.get('/me/profile')
@require_auth()
def me_profile(claims):
    payload, code = get_profile(int(claims['user_id']))
    return jsonify(payload), code

@dashboard_bp.get('/me/consistency')
@require_auth()
def me_consistency(claims):
    payload, code = get_consistency(int(claims['user_id']))
    return jsonify(payload), code

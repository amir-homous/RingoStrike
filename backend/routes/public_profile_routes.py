from flask import Blueprint, jsonify

from services.public_profile_service import get_public_profile
from services.public_consistency_service import get_public_consistency
from services.public_achievement_service import get_public_achievements

public_profile_bp = Blueprint("public_profile_bp", __name__)


@public_profile_bp.get("/api/public/profile/<username>")
def public_profile(username):
    payload, code = get_public_profile(username)
    return jsonify(payload), code

@public_profile_bp.get(
    "/api/public/profile/<username>/achievements"
)
def public_achievements(username):
    payload, code = get_public_achievements(username)
    return jsonify(payload), code


@public_profile_bp.get(
    "/api/public/profile/<username>/consistency"
)
def public_consistency(username):
    payload, code = get_public_consistency(username)
    return jsonify(payload), code
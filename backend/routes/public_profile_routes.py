from flask import Blueprint, jsonify

from services.public_profile_service import get_public_profile

public_profile_bp = Blueprint("public_profile_bp", __name__)


@public_profile_bp.get("/api/public/profile/<username>")
def public_profile(username):
    payload, code = get_public_profile(username)
    return jsonify(payload), code
from flask import Blueprint, jsonify

from auth import require_auth
from services.stats_service import build_user_stats_payload

stats_bp = Blueprint("stats_bp", __name__)


@stats_bp.get("/me/stats")
@require_auth()
def me_stats(claims):
    user_id = claims.get("user_id")
    if user_id is None:
        return jsonify({"ok": False, "error": "invalid_token"}), 401

    payload, code = build_user_stats_payload(int(user_id))
    return jsonify(payload), code

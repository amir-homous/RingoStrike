from flask import (
    Blueprint,
    jsonify,
    request,
)

from routes.auth_routes import require_auth

from services.profile_settings_service import (
    get_profile_settings,
    update_profile_settings,
)


profile_settings_bp = Blueprint(
    "profile_settings_bp",
    __name__,
)


@profile_settings_bp.get(
    "/api/me/profile/settings"
)
@require_auth()
def get_my_profile_settings(claims):
    user_id = claims["user_id"]

    payload, code = get_profile_settings(
        user_id
    )

    return jsonify(payload), code


@profile_settings_bp.patch(
    "/api/me/profile/settings"
)
@require_auth()
def update_my_profile_settings(claims):
    user_id = claims["user_id"]

    payload = request.json or {}

    response, code = update_profile_settings(
        user_id,
        payload,
    )

    return jsonify(response), code
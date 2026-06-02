from flask import (
    Blueprint,
    request,
)

from auth import require_auth

from services.profile_settings_service import (
    get_profile_settings,
    update_profile_settings,
)

from utils.api_response import (
    service_response,
)


profile_settings_bp = Blueprint(
    "profile_settings_bp",
    __name__,
)


def _service_response(payload: dict, code: int):
    return service_response(
        payload,
        code,
        fallback_error="profile_settings_error",
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

    return _service_response(payload, code)


@profile_settings_bp.patch(
    "/api/me/profile/settings"
)
@require_auth()
def update_my_profile_settings(claims):
    user_id = claims["user_id"]

    payload = request.get_json(silent=True)

    if payload is None:
        payload = {}

    response, code = update_profile_settings(
        user_id,
        payload,
    )

    return _service_response(response, code)

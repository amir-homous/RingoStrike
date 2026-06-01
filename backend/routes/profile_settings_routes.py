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
    error_response,
    ok_response,
)


profile_settings_bp = Blueprint(
    "profile_settings_bp",
    __name__,
)


def _service_response(payload: dict, code: int):
    if not payload.get("ok"):
        return error_response(
            payload.get("error", "profile_settings_error"),
            code,
        )

    clean_payload = {
        key: value
        for key, value in payload.items()
        if key != "ok"
    }

    return ok_response(clean_payload, code)


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
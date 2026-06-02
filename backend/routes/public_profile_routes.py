from flask import Blueprint, jsonify, request

from auth import require_auth

from services.public_profile_service import (
    get_public_profile,
)

from services.profile_visibility_service import (
    update_profile_visibility,
)

from services.public_consistency_service import (
    get_public_consistency,
)

from services.public_achievement_service import (
    get_public_achievements,
)

from services.profile_update_service import (
    FIELD_UNSET,
    update_profile,
)
from utils.api_response import error_response
from utils.validation_utils import parse_json_object_payload

public_profile_bp = Blueprint(
    "public_profile_bp",
    __name__,
)


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


@public_profile_bp.patch(
    "/api/profile/visibility"
)
@require_auth()
def patch_profile_visibility(claims):
    data, payload_error = parse_json_object_payload(request)

    if payload_error:
        return error_response(payload_error, 400)

    visibility = data.get("visibility")

    payload, code = update_profile_visibility(
        user_id=claims["user_id"],
        visibility=visibility,
    )

    return jsonify(payload), code

@public_profile_bp.patch(
    "/api/profile"
)

@require_auth()
def patch_profile(claims):
    data, payload_error = parse_json_object_payload(request)

    if payload_error:
        return error_response(payload_error, 400)

    payload, code = update_profile(
        user_id=claims["user_id"],
        name=data["name"] if "name" in data else FIELD_UNSET,
        bio=data["bio"] if "bio" in data else FIELD_UNSET,
        avatar_url=(
            data["avatar_url"]
            if "avatar_url" in data
            else FIELD_UNSET
        ),
    )

    return jsonify(payload), code

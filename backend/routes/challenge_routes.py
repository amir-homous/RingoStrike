from flask import Blueprint, request

from auth import require_auth
from services.challenge_service import (
    get_challenge_detail,
    get_challenge_members,
    get_enrollment_detail,
    join_challenge,
    list_challenges,
    list_public_challenges,
)
from utils.api_response import error_response, ok_response, service_response

challenge_bp = Blueprint("challenge_bp", __name__)


@challenge_bp.get('/challenges/public')
def public_challenges():
    return ok_response({"items": list_public_challenges()})


@challenge_bp.get('/challenges')
@require_auth()
def list_challenges_route(claims):
    payload, code = list_challenges(int(claims["user_id"]))
    return service_response(payload, code)


@challenge_bp.get('/challenges/<int:challenge_id>')
def challenge_detail_route(challenge_id):
    payload, code = get_challenge_detail(challenge_id)
    return service_response(payload, code)


@challenge_bp.get('/challenges/<int:challenge_id>/members')
def challenge_members_route(challenge_id):
    payload, code = get_challenge_members(
        challenge_id,
        request.args.get("limit"),
        request.args.get("offset"),
    )
    return service_response(payload, code)


@challenge_bp.get('/me/enrollments/<int:enrollment_id>')
@require_auth()
def enrollment_detail_route(claims, enrollment_id):
    payload, code = get_enrollment_detail(int(claims["user_id"]), enrollment_id)
    return service_response(payload, code)


@challenge_bp.post('/challenges/<int:challenge_id>/join')
@require_auth()
def join_challenge_route(claims, challenge_id):
    body = request.get_json(silent=True)

    if body is None:
        body = {}

    if not isinstance(body, dict):
        return error_response("invalid_json_body", 400)

    join_code = body.get("join_code", "")

    if join_code is None:
        join_code = ""

    if not isinstance(join_code, str):
        return error_response("invalid_join_code_type", 400)

    join_code = join_code.strip()

    if len(join_code) > 64:
        return error_response("join_code_too_long", 400)

    payload, code = join_challenge(
        int(claims["user_id"]),
        challenge_id,
        join_code,
    )
    return service_response(payload, code)

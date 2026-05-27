from flask import Blueprint, jsonify, request

from auth import require_auth
from services.challenge_service import (
    get_challenge_detail,
    get_challenge_members,
    get_enrollment_detail,
    join_challenge,
    list_challenges,
    list_public_challenges,
)

challenge_bp = Blueprint("challenge_bp", __name__)


@challenge_bp.get('/challenges/public')
def public_challenges():
    return jsonify({"ok": True, "items": list_public_challenges()})


@challenge_bp.get('/challenges')
@require_auth()
def list_challenges_route(claims):
    payload, code = list_challenges(int(claims["user_id"]))
    return jsonify(payload), code


@challenge_bp.get('/challenges/<int:challenge_id>')
def challenge_detail_route(challenge_id):
    payload, code = get_challenge_detail(challenge_id)
    return jsonify(payload), code


@challenge_bp.get('/challenges/<int:challenge_id>/members')
def challenge_members_route(challenge_id):
    payload, code = get_challenge_members(
        challenge_id,
        request.args.get("limit"),
        request.args.get("offset"),
    )
    return jsonify(payload), code


@challenge_bp.get('/me/enrollments/<int:enrollment_id>')
@require_auth()
def enrollment_detail_route(claims, enrollment_id):
    payload, code = get_enrollment_detail(int(claims["user_id"]), enrollment_id)
    return jsonify(payload), code


@challenge_bp.post('/challenges/<int:challenge_id>/join')
@require_auth()
def join_challenge_route(claims, challenge_id):
    body = request.get_json(silent=True) or {}
    payload, code = join_challenge(
        int(claims['user_id']), challenge_id, str(body.get('join_code') or '').strip()
    )
    return jsonify(payload), code
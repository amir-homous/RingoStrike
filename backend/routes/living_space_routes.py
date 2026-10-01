from flask import Blueprint

from auth import require_auth
from services.living_space_service import (
    get_user_space_state,
    mark_reward_seen,
)
from utils.api_response import service_response


living_space_bp = Blueprint("living_space_bp", __name__)


@living_space_bp.get("/me/space")
@require_auth()
def me_space_route(claims):
    payload, code = get_user_space_state(int(claims["user_id"]))
    return service_response(payload, code)


@living_space_bp.get("/me/space/rewards")
@require_auth()
def me_space_rewards_route(claims):
    payload, code = get_user_space_state(int(claims["user_id"]))
    if payload.get("ok"):
        payload = {
            "ok": True,
            "rewards": payload["rewards"],
            "has_unseen_rewards": payload["has_unseen_rewards"],
        }
    return service_response(payload, code)


@living_space_bp.post("/me/space/rewards/<int:reward_id>/seen")
@require_auth()
def me_space_reward_seen_route(claims, reward_id):
    payload, code = mark_reward_seen(int(claims["user_id"]), reward_id)
    return service_response(payload, code)

from flask import Blueprint

from auth import require_auth
from services.path_service import (
    get_path_challenges,
    list_paths,
    start_user_path,
)
from utils.api_response import service_response

path_bp = Blueprint("path_bp", __name__)


@path_bp.get("/paths")
@require_auth(optional=True)
def list_paths_route(claims=None):
    user_id = int(claims["user_id"]) if claims and claims.get("user_id") else None
    payload, code = list_paths(user_id)
    return service_response(payload, code)


@path_bp.get("/paths/<int:path_id>/challenges")
@require_auth(optional=True)
def path_challenges_route(claims=None, path_id=None):
    user_id = int(claims["user_id"]) if claims and claims.get("user_id") else None
    payload, code = get_path_challenges(path_id, user_id)
    return service_response(payload, code)


@path_bp.post("/paths/<int:path_id>/start")
@require_auth()
def start_path_route(claims, path_id):
    payload, code = start_user_path(int(claims["user_id"]), path_id)
    return service_response(payload, code)

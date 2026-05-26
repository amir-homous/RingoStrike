import os

from flask import Blueprint, jsonify, make_response, request

from services.auth_service import (
    get_me_payload,
    login_local_user,
    register_local_user,
    require_auth,
    set_auth_cookie,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    result, status = register_local_user(
        username=data.get("username"),
        password=data.get("password"),
        name=data.get("name"),
        email=data.get("email"),
    )
    if not result.get("ok"):
        return jsonify(result), status

    token = result["access_token"]
    return set_auth_cookie(jsonify(result), token), status


@auth_bp.post("/auth/login")
def auth_login():
    data = request.get_json(silent=True) or {}
    result, status = login_local_user(
        username=data.get("username"),
        password=data.get("password"),
    )
    if not result.get("ok"):
        return jsonify(result), status

    token = result["access_token"]
    return set_auth_cookie(jsonify(result), token), status


@auth_bp.post("/auth/logout")
def logout():
    resp = make_response(jsonify({"ok": True}), 200)

    cookie_name = os.getenv("JWT_COOKIE_NAME", "ringo_token")
    secure = os.getenv("JWT_COOKIE_SECURE", "0") == "1"
    samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    resp.set_cookie(
        cookie_name,
        "",
        max_age=0,
        expires=0,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )
    return resp


@auth_bp.get("/me")
def me():
    claims = require_auth()
    payload, status = get_me_payload(claims)
    return jsonify(payload), status

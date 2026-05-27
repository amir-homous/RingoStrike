import os
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app, request

from database import create_user, get_user_by_id, verify_password


def make_jwt(payload: dict):
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    payload = dict(payload)
    payload["exp"] = int(exp.timestamp())
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def require_auth():
    token = None

    cookie_name = current_app.config.get("JWT_COOKIE_NAME", "ringo_token")
    token = request.cookies.get(cookie_name)

    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

    if not token:
        return None

    try:
        claims = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
        return claims
    except Exception:
        return None


def set_auth_cookie(resp, token: str):
    cookie_name = current_app.config.get("JWT_COOKIE_NAME", "ringo_token")
    secure = (os.getenv("JWT_COOKIE_SECURE", "0") == "1")
    samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    resp.set_cookie(
        cookie_name,
        token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=7 * 24 * 3600,
        path="/",
    )
    return resp


def register_local_user(username: str, password: str, name: str, email: str):
    username = (username or "").strip()
    password = (password or "").strip()
    name = (name or "").strip()
    email = (email or "").strip()

    if not username or len(username) < 3:
        return {"ok": False, "error": "username_min_3_chars"}, 400
    if not password or len(password) < 6:
        return {"ok": False, "error": "password_min_6_chars"}, 400
    if email and "@" not in email:
        return {"ok": False, "error": "invalid_email"}, 400

    try:
        user_id = create_user(
            username=username,
            password=password,
            name=name or username,
            email=email or None,
        )
    except ValueError as e:
        return {"ok": False, "error": str(e)}, 409

    claims = {
        "user_id": user_id,
        "username": username,
        "name": name or username,
        "auth_method": "local",
    }
    token = make_jwt(claims)
    return {
        "ok": True,
        "user_id": user_id,
        "username": username,
        "access_token": token,
    }, 201


def login_local_user(username: str, password: str):
    username = (username or "").strip()
    password = (password or "").strip()

    if not username or not password:
        return {"ok": False, "error": "username_and_password_required"}, 400

    user = verify_password(username, password)
    if not user:
        return {"ok": False, "error": "invalid_credentials"}, 401

    claims = {
        "user_id": user["id"],
        "username": user["username"],
        "name": user["name"],
        "auth_method": "local",
    }
    token = make_jwt(claims)
    return {
        "ok": True,
        "user_id": user["id"],
        "username": user["username"],
        "access_token": token,
    }, 200


def get_me_payload(claims):
    if not claims:
        return {"ok": False, "error": "unauthorized"}, 401

    auth_method = claims.get("auth_method", "telegram")
    if auth_method == "local":
        user = get_user_by_id(claims["user_id"])
        if not user:
            return {"ok": False, "error": "user_not_found"}, 404
        return {
            "ok": True,
            "user_id": claims.get("user_id"),
            "username": user.get("username"),
            "name": user.get("name"),
            "email": user.get("email"),
            "auth_method": "local",
            "registered": True,
        }, 200

    return {
        "ok": True,
        "telegram_id": claims.get("telegram_id"),
        "user_id": claims.get("user_id"),
        "telegram_username": claims.get("telegram_username"),
        "first_name": claims.get("first_name"),
        "registered": claims.get("registered", False),
        "auth_method": "telegram",
    }, 200
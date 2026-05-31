from __future__ import annotations

import os
from flask import Blueprint, jsonify

from config import Config


health_bp = Blueprint("health_bp", __name__)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _is_configured(value) -> bool:
    return bool(str(value or "").strip())


@health_bp.get("/health")
def health():
    return jsonify({"ok": True}), 200


@health_bp.get("/health/config")
def health_config():
    """
    Safe production-readiness config snapshot.

    This endpoint must never expose secrets, tokens,
    full database paths, or integration credentials.
    """

    flask_env = os.getenv("FLASK_ENV", "development")

    public_base_url = (
        os.getenv("PUBLIC_BASE_URL")
        or os.getenv("BASE_URL")
        or ""
    )

    frontend_base_url = (
        os.getenv("FRONTEND_BASE_URL")
        or os.getenv("FRONTEND_ORIGIN")
        or ""
    )

    db_path = (
        os.getenv("DB_PATH")
        or os.getenv("DATABASE_URL")
        or getattr(Config, "DB_PATH", "")
    )

    payload = {
        "ok": True,
        "env": flask_env,
        "database_configured": _is_configured(db_path),
        "local_login_enabled": _env_bool(
            "LOCAL_LOGIN_ENABLED",
            default=True,
        ),
        "jwt_cookie_secure": _env_bool(
            "JWT_COOKIE_SECURE",
            default=False,
        ),
        "jwt_cookie_samesite": os.getenv(
            "JWT_COOKIE_SAMESITE",
            "Lax",
        ),
        "jwt_cookie_name_configured": _is_configured(
            os.getenv("JWT_COOKIE_NAME", "ringo_token")
        ),
        "public_base_url_configured": _is_configured(
            public_base_url
        ),
        "frontend_base_url_configured": _is_configured(
            frontend_base_url
        ),
        "telegram_configured": _is_configured(
            os.getenv("TELEGRAM_BOT_TOKEN")
        ),
        "notion_configured": _is_configured(
            os.getenv("NOTION_TOKEN")
        ),
    }

    return jsonify(payload), 200
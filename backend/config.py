import os
from dotenv import load_dotenv


load_dotenv()


def _env_bool(
    name: str,
    default: bool = False,
) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _require_secret(
    name: str,
    fallback: str,
    flask_env: str,
) -> str:
    value = os.getenv(name)

    if value:
        return value

    if flask_env == "development":
        return fallback

    raise RuntimeError(
        f"{name} must be set outside development"
    )


class Config:
    FLASK_ENV = os.getenv(
        "FLASK_ENV",
        "development",
    )

    SECRET_KEY = _require_secret(
        "SECRET_KEY",
        "dev_secret_key_only_for_local",
        FLASK_ENV,
    )

    JWT_SECRET = _require_secret(
        "JWT_SECRET",
        "dev_jwt_secret_only_for_local",
        FLASK_ENV,
    )

    # Database
    DB_PATH = os.getenv(
        "DB_PATH",
        "ringostrike.db",
    )

    # Public URLs
    PUBLIC_BASE_URL = os.getenv(
        "PUBLIC_BASE_URL",
        "http://localhost:5005",
    )

    FRONTEND_BASE_URL = os.getenv(
        "FRONTEND_BASE_URL",
        "http://localhost:5173",
    )

    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        FRONTEND_BASE_URL,
    )

    # Cookie auth
    JWT_COOKIE_NAME = os.getenv(
        "JWT_COOKIE_NAME",
        "ringo_token",
    )

    JWT_COOKIE_SECURE = _env_bool(
        "JWT_COOKIE_SECURE",
        default=False,
    )

    JWT_COOKIE_SAMESITE = os.getenv(
        "JWT_COOKIE_SAMESITE",
        "Lax",
    )

    # Local fallback auth
    LOCAL_LOGIN_ENABLED = _env_bool(
        "LOCAL_LOGIN_ENABLED",
        default=True,
    )

    LOCAL_LOGIN_SECRET = os.getenv(
        "LOCAL_LOGIN_SECRET",
        "supersecret123",
    ).strip()

    AUTH_MODE = os.getenv(
        "AUTH_MODE",
        "all",
    )

    # Telegram integration
    TELEGRAM_BOT_TOKEN = os.getenv(
        "TELEGRAM_BOT_TOKEN",
    )

    TELEGRAM_BOT_USERNAME = os.getenv(
        "TELEGRAM_BOT_USERNAME",
    )

    # Notion integration legacy/future support
    NOTION_TOKEN = os.getenv(
        "NOTION_TOKEN",
    )

    NOTION_USERS_DB_ID = os.getenv(
        "NOTION_USERS_DB_ID",
    )

    NOTION_ENROLLMENTS_DB_ID = os.getenv(
        "NOTION_ENROLLMENTS_DB_ID",
    )

    NOTION_CHALLENGES_DB_ID = os.getenv(
        "NOTION_CHALLENGES_DB_ID",
    )

    NOTION_DAILY_LOGS_DB_ID = os.getenv(
        "NOTION_DAILY_LOGS_DB_ID",
    )

    NOTION_TELEGRAM_PROP = os.getenv(
        "NOTION_TELEGRAM_PROP",
        "Telegram ID",
    )

    # Demo / local debug support
    DEMO_USER_ID = os.getenv(
        "DEMO_USER_ID",
        "12345",
    )
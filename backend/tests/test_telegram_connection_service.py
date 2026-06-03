from datetime import datetime, timedelta, timezone

from helpers import auth_headers, register_user


def _connect_header():
    return {"X-Reminder-Token": "test-reminder-token"}


def test_authenticated_user_can_generate_connect_code(client, monkeypatch):
    from services import telegram_connection_service

    monkeypatch.setattr(telegram_connection_service.Config, "TELEGRAM_BOT_USERNAME", "ringo_test_bot")
    user = register_user(client, username="TelegramCodeUser")

    res = client.post(
        "/api/me/telegram/connect-code",
        headers=auth_headers(user["access_token"]),
    )

    assert res.status_code == 201
    data = res.get_json()
    assert data["ok"] is True
    assert data["connect_code"]["code"].startswith("RS-")
    assert data["connect_code"]["bot_link"].startswith("https://t.me/ringo_test_bot?start=RS-")
    assert data["connect_code"]["expires_at"]


def test_new_connect_code_replaces_previous_pending_code(client):
    user = register_user(client, username="TelegramReplaceUser")
    headers = auth_headers(user["access_token"])

    first = client.post(
        "/api/me/telegram/connect-code",
        headers=headers,
    ).get_json()["connect_code"]["code"]

    second = client.post(
        "/api/me/telegram/connect-code",
        headers=headers,
    ).get_json()["connect_code"]["code"]

    assert first != second

    import database

    conn = database.get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT code, status
            FROM telegram_connections
            WHERE user_id = ?
            ORDER BY id
            """,
            (user["user_id"],),
        ).fetchall()
    finally:
        conn.close()

    assert [(row["code"], row["status"]) for row in rows] == [
        (first, "expired"),
        (second, "pending"),
    ]


def test_valid_connect_code_stores_chat_id(client, monkeypatch):
    from routes import telegram_routes

    monkeypatch.setattr(telegram_routes.Config, "REMINDER_ADMIN_TOKEN", "test-reminder-token")
    user = register_user(client, username="TelegramConnectUser")
    code = client.post(
        "/api/me/telegram/connect-code",
        headers=auth_headers(user["access_token"]),
    ).get_json()["connect_code"]["code"]

    res = client.post(
        "/api/telegram/connect",
        headers=_connect_header(),
        json={
            "code": code,
            "telegram_chat_id": "777001",
            "telegram_username": "ringouser",
        },
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["settings"]["connected"] is True
    assert data["settings"]["reminders_enabled"] is True
    assert data["settings"]["telegram_username"] == "ringouser"

    import database

    conn = database.get_db_connection()
    try:
        user_row = conn.execute(
            "SELECT telegram_id FROM users WHERE id = ?",
            (user["user_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert user_row["telegram_id"] == "777001"


def test_invalid_and_expired_connect_codes_are_rejected(client, monkeypatch):
    from routes import telegram_routes

    monkeypatch.setattr(telegram_routes.Config, "REMINDER_ADMIN_TOKEN", "test-reminder-token")
    user = register_user(client, username="TelegramExpiredUser")
    code = client.post(
        "/api/me/telegram/connect-code",
        headers=auth_headers(user["access_token"]),
    ).get_json()["connect_code"]["code"]

    invalid = client.post(
        "/api/telegram/connect",
        headers=_connect_header(),
        json={
            "code": "RS-NOPE0000",
            "telegram_chat_id": "777002",
        },
    )

    assert invalid.status_code == 404
    assert invalid.get_json()["error"] == "invalid_connect_code"

    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            UPDATE telegram_connections
            SET expires_at = ?
            WHERE code = ?
            """,
            (
                (datetime.now(timezone.utc) - timedelta(minutes=1))
                .replace(microsecond=0)
                .isoformat(),
                code,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    expired = client.post(
        "/api/telegram/connect",
        headers=_connect_header(),
        json={
            "code": code,
            "telegram_chat_id": "777003",
        },
    )

    assert expired.status_code == 410
    assert expired.get_json()["error"] == "connect_code_expired"


def test_telegram_settings_update_and_disconnect(client):
    user = register_user(client, username="TelegramSettingsUser")
    headers = auth_headers(user["access_token"])

    update = client.patch(
        "/api/me/telegram/settings",
        headers=headers,
        json={
            "reminders_enabled": True,
            "daily_checkin_enabled": False,
            "streak_risk_enabled": False,
            "weekly_summary_enabled": True,
        },
    )

    assert update.status_code == 200
    settings = update.get_json()["settings"]
    assert settings["reminders_enabled"] is True
    assert settings["daily_checkin_enabled"] is False
    assert settings["streak_risk_enabled"] is False
    assert settings["weekly_summary_enabled"] is True

    disconnect = client.post(
        "/api/me/telegram/disconnect",
        headers=headers,
    )

    assert disconnect.status_code == 200
    assert disconnect.get_json()["settings"]["connected"] is False

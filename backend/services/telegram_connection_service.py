from __future__ import annotations

import secrets
import sqlite3
import string
from datetime import datetime, timedelta, timezone

from config import Config
from database import get_db_connection


CONNECT_CODE_TTL_MINUTES = 15
CONNECT_CODE_ALPHABET = string.ascii_uppercase + string.digits


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _bool(value) -> bool:
    return bool(int(value or 0))


def _make_connect_code() -> str:
    suffix = "".join(secrets.choice(CONNECT_CODE_ALPHABET) for _ in range(8))
    return f"RS-{suffix}"


def _bot_link(code: str | None = None) -> str | None:
    username = Config.TELEGRAM_BOT_USERNAME

    if not username:
        return None

    username = username.lstrip("@")

    if not code:
        return f"https://t.me/{username}"

    return f"https://t.me/{username}?start={code}"


def _settings_from_row(row) -> dict:
    connected = bool(
        row
        and row["status"] == "connected"
        and row["telegram_chat_id"]
    )

    return {
        "connected": connected,
        "telegram_username": row["telegram_username"] if row else None,
        "reminders_enabled": _bool(row["reminders_enabled"]) if row else False,
        "daily_checkin_enabled": _bool(row["daily_checkin_enabled"]) if row else True,
        "streak_risk_enabled": _bool(row["streak_risk_enabled"]) if row else True,
        "weekly_summary_enabled": _bool(row["weekly_summary_enabled"]) if row else False,
        "bot_username": Config.TELEGRAM_BOT_USERNAME,
        "bot_link": _bot_link(),
    }


def _latest_connection(conn, user_id: int):
    return conn.execute(
        """
        SELECT *
        FROM telegram_connections
        WHERE user_id = ?
        ORDER BY
            CASE status
                WHEN 'connected' THEN 0
                WHEN 'pending' THEN 1
                ELSE 2
            END,
            COALESCE(connected_at, updated_at, created_at) DESC,
            id DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()


def _ensure_settings_row(conn, user_id: int):
    row = _latest_connection(conn, user_id)

    if row:
        return row

    code = _make_connect_code()
    conn.execute(
        """
        INSERT INTO telegram_connections (
            user_id,
            code,
            status,
            reminders_enabled,
            daily_checkin_enabled,
            streak_risk_enabled,
            weekly_summary_enabled,
            created_at,
            updated_at
        )
        VALUES (?, ?, 'disconnected', 0, 1, 1, 0, ?, ?)
        """,
        (
            user_id,
            code,
            _iso(_now_utc()),
            _iso(_now_utc()),
        ),
    )
    conn.commit()
    return _latest_connection(conn, user_id)


def get_telegram_settings(user_id: int):
    conn = get_db_connection()
    try:
        row = _latest_connection(conn, user_id)
        return {
            "ok": True,
            "settings": _settings_from_row(row),
        }, 200
    finally:
        conn.close()


def create_connect_code(user_id: int, ttl_minutes: int = CONNECT_CODE_TTL_MINUTES):
    expires_at = _now_utc() + timedelta(minutes=ttl_minutes)
    created_at = _now_utc()

    conn = get_db_connection()
    try:
        previous = _latest_connection(conn, user_id)

        conn.execute(
            """
            UPDATE telegram_connections
            SET status = 'expired',
                updated_at = ?
            WHERE user_id = ?
              AND status = 'pending'
            """,
            (_iso(created_at), user_id),
        )
        conn.commit()

        for _ in range(5):
            code = _make_connect_code()

            try:
                conn.execute(
                    """
                    INSERT INTO telegram_connections (
                        user_id,
                        code,
                        status,
                        reminders_enabled,
                        daily_checkin_enabled,
                        streak_risk_enabled,
                        weekly_summary_enabled,
                        created_at,
                        expires_at,
                        updated_at
                    )
                    VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        code,
                        int(_bool(previous["reminders_enabled"])) if previous else 0,
                        int(_bool(previous["daily_checkin_enabled"])) if previous else 1,
                        int(_bool(previous["streak_risk_enabled"])) if previous else 1,
                        int(_bool(previous["weekly_summary_enabled"])) if previous else 0,
                        _iso(created_at),
                        _iso(expires_at),
                        _iso(created_at),
                    ),
                )
                conn.commit()
                break
            except sqlite3.IntegrityError:
                conn.rollback()
                continue
        else:
            return {
                "ok": False,
                "error": "connect_code_generation_failed",
            }, 500

        return {
            "ok": True,
            "connect_code": {
                "code": code,
                "expires_at": _iso(expires_at),
                "bot_username": Config.TELEGRAM_BOT_USERNAME,
                "bot_link": _bot_link(code),
            },
        }, 201
    finally:
        conn.close()


def connect_telegram_code(code: str, telegram_chat_id: str, telegram_username: str | None = None):
    normalized_code = (code or "").strip().upper()
    chat_id = str(telegram_chat_id or "").strip()
    username = (telegram_username or "").strip() or None

    if not normalized_code:
        return {"ok": False, "error": "connect_code_required"}, 400

    if not chat_id:
        return {"ok": False, "error": "telegram_chat_id_required"}, 400

    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT *
            FROM telegram_connections
            WHERE code = ?
              AND status = 'pending'
            LIMIT 1
            """,
            (normalized_code,),
        ).fetchone()

        if not row:
            return {"ok": False, "error": "invalid_connect_code"}, 404

        expires_at = _parse_iso(row["expires_at"])

        if expires_at and expires_at < _now_utc():
            conn.execute(
                """
                UPDATE telegram_connections
                SET status = 'expired',
                    updated_at = ?
                WHERE id = ?
                """,
                (_iso(_now_utc()), row["id"]),
            )
            conn.commit()
            return {"ok": False, "error": "connect_code_expired"}, 410

        now = _iso(_now_utc())

        conn.execute(
            """
            UPDATE telegram_connections
            SET status = 'disconnected',
                updated_at = ?
            WHERE status = 'connected'
              AND (
                user_id = ?
                OR telegram_chat_id = ?
              )
            """,
            (now, row["user_id"], chat_id),
        )

        conn.execute(
            """
            UPDATE telegram_connections
            SET status = 'connected',
                telegram_chat_id = ?,
                telegram_username = ?,
                reminders_enabled = 1,
                connected_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                chat_id,
                username,
                now,
                now,
                row["id"],
            ),
        )

        conn.execute(
            """
            UPDATE users
            SET telegram_id = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = ?
              AND id != ?
            """,
            (chat_id, row["user_id"]),
        )

        conn.execute(
            """
            UPDATE users
            SET telegram_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (chat_id, row["user_id"]),
        )

        conn.commit()

        return {
            "ok": True,
            "user_id": row["user_id"],
            "settings": _settings_from_row(_latest_connection(conn, row["user_id"])),
        }, 200
    finally:
        conn.close()


def update_telegram_settings(user_id: int, payload: dict):
    allowed = {
        "reminders_enabled",
        "daily_checkin_enabled",
        "streak_risk_enabled",
        "weekly_summary_enabled",
    }

    updates = {
        key: int(bool(payload[key]))
        for key in allowed
        if key in payload
    }

    conn = get_db_connection()
    try:
        row = _ensure_settings_row(conn, user_id)

        if updates:
            assignments = ", ".join(f"{key} = ?" for key in updates)
            params = [
                *updates.values(),
                _iso(_now_utc()),
                row["id"],
            ]

            conn.execute(
                f"""
                UPDATE telegram_connections
                SET {assignments},
                    updated_at = ?
                WHERE id = ?
                """,
                params,
            )
            conn.commit()

        return {
            "ok": True,
            "settings": _settings_from_row(_latest_connection(conn, user_id)),
        }, 200
    finally:
        conn.close()


def disconnect_telegram(user_id: int):
    conn = get_db_connection()
    try:
        now = _iso(_now_utc())

        conn.execute(
            """
            UPDATE telegram_connections
            SET status = 'disconnected',
                telegram_chat_id = NULL,
                updated_at = ?
            WHERE user_id = ?
              AND status IN ('pending', 'connected')
            """,
            (now, user_id),
        )

        conn.execute(
            """
            UPDATE users
            SET telegram_id = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (user_id,),
        )

        conn.commit()

        return {
            "ok": True,
            "settings": _settings_from_row(_latest_connection(conn, user_id)),
        }, 200
    finally:
        conn.close()

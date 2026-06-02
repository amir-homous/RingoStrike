from database import get_db_connection
from services.username_service import normalize_username


def get_public_consistency(username: str):
    username = normalize_username(username)
    conn = get_db_connection()

    try:
        user = conn.execute(
            """
            SELECT id, profile_visibility
            FROM users
            WHERE lower(username) = lower(?)
            """,
            (username,),
        ).fetchone()

        if not user:
            return {
                "ok": False,
                "error": "profile_not_found",
            }, 404

        if user["profile_visibility"] != "public":
            return {
                "ok": False,
                "error": "profile_private",
            }, 403

        rows = conn.execute(
            """
            SELECT date
            FROM checkins
            WHERE user_id = ?
              AND is_counted = 1
            ORDER BY date DESC
            LIMIT 365
            """,
            (user["id"],),
        ).fetchall()

        return {
            "ok": True,
            "days": [
                r["date"]
                for r in rows
            ],
        }, 200

    finally:
        conn.close()

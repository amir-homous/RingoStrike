from database import get_db_connection
from services.username_service import normalize_username


def get_public_identity(username: str, *, conn=None):
    normalized_username = normalize_username(username)
    owns_connection = conn is None

    if owns_connection:
        conn = get_db_connection()

    try:
        user = conn.execute(
            """
            SELECT id, username, profile_visibility
            FROM users
            WHERE lower(username) = lower(?)
            """,
            (normalized_username,),
        ).fetchone()

        if not user:
            return None, {
                "ok": False,
                "error": "profile_not_found",
            }, 404

        if user["profile_visibility"] != "public":
            return None, {
                "ok": False,
                "error": "profile_private",
            }, 403

        return user, None, 200

    finally:
        if owns_connection:
            conn.close()

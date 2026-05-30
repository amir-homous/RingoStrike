from __future__ import annotations

from database import get_db_connection


ALLOWED_VISIBILITY = {
    "public",
    "private",
}


def get_profile_settings(user_id: int):
    conn = get_db_connection()

    try:
        user = conn.execute(
            """
            SELECT
                avatar_url,
                bio,
                profile_visibility
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        if not user:
            return {
                "ok": False,
                "error": "user_not_found",
            }, 404

        return {
            "ok": True,
            "settings": {
                "avatar_url": user["avatar_url"],
                "bio": user["bio"] or "",
                "profile_visibility":
                    user["profile_visibility"] or "public",
            },
        }, 200

    finally:
        conn.close()


def update_profile_settings(
    user_id: int,
    payload: dict,
):
    conn = get_db_connection()

    try:
        user = conn.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        if not user:
            return {
                "ok": False,
                "error": "user_not_found",
            }, 404

        bio = (
            payload.get("bio", "")
            .strip()
        )[:280]

        avatar_url = (
            payload.get("avatar_url")
            or None
        )

        profile_visibility = (
            payload.get("profile_visibility")
            or "public"
        ).lower()

        if (
            profile_visibility
            not in ALLOWED_VISIBILITY
        ):
            return {
                "ok": False,
                "error": "invalid_visibility",
            }, 400

        conn.execute(
            """
            UPDATE users
            SET
                bio = ?,
                avatar_url = ?,
                profile_visibility = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                bio,
                avatar_url,
                profile_visibility,
                user_id,
            ),
        )

        conn.commit()

        return {
            "ok": True,
            "message":
                "profile_settings_updated",
        }, 200

    finally:
        conn.close()
from __future__ import annotations

from database import get_db_connection


ALLOWED_VISIBILITY = {
    "public",
    "private",
}

MAX_BIO_LENGTH = 280
MAX_AVATAR_URL_LENGTH = 500


def _validate_optional_string(value, field_name: str):
    if value is None:
        return "", None, None

    if not isinstance(value, str):
        return None, {
            "ok": False,
            "error": f"invalid_{field_name}_type",
        }, 400

    return value.strip(), None, None


def _validate_avatar_url(value: str):
    if not value:
        return None, None

    if len(value) > MAX_AVATAR_URL_LENGTH:
        return {
            "ok": False,
            "error": "avatar_url_too_long",
        }, 400

    is_local_path = (
        value.startswith("/")
        and not value.startswith("//")
    )
    is_absolute_url = (
        value.startswith("http://")
        or value.startswith("https://")
    )

    if not (is_local_path or is_absolute_url):
        return {
            "ok": False,
            "error": "invalid_avatar_url",
        }, 400

    return None, None


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
    if not isinstance(payload, dict):
        return {
            "ok": False,
            "error": "invalid_json_body",
        }, 400

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

        bio, error, code = _validate_optional_string(
            payload.get("bio", ""),
            "bio",
        )
        if error:
            return error, code

        avatar_url, error, code = _validate_optional_string(
            payload.get("avatar_url"),
            "avatar_url",
        )
        if error:
            return error, code

        if len(bio) > MAX_BIO_LENGTH:
            return {
                "ok": False,
                "error": "bio_too_long",
            }, 400

        avatar_error, avatar_code = _validate_avatar_url(avatar_url)
        if avatar_error:
            return avatar_error, avatar_code

        profile_visibility = (
            payload.get("profile_visibility")
            or "public"
        )

        if not isinstance(profile_visibility, str):
            return {
                "ok": False,
                "error": "invalid_visibility_type",
            }, 400

        profile_visibility = profile_visibility.lower().strip()

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
                avatar_url or None,
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

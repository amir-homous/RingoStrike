from database import get_db_connection


MAX_NAME_LENGTH = 60
MAX_BIO_LENGTH = 280
MAX_AVATAR_URL_LENGTH = 500
FIELD_UNSET = object()


def _validate_optional_string(value, field_name: str):
    if value is FIELD_UNSET:
        return FIELD_UNSET, None, None

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

    allowed_prefixes = (
        "/",
        "http://",
        "https://",
    )

    if not value.startswith(allowed_prefixes):
        return {
            "ok": False,
            "error": "invalid_avatar_url",
        }, 400

    return None, None


def update_profile(
    user_id: int,
    name: str | None | object = FIELD_UNSET,
    bio: str | None | object = FIELD_UNSET,
    avatar_url: str | None | object = FIELD_UNSET,
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

        clean_name, error, code = _validate_optional_string(name, "name")
        if error:
            return error, code

        clean_bio, error, code = _validate_optional_string(bio, "bio")
        if error:
            return error, code

        clean_avatar, error, code = _validate_optional_string(avatar_url, "avatar_url")
        if error:
            return error, code

        if (
            clean_name is not FIELD_UNSET
            and len(clean_name) > MAX_NAME_LENGTH
        ):
            return {
                "ok": False,
                "error": "name_too_long",
            }, 400

        if (
            clean_bio is not FIELD_UNSET
            and len(clean_bio) > MAX_BIO_LENGTH
        ):
            return {
                "ok": False,
                "error": "bio_too_long",
            }, 400

        if clean_avatar is not FIELD_UNSET:
            avatar_error, avatar_code = _validate_avatar_url(clean_avatar)
            if avatar_error:
                return avatar_error, avatar_code

        updates = []
        values = []

        if clean_name is not FIELD_UNSET:
            updates.append("name = ?")
            values.append(clean_name)

        if clean_bio is not FIELD_UNSET:
            updates.append("bio = ?")
            values.append(clean_bio)

        if clean_avatar is not FIELD_UNSET:
            updates.append("avatar_url = ?")
            values.append(clean_avatar or None)

        if not updates:
            return {
                "ok": True,
            }, 200

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)

        conn.execute(
            f"""
            UPDATE users
            SET {", ".join(updates)}
            WHERE id = ?
            """,
            values,
        )

        conn.commit()

        return {
            "ok": True,
        }, 200

    finally:
        conn.close()

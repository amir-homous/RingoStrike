from database import get_db_connection


MAX_BIO_LENGTH = 280


def update_profile(
    user_id: int,
    name: str | None = None,
    bio: str | None = None,
    avatar_url: str | None = None,
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

        clean_name = (
            (name or "").strip()
        )[:60]

        clean_bio = (
            (bio or "").strip()
        )[:MAX_BIO_LENGTH]

        clean_avatar = (
            (avatar_url or "").strip()
        )[:500]

        conn.execute(
            """
            UPDATE users
            SET
                name = ?,
                bio = ?,
                avatar_url = ?
            WHERE id = ?
            """,
            (
                clean_name,
                clean_bio,
                clean_avatar,
                user_id,
            ),
        )

        conn.commit()

        return {
            "ok": True,
        }, 200

    finally:
        conn.close()
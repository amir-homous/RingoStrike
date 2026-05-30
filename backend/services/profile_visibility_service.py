from database import get_db_connection


ALLOWED_VISIBILITY = {
    "public",
    "private",
}


def update_profile_visibility(
    user_id: int,
    visibility: str,
):
    if visibility not in ALLOWED_VISIBILITY:
        return {
            "ok": False,
            "error": "invalid_visibility",
        }, 400

    conn = get_db_connection()

    try:
        conn.execute(
            """
            UPDATE users
            SET profile_visibility = ?
            WHERE id = ?
            """,
            (visibility, user_id),
        )

        conn.commit()

        return {
            "ok": True,
            "visibility": visibility,
        }, 200

    finally:
        conn.close()
from database import get_db_connection
from services.public_identity_service import get_public_identity


def get_public_consistency(username: str):
    conn = get_db_connection()

    try:
        user, error_payload, code = get_public_identity(username, conn=conn)
        if error_payload:
            return error_payload, code

        rows = conn.execute(
            """
            SELECT DISTINCT date
            FROM checkins
            WHERE user_id = ?
              AND status = 'Done'
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

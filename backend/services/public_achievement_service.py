from database import get_db_connection
from services.public_identity_service import get_public_identity


def get_public_achievements(username: str):
    conn = get_db_connection()

    try:
        user, error_payload, code = get_public_identity(username, conn=conn)
        if error_payload:
            return error_payload, code

        achievements = conn.execute(
            """
            SELECT
                a.key,
                a.title,
                a.description,
                a.rarity,
                a.xp_reward,
                ua.unlocked_at
            FROM user_achievements ua
            JOIN achievements a
              ON a.id = ua.achievement_id
            WHERE ua.user_id = ?
            ORDER BY ua.unlocked_at DESC
            LIMIT 6
            """,
            (user["id"],),
        ).fetchall()

        return {
            "ok": True,
            "achievements": [
                {
                    "key": a["key"],
                    "title": a["title"],
                    "description": a["description"],
                    "rarity": a["rarity"],
                    "xp_reward": a["xp_reward"],
                    "unlocked": True,
                    "unlocked_at": a["unlocked_at"],
                }
                for a in achievements
            ],
        }, 200

    finally:
        conn.close()

from database import get_db_connection
from services.username_service import normalize_username


def get_public_achievements(username: str):
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
            return {"ok": False, "error": "profile_not_found"}, 404

        if user["profile_visibility"] != "public":
            return {"ok": False, "error": "profile_private"}, 403

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

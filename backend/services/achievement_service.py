from __future__ import annotations

from database import get_db_connection
from services.stats_service import calculate_level

ACHIEVEMENT_DEFS = [
    ("first_checkin", "First Step Forward", "Complete your first check-in", "spark", "checkin", "total_checkins", 1, 10, "common", 0, 10),
    ("first_challenge_completed", "Challenge Ignition", "Complete check-ins in your first active challenge", "target", "consistency", "active_challenge_checkins", 1, 15, "common", 0, 20),
    ("streak_3", "3-Day Warrior", "Maintain a 3-day streak", "flame", "streak", "streak", 3, 20, "rare", 0, 30),
    ("streak_7", "7-Day Warrior", "Maintain a 7-day streak", "flame", "streak", "streak", 7, 40, "epic", 0, 40),
    ("streak_30", "Unbreakable 30", "Maintain a 30-day streak", "crown", "streak", "streak", 30, 120, "legendary", 0, 50),
    ("xp_100", "Momentum Initiate", "Reach 100 XP", "bolt", "xp", "total_xp", 100, 20, "common", 0, 60),
    ("xp_500", "Momentum Builder", "Reach 500 XP", "bolt", "xp", "total_xp", 500, 60, "rare", 0, 70),
    ("xp_1000", "Momentum Vanguard", "Reach 1000 XP", "star", "xp", "total_xp", 1000, 120, "epic", 0, 80),
    ("checkins_10", "Consistency Starter", "Complete 10 total check-ins", "check", "checkin", "total_checkins", 10, 30, "rare", 0, 90),
    ("checkins_50", "Consistency Architect", "Complete 50 total check-ins", "check", "checkin", "total_checkins", 50, 100, "epic", 0, 100),
]


def ensure_achievement_definitions(conn):
    for row in ACHIEVEMENT_DEFS:
        conn.execute(
            """
            INSERT INTO achievements (key, title, description, icon, category, condition_type, condition_value, xp_reward, rarity, is_hidden, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
              title=excluded.title,
              description=excluded.description,
              icon=excluded.icon,
              category=excluded.category,
              condition_type=excluded.condition_type,
              condition_value=excluded.condition_value,
              xp_reward=excluded.xp_reward,
              rarity=excluded.rarity,
              is_hidden=excluded.is_hidden,
              sort_order=excluded.sort_order
            """,
            row,
        )


def _build_metrics(conn, user_id: int) -> dict:
    stats = conn.execute(
        "SELECT total_checkins, total_points, current_streak FROM user_stats WHERE user_id=?",
        (user_id,),
    ).fetchone()
    challenge_progress = conn.execute(
        """
        SELECT CAST(COUNT(*) AS INTEGER) AS n
        FROM checkins
        WHERE user_id=? AND status='Done' AND is_counted = 1
        """,
        (user_id,),
    ).fetchone()["n"]
    xp = int((stats or {})["total_points"] or 0)
    return {
        "total_checkins": int((stats or {})["total_checkins"] or 0),
        "total_xp": xp,
        "streak": int((stats or {})["current_streak"] or 0),
        "level": int(calculate_level(xp)),
        "active_challenge_checkins": int(challenge_progress or 0),
    }


def evaluate_and_unlock(user_id: int):
    conn = get_db_connection()
    try:
        ensure_achievement_definitions(conn)
        metrics = _build_metrics(conn, user_id)
        defs = conn.execute("SELECT * FROM achievements ORDER BY sort_order ASC, id ASC").fetchall()
        unlocked_ids = {
            r["achievement_id"]
            for r in conn.execute("SELECT achievement_id FROM user_achievements WHERE user_id=?", (user_id,)).fetchall()
        }

        newly = []
        for ach in defs:
            if ach["id"] in unlocked_ids:
                continue
            condition_type = ach["condition_type"]
            current_value = int(metrics.get(condition_type, 0))
            if current_value >= int(ach["condition_value"]):
                conn.execute(
                    "INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
                    (user_id, ach["id"]),
                )
                newly.append({
                    "id": ach["id"],
                    "key": ach["key"],
                    "title": ach["title"],
                    "description": ach["description"],
                    "icon": ach["icon"],
                    "category": ach["category"],
                    "rarity": ach["rarity"],
                    "xp_reward": int(ach["xp_reward"] or 0),
                })

        total_reward = sum(a["xp_reward"] for a in newly)
        conn.commit()
        return {"ok": True, "newly_unlocked": newly, "xp_reward_total": total_reward}
    finally:
        conn.close()


def get_user_achievements(user_id: int):
    conn = get_db_connection()
    try:
        ensure_achievement_definitions(conn)
        rows = conn.execute(
            """
            SELECT a.id, a.key, a.title, a.description, a.icon, a.category, a.rarity, a.xp_reward,
                   ua.unlocked_at
            FROM achievements a
            LEFT JOIN user_achievements ua
              ON ua.achievement_id = a.id AND ua.user_id = ?
            ORDER BY a.sort_order ASC, a.id ASC
            """,
            (user_id,),
        ).fetchall()
        achievements = [{
            "id": r["id"], "key": r["key"], "title": r["title"], "description": r["description"],
            "icon": r["icon"], "category": r["category"], "rarity": r["rarity"], "xp_reward": int(r["xp_reward"] or 0),
            "unlocked": bool(r["unlocked_at"]), "unlocked_at": r["unlocked_at"],
        } for r in rows]
        return {"ok": True, "achievements": achievements}, 200
    finally:
        conn.close()

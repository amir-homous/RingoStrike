from __future__ import annotations

from datetime import datetime

from database import get_db_connection
from services.stats_service import build_level_progress, sync_user_stats
from services.title_service import evaluate_user_title


def _ensure_avatar_column(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "avatar_url" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
        conn.commit()


def get_profile(user_id: int):
    sync = sync_user_stats(user_id)
    conn = get_db_connection()
    try:
        _ensure_avatar_column(conn)
        user = conn.execute(
            """
            SELECT
                id,
                name,
                username,
                created_at,
                avatar_url,
                bio,
                profile_visibility
            FROM users
            WHERE id=?
            """,
            (user_id,),
        ).fetchone()

        if not user:
            return {"ok": False, "error": "user_not_found"}, 404

        achievements_unlocked = conn.execute(
            "SELECT CAST(COUNT(*) AS INTEGER) AS n FROM user_achievements WHERE user_id=?", (user_id,)
        ).fetchone()["n"]
        active_challenges = conn.execute(
            "SELECT CAST(COUNT(*) AS INTEGER) AS n FROM enrollments WHERE user_id=? AND status='Active'", (user_id,)
        ).fetchone()["n"]
        recent_7 = conn.execute(
            """
            SELECT CAST(COUNT(*) AS INTEGER) AS n
            FROM checkins
            WHERE user_id=?
              AND status='Done'
              AND is_counted = 1
              AND date >= date('now','-6 day')
            """,
            (user_id,),
        ).fetchone()["n"]

        total_xp = int(sync.get("total_points", 0))
        total_checkins = int(sync.get("total_checkins", 0))
        current_streak = int(sync.get("current_streak", 0))
        longest_streak = int(sync.get("longest_streak", 0))
        level = build_level_progress(total_xp)["level"]

        title = evaluate_user_title(
            level=level,
            streak=current_streak,
            total_xp=total_xp,
            achievements_unlocked=int(achievements_unlocked),
        )

        created_at = user["created_at"] or ""
        joined_date = created_at.split(" ")[0] if created_at else ""

        return {
            "ok": True,
            "profile": {
                "id": int(user["id"]),
                "name": user["name"] or user["username"] or "Player",
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "joined_date": joined_date,
                "profile_visibility": (
                    user["profile_visibility"] or "public"
                ),
                "title": title,
                "tagline": "Building consistency one strike at a time.",
                "stats": {
                    "level": level,
                    "total_xp": total_xp,
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "total_checkins": total_checkins,
                    "achievements_unlocked": int(achievements_unlocked),
                    "active_challenges": int(active_challenges),
                    "average_weekly_activity": int(recent_7),
                },
            },
        }, 200
    finally:
        conn.close()

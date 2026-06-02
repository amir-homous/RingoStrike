from __future__ import annotations

from datetime import datetime, timedelta
from math import floor
from sqlite3 import DatabaseError

from database import get_db_connection
from utils.date_utils import utc_today_iso

XP_PER_CHECKIN = 10


def _iso_to_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def calculate_current_streak(checkin_dates_iso: list[str], today_iso: str | None = None) -> int:
    if not checkin_dates_iso:
        return 0
    today_iso = today_iso or utc_today_iso()
    dates = set(checkin_dates_iso)
    today = _iso_to_date(today_iso)
    yesterday = today - timedelta(days=1)
    anchor = today if today_iso in dates else yesterday
    if anchor.isoformat() not in dates:
        return 0

    streak = 0
    probe = anchor
    while probe.isoformat() in dates:
        streak += 1
        probe -= timedelta(days=1)
    return streak


def calculate_longest_streak(checkin_dates_iso: list[str]) -> int:
    if not checkin_dates_iso:
        return 0

    dates = sorted({_iso_to_date(value) for value in checkin_dates_iso})
    longest = current = 1
    prev = dates[0]

    for current_date in dates[1:]:
        if (current_date - prev).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
        prev = current_date

    return longest


def calculate_level(xp: int) -> int:
    xp = max(0, int(xp))
    level = 1
    while xp >= calculate_next_level_xp(level):
        level += 1
    return level


def calculate_next_level_xp(level: int) -> int:
    safe_level = max(1, int(level))
    return int(round(100 * (safe_level ** 1.5)))


def calculate_progress_percent(xp: int, level: int) -> int:
    safe_xp = max(0, int(xp))
    safe_level = max(1, int(level))

    current_level_floor = 0 if safe_level <= 1 else calculate_next_level_xp(safe_level - 1)
    next_level_xp = calculate_next_level_xp(safe_level)
    span = max(1, next_level_xp - current_level_floor)
    progressed = max(0, safe_xp - current_level_floor)

    percent = floor((progressed / span) * 100)
    return max(0, min(100, percent))


def build_user_stats_payload(user_id: int) -> tuple[dict, int]:
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return {"ok": False, "error": "user_not_found"}, 404

        checkin_totals_row = conn.execute(
            """
            SELECT
                CAST(COUNT(*) AS INTEGER) AS total_checkins,
                CAST(COUNT(*) * ? AS INTEGER) AS base_points
            FROM checkins
            WHERE user_id = ? AND status = 'Done'
            """,
            (XP_PER_CHECKIN, user_id),
        ).fetchone()

        achievement_reward_row = conn.execute(
            """
            SELECT CAST(COALESCE(SUM(a.xp_reward), 0) AS INTEGER) AS reward_points
            FROM user_achievements ua
            JOIN achievements a ON a.id = ua.achievement_id
            WHERE ua.user_id = ?
            """,
            (user_id,),
        ).fetchone()

        rows = conn.execute(
            "SELECT DISTINCT date FROM checkins WHERE user_id = ? AND status = 'Done' ORDER BY date DESC",
            (user_id,),
        ).fetchall()

        dates = [row["date"] for row in rows]
        total_checkins = int((checkin_totals_row or {})["total_checkins"] or 0)
        base_points = int((checkin_totals_row or {})["base_points"] or 0)
        reward_points = int((achievement_reward_row or {})["reward_points"] or 0)
        total_points = base_points + reward_points
        current_streak = calculate_current_streak(dates, utc_today_iso())
        longest_streak = calculate_longest_streak(dates)

        conn.execute(
            """
            INSERT INTO user_stats (user_id, total_checkins, total_points, current_streak, longest_streak, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                total_checkins = excluded.total_checkins,
                total_points = excluded.total_points,
                current_streak = excluded.current_streak,
                longest_streak = excluded.longest_streak,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, total_checkins, total_points, current_streak, longest_streak),
        )
        conn.commit()

        xp = total_points
        level = calculate_level(xp)
        next_level_xp = calculate_next_level_xp(level)
        progress_percent = calculate_progress_percent(xp, level)

        return {
            "ok": True,
            "user": {"id": int(user["id"]), "name": user["name"]},
            "stats": {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "total_checkins": total_checkins,
                "total_points": total_points,
                "xp": xp,
                "level": level,
                "next_level_xp": next_level_xp,
                "progress_percent": progress_percent,
            },
        }, 200
    except DatabaseError:
        return {"ok": False, "error": "db_error"}, 500
    finally:
        conn.close()


def sync_user_stats(user_id: int) -> dict:
    payload, _ = build_user_stats_payload(user_id)
    if not payload.get("ok"):
        return {"total_checkins": 0, "total_points": 0, "current_streak": 0, "longest_streak": 0}
    stats = payload["stats"]
    return {
        "total_checkins": stats["total_checkins"],
        "total_points": stats["total_points"],
        "current_streak": stats["current_streak"],
        "longest_streak": stats["longest_streak"],
    }

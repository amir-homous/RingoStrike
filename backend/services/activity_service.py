from __future__ import annotations

from datetime import datetime, timezone

from database import get_db_connection
from services.stats_service import XP_PER_CHECKIN, calculate_level, calculate_current_streak


def _iso_label(created_at: str) -> str:
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()


def get_activity_feed(user_id: int, limit: int = 40):
    conn = get_db_connection()
    try:
        safe_limit = max(1, min(int(limit or 40), 100))
        rows = conn.execute(
            """SELECT c.id, c.date, ch.name AS challenge_name
            FROM checkins c JOIN challenges ch ON ch.id = c.challenge_id
            WHERE c.user_id = ? AND c.status = 'Done'
            ORDER BY c.date DESC, c.id DESC LIMIT ?""",
            (user_id, safe_limit),
        ).fetchall()

        all_dates = [r["date"] for r in conn.execute(
            "SELECT DISTINCT date FROM checkins WHERE user_id = ? AND status = 'Done' ORDER BY date ASC", (user_id,)
        ).fetchall()]

        events = []
        seen_streak_dates, seen_level_dates = set(), set()
        for row in rows:
            created_at = _iso_label(f"{row['date']}T12:00:00+00:00")
            events.append({"id": f"checkin-{row['id']}", "type": "checkin", "title": f"Completed {row['challenge_name'] or 'Challenge'}", "subtitle": f"+{XP_PER_CHECKIN} XP earned", "xp_delta": XP_PER_CHECKIN, "icon": "check", "created_at": created_at})
            if row["date"] not in seen_streak_dates:
                streak = calculate_current_streak([d for d in all_dates if d <= row["date"]], row["date"])
                if streak >= 2:
                    events.append({"id": f"streak-{row['date']}", "type": "streak", "title": f"{streak}-day streak maintained", "subtitle": "Consistency is compounding", "icon": "flame", "created_at": created_at})
                seen_streak_dates.add(row["date"])
            if row["date"] not in seen_level_dates:
                points_until = len([d for d in all_dates if d <= row["date"]]) * XP_PER_CHECKIN
                points_before = len([d for d in all_dates if d < row["date"]]) * XP_PER_CHECKIN
                if calculate_level(points_until) > calculate_level(points_before):
                    lvl = calculate_level(points_until)
                    events.append({"id": f"level-{row['date']}-{lvl}", "type": "level_up", "title": f"Reached Level {lvl}", "subtitle": "Milestone unlocked", "icon": "level", "created_at": created_at})
                seen_level_dates.add(row["date"])

        achievement_rows = conn.execute(
            """SELECT ua.id, ua.unlocked_at, a.title, a.rarity
            FROM user_achievements ua JOIN achievements a ON a.id = ua.achievement_id
            WHERE ua.user_id = ? ORDER BY ua.unlocked_at DESC, ua.id DESC LIMIT ?""",
            (user_id, safe_limit),
        ).fetchall()
        for r in achievement_rows:
            created = (r["unlocked_at"] or "").replace(" ", "T")
            if created and "+" not in created:
                created = f"{created}+00:00"
            events.append({"id": f"achievement-{r['id']}", "type": "achievement", "title": "Achievement unlocked", "subtitle": r["title"], "icon": "trophy", "rarity": r["rarity"], "created_at": _iso_label(created or datetime.now(timezone.utc).isoformat())})

        events.sort(key=lambda e: e["created_at"], reverse=True)
        return {"ok": True, "events": events[: safe_limit * 3]}, 200
    finally:
        conn.close()

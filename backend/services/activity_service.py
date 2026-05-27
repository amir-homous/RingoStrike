from __future__ import annotations

from datetime import datetime, timezone

from database import get_db_connection
from services.stats_service import XP_PER_CHECKIN, calculate_level, calculate_current_streak


def _parse_iso_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _iso_label(created_at: str) -> str:
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()


def get_activity_feed(user_id: int, limit: int = 40):
    conn = get_db_connection()
    try:
        safe_limit = max(1, min(int(limit or 40), 100))
        rows = conn.execute(
            """
            SELECT c.id, c.date, c.challenge_id, ch.name AS challenge_name
            FROM checkins c
            JOIN challenges ch ON ch.id = c.challenge_id
            WHERE c.user_id = ? AND c.status = 'Done'
            ORDER BY c.date DESC, c.id DESC
            LIMIT ?
            """,
            (user_id, safe_limit),
        ).fetchall()

        if not rows:
            return {"ok": True, "events": []}, 200

        all_dates_rows = conn.execute(
            "SELECT DISTINCT date FROM checkins WHERE user_id = ? AND status = 'Done' ORDER BY date ASC",
            (user_id,),
        ).fetchall()
        all_dates = [r["date"] for r in all_dates_rows]

        events = []

        seen_streak_dates = set()
        seen_level_dates = set()

        for row in rows:
            created_at = f"{row['date']}T12:00:00+00:00"
            checkin_id = int(row["id"])
            challenge_name = row["challenge_name"] or "Challenge"
            xp_delta = XP_PER_CHECKIN
            events.append(
                {
                    "id": f"checkin-{checkin_id}",
                    "type": "checkin",
                    "title": f"Completed {challenge_name}",
                    "subtitle": f"+{xp_delta} XP earned",
                    "xp_delta": xp_delta,
                    "icon": "check",
                    "created_at": _iso_label(created_at),
                }
            )

            if row["date"] not in seen_streak_dates:
                up_to_day = [d for d in all_dates if d <= row["date"]]
                streak = calculate_current_streak(up_to_day, row["date"])
                if streak >= 2:
                    events.append(
                        {
                            "id": f"streak-{row['date']}",
                            "type": "streak",
                            "title": f"{streak}-day streak maintained",
                            "subtitle": "Consistency is compounding",
                            "icon": "flame",
                            "created_at": _iso_label(created_at),
                        }
                    )
                seen_streak_dates.add(row["date"])

            if row["date"] not in seen_level_dates:
                points_until_day = len([d for d in all_dates if d <= row["date"]]) * XP_PER_CHECKIN
                points_before_day = len([d for d in all_dates if d < row["date"]]) * XP_PER_CHECKIN
                level_at_day = calculate_level(points_until_day)
                level_before_day = calculate_level(points_before_day)
                if level_at_day > level_before_day:
                    events.append(
                        {
                            "id": f"level-{row['date']}-{level_at_day}",
                            "type": "level_up",
                            "title": f"Reached Level {level_at_day}",
                            "subtitle": "Milestone unlocked",
                            "icon": "level",
                            "created_at": _iso_label(created_at),
                        }
                    )
                seen_level_dates.add(row["date"])

        events.sort(key=lambda e: e["created_at"], reverse=True)
        return {"ok": True, "events": events[: safe_limit * 2]}, 200
    finally:
        conn.close()

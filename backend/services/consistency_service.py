from __future__ import annotations

from datetime import datetime, timedelta, timezone

from database import get_db_connection


def get_consistency(user_id: int, days: int = 140):
    safe_days = max(28, min(int(days or 140), 366))
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=safe_days - 1)

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT date, CAST(COUNT(*) AS INTEGER) AS count
            FROM checkins
            WHERE user_id = ?
              AND status = 'Done'
              AND is_counted = 1
              AND date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date ASC
            """,
            (user_id, start_date.isoformat(), end_date.isoformat()),
        ).fetchall()
        return {"ok": True, "days": [{"date": r["date"], "count": int(r["count"])} for r in rows]}, 200
    finally:
        conn.close()

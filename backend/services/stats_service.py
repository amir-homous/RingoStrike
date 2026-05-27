from datetime import datetime, timedelta
from database import get_db_connection
from utils.date_utils import utc_today_iso


def _iso_to_date(s: str):
    return datetime.strptime(s, "%Y-%m-%d").date()


def calculate_current_streak(checkin_dates_iso: list[str], today_iso: str | None = None) -> int:
    if not checkin_dates_iso:
        return 0
    today_iso = today_iso or utc_today_iso()
    s = set(checkin_dates_iso)
    today = _iso_to_date(today_iso)
    yesterday = today - timedelta(days=1)
    anchor = today if today_iso in s else yesterday
    if anchor.isoformat() not in s:
        return 0
    streak = 0
    d = anchor
    while d.isoformat() in s:
        streak += 1
        d = d - timedelta(days=1)
    return streak


def calculate_longest_streak(checkin_dates_iso: list[str]) -> int:
    if not checkin_dates_iso:
        return 0
    dates = sorted({_iso_to_date(d) for d in checkin_dates_iso})
    longest = run = 1
    prev = dates[0]
    for d in dates[1:]:
        if (d - prev).days == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1
        prev = d
    return longest


def sync_user_stats(user_id: int) -> dict:
    conn = get_db_connection()
    try:
        today = utc_today_iso()
        points_row = conn.execute("SELECT COUNT(*) as total FROM checkins WHERE user_id = ? AND status = 'Done'", (user_id,)).fetchone()
        total_checkins = int(points_row['total'] or 0)
        total_points = total_checkins * 10
        rows = conn.execute("SELECT DISTINCT date FROM checkins WHERE user_id = ? AND status = 'Done' ORDER BY date DESC", (user_id,)).fetchall()
        dates = [r['date'] for r in rows]
        current = calculate_current_streak(dates, today)
        longest = calculate_longest_streak(dates)
        conn.execute("UPDATE users SET total_points=?, current_streak=?, longest_streak=? WHERE id=?", (total_points, current, longest, user_id))
        conn.execute("""
            INSERT INTO user_stats (user_id, total_checkins, total_points, current_streak, longest_streak, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                total_checkins=excluded.total_checkins,
                total_points=excluded.total_points,
                current_streak=excluded.current_streak,
                longest_streak=excluded.longest_streak,
                updated_at=CURRENT_TIMESTAMP
        """, (user_id, total_checkins, total_points, current, longest))
        conn.commit()
        return {"total_checkins": total_checkins, "total_points": total_points, "current_streak": current, "longest_streak": longest}
    finally:
        conn.close()
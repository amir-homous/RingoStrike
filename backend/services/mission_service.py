from datetime import datetime, timezone

from database import get_db_connection
from services.enrollment_service import checkin
from services.ringo_decision_service import decide_ringo_state
from utils.date_utils import utc_today_iso


def _row_status(row):
    return row["log_status"] or "pending"


def _mission_payload(row):
    return {
        "mission_id": row["mission_id"],
        "key": row["key"],
        "title": row["title"],
        "description": row["description"] or "",
        "mission_type": row["mission_type"] or "daily",
        "difficulty": row["difficulty"] or "easy",
        "is_core": bool(row["is_core"]),
        "xp_reward": int(row["xp_reward"] or 0),
        "order_index": int(row["order_index"] or 0),
        "suggested_time": row["suggested_time"] or "",
        "unlock_after_days": int(row["unlock_after_days"] or 0),
        "ringo_message": row["ringo_message"] or "",
        "status": _row_status(row),
        "reminder_at": row["reminder_at"],
        "xp_earned": int(row["xp_earned"] or 0),
        "challenge_id": row["challenge_id"],
        "challenge_name": row["challenge_name"],
        "enrollment_id": row["enrollment_id"],
        "path_id": row["path_id"],
        "path_title": row["path_title"],
    }


def _active_path_count(conn, user_id):
    return conn.execute(
        """
        SELECT COUNT(*) AS n
        FROM user_paths
        WHERE user_id = ? AND status = 'Active'
        """,
        (user_id,),
    ).fetchone()["n"]


def _active_enrollment_count(conn, user_id):
    return conn.execute(
        """
        SELECT COUNT(*) AS n
        FROM enrollments
        WHERE user_id = ? AND status = 'Active'
        """,
        (user_id,),
    ).fetchone()["n"]


def _stats_row(conn, user_id):
    return conn.execute(
        """
        SELECT total_checkins, current_streak
        FROM user_stats
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()


def _today_mission_rows(conn, user_id, today):
    return conn.execute(
        """
        SELECT
            m.id AS mission_id,
            m.key,
            m.title,
            m.description,
            m.mission_type,
            m.difficulty,
            m.is_core,
            m.xp_reward,
            m.order_index,
            m.suggested_time,
            m.unlock_after_days,
            m.ringo_message,
            c.id AS challenge_id,
            c.name AS challenge_name,
            c.path_id,
            p.title AS path_title,
            e.id AS enrollment_id,
            ml.status AS log_status,
            ml.reminder_at,
            ml.xp_earned
        FROM enrollments e
        JOIN challenges c ON c.id = e.challenge_id
        JOIN missions m ON m.challenge_id = c.id
        LEFT JOIN paths p ON p.id = c.path_id
        LEFT JOIN mission_logs ml
          ON ml.mission_id = m.id
         AND ml.user_id = e.user_id
         AND ml.date = ?
        WHERE e.user_id = ?
          AND e.status = 'Active'
          AND c.status = 'Active'
          AND m.status = 'Active'
          AND m.mission_type = 'daily'
          AND COALESCE(m.unlock_after_days, 0) <= CAST(julianday(?) - julianday(date(e.joined_at)) AS INTEGER)
        ORDER BY
            CASE WHEN ml.status = 'done' THEN 1 ELSE 0 END,
            CASE WHEN m.is_core = 1 THEN 0 ELSE 1 END,
            m.order_index ASC,
            e.joined_at ASC,
            m.id ASC
        """,
        (today, user_id, today),
    ).fetchall()


def get_today_missions(user_id):
    today = utc_today_iso()
    conn = get_db_connection()
    try:
        missions = [_mission_payload(row) for row in _today_mission_rows(conn, user_id, today)]
        stats = _stats_row(conn, user_id)
        checkins_total = int(stats["total_checkins"] or 0) if stats else 0
        current_streak = int(stats["current_streak"] or 0) if stats else 0

        ringo = decide_ringo_state(
            has_active_path=_active_path_count(conn, user_id) > 0,
            has_active_enrollment=_active_enrollment_count(conn, user_id) > 0,
            missions=missions,
            checkins_total=checkins_total,
            current_streak=current_streak,
        )

        return {
            "ok": True,
            "date": today,
            "ringo": ringo,
            "missions": missions,
        }, 200
    finally:
        conn.close()


def _find_user_mission_context(conn, user_id, mission_id):
    return conn.execute(
        """
        SELECT
            m.id AS mission_id,
            m.title,
            m.xp_reward,
            m.challenge_id,
            e.id AS enrollment_id
        FROM missions m
        JOIN enrollments e
          ON e.challenge_id = m.challenge_id
         AND e.user_id = ?
         AND e.status = 'Active'
        JOIN challenges c ON c.id = m.challenge_id
        WHERE m.id = ?
          AND m.status = 'Active'
          AND c.status = 'Active'
        LIMIT 1
        """,
        (user_id, mission_id),
    ).fetchone()


def _upsert_mission_log(user_id, mission_id, status, *, reminder_at=None, notes=None):
    today = utc_today_iso()
    conn = get_db_connection()
    try:
        mission = _find_user_mission_context(conn, user_id, mission_id)

        if not mission:
            return {"ok": False, "error": "mission_not_found"}, 404

        xp_earned = int(mission["xp_reward"] or 0) if status == "done" else 0

        conn.execute(
            """
            INSERT INTO mission_logs (
                user_id,
                enrollment_id,
                challenge_id,
                mission_id,
                date,
                status,
                reminder_at,
                notes,
                xp_earned,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id, mission_id, date) DO UPDATE SET
                status = excluded.status,
                reminder_at = excluded.reminder_at,
                notes = COALESCE(excluded.notes, mission_logs.notes),
                xp_earned = excluded.xp_earned,
                updated_at = datetime('now')
            """,
            (
                user_id,
                mission["enrollment_id"],
                mission["challenge_id"],
                mission_id,
                today,
                status,
                reminder_at,
                notes,
                xp_earned,
            ),
        )
        conn.commit()

        return {
            "ok": True,
            "mission": {
                "mission_id": mission_id,
                "title": mission["title"],
                "status": status,
                "date": today,
                "xp_earned": xp_earned,
                "enrollment_id": mission["enrollment_id"],
                "challenge_id": mission["challenge_id"],
                "reminder_at": reminder_at,
            },
        }, 200
    finally:
        conn.close()


def mark_mission_done(user_id, mission_id):
    payload, code = _upsert_mission_log(user_id, mission_id, "done")

    if not payload.get("ok"):
        return payload, code

    checkin_payload, checkin_code = checkin(
        user_id,
        payload["mission"]["enrollment_id"],
    )

    payload["checkin"] = checkin_payload
    payload["checkin_status_code"] = checkin_code

    return payload, code


def remind_mission_later(user_id, mission_id, reminder_at):
    value = str(reminder_at or "").strip()

    if not value:
        return {"ok": False, "error": "reminder_at_required"}, 400

    if len(value) > 80:
        return {"ok": False, "error": "reminder_at_too_long"}, 400

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return {"ok": False, "error": "invalid_reminder_at"}, 400

    return _upsert_mission_log(user_id, mission_id, "remind_later", reminder_at=value)


def skip_mission(user_id, mission_id):
    return _upsert_mission_log(user_id, mission_id, "skipped")

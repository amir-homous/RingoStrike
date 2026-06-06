from database import get_db_connection
from utils.date_utils import utc_today_iso
from services.stats_service import sync_user_stats
from services.achievement_service import evaluate_and_unlock


def _sync_first_mission_done_from_checkin(conn, user_id, enrollment_id, date_iso):
    existing_done = conn.execute(
        """
        SELECT 1
        FROM mission_logs
        WHERE user_id = ?
          AND enrollment_id = ?
          AND date = ?
          AND status = 'done'
        LIMIT 1
        """,
        (user_id, enrollment_id, date_iso),
    ).fetchone()

    if existing_done:
        return None

    mission = conn.execute(
        """
        SELECT
            m.id AS mission_id,
            m.challenge_id,
            m.xp_reward
        FROM enrollments e
        JOIN challenges c ON c.id = e.challenge_id
        JOIN missions m ON m.challenge_id = c.id
        LEFT JOIN mission_logs ml
          ON ml.mission_id = m.id
         AND ml.user_id = e.user_id
         AND ml.date = ?
        WHERE e.id = ?
          AND e.user_id = ?
          AND e.status = 'Active'
          AND c.status = 'Active'
          AND m.status = 'Active'
          AND m.mission_type = 'daily'
          AND COALESCE(m.unlock_after_days, 0) <= CAST(julianday(?) - julianday(date(e.joined_at)) AS INTEGER)
          AND (ml.status IS NULL OR ml.status IN ('pending', 'remind_later'))
        ORDER BY
            CASE WHEN m.is_core = 1 THEN 0 ELSE 1 END,
            m.order_index ASC,
            m.id ASC
        LIMIT 1
        """,
        (date_iso, enrollment_id, user_id, date_iso),
    ).fetchone()

    if not mission:
        return None

    conn.execute(
        """
        INSERT INTO mission_logs (
            user_id,
            enrollment_id,
            challenge_id,
            mission_id,
            date,
            status,
            xp_earned,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, 'done', ?, datetime('now'))
        ON CONFLICT(user_id, mission_id, date) DO UPDATE SET
            status = 'done',
            reminder_at = NULL,
            xp_earned = excluded.xp_earned,
            updated_at = datetime('now')
        """,
        (
            user_id,
            enrollment_id,
            mission["challenge_id"],
            mission["mission_id"],
            date_iso,
            int(mission["xp_reward"] or 0),
        ),
    )

    return mission["mission_id"]


def checkin(user_id:int,enrollment_id:int):
    date_iso=utc_today_iso(); conn=get_db_connection()
    synced_mission_id = None
    try:
        enroll=conn.execute("SELECT id, challenge_id, status FROM enrollments WHERE id=? AND user_id=?",(enrollment_id,user_id)).fetchone()
        if not enroll: return {"ok":False,"error":"forbidden_enrollment"},403
        if (enroll["status"] or "") != "Active": return {"ok":False,"error":"enrollment_inactive"},403
        ex=conn.execute("SELECT id FROM checkins WHERE enrollment_id=? AND date=?",(enrollment_id,date_iso)).fetchone()
        created = ex is None
        if ex: conn.execute("UPDATE checkins SET status='Done', is_counted=1 WHERE id=?",(ex['id'],))
        else: conn.execute("INSERT INTO checkins (enrollment_id, user_id, challenge_id, date, status, is_counted) VALUES (?, ?, ?, ?, 'Done', 1)",(enrollment_id,user_id,enroll['challenge_id'],date_iso))
        synced_mission_id = _sync_first_mission_done_from_checkin(
            conn,
            user_id,
            enrollment_id,
            date_iso,
        )
        conn.commit()
    finally:
        conn.close()

    sync_user_stats(user_id)
    achievement_result = evaluate_and_unlock(user_id)
    sync = sync_user_stats(user_id)
    return {
        "ok": True,
        "message": "Check-in recorded",
        "mode": "created" if created else "existing",
        "already_checked": not created,
        "synced_mission_id": synced_mission_id,
        "rewards": {
            "xp_total": int(sync.get("total_points", 0)),
            "achievements": achievement_result.get("newly_unlocked", []),
            "achievement_xp_reward": int(achievement_result.get("xp_reward_total", 0)),
        },
    },200

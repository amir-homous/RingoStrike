import sqlite3
from datetime import datetime, timedelta, timezone

from database import get_db_connection
from services.stats_service import calculate_current_streak
from utils.date_utils import utc_today_iso
from utils.validation_utils import safe_int


def list_public_challenges():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM challenges WHERE visibility = 'Public' AND status = 'Active'"
        ).fetchall()
        return [
            {
                "challenge_id": r["id"],
                "name": r["name"],
                "visibility": r["visibility"],
                "status": r["status"],
                "description": r["description"],
                "duration_days": r["duration_days"],
            }
            for r in rows
        ]
    finally:
        conn.close()


def list_challenges(user_id: int):
    conn = get_db_connection()
    try:
        challenges = conn.execute(
            """
            SELECT c.* FROM challenges c
            LEFT JOIN enrollments e
              ON c.id = e.challenge_id
             AND e.user_id = ?
             AND e.status = 'Active'
            WHERE c.status = 'Active'
            AND (c.visibility IN ('Public', 'Invite-only') OR e.id IS NOT NULL)
            """,
            (user_id,),
        ).fetchall()

        enrollments = conn.execute(
            """
            SELECT id, challenge_id
            FROM enrollments
            WHERE user_id = ? AND status = 'Active'
            """,
            (user_id,),
        ).fetchall()
        enroll_map = {e["challenge_id"]: e["id"] for e in enrollments}

        items = []
        for ch in challenges:
            ch_id = ch["id"]
            enroll_id = enroll_map.get(ch_id)
            vis_lower = ch["visibility"].lower()

            members_count = conn.execute(
                "SELECT COUNT(*) as n FROM enrollments WHERE challenge_id = ? AND status = 'Active'",
                (ch_id,),
            ).fetchone()["n"]

            previews = conn.execute(
                """
                SELECT u.name FROM users u
                JOIN enrollments e ON u.id = e.user_id
                WHERE e.challenge_id = ? AND e.status = 'Active'
                LIMIT 3
                """,
                (ch_id,),
            ).fetchall()

            items.append(
                {
                    "challenge_id": ch_id,
                    "name": ch["name"],
                    "description": ch["description"],
                    "visibility": vis_lower,
                    "status": ch["status"].lower(),
                    "duration_days": ch["duration_days"],
                    "members_count": members_count,
                    "members_preview": [p["name"] for p in previews],
                    "is_joined": enroll_id is not None,
                    "enrollment_id": enroll_id,
                    "needs_code": vis_lower in ["private", "invite-only"],
                }
            )

        return {"ok": True, "items": items}, 200
    finally:
        conn.close()


def get_challenge_detail(challenge_id: int):
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,)).fetchone()
        if row is None:
            return {"ok": False, "error": f"Challenge with ID {challenge_id} not found"}, 404

        visibility = (row["visibility"] or "Private").strip()
        visibility_key = visibility.lower()
        status = (row["status"] or "Active").strip()

        if visibility_key == "private":
            return {"ok": False, "error": "challenge_private"}, 403

        if status.lower() != "active":
            return {"ok": False, "error": "challenge_inactive"}, 403

        count_row = conn.execute(
            "SELECT COUNT(*) FROM enrollments WHERE challenge_id = ? AND status = 'Active'",
            (challenge_id,),
        ).fetchone()
        members_count = count_row[0] if count_row else 0

        tags_list = row["tags"].split(",") if row["tags"] else []
        return {
            "ok": True,
            "item": {
                "challenge_id": row["id"],
                "name": row["name"],
                "description": row["description"] or "",
                "visibility": row["visibility"] or "Public",
                "status": row["status"] or "Active",
                "duration_days": row["duration_days"] or 0,
                "max_members": row["max_members"] or 0,
                "requires_proof": bool(row["requires_proof"] or 0),
                "checkin_method": row["checkin_method"] or "Manual",
                "goal_type": row["goal_type"] or "",
                "tags": tags_list,
                "members_count": members_count,
                "join_code_required": (visibility_key == "invite-only" and bool(row["join_code"])),
            },
        }, 200
    finally:
        conn.close()


def get_challenge_members(challenge_id: int, limit_arg, offset_arg):
    conn = get_db_connection()
    try:
        challenge = conn.execute(
            "SELECT visibility, status FROM challenges WHERE id = ?",
            (challenge_id,),
        ).fetchone()

        if not challenge:
            return {"ok": False, "error": "challenge_not_found"}, 404

        visibility_key = (challenge["visibility"] or "Private").strip().lower()
        status = (challenge["status"] or "Active").strip()

        if visibility_key == "private":
            return {"ok": False, "error": "challenge_private"}, 403

        if status.lower() != "active":
            return {"ok": False, "error": "challenge_inactive"}, 403

        limit = max(1, min(safe_int(limit_arg, 20), 50))
        offset = max(0, safe_int(offset_arg, 0))

        rows = conn.execute(
            """
            SELECT
                enrollments.id,
                enrollments.status,
                enrollments.role,
                users.id AS u_id,
                users.name,
                users.username
            FROM enrollments
            JOIN users ON enrollments.user_id = users.id
            WHERE enrollments.challenge_id = ? AND enrollments.status = 'Active'
            LIMIT ? OFFSET ?
            """,
            (challenge_id, limit + 1, offset),
        ).fetchall()

        items = [
            {
                "enrollment_id": row[0],
                "enrollment_status": row[1],
                "role": row[2] if len(row) > 2 else "Member",
                "user_id": row["u_id"],
                "user_name": row["name"],
                "username": row["username"],
                "telegram_username": row["username"],
            }
            for row in rows[:limit]
        ]

        return {"ok": True, "challenge_id": challenge_id, "items": items, "has_more": len(rows) > limit}, 200
    finally:
        conn.close()


def join_challenge(user_id: int, challenge_id: int, provided_code: str):
    conn = get_db_connection()
    try:
        ch = conn.execute(
            "SELECT id,name,visibility,join_code,status,path_id FROM challenges WHERE id=?", (challenge_id,)
        ).fetchone()
        if not ch:
            return {"ok": False, "error": "challenge_not_found"}, 404
        if (ch["status"] or "Active") != "Active":
            return {"ok": False, "error": "challenge_inactive"}, 403

        visibility = (ch["visibility"] or "Private").strip()
        visibility_key = visibility.lower()
        required = (ch["join_code"] or "").strip()

        if visibility_key == "private":
            return {"ok": False, "error": "challenge_private"}, 403

        if visibility_key == "invite-only":
            if not required:
                return {"ok": False, "error": "invite_only_not_configured"}, 403
            if not provided_code:
                return {"ok": False, "error": "join_code_required"}, 400
            if provided_code != required:
                return {"ok": False, "error": "invalid_join_code"}, 403

        path_id = ch["path_id"]

        def activate_challenge_path():
            if not path_id:
                return None

            existing_path = conn.execute(
                """
                SELECT id
                FROM user_paths
                WHERE user_id = ? AND path_id = ?
                """,
                (user_id, path_id),
            ).fetchone()

            if existing_path:
                conn.execute(
                    """
                    UPDATE user_paths
                    SET status = 'Active',
                        completed_at = NULL,
                        updated_at = datetime('now')
                    WHERE id = ?
                    """,
                    (existing_path["id"],),
                )
                return existing_path["id"]

            cur_path = conn.execute(
                """
                INSERT INTO user_paths (user_id, path_id, status, current_stage)
                VALUES (?, ?, 'Active', 1)
                """,
                (user_id, path_id),
            )
            return cur_path.lastrowid

        try:
            cur = conn.execute(
                "INSERT INTO enrollments (user_id, challenge_id, status) VALUES (?, ?, 'Active')",
                (user_id, challenge_id),
            )
            user_path_id = activate_challenge_path()
            conn.commit()
            return {
                "ok": True,
                "mode": "created",
                "enrollment_id": cur.lastrowid,
                "challenge_id": challenge_id,
                "path_id": path_id,
                "user_path_id": user_path_id,
            }, 200
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT id,status FROM enrollments WHERE user_id=? AND challenge_id=?",
                (user_id, challenge_id),
            ).fetchone()
            if row and row["status"] == "Left":
                conn.execute("UPDATE enrollments SET status='Active' WHERE id=?", (row["id"],))
                user_path_id = activate_challenge_path()
                conn.commit()
                return {
                    "ok": True,
                    "mode": "reactivated",
                    "enrollment_id": row["id"],
                    "challenge_id": challenge_id,
                    "path_id": path_id,
                    "user_path_id": user_path_id,
                }, 200
            user_path_id = activate_challenge_path()
            conn.commit()
            return {
                "ok": True,
                "mode": "existing",
                "enrollment_id": row["id"] if row else None,
                "challenge_id": challenge_id,
                "path_id": path_id,
                "user_path_id": user_path_id,
            }, 200
    finally:
        conn.close()


def get_enrollment_detail(user_id: int, enrollment_id: int):
    conn = get_db_connection()
    today = utc_today_iso()
    next_reset_at = (
        datetime.fromisoformat(today)
        .replace(tzinfo=timezone.utc)
        + timedelta(days=1)
    ).isoformat().replace("+00:00", "Z")
    try:
        row = conn.execute(
            """
            SELECT
                e.id AS enrollment_id,
                e.user_id AS user_id,
                e.challenge_id AS challenge_id,
                e.status AS status,
                e.joined_at AS joined_at,
                c.name AS challenge_name,
                c.description AS challenge_description,
                c.duration_days AS duration_days
            FROM enrollments e
            JOIN challenges c ON c.id = e.challenge_id
            WHERE e.id = ? AND e.user_id = ?
            LIMIT 1
            """,
            (enrollment_id, user_id),
        ).fetchone()

        if not row:
            return {"ok": False, "error": "enrollment_not_found"}, 404

        today_checked = (
            conn.execute(
                """
                SELECT 1
                FROM checkins
                WHERE enrollment_id = ?
                  AND date = ?
                  AND status = 'Done'
                  AND is_counted = 1
                LIMIT 1
                """,
                (enrollment_id, today),
            ).fetchone()
            is not None
        )

        total_checkins = conn.execute(
            """
            SELECT COUNT(*) AS n
            FROM checkins
            WHERE enrollment_id = ?
              AND status = 'Done'
              AND is_counted = 1
            """,
            (enrollment_id,),
        ).fetchone()["n"]

        dates = conn.execute(
            """
            SELECT date
            FROM checkins
            WHERE enrollment_id = ?
              AND status = 'Done'
              AND is_counted = 1
            GROUP BY date
            ORDER BY date DESC
            """,
            (enrollment_id,),
        ).fetchall()
        current_streak = calculate_current_streak([r["date"] for r in dates if r["date"]], today)

        logs = conn.execute(
            """
            SELECT id AS daily_log_id, date
            FROM checkins
            WHERE enrollment_id = ?
              AND status = 'Done'
              AND is_counted = 1
            ORDER BY date DESC, id DESC
            LIMIT 20
            """,
            (enrollment_id,),
        ).fetchall()

        duration_days = int(row["duration_days"] or 0)
        joined_at = row["joined_at"]

        start_date = None
        end_date = None
        remaining_days = None
        progress_percent = 0

        if joined_at and duration_days > 0:
            joined_date = datetime.fromisoformat(str(joined_at).replace("Z", "+00:00")).date()
            today_date = datetime.fromisoformat(today).date()

            start_date = joined_date.isoformat()
            end_date = (joined_date + timedelta(days=duration_days)).isoformat()

            days_elapsed = max(0, (today_date - joined_date).days)
            remaining_days = max(0, duration_days - days_elapsed)
            progress_percent = min(100, int((days_elapsed / duration_days) * 100))
        else:
            days_elapsed = 0

        mission_rows = conn.execute(
            """
            SELECT
                m.id,
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
                COALESCE(m.mission_intensity, 'main') AS mission_intensity,
                m.estimated_minutes,
                m.parent_mission_id,
                m.ringo_message,
                ml.status AS log_status,
                ml.reminder_at,
                ml.xp_earned
            FROM missions m
            LEFT JOIN mission_logs ml
              ON ml.mission_id = m.id
             AND ml.user_id = ?
             AND ml.enrollment_id = ?
             AND ml.date = ?
            WHERE m.challenge_id = ?
              AND m.status = 'Active'
            ORDER BY m.order_index ASC, m.id ASC
            """,
            (user_id, enrollment_id, today, row["challenge_id"]),
        ).fetchall()

        missions = []

        for mission in mission_rows:
            unlock_after_days = int(mission["unlock_after_days"] or 0)
            available_today = unlock_after_days <= days_elapsed
            missions.append({
                "mission_id": mission["id"],
                "key": mission["key"],
                "title": mission["title"],
                "description": mission["description"] or "",
                "mission_type": mission["mission_type"] or "daily",
                "difficulty": mission["difficulty"] or "easy",
                "is_core": bool(mission["is_core"]),
                "xp_reward": int(mission["xp_reward"] or 0),
                "order_index": int(mission["order_index"] or 0),
                "suggested_time": mission["suggested_time"] or "",
                "unlock_after_days": unlock_after_days,
                "mission_intensity": mission["mission_intensity"] or "main",
                "estimated_minutes": int(mission["estimated_minutes"]) if mission["estimated_minutes"] is not None else None,
                "parent_mission_id": mission["parent_mission_id"],
                "unlocks_in_days": max(0, unlock_after_days - days_elapsed),
                "available_today": available_today,
                "today_status": (mission["log_status"] or "pending") if available_today else "locked",
                "reminder_at": mission["reminder_at"],
                "xp_earned": int(mission["xp_earned"] or 0),
                "ringo_message": mission["ringo_message"] or "",
            })

        available_missions = [mission for mission in missions if mission["available_today"]]
        mission_summary = {
            "days_elapsed": int(days_elapsed),
            "today_missions_done": sum(1 for mission in available_missions if mission["today_status"] == "done"),
            "today_missions_total": len(available_missions),
            "future_missions_total": sum(1 for mission in missions if not mission["available_today"]),
        }

        return {
            "ok": True,
            "enrollment": {
                "enrollment_id": row["enrollment_id"],
                "name": row["challenge_name"],
                "status": row["status"],
                "challenge_id": row["challenge_id"],
                "joined_at": joined_at,
                "start_date": start_date,
                "end_date": end_date,
                "remaining_days": remaining_days,
                "progress_percent": progress_percent,
                "today_checked": bool(today_checked),
                "total_checkins": int(total_checkins),
                "today_date": today,
                "next_reset_at": next_reset_at,
                "reset_timezone": "UTC",
                "current_streak": int(current_streak),
                
            },
            "challenge": {
                "id": row["challenge_id"],
                "name": row["challenge_name"],
                "description": row["challenge_description"],
                "duration_days": duration_days,
            },
            "mission_summary": mission_summary,
            "missions": missions,
            "recent_logs": [{"daily_log_id": r["daily_log_id"], "date": r["date"]} for r in logs],
        }, 200
    finally:
        conn.close()

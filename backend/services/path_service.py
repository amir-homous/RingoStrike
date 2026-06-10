from datetime import datetime

from database import get_db_connection
from utils.date_utils import utc_today_iso


def _path_payload(row, user_path=None):
    return {
        "path_id": row["id"],
        "key": row["key"],
        "title": row["title"],
        "description": row["description"] or "",
        "icon": row["icon"] or "",
        "color": row["color"] or "",
        "sort_order": int(row["sort_order"] or 0),
        "status": row["status"] or "Active",
        "user_status": user_path["status"] if user_path else None,
        "current_stage": int(user_path["current_stage"] or 1) if user_path else None,
    }


def list_paths(user_id=None):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT *
            FROM paths
            WHERE status = 'Active'
            ORDER BY sort_order ASC, id ASC
            """
        ).fetchall()

        user_paths = {}

        if user_id is not None:
            user_rows = conn.execute(
                """
                SELECT path_id, status, current_stage
                FROM user_paths
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchall()
            user_paths = {row["path_id"]: row for row in user_rows}

        return {
            "ok": True,
            "items": [_path_payload(row, user_paths.get(row["id"])) for row in rows],
        }, 200
    finally:
        conn.close()


def _challenge_progress_map(conn, user_id, challenge_ids, today):
    if not user_id or not challenge_ids:
        return {}

    placeholders = ",".join("?" for _ in challenge_ids)
    rows = conn.execute(
        f"""
        SELECT
            e.challenge_id,
            e.id AS enrollment_id,
            e.status AS enrollment_status,
            e.joined_at,
            EXISTS (
                SELECT 1
                FROM checkins ci
                WHERE ci.enrollment_id = e.id
                  AND ci.date = ?
                  AND ci.status = 'Done'
                  AND ci.is_counted = 1
            ) AS today_checked,
            (
                SELECT COUNT(*)
                FROM checkins ci
                WHERE ci.enrollment_id = e.id
                  AND ci.status = 'Done'
                  AND ci.is_counted = 1
            ) AS total_checkins
        FROM enrollments e
        WHERE e.user_id = ?
          AND e.challenge_id IN ({placeholders})
        """,
        (today, user_id, *challenge_ids),
    ).fetchall()

    return {
        row["challenge_id"]: {
            "is_joined": row["enrollment_status"] == "Active",
            "enrollment_id": row["enrollment_id"],
            "enrollment_status": row["enrollment_status"],
            "joined_at": row["joined_at"],
            "today_checked": bool(row["today_checked"]),
            "total_checkins": int(row["total_checkins"] or 0),
        }
        for row in rows
    }


def _days_since_join(joined_at, today):
    if not joined_at:
        return 0

    try:
        joined_date = datetime.fromisoformat(
            str(joined_at).replace("Z", "+00:00")
        ).date()
        today_date = datetime.fromisoformat(today).date()
    except ValueError:
        return 0

    return max(0, (today_date - joined_date).days)


def _mission_status_map(conn, user_id, mission_ids, today):
    if not user_id or not mission_ids:
        return {}

    placeholders = ",".join("?" for _ in mission_ids)
    rows = conn.execute(
        f"""
        SELECT mission_id, status, reminder_at, xp_earned
        FROM mission_logs
        WHERE user_id = ?
          AND date = ?
          AND mission_id IN ({placeholders})
        """,
        (user_id, today, *mission_ids),
    ).fetchall()

    return {
        row["mission_id"]: {
            "status": row["status"] or "pending",
            "reminder_at": row["reminder_at"],
            "xp_earned": int(row["xp_earned"] or 0),
        }
        for row in rows
    }


def get_path_challenges(path_id, user_id=None):
    today = utc_today_iso()
    conn = get_db_connection()
    try:
        path = conn.execute(
            "SELECT * FROM paths WHERE id = ? AND status = 'Active'",
            (path_id,),
        ).fetchone()

        if not path:
            return {"ok": False, "error": "path_not_found"}, 404

        rows = conn.execute(
            """
            SELECT
                id,
                name,
                description,
                visibility,
                status,
                duration_days,
                goal_type,
                tags,
                difficulty,
                stage,
                estimated_days,
                ringo_intro
            FROM challenges
            WHERE path_id = ? AND status = 'Active'
            ORDER BY stage ASC, id ASC
            """,
            (path_id,),
        ).fetchall()

        mission_rows = conn.execute(
            """
            SELECT
                id,
                challenge_id,
                key,
                title,
                description,
                mission_type,
                difficulty,
                is_core,
                xp_reward,
                order_index,
                suggested_time,
                unlock_after_days,
                ringo_message,
                status
            FROM missions
            WHERE challenge_id IN (
                SELECT id FROM challenges WHERE path_id = ? AND status = 'Active'
            )
              AND status = 'Active'
            ORDER BY challenge_id ASC, order_index ASC, id ASC
            """,
            (path_id,),
        ).fetchall()
        challenge_ids = [row["id"] for row in rows]
        progress_by_challenge = _challenge_progress_map(conn, user_id, challenge_ids, today)
        mission_ids = [row["id"] for row in mission_rows]
        mission_statuses = _mission_status_map(conn, user_id, mission_ids, today)
        missions_by_challenge = {}

        for mission in mission_rows:
            challenge_progress = progress_by_challenge.get(mission["challenge_id"], {})
            days_elapsed = _days_since_join(challenge_progress.get("joined_at"), today)
            unlock_after_days = int(mission["unlock_after_days"] or 0)
            available_today = bool(challenge_progress.get("is_joined")) and unlock_after_days <= days_elapsed
            progress = mission_statuses.get(mission["id"], {})
            status = progress.get("status", "pending") if available_today else "locked"

            missions_by_challenge.setdefault(mission["challenge_id"], []).append({
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
                "unlocks_in_days": max(0, unlock_after_days - days_elapsed),
                "available_today": available_today,
                "ringo_message": mission["ringo_message"] or "",
                "today_status": status,
                "reminder_at": progress.get("reminder_at"),
                "xp_earned": progress.get("xp_earned", 0),
            })

        items = []

        for row in rows:
            missions = missions_by_challenge.get(row["id"], [])
            progress = progress_by_challenge.get(row["id"], {})
            today_missions_total = sum(1 for mission in missions if mission.get("available_today"))
            today_missions_done = sum(
                1 for mission in missions
                if mission.get("available_today") and mission.get("today_status") == "done"
            )

            items.append({
                "challenge_id": row["id"],
                "name": row["name"],
                "description": row["description"] or "",
                "visibility": row["visibility"] or "Public",
                "status": row["status"] or "Active",
                "duration_days": row["duration_days"] or row["estimated_days"] or 0,
                "goal_type": row["goal_type"] or "",
                "tags": row["tags"].split(",") if row["tags"] else [],
                "difficulty": row["difficulty"] or "beginner",
                "stage": int(row["stage"] or 1),
                "estimated_days": row["estimated_days"] or row["duration_days"] or 0,
                "ringo_intro": row["ringo_intro"] or "",
                "is_joined": bool(progress.get("is_joined")),
                "enrollment_id": progress.get("enrollment_id"),
                "enrollment_status": progress.get("enrollment_status"),
                "today_checked": bool(progress.get("today_checked")),
                "total_checkins": int(progress.get("total_checkins") or 0),
                "today_missions_done": today_missions_done,
                "today_missions_total": today_missions_total,
                "missions": missions,
            })

        return {
            "ok": True,
            "date": today,
            "path": _path_payload(path),
            "summary": {
                "joined_challenges": sum(1 for item in items if item["is_joined"]),
                "today_checked_challenges": sum(1 for item in items if item["today_checked"]),
                "today_missions_done": sum(item["today_missions_done"] for item in items),
                "today_missions_total": sum(
                    item["today_missions_total"] for item in items if item["is_joined"]
                ),
            },
            "items": items,
        }, 200
    finally:
        conn.close()


def start_user_path(user_id, path_id):
    conn = get_db_connection()
    try:
        path = conn.execute(
            "SELECT * FROM paths WHERE id = ? AND status = 'Active'",
            (path_id,),
        ).fetchone()

        if not path:
            return {"ok": False, "error": "path_not_found"}, 404

        existing = conn.execute(
            """
            SELECT id, status, current_stage
            FROM user_paths
            WHERE user_id = ? AND path_id = ?
            """,
            (user_id, path_id),
        ).fetchone()

        if existing:
            mode = "existing" if existing["status"] == "Active" else "reactivated"
            conn.execute(
                """
                UPDATE user_paths
                SET status = 'Active',
                    completed_at = NULL,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (existing["id"],),
            )
            user_path_id = existing["id"]
        else:
            mode = "created"
            cur = conn.execute(
                """
                INSERT INTO user_paths (user_id, path_id, status, current_stage)
                VALUES (?, ?, 'Active', 1)
                """,
                (user_id, path_id),
            )
            user_path_id = cur.lastrowid

        conn.commit()

        return {
            "ok": True,
            "mode": mode,
            "user_path_id": user_path_id,
            "path": _path_payload(path, {"status": "Active", "current_stage": 1}),
        }, 200
    finally:
        conn.close()

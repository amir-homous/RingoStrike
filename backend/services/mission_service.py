from datetime import datetime, timezone

from database import get_db_connection
from services.enrollment_service import checkin
from services.ringo_decision_service import decide_ringo_state
from utils.date_utils import ringo_day_metadata, utc_iso_z, utc_today_iso


ALLOWED_SKIP_REASONS = {
    "too_tired",
    "no_time",
    "too_hard",
    "not_relevant",
    "disliked",
    "other",
}


def _row_status(row):
    return row["log_status"] or "pending"


def _mission_log_timestamp(value):
    if not value:
        return None

    raw_value = str(value).strip()
    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(raw_value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)

    return utc_iso_z(parsed)


def _mission_payload(row):
    status = _row_status(row)
    status_updated_at = _mission_log_timestamp(row["log_updated_at"])

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
        "mission_intensity": row["mission_intensity"] or "main",
        "estimated_minutes": int(row["estimated_minutes"]) if row["estimated_minutes"] is not None else None,
        "parent_mission_id": row["parent_mission_id"],
        "ringo_message": row["ringo_message"] or "",
        "status": status,
        "reminder_at": row["reminder_at"],
        "done_at": status_updated_at if status == "done" else None,
        "skipped_at": status_updated_at if status == "skipped" else None,
        "reminder_set_at": status_updated_at if status == "remind_later" else None,
        "status_updated_at": status_updated_at,
        "skip_reason": row["skip_reason"],
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
            COALESCE(m.mission_intensity, 'main') AS mission_intensity,
            m.estimated_minutes,
            m.parent_mission_id,
            m.ringo_message,
            c.id AS challenge_id,
            c.name AS challenge_name,
            c.path_id,
            p.title AS path_title,
            e.id AS enrollment_id,
            ml.status AS log_status,
            ml.reminder_at,
            ml.skip_reason,
            ml.xp_earned,
            ml.updated_at AS log_updated_at
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
            m.description,
            m.xp_reward,
            m.challenge_id,
            c.name AS challenge_name,
            c.path_id,
            p.title AS path_title,
            e.id AS enrollment_id
        FROM missions m
        JOIN enrollments e
          ON e.challenge_id = m.challenge_id
         AND e.user_id = ?
         AND e.status = 'Active'
        JOIN challenges c ON c.id = m.challenge_id
        LEFT JOIN paths p ON p.id = c.path_id
        WHERE m.id = ?
          AND m.status = 'Active'
          AND c.status = 'Active'
        LIMIT 1
        """,
        (user_id, mission_id),
    ).fetchone()


def _same_mission_id(a, b):
    if a is None or b is None:
        return False

    return str(a) == str(b)


def _completed_mission_from_today_payload(missions, mission_id):
    return next(
        (
            mission for mission in missions
            if _same_mission_id(mission.get("mission_id"), mission_id)
            and mission.get("status") == "done"
        ),
        None,
    )


def _mission_satisfies_today(missions, mission_id):
    completed = _completed_mission_from_today_payload(missions, mission_id)
    if not completed:
        return False

    mission_intensity = completed.get("mission_intensity") or "main"
    if mission_intensity == "main":
        return True

    if mission_intensity != "tiny":
        return False

    parent_id = completed.get("parent_mission_id")
    return any(
        (mission.get("mission_intensity") or "main") == "main"
        and _same_mission_id(mission.get("mission_id"), parent_id)
        for mission in missions
    )


def _completed_linked_tiny_mission(missions):
    main_mission_ids = {
        mission.get("mission_id")
        for mission in missions
        if (mission.get("mission_intensity") or "main") == "main"
    }

    return next(
        (
            mission for mission in missions
            if mission.get("status") == "done"
            and mission.get("mission_intensity") == "tiny"
            and any(
                _same_mission_id(mission.get("parent_mission_id"), main_id)
                for main_id in main_mission_ids
            )
        ),
        None,
    )


def _completed_main_mission(missions):
    return next(
        (
            mission for mission in missions
            if mission.get("status") == "done"
            and (mission.get("mission_intensity") or "main") == "main"
        ),
        None,
    )


def _today_satisfied_by_missions(missions):
    return bool(
        _completed_linked_tiny_mission(missions)
        or _completed_main_mission(missions)
    )


def _reward_step(step_type, title, *, text="", value=None, amount=None, mood=None):
    step = {
        "type": step_type,
        "title": title,
    }

    if text:
        step["text"] = text

    if value is not None:
        step["value"] = value

    if amount is not None:
        step["amount"] = amount

    if mood:
        step["mood"] = mood

    return step


def _build_reward_sequence(payload, today_missions, *, was_today_saved=False):
    mission = payload.get("mission") or {}
    mission_id = mission.get("mission_id")
    mission_title = mission.get("title") or "Mission"
    xp_earned = int(mission.get("xp_earned") or 0)
    already_checked = bool((payload.get("checkin") or {}).get("already_checked"))
    today_saved_by_current = _mission_satisfies_today(today_missions, mission_id)

    steps = [
        _reward_step(
            "ringo_message",
            "Nice work.",
            text=(
                "You added another small win to today."
                if already_checked
                else "You did the small step. That counts."
            ),
            mood="proud",
        ),
        _reward_step(
            "mission_completed",
            mission_title,
            text="This mission is marked done.",
        ),
    ]

    if xp_earned > 0:
        steps.append(_reward_step(
            "xp_earned",
            "XP earned",
            value=f"+{xp_earned} XP",
            amount=xp_earned,
        ))

    if today_saved_by_current and not was_today_saved:
        steps.append(_reward_step(
            "today_saved",
            "Today is safe.",
            text="You did enough for today. Anything else is optional.",
            mood="celebrating",
        ))

    if was_today_saved:
        steps.append(_reward_step(
            "ringo_message",
            "Bonus momentum.",
            text="Today was already safe. This was optional extra progress.",
            mood="happy",
        ))

    steps.append(_reward_step(
        "next_choice",
        "Choose your pace.",
        text="You can stop here, or continue only if you have energy.",
    ))

    return steps


def _upsert_mission_log(
    user_id,
    mission_id,
    status,
    *,
    reminder_at=None,
    notes=None,
    skip_reason=None,
):
    today = utc_today_iso()
    conn = get_db_connection()
    try:
        mission = _find_user_mission_context(conn, user_id, mission_id)

        if not mission:
            return {"ok": False, "error": "mission_not_found"}, 404

        xp_earned = int(mission["xp_reward"] or 0) if status == "done" else 0
        event_at = utc_iso_z(datetime.now(timezone.utc))
        secured_at = datetime.now(timezone.utc).isoformat() if status == "done" else None
        done_before_you = 0

        if status == "done":
            done_before_you = int(conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM mission_logs
                WHERE mission_id = ?
                  AND date = ?
                  AND status = 'done'
                  AND user_id != ?
                """,
                (mission_id, today, user_id),
            ).fetchone()["n"] or 0)

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
                skip_reason,
                notes,
                xp_earned,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, mission_id, date) DO UPDATE SET
                status = excluded.status,
                reminder_at = excluded.reminder_at,
                skip_reason = excluded.skip_reason,
                notes = COALESCE(excluded.notes, mission_logs.notes),
                xp_earned = excluded.xp_earned,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                mission["enrollment_id"],
                mission["challenge_id"],
                mission_id,
                today,
                status,
                reminder_at,
                skip_reason,
                notes,
                xp_earned,
                event_at,
            ),
        )
        conn.commit()

        return {
            "ok": True,
            "mission": {
                "mission_id": mission_id,
                "title": mission["title"],
                "description": mission["description"] or "",
                "status": status,
                "date": today,
                "secured_at": secured_at,
                "done_at": event_at if status == "done" else None,
                "skipped_at": event_at if status == "skipped" else None,
                "reminder_set_at": event_at if status == "remind_later" else None,
                "status_updated_at": event_at,
                "xp_earned": xp_earned,
                "enrollment_id": mission["enrollment_id"],
                "challenge_id": mission["challenge_id"],
                "challenge_name": mission["challenge_name"],
                "path_id": mission["path_id"],
                "path_title": mission["path_title"],
                "reminder_at": reminder_at,
                "skip_reason": skip_reason,
                "today_done_before_you": done_before_you,
                "today_done_count": done_before_you + 1 if status == "done" else None,
            },
        }, 200
    finally:
        conn.close()


def mark_mission_done(user_id, mission_id):
    before_missions_payload, _ = get_today_missions(user_id)
    before_missions = (
        before_missions_payload.get("missions")
        if before_missions_payload.get("ok")
        else []
    )
    was_today_saved = _today_satisfied_by_missions(before_missions or [])

    payload, code = _upsert_mission_log(user_id, mission_id, "done")

    if not payload.get("ok"):
        return payload, code

    checkin_payload, checkin_code = checkin(
        user_id,
        payload["mission"]["enrollment_id"],
    )

    payload["checkin"] = checkin_payload
    payload["checkin_status_code"] = checkin_code
    today_missions_payload, _ = get_today_missions(user_id)
    today_missions = today_missions_payload.get("missions") if today_missions_payload.get("ok") else []
    payload["reward_sequence"] = _build_reward_sequence(
        payload,
        today_missions or [],
        was_today_saved=was_today_saved,
    )

    return payload, code


def remind_mission_later(user_id, mission_id, reminder_at):
    value = str(reminder_at or "").strip()

    if not value:
        return {"ok": False, "error": "reminder_at_required"}, 400

    if len(value) > 80:
        return {"ok": False, "error": "reminder_at_too_long"}, 400

    try:
        parsed_reminder_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return {"ok": False, "error": "invalid_reminder_at"}, 400

    if parsed_reminder_at.tzinfo is None:
        parsed_reminder_at = parsed_reminder_at.replace(tzinfo=timezone.utc)
    else:
        parsed_reminder_at = parsed_reminder_at.astimezone(timezone.utc)

    next_reset_at = datetime.fromisoformat(
        ringo_day_metadata()["next_reset_at"].replace("Z", "+00:00"),
    )
    if parsed_reminder_at >= next_reset_at:
        return {"ok": False, "error": "reminder_after_next_reset"}, 400

    return _upsert_mission_log(user_id, mission_id, "remind_later", reminder_at=value)


def _normalize_skip_reason(reason):
    if reason is None:
        return None, None

    if not isinstance(reason, str):
        return None, "invalid_skip_reason"

    value = reason.strip()
    if not value:
        return None, None

    if len(value) > 40:
        return None, "skip_reason_too_long"

    if value not in ALLOWED_SKIP_REASONS:
        return None, "unsupported_skip_reason"

    return value, None


def skip_mission(user_id, mission_id, reason=None):
    skip_reason, error = _normalize_skip_reason(reason)
    if error:
        return {"ok": False, "error": error}, 400

    return _upsert_mission_log(
        user_id,
        mission_id,
        "skipped",
        skip_reason=skip_reason,
    )

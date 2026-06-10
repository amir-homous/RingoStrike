from sqlite3 import DatabaseError

from database import get_db_connection
from services.mission_service import get_today_missions
from services.stats_service import build_user_stats_payload
from utils.date_utils import utc_today_iso


FALLBACK_RINGO = {
    "user_state": "today_not_started",
    "mood": "calm",
    "tone": "warm_no_shame",
    "message": "One small step is enough for today.",
    "sprite_key": "idle",
}

STATE_MOODS = {
    "new_user": "welcome",
    "no_active_path": "welcome",
    "path_selected_no_challenge": "gentle",
    "today_not_started": "focused",
    "today_in_progress": "encouraging",
    "today_completed": "celebrating",
    "today_reminded": "calm",
    "today_skipped": "gentle",
    "returning_after_absence": "concerned",
    "streak_risk": "concerned",
    "no_mission_today": "resting",
}

STATE_SPRITES = {
    "new_user": "welcome",
    "no_active_path": "welcome",
    "path_selected_no_challenge": "explaining",
    "today_not_started": "focus",
    "today_in_progress": "encouraging",
    "today_completed": "celebration",
    "today_reminded": "thinking",
    "today_skipped": "concerned",
    "returning_after_absence": "concerned",
    "streak_risk": "concerned",
    "no_mission_today": "sleeping",
}

REWARD_SEQUENCE_BY_STATE = {
    "today_completed": "celebration",
    "returning_after_absence": "comeback",
    "streak_risk": "streak_saved",
}


def _count_active_paths(conn, user_id):
    row = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM user_paths
        WHERE user_id = ? AND status = 'Active'
        """,
        (user_id,),
    ).fetchone()
    return int(row["count"] or 0) if row else 0


def _count_active_enrollments(conn, user_id):
    row = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM enrollments
        WHERE user_id = ? AND status = 'Active'
        """,
        (user_id,),
    ).fetchone()
    return int(row["count"] or 0) if row else 0


def _read_context_counts(user_id):
    conn = get_db_connection()
    try:
        return {
            "active_paths": _count_active_paths(conn, user_id),
            "active_enrollments": _count_active_enrollments(conn, user_id),
        }
    finally:
        conn.close()


def _progress(stats):
    return {
        "today_saved": False,
        "current_streak": int(stats.get("current_streak") or 0),
        "total_checkins": int(stats.get("total_checkins") or 0),
    }


def _mission_status_counts(missions):
    return {
        "done": sum(1 for mission in missions if mission.get("status") == "done"),
        "pending": sum(1 for mission in missions if mission.get("status") == "pending"),
        "remind_later": sum(1 for mission in missions if mission.get("status") == "remind_later"),
        "skipped": sum(1 for mission in missions if mission.get("status") == "skipped"),
    }


def _select_mission(missions):
    for status in ("pending", "remind_later", "skipped"):
        mission = next((item for item in missions if item.get("status") == status), None)
        if mission:
            return mission

    return missions[0] if missions else None


def _mission_payload(mission, mission_intensity):
    if not mission:
        return None

    return {
        "mission_id": mission.get("mission_id"),
        "key": mission.get("key"),
        "title": mission.get("title"),
        "description": mission.get("description") or "",
        "mission_intensity": mission_intensity,
        "estimated_minutes": None,
        "xp_reward": int(mission.get("xp_reward") or 0),
        "status": mission.get("status") or "pending",
        "challenge_id": mission.get("challenge_id"),
        "challenge_name": mission.get("challenge_name"),
        "enrollment_id": mission.get("enrollment_id"),
        "path_id": mission.get("path_id"),
        "path_title": mission.get("path_title"),
    }


def _action(action_type, label, mission=None):
    payload = {
        "type": action_type,
        "label": label,
    }

    if mission and mission.get("mission_id") is not None:
        payload["mission_id"] = mission.get("mission_id")

    return payload


def _actions_for_state(user_state, mission):
    if user_state in {"new_user", "no_active_path"}:
        return [_action("start", "Choose a path")]

    if user_state == "path_selected_no_challenge":
        return [_action("start", "Find a challenge")]

    if not mission:
        return [_action("start", "View paths")]

    if user_state == "today_completed":
        return []

    actions = [_action("start", "Start", mission)]

    if user_state != "today_reminded":
        actions.append(_action("remind_later", "Remind me later", mission))

    actions.append(_action("make_smaller", "Make it smaller", mission))
    actions.append(_action("too_tired", "I'm too tired", mission))
    actions.append(_action("skip_today", "Skip today", mission))

    return actions


def _map_legacy_state(legacy_state, stats, context, missions):
    total_checkins = int(stats.get("total_checkins") or 0)
    current_streak = int(stats.get("current_streak") or 0)

    if context["active_paths"] <= 0:
        return "new_user" if total_checkins <= 0 else "no_active_path"

    if context["active_enrollments"] <= 0:
        return "path_selected_no_challenge"

    if not missions:
        return "no_mission_today"

    counts = _mission_status_counts(missions)
    if counts["done"] == len(missions):
        return "today_completed"

    if total_checkins > 0 and current_streak == 0:
        return "returning_after_absence"

    if total_checkins > 0 and current_streak <= 1:
        return "streak_risk"

    state_map = {
        "today_in_progress": "today_in_progress",
        "today_reminded": "today_reminded",
        "today_skipped": "today_skipped",
        "no_mission_today": "no_mission_today",
        "today_completed": "today_completed",
        "today_not_started": "today_not_started",
    }
    return state_map.get(legacy_state, "today_not_started")


def _mission_intensity(user_state, selected_mission):
    if not selected_mission:
        return None

    if user_state in {"returning_after_absence", "streak_risk"}:
        return "tiny"

    if selected_mission.get("mission_type") == "bonus" or not selected_mission.get("is_core", True):
        return "bonus"

    return "main"


def _message_for_state(user_state, mission):
    mission_title = (mission or {}).get("title") or "one small step"

    messages = {
        "new_user": "Welcome. Pick one path and I will keep today's first step small.",
        "no_active_path": "Let's choose a path again. No rush, just one direction for today.",
        "path_selected_no_challenge": "Your path is ready. Start one small challenge so I can guide today's mission.",
        "today_not_started": f"Today's mission is ready: {mission_title}. One clear step is enough.",
        "today_in_progress": f"Nice. Keep going gently with {mission_title}.",
        "today_completed": "Today is safe. You did enough for the day.",
        "today_reminded": f"Okay. {mission_title} is saved for later, and the day is still yours.",
        "today_skipped": f"That's okay. {mission_title} can wait; no shame today.",
        "returning_after_absence": f"I'm glad you're back. Start softly with {mission_title}.",
        "streak_risk": f"Let's protect the rhythm with {mission_title}. Small is enough.",
        "no_mission_today": "No mission is ready right now. You can still use your usual check-in flow.",
    }
    return messages.get(user_state, FALLBACK_RINGO["message"])


def _ringo_payload(user_state, mission):
    return {
        "user_state": user_state,
        "mood": STATE_MOODS.get(user_state, FALLBACK_RINGO["mood"]),
        "tone": "warm_no_shame",
        "message": _message_for_state(user_state, mission),
        "sprite_key": STATE_SPRITES.get(user_state, FALLBACK_RINGO["sprite_key"]),
    }


def _reward_sequence(user_state):
    return {
        "type": REWARD_SEQUENCE_BY_STATE.get(user_state, "standard"),
        "available": user_state != "no_mission_today",
        "placeholder": True,
    }


def _fallback_payload(reason, stats=None):
    stats = stats or {}
    return {
        "ok": True,
        "date": utc_today_iso(),
        "ringo": dict(FALLBACK_RINGO),
        "mission": None,
        "actions": [_action("start", "View paths")],
        "progress": _progress(stats),
        "reward_sequence": {
            "type": "none",
            "available": False,
            "placeholder": True,
        },
        "fallback": {
            "used": True,
            "reason": reason,
        },
    }


def get_today_ringo_guidance(user_id):
    stats_payload, stats_code = build_user_stats_payload(user_id)
    if not stats_payload.get("ok"):
        if stats_code == 404:
            return stats_payload, stats_code
        return _fallback_payload(stats_payload.get("error") or "stats_unavailable"), 200

    stats = stats_payload.get("stats") or {}

    try:
        context = _read_context_counts(user_id)
    except DatabaseError:
        return _fallback_payload("context_unavailable", stats), 200

    try:
        missions_payload, missions_code = get_today_missions(user_id)
    except DatabaseError:
        return _fallback_payload("missions_unavailable", stats), 200

    if not missions_payload.get("ok"):
        if missions_code == 404:
            return missions_payload, missions_code
        return _fallback_payload(missions_payload.get("error") or "missions_unavailable", stats), 200

    missions = missions_payload.get("missions") or []
    legacy_state = (missions_payload.get("ringo") or {}).get("state")
    user_state = _map_legacy_state(legacy_state, stats, context, missions)
    selected_mission = _select_mission(missions)
    mission_intensity = _mission_intensity(user_state, selected_mission)
    progress = _progress(stats)
    progress["today_saved"] = user_state == "today_completed"

    return {
        "ok": True,
        "date": missions_payload.get("date") or utc_today_iso(),
        "ringo": _ringo_payload(user_state, selected_mission),
        "mission": _mission_payload(selected_mission, mission_intensity),
        "actions": _actions_for_state(user_state, selected_mission),
        "progress": progress,
        "reward_sequence": _reward_sequence(user_state),
        "fallback": {
            "used": False,
            "reason": None,
        },
    }, 200

from datetime import datetime, timezone


VALID_SPRITES = {
    "idle",
    "welcome",
    "talking",
    "explaining",
    "thinking",
    "encouraging",
    "warning",
    "concerned",
    "happy",
    "celebration",
    "achievement",
    "proud",
    "sad",
    "sleeping",
    "focus",
    "victory",
}


def _action(label, kind, to=None, mission_id=None):
    payload = {
        "label": label,
        "type": kind,
    }

    if to:
        payload["to"] = to

    if mission_id is not None:
        payload["mission_id"] = mission_id

    return payload


def _mission_label(prefix, mission):
    title = str(mission.get("title") or "").strip()

    if not title:
        return prefix

    return f"{prefix}: {title}"


def _same_mission_id(a, b):
    if a is None or b is None:
        return False

    return str(a) == str(b)


def _mission_intensity_value(mission):
    return mission.get("mission_intensity") or "main"


def _mission_family_key(mission):
    if not mission:
        return ""

    intensity = _mission_intensity_value(mission)
    if intensity == "tiny" and mission.get("parent_mission_id") is not None:
        return str(mission.get("parent_mission_id"))

    return str(mission.get("mission_id") or "")


def _completed_satisfying_mission(missions):
    main_mission_ids = {
        mission.get("mission_id")
        for mission in missions
        if (mission.get("mission_intensity") or "main") == "main"
    }

    linked_tiny = next(
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
    if linked_tiny:
        return linked_tiny

    return next(
        (
            mission for mission in missions
            if mission.get("status") == "done"
            and (mission.get("mission_intensity") or "main") == "main"
        ),
        None,
    )


def _parse_reminder_at(value):
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _due_reminder_mission(deferred):
    now = datetime.now(timezone.utc)
    due = [
        mission for mission in deferred
        if (_parse_reminder_at(mission.get("reminder_at")) or datetime.max.replace(tzinfo=timezone.utc)) <= now
    ]

    if not due:
        return None

    return sorted(
        due,
        key=lambda mission: (
            _parse_reminder_at(mission.get("reminder_at")) or datetime.max.replace(tzinfo=timezone.utc),
            int(mission.get("order_index") or 0),
            int(mission.get("mission_id") or 0),
        ),
    )[0]


def _is_due_reminder(mission, now=None):
    now = now or datetime.now(timezone.utc)
    reminder_at = _parse_reminder_at(mission.get("reminder_at"))

    return bool(reminder_at and reminder_at <= now)


def _family_done_keys(missions):
    main_mission_keys = {
        _mission_family_key(mission)
        for mission in missions
        if _mission_intensity_value(mission) == "main"
    }

    return {
        _mission_family_key(mission)
        for mission in missions
        if mission.get("status") == "done"
        and _mission_intensity_value(mission) in {"main", "tiny"}
        and _mission_family_key(mission) in main_mission_keys
    }


def _main_done_family_keys(missions):
    return {
        _mission_family_key(mission)
        for mission in missions
        if mission.get("status") == "done"
        and _mission_intensity_value(mission) == "main"
    }


def _family_deferred_keys(missions):
    now = datetime.now(timezone.utc)
    return {
        _mission_family_key(mission)
        for mission in missions
        if mission.get("status") == "remind_later"
        and _mission_intensity_value(mission) in {"main", "tiny"}
        and not _is_due_reminder(mission, now)
    }


def _active_deferred_missions(missions, done_keys):
    return [
        mission
        for mission in missions
        if mission.get("status") == "remind_later"
        and not (
            _mission_intensity_value(mission) in {"main", "tiny"}
            and _mission_family_key(mission) in done_keys
        )
    ]


def _preferred_pending_mission(pending, preferred_intensity="main"):
    return next(
        (
            mission for mission in pending
            if (mission.get("mission_intensity") or "main") == preferred_intensity
        ),
        None,
    ) or (pending[0] if pending else None)


def _decision(state, sprite, message, primary_action=None, secondary_action=None):
    sprite_key = sprite if sprite in VALID_SPRITES else "idle"

    return {
        "state": state,
        "sprite": sprite_key,
        "sprite_key": sprite_key,
        "message": message,
        "primary_action": primary_action,
        "secondary_action": secondary_action,
    }


def decide_ringo_state(
    *,
    has_active_path=False,
    has_active_enrollment=False,
    missions=None,
    checkins_total=0,
    current_streak=0,
):
    missions = missions or []

    if not has_active_path:
        return _decision(
            "new_user_no_path",
            "welcome",
            "Choose one growth path first. I will keep today's mission small and clear.",
            _action("Choose a path", "route", "/challenges"),
            _action("View dashboard", "route", "/dashboard"),
        )

    if has_active_path and not has_active_enrollment:
        return _decision(
            "path_selected_no_challenge",
            "explaining",
            "Your path is selected. Start one related challenge so I can guide today's mission.",
            _action("Find a challenge", "route", "/challenges"),
            _action("View paths", "route", "/dashboard"),
        )

    if not missions:
        return _decision(
            "no_mission_today",
            "thinking",
            "No mission is ready for today yet. Your existing challenge check-in still works as usual.",
            _action("Go to challenges", "route", "/challenges"),
            _action("View dashboard", "route", "/dashboard"),
        )

    done_count = sum(1 for mission in missions if mission.get("status") == "done")
    done_family_keys = _family_done_keys(missions)
    main_done_family_keys = _main_done_family_keys(missions)
    deferred_family_keys = _family_deferred_keys(missions)
    pending = [
        mission for mission in missions
        if mission.get("status") == "pending"
        and (
            (
                _mission_intensity_value(mission) in {"main", "tiny"}
                and _mission_family_key(mission) not in done_family_keys
                and _mission_family_key(mission) not in deferred_family_keys
            )
            or (
                _mission_intensity_value(mission) == "bonus"
                and (
                    mission.get("parent_mission_id") is None
                    or str(mission.get("parent_mission_id")) in main_done_family_keys
                )
            )
        )
    ]
    deferred = _active_deferred_missions(missions, done_family_keys)
    skipped = [mission for mission in missions if mission.get("status") == "skipped"]
    due_reminder = _due_reminder_mission(deferred)

    if _completed_satisfying_mission(missions) and not pending and not deferred and not skipped:
        return _decision(
            "today_completed",
            "celebration",
            "Today is secured. You can stop here. If you want more momentum, preview the next path, but you do not need to do more today.",
            _action("Done for today", "dismiss"),
            _action("Preview next path", "route", "/paths"),
        )

    if not pending and deferred:
        next_mission = deferred[0]
        return _decision(
            "today_reminded",
            "thinking",
            f"{next_mission.get('title') or 'Your mission'} is saved for later today. You can leave it paused, complete it now, or explore another path without pressure.",
            _action(_mission_label("Do it now", next_mission), "mission", mission_id=next_mission.get("mission_id")),
            _action("Explore another path", "route", "/paths"),
        )

    if not pending and skipped:
        next_mission = skipped[0]
        return _decision(
            "today_skipped",
            "concerned",
            f"{next_mission.get('title') or 'Your mission'} was skipped. Today is not secured yet, but you can still complete it if you want.",
            _action(_mission_label("Complete anyway", next_mission), "mission", mission_id=next_mission.get("mission_id")),
            _action("Explore another path", "route", "/paths"),
        )

    if done_count > 0:
        next_mission = due_reminder or (pending[0] if pending else deferred[0] if deferred else missions[0])
        return _decision(
            "today_in_progress",
            "encouraging",
            f"Nice. Next mission: {next_mission.get('title') or 'one small action'}. Finish it when you are ready.",
            _action(_mission_label("Finish", next_mission), "mission", mission_id=next_mission.get("mission_id")),
            _action("Remind me later", "mission_reminder", mission_id=next_mission.get("mission_id")),
        )

    if checkins_total > 0 and current_streak == 0:
        next_mission = due_reminder or _preferred_pending_mission(pending, "tiny") or missions[0]
        return _decision(
            "returning_after_break",
            "concerned",
            f"You are back after a break. Start gently with {next_mission.get('title') or 'one small mission'} and rebuild the rhythm.",
            _action(_mission_label("Start", next_mission), "mission", mission_id=next_mission.get("mission_id")),
            _action("Choose another path", "route", "/challenges"),
        )

    if checkins_total > 0 and current_streak <= 1:
        next_mission = due_reminder or _preferred_pending_mission(pending, "tiny") or missions[0]
        return _decision(
            "streak_at_risk",
            "warning",
            f"Your rhythm is still young. Protect it with {next_mission.get('title') or 'one small mission'} today.",
            _action(_mission_label("Secure", next_mission), "mission", mission_id=next_mission.get("mission_id")),
            _action("Remind me later", "mission_reminder", mission_id=next_mission.get("mission_id")),
        )

    next_mission = due_reminder or _preferred_pending_mission(pending, "main") or missions[0]
    reminder_context = (
        "I saved that reminder. While we wait, "
        if deferred and pending and not due_reminder
        else ""
    )
    return _decision(
        "today_not_started",
        "focus",
        f"{reminder_context}Today's mission is ready: {next_mission.get('title') or 'one small action'}. Complete it, then mark it done.",
        _action(_mission_label("Start", next_mission), "mission", mission_id=next_mission.get("mission_id")),
        _action("View path details", "route", f"/enrollment/{next_mission.get('enrollment_id')}"),
    )

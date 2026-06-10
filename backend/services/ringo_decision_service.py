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
    pending = [mission for mission in missions if mission.get("status") == "pending"]
    deferred = [mission for mission in missions if mission.get("status") == "remind_later"]
    skipped = [mission for mission in missions if mission.get("status") == "skipped"]

    if done_count == len(missions):
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
        next_mission = pending[0] if pending else deferred[0] if deferred else missions[0]
        return _decision(
            "today_in_progress",
            "encouraging",
            f"Nice. Next mission: {next_mission.get('title') or 'one small action'}. Finish it when you are ready.",
            _action(_mission_label("Finish", next_mission), "mission", mission_id=next_mission.get("mission_id")),
            _action("Remind me later", "mission_reminder", mission_id=next_mission.get("mission_id")),
        )

    if checkins_total > 0 and current_streak == 0:
        return _decision(
            "returning_after_break",
            "concerned",
            f"You are back after a break. Start gently with {missions[0].get('title') or 'one small mission'} and rebuild the rhythm.",
            _action(_mission_label("Start", missions[0]), "mission", mission_id=missions[0].get("mission_id")),
            _action("Choose another path", "route", "/challenges"),
        )

    if checkins_total > 0 and current_streak <= 1:
        return _decision(
            "streak_at_risk",
            "warning",
            f"Your rhythm is still young. Protect it with {missions[0].get('title') or 'one small mission'} today.",
            _action(_mission_label("Secure", missions[0]), "mission", mission_id=missions[0].get("mission_id")),
            _action("Remind me later", "mission_reminder", mission_id=missions[0].get("mission_id")),
        )

    return _decision(
        "today_not_started",
        "focus",
        f"Today's mission is ready: {missions[0].get('title') or 'one small action'}. Complete it, then mark it done.",
        _action(_mission_label("Start", missions[0]), "mission", mission_id=missions[0].get("mission_id")),
        _action("View path details", "route", f"/enrollment/{missions[0].get('enrollment_id')}"),
    )

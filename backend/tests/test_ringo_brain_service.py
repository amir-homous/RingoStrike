from datetime import datetime, timedelta, timezone

from helpers import auth_headers, register_user
from services.ringo_brain_service import get_today_ringo_guidance
from utils.date_utils import ringo_day_metadata, utc_today_iso


def _start_path_and_join_first_challenge(client, headers, path_key="fitness"):
    paths_data = client.get("/paths", headers=headers).get_json()
    path = next(item for item in paths_data["items"] if item["key"] == path_key)

    client.post(f"/paths/{path['path_id']}/start", headers=headers)
    challenges = client.get(
        f"/paths/{path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"]
    challenge = challenges[0]

    join_data = client.post(
        f"/challenges/{challenge['challenge_id']}/join",
        json={},
        headers=headers,
    ).get_json()

    return {
        "path": path,
        "challenge": challenge,
        "enrollment_id": join_data["enrollment_id"],
    }


def _insert_counted_checkin(user_id, enrollment_id, challenge_id, date):
    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO checkins (
                enrollment_id,
                user_id,
                challenge_id,
                date,
                status,
                source,
                is_counted
            )
            VALUES (?, ?, ?, ?, 'Done', 'test', 1)
            """,
            (enrollment_id, user_id, challenge_id, date),
        )
        conn.commit()
    finally:
        conn.close()


def _today_missions(client, headers):
    data = client.get("/me/today-missions", headers=headers).get_json()
    assert data["ok"] is True
    return data["missions"]


def _main_mission(missions):
    return next(
        mission for mission in missions
        if mission["mission_intensity"] == "main"
    )


def _linked_tiny_mission(missions, main_mission):
    return next(
        mission for mission in missions
        if mission["mission_intensity"] == "tiny"
        and mission["parent_mission_id"] == main_mission["mission_id"]
    )


def _linked_bonus_mission(missions, main_mission):
    return next(
        mission for mission in missions
        if mission["mission_intensity"] == "bonus"
        and mission["parent_mission_id"] == main_mission["mission_id"]
    )


def _set_challenge_missions_available(challenge_id):
    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            "UPDATE missions SET unlock_after_days = 0 WHERE challenge_id = ?",
            (challenge_id,),
        )
        conn.commit()
    finally:
        conn.close()


def _set_mission_log_status(user_id, mission, status, *, reminder_at=None):
    import database

    conn = database.get_db_connection()
    try:
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
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, mission_id, date) DO UPDATE SET
                status = excluded.status,
                reminder_at = excluded.reminder_at,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                mission["enrollment_id"],
                mission["challenge_id"],
                mission["mission_id"],
                utc_today_iso(),
                status,
                reminder_at,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _reminder_at():
    next_reset = datetime.fromisoformat(
        ringo_day_metadata()["next_reset_at"].replace("Z", "+00:00"),
    )
    target = min(
        datetime.now(timezone.utc) + timedelta(hours=2),
        next_reset - timedelta(seconds=1),
    )
    return target.isoformat()


def _due_reminder_at():
    return (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()


def _stale_reminder_at():
    return (datetime.now(timezone.utc) - timedelta(days=1, minutes=5)).isoformat()


def _status_counts(missions):
    return {
        "pending": sum(1 for mission in missions if mission["status"] == "pending"),
        "reminded": sum(1 for mission in missions if mission["status"] == "remind_later"),
        "skipped": sum(1 for mission in missions if mission["status"] == "skipped"),
        "done": sum(1 for mission in missions if mission["status"] == "done"),
    }


def test_ringo_brain_returns_new_user_guidance_without_endpoint(client):
    user = register_user(client, username="BrainNewUser")

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ok"] is True
    assert payload["ringo"]["user_state"] == "new_user"
    assert payload["ringo"]["tone"] == "warm_no_shame"
    assert payload["mission"] is None
    assert payload["progress"] == {
        "today_saved": False,
        "current_streak": 0,
        "total_checkins": 0,
    }
    assert payload["ringo_day"]["date"] == utc_today_iso()
    assert payload["ringo_day"]["reset_basis"] == "utc"
    assert payload["ringo_day"]["next_reset_at"].endswith("T00:00:00Z")
    assert payload["ringo_day"]["server_now"].endswith("Z")
    assert payload["fallback"]["used"] is False


def test_ringo_brain_returns_today_not_started_for_available_mission(client):
    user = register_user(client, username="BrainStarted")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_not_started"
    assert payload["ringo"]["mood"] == "focused"
    assert payload["mission"]["mission_intensity"] == "main"
    assert payload["actions"][0]["type"] == "start"
    assert {action["type"] for action in payload["actions"]} >= {
        "remind_later",
        "make_smaller",
        "too_tired",
        "skip_today",
    }


def test_ringo_brain_returns_today_completed_after_mission_done(client):
    user = register_user(client, username="BrainDone")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)

    for mission in missions:
        done_res = client.post(
            f"/me/missions/{mission['mission_id']}/done",
            headers=headers,
        )
        assert done_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["progress"]["today_saved"] is True
    assert payload["reward_sequence"]["type"] == "celebration"


def test_ringo_brain_treats_linked_tiny_completion_as_today_saved(client):
    user = register_user(client, username="BrainTinyDone")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )
    assert done_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["progress"]["today_saved"] is True
    assert payload["mission"]["mission_id"] == tiny_mission["mission_id"]
    assert payload["mission"]["mission_intensity"] == "tiny"
    assert payload["actions"] == [{"type": "dismiss", "label": "Finish for today"}]
    assert payload["agenda"]["next_action_type"] == "done_for_today"


def test_ringo_brain_tiny_completion_does_not_auto_suggest_bonus(client):
    user = register_user(client, username="BrainTinyDoneNoBonus")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)
    bonus_mission = _linked_bonus_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )
    assert done_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["agenda"]["next_action_type"] == "done_for_today"
    assert payload["agenda"]["next_mission_id"] is None
    assert payload["mission"]["mission_id"] == tiny_mission["mission_id"]
    assert payload["mission"]["mission_id"] != bonus_mission["mission_id"]


def test_ringo_brain_main_completion_can_suggest_bonus(client):
    user = register_user(client, username="BrainMainDoneBonus")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    bonus_mission = _linked_bonus_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    assert done_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] == "optional_mission"
    assert payload["agenda"]["next_mission_id"] == bonus_mission["mission_id"]
    assert payload["mission"]["mission_id"] == bonus_mission["mission_id"]
    assert "Today is safe" in payload["ringo"]["message"]
    assert "optional step" in payload["ringo"]["message"]
    assert payload["actions"][0]["type"] == "dismiss"
    assert payload["actions"][1]["mission_id"] == bonus_mission["mission_id"]


def test_ringo_brain_main_completion_can_suggest_unrelated_pending_as_optional(client):
    user = register_user(client, username="BrainMainOther")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    path_id = context["path"]["path_id"]
    challenges = client.get(
        f"/paths/{path_id}/challenges",
        headers=headers,
    ).get_json()["items"]
    second_challenge = next(
        challenge for challenge in challenges
        if challenge["challenge_id"] != context["challenge"]["challenge_id"]
    )
    client.post(
        f"/challenges/{second_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    _set_challenge_missions_available(second_challenge["challenge_id"])
    missions = _today_missions(client, headers)
    first_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == context["challenge"]["challenge_id"]
    ])
    first_bonus = _linked_bonus_mission(missions, first_main)
    second_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == second_challenge["challenge_id"]
    ])

    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            "UPDATE missions SET status = 'Archived' WHERE id = ?",
            (first_bonus["mission_id"],),
        )
        conn.commit()
    finally:
        conn.close()

    assert client.post(
        f"/me/missions/{first_main['mission_id']}/done",
        headers=headers,
    ).status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["agenda"]["next_action_type"] == "optional_mission"
    assert payload["agenda"]["next_mission_id"] == second_main["mission_id"]
    assert payload["mission"]["mission_id"] == second_main["mission_id"]
    assert "optional step" in payload["ringo"]["message"]
    assert payload["actions"][0]["type"] == "dismiss"
    assert payload["actions"][1]["mission_id"] == second_main["mission_id"]
    assert payload["agenda"]["pending_count"] > 1


def test_ringo_brain_tiny_completion_can_softly_suggest_unrelated_pending_only(client):
    user = register_user(client, username="BrainTinyOther")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    path_id = context["path"]["path_id"]
    challenges = client.get(
        f"/paths/{path_id}/challenges",
        headers=headers,
    ).get_json()["items"]
    second_challenge = next(
        challenge for challenge in challenges
        if challenge["challenge_id"] != context["challenge"]["challenge_id"]
    )
    client.post(
        f"/challenges/{second_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    _set_challenge_missions_available(second_challenge["challenge_id"])
    missions = _today_missions(client, headers)
    first_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == context["challenge"]["challenge_id"]
    ])
    first_tiny = _linked_tiny_mission(missions, first_main)
    first_bonus = _linked_bonus_mission(missions, first_main)
    second_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == second_challenge["challenge_id"]
    ])

    assert client.post(
        f"/me/missions/{first_tiny['mission_id']}/done",
        headers=headers,
    ).status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["agenda"]["next_action_type"] == "optional_mission"
    assert payload["agenda"]["next_mission_id"] == second_main["mission_id"]
    assert payload["mission"]["mission_id"] == second_main["mission_id"]
    assert payload["agenda"]["next_mission_id"] != first_main["mission_id"]
    assert payload["agenda"]["next_mission_id"] != first_bonus["mission_id"]
    assert "optional step" in payload["ringo"]["message"]


def test_ringo_brain_bonus_completion_prefers_done_over_another_bonus(client):
    user = register_user(client, username="BrainBonusDoneStops")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    path_id = context["path"]["path_id"]
    challenges = client.get(
        f"/paths/{path_id}/challenges",
        headers=headers,
    ).get_json()["items"]
    second_challenge = next(
        challenge for challenge in challenges
        if challenge["challenge_id"] != context["challenge"]["challenge_id"]
    )
    client.post(
        f"/challenges/{second_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    _set_challenge_missions_available(second_challenge["challenge_id"])
    missions = _today_missions(client, headers)
    first_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == context["challenge"]["challenge_id"]
    ])
    first_bonus = _linked_bonus_mission(missions, first_main)
    second_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == second_challenge["challenge_id"]
    ])
    second_bonus = _linked_bonus_mission(missions, second_main)

    assert client.post(
        f"/me/missions/{first_main['mission_id']}/done",
        headers=headers,
    ).status_code == 200
    assert client.post(
        f"/me/missions/{second_main['mission_id']}/done",
        headers=headers,
    ).status_code == 200
    assert client.post(
        f"/me/missions/{first_bonus['mission_id']}/done",
        headers=headers,
    ).status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] == "done_for_today"
    assert payload["agenda"]["next_mission_id"] is None
    assert payload["mission"]["mission_id"] != second_bonus["mission_id"]


def test_ringo_brain_bonus_reminder_not_suppressed_after_tiny_done(client):
    user = register_user(client, username="BrainTinyBonusRem")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)
    bonus_mission = _linked_bonus_mission(missions, main_mission)
    reminder_at = _reminder_at()

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )
    remind_res = client.post(
        f"/me/missions/{bonus_mission['mission_id']}/remind-later",
        json={"reminder_at": reminder_at},
        headers=headers,
    )
    assert done_res.status_code == 200
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] != "upcoming_reminder"
    assert payload["agenda"]["next_mission_id"] != bonus_mission["mission_id"]
    assert payload["agenda"]["next_reminder_at"] is None
    assert payload["agenda"]["has_optional_work"] is True


def test_linked_tiny_completion_leaves_parent_main_pending_for_compatibility(client):
    user = register_user(client, username="BrainTinyCompat")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )
    assert done_res.status_code == 200

    updated_missions = _today_missions(client, headers)
    updated_main = next(
        mission for mission in updated_missions
        if mission["mission_id"] == main_mission["mission_id"]
    )
    updated_tiny = next(
        mission for mission in updated_missions
        if mission["mission_id"] == tiny_mission["mission_id"]
    )

    assert updated_tiny["status"] == "done"
    assert updated_main["status"] == "pending"


def test_ringo_brain_main_completion_still_saves_today(client):
    user = register_user(client, username="BrainMainDone")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    bonus_mission = _linked_bonus_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    assert done_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] == "optional_mission"
    assert payload["mission"]["mission_id"] == bonus_mission["mission_id"]
    assert payload["mission"]["mission_intensity"] == "bonus"


def test_ringo_brain_prioritizes_today_saved_over_skipped_after_main_done(client):
    user = register_user(client, username="BrainDoneSkip")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    skip_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/skip",
        json={"reason": "too_tired"},
        headers=headers,
    )
    assert done_res.status_code == 200
    assert skip_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["progress"]["today_saved"] is True
    assert "not secured" not in payload["ringo"]["message"].lower()


def test_ringo_brain_prioritizes_today_saved_over_reminded_after_main_done(client):
    user = register_user(client, username="BrainDoneRemind")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    remind_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/remind-later",
        json={"reminder_at": _reminder_at()},
        headers=headers,
    )
    assert done_res.status_code == 200
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["progress"]["today_saved"] is True
    assert "not secured" not in payload["ringo"]["message"].lower()


def test_ringo_brain_agenda_today_saved_keeps_future_reminder_quiet(client):
    user = register_user(client, username="BrainAgendaReminder")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)
    reminder_at = _reminder_at()

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    remind_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/remind-later",
        json={"reminder_at": reminder_at},
        headers=headers,
    )
    assert done_res.status_code == 200
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] != "upcoming_reminder"
    assert payload["agenda"]["next_mission_id"] != tiny_mission["mission_id"]
    assert payload["agenda"]["has_optional_work"] is True
    assert "paused for a reminder" not in payload["ringo"]["message"]


def test_ringo_brain_agenda_today_saved_with_skipped_mission(client):
    user = register_user(client, username="BrainAgendaSkipped")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    skip_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/skip",
        json={"reason": "too_tired"},
        headers=headers,
    )
    assert done_res.status_code == 200
    assert skip_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] == "skipped_optional"
    assert payload["agenda"]["next_mission_id"] == tiny_mission["mission_id"]
    assert payload["agenda"]["skipped_count"] == 1
    assert payload["agenda"]["has_optional_work"] is True
    assert "no-pressure" in payload["ringo"]["message"]


def test_ringo_brain_agenda_not_saved_prioritizes_pending_mission(client):
    user = register_user(client, username="BrainAgendaPending")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "primary_mission"
    assert payload["agenda"]["next_mission_id"] == main_mission["mission_id"]
    assert payload["agenda"]["next_mission_title"] == main_mission["title"]
    assert payload["agenda"]["pending_count"] >= 1


def test_ringo_brain_agenda_not_saved_future_reminder_does_not_block_pending(client):
    user = register_user(client, username="BrainAgendaFuture")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    other_pending = next(
        mission for mission in missions
        if mission["mission_id"] != main_mission["mission_id"]
        and mission["status"] == "pending"
    )
    reminder_at = _reminder_at()

    remind_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/remind-later",
        json={"reminder_at": reminder_at},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "primary_mission"
    assert payload["agenda"]["next_mission_id"] == other_pending["mission_id"]
    assert payload["agenda"]["next_reminder_at"] is None
    assert payload["agenda"]["reminded_count"] == 1
    assert payload["mission"]["mission_id"] == other_pending["mission_id"]
    assert "I saved that reminder" in payload["ringo"]["message"]
    assert other_pending["title"] in payload["ringo"]["message"]


def test_ringo_brain_agenda_not_saved_main_mission_outranks_unrelated_due_reminder(client):
    user = register_user(client, username="BrainAgendaDueUnrelated")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    path_id = context["path"]["path_id"]
    challenges = client.get(
        f"/paths/{path_id}/challenges",
        headers=headers,
    ).get_json()["items"]
    second_challenge = next(
        challenge for challenge in challenges
        if challenge["challenge_id"] != context["challenge"]["challenge_id"]
    )
    client.post(
        f"/challenges/{second_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    _set_challenge_missions_available(second_challenge["challenge_id"])
    missions = _today_missions(client, headers)
    first_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == context["challenge"]["challenge_id"]
    ])
    second_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == second_challenge["challenge_id"]
    ])

    remind_res = client.post(
        f"/me/missions/{first_main['mission_id']}/remind-later",
        json={"reminder_at": _due_reminder_at()},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "primary_mission"
    assert payload["agenda"]["next_mission_id"] == second_main["mission_id"]
    assert payload["mission"]["mission_id"] == second_main["mission_id"]
    assert second_main["title"] in payload["ringo"]["message"]


def test_ringo_brain_agenda_stale_reminder_does_not_dominate_after_reset(client):
    user = register_user(client, username="BrainAgendaStaleReminder")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)

    _set_mission_log_status(
        user["user_id"],
        main_mission,
        "remind_later",
        reminder_at=_stale_reminder_at(),
    )

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "primary_mission"
    assert payload["agenda"]["next_mission_id"] == main_mission["mission_id"]
    assert payload["agenda"]["next_reminder_at"] is None
    assert payload["mission"]["mission_id"] == main_mission["mission_id"]


def test_ringo_brain_bonus_reminder_does_not_become_primary_before_today_saved(client):
    user = register_user(client, username="BrainUnsafeBonus")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    bonus_mission = _linked_bonus_mission(missions, main_mission)

    remind_res = client.post(
        f"/me/missions/{bonus_mission['mission_id']}/remind-later",
        json={"reminder_at": _due_reminder_at()},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "primary_mission"
    assert payload["agenda"]["next_mission_id"] == main_mission["mission_id"]
    assert payload["mission"]["mission_id"] == main_mission["mission_id"]
    assert payload["agenda"]["next_mission_id"] != bonus_mission["mission_id"]


def test_ringo_brain_linked_tiny_reminder_covers_parent_main(client):
    user = register_user(client, username="BrainAgendaTinyCovered")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    path_id = context["path"]["path_id"]
    challenges = client.get(
        f"/paths/{path_id}/challenges",
        headers=headers,
    ).get_json()["items"]
    second_challenge = next(
        challenge for challenge in challenges
        if challenge["challenge_id"] != context["challenge"]["challenge_id"]
    )
    client.post(
        f"/challenges/{second_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    _set_challenge_missions_available(second_challenge["challenge_id"])
    missions = _today_missions(client, headers)
    first_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == context["challenge"]["challenge_id"]
    ])
    first_tiny = _linked_tiny_mission(missions, first_main)
    second_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == second_challenge["challenge_id"]
    ])

    remind_res = client.post(
        f"/me/missions/{first_tiny['mission_id']}/remind-later",
        json={"reminder_at": _reminder_at()},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "primary_mission"
    assert payload["agenda"]["next_mission_id"] == second_main["mission_id"]
    assert payload["mission"]["mission_id"] == second_main["mission_id"]
    assert second_main["title"] in payload["ringo"]["message"]
    assert first_main["title"] not in payload["ringo"]["message"]


def test_ringo_brain_due_linked_tiny_reminder_beats_parent_and_pending(client):
    user = register_user(client, username="BrainAgendaTinyDue")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)
    reminder_at = _due_reminder_at()

    remind_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/remind-later",
        json={"reminder_at": reminder_at},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["agenda"]["next_action_type"] == "due_reminder"
    assert payload["agenda"]["next_mission_id"] == tiny_mission["mission_id"]
    assert payload["mission"]["mission_id"] == tiny_mission["mission_id"]


def test_ringo_brain_agenda_not_saved_due_reminder_beats_pending(client):
    user = register_user(client, username="BrainAgendaDueReminder")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    reminder_at = _due_reminder_at()

    remind_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/remind-later",
        json={"reminder_at": reminder_at},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "due_reminder"
    assert payload["agenda"]["next_mission_id"] == main_mission["mission_id"]
    assert payload["agenda"]["next_reminder_at"] == reminder_at
    assert payload["mission"]["mission_id"] == main_mission["mission_id"]


def test_ringo_brain_agenda_not_saved_future_reminder_is_not_actionable(client):
    user = register_user(client, username="BrainAgendaOnlyFuture")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)
    missions = _today_missions(client, headers)
    reminder_at = _reminder_at()

    for mission in missions:
        remind_res = client.post(
            f"/me/missions/{mission['mission_id']}/remind-later",
            json={"reminder_at": reminder_at},
            headers=headers,
        )
        assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] != "upcoming_reminder"
    assert payload["agenda"]["next_reminder_at"] is None
    assert payload["agenda"]["has_optional_work"] is True


def test_ringo_brain_agenda_all_done_returns_done_for_today(client):
    user = register_user(client, username="BrainAgendaAllDone")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)

    for mission in _today_missions(client, headers):
        done_res = client.post(
            f"/me/missions/{mission['mission_id']}/done",
            headers=headers,
        )
        assert done_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] == "done_for_today"
    assert payload["agenda"]["next_mission_id"] is None
    assert payload["agenda"]["next_mission_title"] == ""
    assert payload["agenda"]["has_optional_work"] is False


def test_ringo_brain_agenda_counts_match_mission_statuses(client):
    user = register_user(client, username="BrainAgendaCounts")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)
    other_mission = next(
        mission for mission in missions
        if mission["mission_id"] not in {
            main_mission["mission_id"],
            tiny_mission["mission_id"],
        }
    )

    assert client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    ).status_code == 200
    assert client.post(
        f"/me/missions/{tiny_mission['mission_id']}/remind-later",
        json={"reminder_at": _due_reminder_at()},
        headers=headers,
    ).status_code == 200
    assert client.post(
        f"/me/missions/{other_mission['mission_id']}/skip",
        json={"reason": "other"},
        headers=headers,
    ).status_code == 200

    updated_missions = _today_missions(client, headers)
    counts = _status_counts(updated_missions)
    payload, code = get_today_ringo_guidance(user["user_id"])
    agenda = payload["agenda"]

    assert code == 200
    assert agenda["pending_count"] == counts["pending"]
    assert agenda["reminded_count"] == counts["reminded"]
    assert agenda["skipped_count"] == counts["skipped"]
    assert agenda["done_count"] == counts["done"]
    assert agenda["next_action_type"] == "skipped_optional"
    assert agenda["next_mission_id"] != tiny_mission["mission_id"]


def test_ringo_brain_main_reminded_does_not_suggest_linked_tiny(client):
    user = register_user(client, username="BrainMainRemindedFamily")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    path_id = context["path"]["path_id"]
    challenges = client.get(
        f"/paths/{path_id}/challenges",
        headers=headers,
    ).get_json()["items"]
    second_challenge = next(
        challenge for challenge in challenges
        if challenge["challenge_id"] != context["challenge"]["challenge_id"]
    )
    client.post(
        f"/challenges/{second_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    _set_challenge_missions_available(second_challenge["challenge_id"])
    missions = _today_missions(client, headers)
    first_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == context["challenge"]["challenge_id"]
    ])
    first_tiny = _linked_tiny_mission(missions, first_main)
    second_main = _main_mission([
        mission for mission in missions
        if mission["challenge_id"] == second_challenge["challenge_id"]
    ])

    remind_res = client.post(
        f"/me/missions/{first_main['mission_id']}/remind-later",
        json={"reminder_at": _reminder_at()},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_action_type"] == "primary_mission"
    assert payload["agenda"]["next_mission_id"] == second_main["mission_id"]
    assert payload["mission"]["mission_id"] == second_main["mission_id"]
    assert payload["mission"]["mission_id"] != first_tiny["mission_id"]
    assert second_main["title"] in payload["ringo"]["message"]
    assert first_tiny["title"] not in payload["ringo"]["message"]


def test_ringo_brain_tiny_reminded_does_not_suggest_parent_main(client):
    user = register_user(client, username="BrainTinyRemindedFamily")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)

    remind_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/remind-later",
        json={"reminder_at": _reminder_at()},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["progress"]["today_saved"] is False
    assert payload["agenda"]["next_mission_id"] != main_mission["mission_id"]
    assert payload["mission"]["mission_id"] != main_mission["mission_id"]


def test_ringo_brain_prioritizes_linked_tiny_done_over_skipped_and_reminded(client):
    user = register_user(client, username="BrainTinyMixed")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    _set_challenge_missions_available(context["challenge"]["challenge_id"])
    missions = _today_missions(client, headers)
    main_mission = _main_mission(missions)
    tiny_mission = _linked_tiny_mission(missions, main_mission)
    other_mission = next(
        mission for mission in missions
        if mission["mission_id"] not in {
            main_mission["mission_id"],
            tiny_mission["mission_id"],
        }
    )

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )
    skip_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/skip",
        json={"reason": "no_time"},
        headers=headers,
    )
    remind_res = client.post(
        f"/me/missions/{other_mission['mission_id']}/remind-later",
        json={"reminder_at": _reminder_at()},
        headers=headers,
    )
    assert done_res.status_code == 200
    assert skip_res.status_code == 200
    assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["progress"]["today_saved"] is True
    assert payload["agenda"]["next_action_type"] != "upcoming_reminder"
    assert payload["mission"]["mission_id"] != other_mission["mission_id"]
    assert payload["actions"] == [{"type": "dismiss", "label": "Finish for today"}]


def test_ringo_brain_returns_today_skipped_when_no_satisfying_mission_done(client):
    user = register_user(client, username="BrainOnlySkipped")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)

    for mission in _today_missions(client, headers):
        skip_res = client.post(
            f"/me/missions/{mission['mission_id']}/skip",
            json={"reason": "other"},
            headers=headers,
        )
        assert skip_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_skipped"
    assert payload["progress"]["today_saved"] is False


def test_ringo_brain_returns_today_reminded_when_no_satisfying_mission_done(client):
    user = register_user(client, username="BrainOnlyReminded")
    headers = auth_headers(user["access_token"])
    _start_path_and_join_first_challenge(client, headers)

    for mission in _today_missions(client, headers):
        remind_res = client.post(
            f"/me/missions/{mission['mission_id']}/remind-later",
            json={"reminder_at": _reminder_at()},
            headers=headers,
        )
        assert remind_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_reminded"
    assert payload["progress"]["today_saved"] is False


def test_ringo_brain_returns_returning_after_absence(client):
    user = register_user(client, username="BrainReturn")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    old_date = (datetime.now(timezone.utc).date() - timedelta(days=3)).isoformat()
    _insert_counted_checkin(
        user["user_id"],
        context["enrollment_id"],
        context["challenge"]["challenge_id"],
        old_date,
    )

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "returning_after_absence"
    assert payload["mission"]["mission_intensity"] == "main"
    assert payload["mission"]["parent_mission_id"] is None
    assert payload["reward_sequence"]["type"] == "comeback"


def test_ringo_brain_returns_streak_risk_for_young_streak(client):
    user = register_user(client, username="BrainRisk")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    _insert_counted_checkin(
        user["user_id"],
        context["enrollment_id"],
        context["challenge"]["challenge_id"],
        utc_today_iso(),
    )

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "streak_risk"
    assert payload["mission"]["mission_intensity"] == "main"
    assert payload["mission"]["parent_mission_id"] is None
    assert payload["reward_sequence"]["type"] == "streak_saved"


def test_ringo_brain_defaults_to_main_mission_for_low_pressure_state(client):
    user = register_user(client, username="BrainMainDefault")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    old_date = (datetime.now(timezone.utc).date() - timedelta(days=3)).isoformat()
    _insert_counted_checkin(
        user["user_id"],
        context["enrollment_id"],
        context["challenge"]["challenge_id"],
        old_date,
    )

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "returning_after_absence"
    assert payload["mission"]["mission_intensity"] == "main"
    assert payload["mission"]["parent_mission_id"] is None


def test_ringo_brain_low_pressure_state_falls_back_to_tiny_without_main(client):
    user = register_user(client, username="BrainNoMain")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)
    old_date = (datetime.now(timezone.utc).date() - timedelta(days=3)).isoformat()
    _insert_counted_checkin(
        user["user_id"],
        context["enrollment_id"],
        context["challenge"]["challenge_id"],
        old_date,
    )

    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            UPDATE missions
            SET status = 'Archived'
            WHERE challenge_id = ?
              AND mission_intensity = 'main'
            """,
            (context["challenge"]["challenge_id"],),
        )
        conn.commit()
    finally:
        conn.close()

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "returning_after_absence"
    assert payload["mission"]["mission_intensity"] == "tiny"
    assert payload["mission"]["parent_mission_id"] is not None


def test_ringo_brain_returns_no_mission_today_when_none_available(client):
    user = register_user(client, username="BrainNoMission")
    headers = auth_headers(user["access_token"])
    context = _start_path_and_join_first_challenge(client, headers)

    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            "UPDATE missions SET unlock_after_days = 99 WHERE challenge_id = ?",
            (context["challenge"]["challenge_id"],),
        )
        conn.commit()
    finally:
        conn.close()

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "no_mission_today"
    assert payload["mission"] is None
    assert payload["reward_sequence"]["available"] is False


def test_ringo_today_guidance_endpoint_requires_auth(client):
    res = client.get("/me/ringo/today")

    assert res.status_code == 401
    assert res.get_json() == {"ok": False, "error": "unauthorized"}


def test_ringo_today_guidance_endpoint_returns_contract_shape(client):
    user = register_user(client, username="BrainEndpoint")
    headers = auth_headers(user["access_token"])

    res = client.get("/me/ringo/today", headers=headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert "ringo" in data
    assert "actions" in data
    assert "progress" in data
    assert "agenda" in data
    assert "reward_sequence" in data
    assert "fallback" in data
    assert data["ringo"]["tone"] == "warm_no_shame"
    assert {"today_saved", "next_action_type", "pending_count", "done_count"} <= set(data["agenda"])

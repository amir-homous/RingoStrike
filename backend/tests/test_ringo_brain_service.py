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


def _reminder_at():
    next_reset = datetime.fromisoformat(
        ringo_day_metadata()["next_reset_at"].replace("Z", "+00:00"),
    )
    target = min(
        datetime.now(timezone.utc) + timedelta(hours=2),
        next_reset - timedelta(minutes=1),
    )
    return target.isoformat()


def _due_reminder_at():
    return (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()


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
    assert payload["actions"] == []


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
    main_mission = _main_mission(_today_missions(client, headers))

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    assert done_res.status_code == 200

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "today_completed"
    assert payload["progress"]["today_saved"] is True
    assert payload["mission"]["mission_id"] == main_mission["mission_id"]
    assert payload["mission"]["mission_intensity"] == "main"


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


def test_ringo_brain_agenda_today_saved_with_upcoming_reminder(client):
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
    assert payload["agenda"]["next_action_type"] == "upcoming_reminder"
    assert payload["agenda"]["next_mission_id"] == tiny_mission["mission_id"]
    assert payload["agenda"]["next_mission_title"] == tiny_mission["title"]
    assert payload["agenda"]["next_reminder_at"] == reminder_at
    assert payload["agenda"]["has_optional_work"] is True
    assert "paused for a reminder" in payload["ringo"]["message"]


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
    assert agenda["next_action_type"] == "due_reminder"


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
    assert payload["mission"]["mission_id"] == tiny_mission["mission_id"]
    assert payload["actions"] == []


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
    assert payload["mission"]["mission_intensity"] == "tiny"
    assert payload["mission"]["estimated_minutes"] in {1, 2, 3}
    assert payload["mission"]["parent_mission_id"] is not None
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
    assert payload["mission"]["mission_intensity"] == "tiny"
    assert payload["mission"]["estimated_minutes"] in {1, 2, 3}
    assert payload["mission"]["parent_mission_id"] is not None
    assert payload["reward_sequence"]["type"] == "streak_saved"


def test_ringo_brain_prefers_tiny_mission_for_low_pressure_state(client):
    user = register_user(client, username="BrainTiny")
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
    assert payload["mission"]["mission_intensity"] == "tiny"
    assert payload["mission"]["estimated_minutes"] in {1, 2, 3}
    assert payload["mission"]["parent_mission_id"] is not None


def test_ringo_brain_low_pressure_state_falls_back_to_main_without_tiny(client):
    user = register_user(client, username="BrainNoTiny")
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
              AND mission_intensity = 'tiny'
            """,
            (context["challenge"]["challenge_id"],),
        )
        conn.commit()
    finally:
        conn.close()

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "returning_after_absence"
    assert payload["mission"]["mission_intensity"] == "main"


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

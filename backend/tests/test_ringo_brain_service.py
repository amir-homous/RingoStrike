from datetime import datetime, timedelta, timezone

from helpers import auth_headers, register_user
from services.ringo_brain_service import get_today_ringo_guidance
from utils.date_utils import utc_today_iso


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


def _first_today_mission(user_id):
    payload, code = get_today_ringo_guidance(user_id)
    assert code == 200
    assert payload["ok"] is True
    assert payload["mission"]
    return payload["mission"]


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
    mission = _first_today_mission(user["user_id"])

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

    import database

    conn = database.get_db_connection()
    try:
        main_mission = conn.execute(
            """
            SELECT id
            FROM missions
            WHERE challenge_id = ?
            ORDER BY order_index ASC, id ASC
            LIMIT 1
            """,
            (context["challenge"]["challenge_id"],),
        ).fetchone()
        tiny_mission = conn.execute(
            """
            SELECT id
            FROM missions
            WHERE challenge_id = ?
            ORDER BY order_index ASC, id ASC
            LIMIT 1 OFFSET 1
            """,
            (context["challenge"]["challenge_id"],),
        ).fetchone()
        conn.execute(
            """
            UPDATE missions
            SET mission_intensity = 'tiny',
                estimated_minutes = 1,
                parent_mission_id = ?,
                unlock_after_days = 0
            WHERE id = ?
            """,
            (main_mission["id"], tiny_mission["id"]),
        )
        conn.commit()
    finally:
        conn.close()

    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["ringo"]["user_state"] == "returning_after_absence"
    assert payload["mission"]["mission_id"] == tiny_mission["id"]
    assert payload["mission"]["mission_intensity"] == "tiny"
    assert payload["mission"]["estimated_minutes"] == 1
    assert payload["mission"]["parent_mission_id"] == main_mission["id"]


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
    assert "reward_sequence" in data
    assert "fallback" in data
    assert data["ringo"]["tone"] == "warm_no_shame"

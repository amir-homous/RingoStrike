from helpers import auth_headers, register_user
from services.mission_service import _upsert_mission_log
from services.ringo_brain_service import get_today_ringo_guidance
from test_mission_family import _by_id, _family, _join_first_fitness_challenge, _log_rows, _soon, _stats, _today


def _setup(client, username):
    user = register_user(client, username=username)
    headers = auth_headers(user["access_token"])
    _join_first_fitness_challenge(client, headers)
    main, tiny, bonus = _family(_today(client, headers))
    return user, headers, main, tiny, bonus


def _today_saved(user):
    payload, _ = get_today_ringo_guidance(user["user_id"])
    return payload["progress"]["today_saved"]


def _assert_already_counted(res):
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["mission"]["already_done"] is True
    assert data["mission"]["family_closed"] is True
    assert data["mission"]["xp_awarded"] == 0
    assert data["mission"]["status"] == "done"


def _assert_reminder_refused(res):
    assert res.status_code == 409
    assert res.get_json() == {"ok": False, "error": "already_counted_today"}


def test_skip_on_a_done_main_changes_nothing(client):
    user, headers, main, _, _ = _setup(client, "FinalSkipMain")
    client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)
    before_rows = _log_rows(main["mission_id"])
    before = _stats(client, headers)

    res = client.post(f"/me/missions/{main['mission_id']}/skip", json={"reason": "no_time"}, headers=headers)

    _assert_already_counted(res)
    assert [tuple(row) for row in _log_rows(main["mission_id"])] == [tuple(row) for row in before_rows]
    assert _log_rows(main["mission_id"])[0]["status"] == "done"
    assert _stats(client, headers)["total_points"] == before["total_points"]
    assert _today_saved(user) is True


def test_skip_on_a_done_tiny_changes_nothing(client):
    user, headers, _, tiny, _ = _setup(client, "FinalSkipTiny")
    client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers)
    before_rows = _log_rows(tiny["mission_id"])
    before = _stats(client, headers)

    res = client.post(f"/me/missions/{tiny['mission_id']}/skip", headers=headers)

    _assert_already_counted(res)
    assert [tuple(row) for row in _log_rows(tiny["mission_id"])] == [tuple(row) for row in before_rows]
    assert _stats(client, headers)["total_points"] == before["total_points"]
    assert _today_saved(user) is True


def test_remind_on_a_done_main_or_tiny_is_refused(client):
    for name, pick in (("FinalRemindMain", 0), ("FinalRemindTiny", 1)):
        user, headers, main, tiny, _ = _setup(client, name)
        mission = (main, tiny)[pick]
        client.post(f"/me/missions/{mission['mission_id']}/done", headers=headers)
        before_rows = _log_rows(mission["mission_id"])
        before = _stats(client, headers)

        later = client.post(
            f"/me/missions/{mission['mission_id']}/remind-later",
            json={"reminder_at": _soon()},
            headers=headers,
        )
        single = client.post(f"/me/missions/{mission['mission_id']}/plan-reminder", headers=headers)

        _assert_reminder_refused(later)
        _assert_reminder_refused(single)
        assert [tuple(row) for row in _log_rows(mission["mission_id"])] == [tuple(row) for row in before_rows]
        assert _by_id(_today(client, headers), mission)["reminder_at"] is None
        assert _stats(client, headers)["total_points"] == before["total_points"]
        assert _today_saved(user) is True


def test_issue_427_remind_on_a_done_main_then_tiny_keeps_total_points(client):
    user, headers, main, tiny, _ = _setup(client, "Final427")
    client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)
    before = _stats(client, headers)

    remind = client.post(
        f"/me/missions/{main['mission_id']}/remind-later",
        json={"reminder_at": _soon()},
        headers=headers,
    )
    tiny_done = client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers)

    _assert_reminder_refused(remind)
    assert tiny_done.get_json()["mission"]["already_done"] is True
    assert tiny_done.get_json()["mission"]["xp_awarded"] == 0
    assert _log_rows(tiny["mission_id"]) == []
    assert _log_rows(main["mission_id"])[0]["status"] == "done"
    assert _log_rows(main["mission_id"])[0]["xp_earned"] > 0
    assert _stats(client, headers)["total_points"] == before["total_points"]
    assert _today_saved(user) is True


def test_planner_leaves_a_done_mission_alone(client):
    _, headers, main, _, _ = _setup(client, "FinalPlanner")
    client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)
    before_rows = _log_rows(main["mission_id"])

    plan = client.post("/me/missions/plan-reminders", headers=headers).get_json()

    assert plan["ok"] is True
    assert main["mission_id"] not in {item["mission_id"] for item in plan["scheduled"]}
    assert [tuple(row) for row in _log_rows(main["mission_id"])] == [tuple(row) for row in before_rows]


def test_log_write_never_overwrites_a_done_row(client):
    user, headers, main, _, _ = _setup(client, "FinalUpsertGuard")
    client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)
    before_rows = _log_rows(main["mission_id"])

    for status in ("skipped", "remind_later", "pending"):
        payload, code = _upsert_mission_log(user["user_id"], main["mission_id"], status, reminder_at=_soon())
        assert code == 409
        assert payload == {"ok": False, "error": "already_counted_today"}

    assert [tuple(row) for row in _log_rows(main["mission_id"])] == [tuple(row) for row in before_rows]


def test_a_skipped_mission_can_still_be_reminded_or_done(client):
    _, headers, main, _, _ = _setup(client, "FinalSkippedStillOpen")
    client.post(f"/me/missions/{main['mission_id']}/skip", headers=headers)

    later = client.post(
        f"/me/missions/{main['mission_id']}/remind-later",
        json={"reminder_at": _soon()},
        headers=headers,
    )
    done = client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)

    assert later.status_code == 200
    assert done.status_code == 200
    assert done.get_json()["mission"]["xp_awarded"] > 0

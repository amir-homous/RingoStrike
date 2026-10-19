"""B26 (#383): optional check-in context on a done mission.

Context lives on mission_logs; checkins stays the counted record. Context never changes XP or
the counted check-in, invalid input writes nothing, and the fields stay private to the owner.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest

from helpers import auth_headers, register_user
from services.checkin_context import FEELING_KEYS, PLACE_KEYS, parse_checkin_context

CONTEXT_COLUMNS = ("performed_at", "mode", "place_key", "place_label", "feeling_key", "duration_seconds", "notes")


def _user_with_missions(client, username):
    user = register_user(client, username=username)
    headers = auth_headers(user["access_token"])
    paths = client.get("/paths", headers=headers).get_json()["items"]
    learning = next(item for item in paths if item["key"] == "learning")
    client.post(f"/paths/{learning['path_id']}/start", headers=headers)
    challenges = client.get(f"/paths/{learning['path_id']}/challenges", headers=headers).get_json()["items"]
    join = client.post(f"/challenges/{challenges[0]['challenge_id']}/join", json={}, headers=headers)
    assert join.status_code == 200
    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    by_intensity = {m["mission_intensity"]: m["mission_id"] for m in missions}
    me = client.get("/me", headers=headers).get_json()
    user_id = user.get("user_id") or me.get("user_id") or me.get("id")
    return headers, int(user_id), by_intensity


def _db():
    import database

    return database.get_db_connection()


def _counted_checkins(user_id):
    conn = _db()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM checkins WHERE user_id = ? AND status = 'Done' AND is_counted = 1",
            (user_id,),
        ).fetchone()[0]
    finally:
        conn.close()


def _logs(user_id):
    conn = _db()
    try:
        rows = conn.execute(
            f"SELECT mission_id, status, xp_earned, {', '.join(CONTEXT_COLUMNS)} FROM mission_logs WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _today_earlier_iso():
    """A moment earlier today (UTC), never before today's midnight."""
    now = datetime.now(timezone.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    moment = max(midnight, now - timedelta(minutes=30))
    return moment.isoformat().replace("+00:00", "Z")


FULL_NOW = {
    "mode": "now",
    "place_key": "other",
    "place_label": "  Library corner  ",
    "feeling_key": "hard_but_done",
    "note": "b26-private-note-7f3a",
    "duration_seconds": 900,
}


def test_done_without_body_is_unchanged(client):
    headers, user_id, missions = _user_with_missions(client, "CtxNoBody")

    res = client.post(f"/me/missions/{missions['main']}/done", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["mission"]["status"] == "done"
    assert data["mission"]["context"] is None
    assert data["checkin"]["mode"] == "created"
    assert _counted_checkins(user_id) == 1
    log = _logs(user_id)[0]
    assert all(log[column] is None for column in CONTEXT_COLUMNS)


def test_done_with_empty_json_is_unchanged(client):
    headers, user_id, missions = _user_with_missions(client, "CtxEmpty")
    res = client.post(f"/me/missions/{missions['main']}/done", json={}, headers=headers)
    assert res.status_code == 200
    assert res.get_json()["mission"]["context"] is None
    assert _counted_checkins(user_id) == 1


def test_full_context_now_is_stored_with_same_xp_and_one_checkin(client):
    plain_headers, plain_id, plain_missions = _user_with_missions(client, "CtxPlain")
    plain = client.post(f"/me/missions/{plain_missions['main']}/done", json={}, headers=plain_headers).get_json()

    headers, user_id, missions = _user_with_missions(client, "CtxNow")
    before = datetime.now(timezone.utc).replace(microsecond=0)
    res = client.post(f"/me/missions/{missions['main']}/done", json=FULL_NOW, headers=headers)
    assert res.status_code == 200
    data = res.get_json()

    # Exactly one counted check-in, the same XP and total as without context.
    assert _counted_checkins(user_id) == 1
    assert data["mission"]["xp_earned"] == plain["mission"]["xp_earned"]
    assert data["mission"]["xp_awarded"] == plain["mission"]["xp_awarded"]
    assert data["checkin"]["rewards"]["xp_total"] == plain["checkin"]["rewards"]["xp_total"]

    log = _logs(user_id)[0]
    assert log["mode"] == "now"
    assert log["place_key"] == "other"
    assert log["place_label"] == "Library corner"
    assert log["feeling_key"] == "hard_but_done"
    assert log["notes"] == "b26-private-note-7f3a"
    assert log["duration_seconds"] == 900
    performed = datetime.fromisoformat(log["performed_at"].replace("Z", "+00:00"))
    assert before <= performed <= datetime.now(timezone.utc) + timedelta(seconds=1)

    # Owner-only echo: no note text.
    assert data["mission"]["context"] == {
        "mode": "now",
        "performed_at": log["performed_at"],
        "place_key": "other",
        "place_label": "Library corner",
        "feeling_key": "hard_but_done",
        "has_note": True,
        "duration_seconds": 900,
    }
    assert "b26-private-note-7f3a" not in json.dumps(data)


def test_earlier_context_keeps_the_given_time(client):
    headers, user_id, missions = _user_with_missions(client, "CtxEarlier")
    performed = _today_earlier_iso()
    res = client.post(
        f"/me/missions/{missions['main']}/done",
        json={"mode": "earlier", "performed_at": performed, "place_key": "home", "feeling_key": "good"},
        headers=headers,
    )
    assert res.status_code == 200
    log = _logs(user_id)[0]
    assert log["mode"] == "earlier"
    assert datetime.fromisoformat(log["performed_at"].replace("Z", "+00:00")) == datetime.fromisoformat(performed.replace("Z", "+00:00")).replace(microsecond=0)
    assert log["place_key"] == "home" and log["feeling_key"] == "good"
    assert log["duration_seconds"] is None and log["place_label"] is None
    assert _counted_checkins(user_id) == 1


INVALID_BODIES = [
    ({"mood": "good"}, "unknown_context_field"),
    ({"mode": "later"}, "invalid_mode"),
    ({"place_key": "gps:35.7,51.4"}, "invalid_place_key"),
    ({"feeling_key": "happy"}, "invalid_feeling_key"),
    ({"place_key": "other", "place_label": "x" * 41}, "place_label_too_long"),
    ({"place_key": "home", "place_label": "Kitchen"}, "place_label_requires_other"),
    ({"note": "x" * 281}, "note_too_long"),
    ({"note": 5}, "invalid_note"),
    ({"mode": "earlier", "duration_seconds": 60}, "duration_requires_now"),
    ({"duration_seconds": 60}, "duration_requires_now"),
    ({"mode": "now", "duration_seconds": -5}, "invalid_duration_seconds"),
    ({"mode": "now", "duration_seconds": 0}, "invalid_duration_seconds"),
    ({"mode": "now", "duration_seconds": 86401}, "invalid_duration_seconds"),
    ({"mode": "now", "duration_seconds": "900"}, "invalid_duration_seconds"),
    ({"mode": "now", "duration_seconds": True}, "invalid_duration_seconds"),
    ({"mode": "earlier", "performed_at": "yesterday"}, "invalid_performed_at"),
]


@pytest.mark.parametrize("body,error", INVALID_BODIES)
def test_invalid_context_writes_nothing(client, body, error):
    headers, user_id, missions = _user_with_missions(client, f"CtxBad{abs(hash(error)) % 10000}")
    res = client.post(f"/me/missions/{missions['main']}/done", json=body, headers=headers)
    assert res.status_code == 400
    assert error in json.dumps(res.get_json())
    assert _logs(user_id) == []
    assert _counted_checkins(user_id) == 0


def test_non_object_body_is_rejected_without_write(client):
    headers, user_id, missions = _user_with_missions(client, "CtxList")
    res = client.post(f"/me/missions/{missions['main']}/done", json=["mode", "now"], headers=headers)
    assert res.status_code == 400
    assert _logs(user_id) == [] and _counted_checkins(user_id) == 0


def test_performed_at_must_be_today_and_not_future(client):
    headers, user_id, missions = _user_with_missions(client, "CtxToday")
    now = datetime.now(timezone.utc)
    yesterday = (now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(minutes=1)).isoformat()
    future = (now + timedelta(minutes=5)).isoformat()
    for value in (yesterday, future):
        res = client.post(
            f"/me/missions/{missions['main']}/done",
            json={"mode": "earlier", "performed_at": value},
            headers=headers,
        )
        assert res.status_code == 400
        assert res.get_json()["error"] in {"performed_at_not_today", "performed_at_in_future"}
    assert _logs(user_id) == [] and _counted_checkins(user_id) == 0


def test_already_done_ignores_new_context(client):
    headers, user_id, missions = _user_with_missions(client, "CtxRepeat")
    first = client.post(f"/me/missions/{missions['main']}/done", json={"mode": "now", "feeling_key": "good"}, headers=headers)
    assert first.status_code == 200
    stored = _logs(user_id)

    again = client.post(f"/me/missions/{missions['main']}/done", json=FULL_NOW, headers=headers)
    assert again.status_code == 200
    data = again.get_json()
    assert data["mission"]["already_done"] is True
    assert data["mission"]["context"] is None
    assert _logs(user_id) == stored
    assert _counted_checkins(user_id) == 1


def test_tiny_and_bonus_keep_their_checkin_rules(client):
    headers, user_id, missions = _user_with_missions(client, "CtxTiny")
    tiny = client.post(f"/me/missions/{missions['tiny']}/done", json={"mode": "now", "duration_seconds": 120}, headers=headers)
    assert tiny.status_code == 200
    assert _counted_checkins(user_id) == 1

    bonus = client.post(f"/me/missions/{missions['bonus']}/done", json={"mode": "earlier", "feeling_key": "light"}, headers=headers)
    assert bonus.status_code == 200
    assert bonus.get_json()["checkin"]["mode"] == "not_applicable"
    assert _counted_checkins(user_id) == 1
    stored = {log["mission_id"]: log for log in _logs(user_id)}
    assert stored[missions["tiny"]]["duration_seconds"] == 120
    assert stored[missions["bonus"]]["feeling_key"] == "light"


def test_context_stays_private(client):
    headers, user_id, missions = _user_with_missions(client, "CtxPrivate")
    res = client.post(f"/me/missions/{missions['main']}/done", json=FULL_NOW, headers=headers)
    assert res.status_code == 200

    secrets = ("b26-private-note-7f3a", "Library corner", "hard_but_done", "duration_seconds", "place_key", "feeling_key")
    payloads = [
        client.get("/api/public/profile/ctxprivate").get_data(as_text=True),
        client.get("/me/activity", headers=headers).get_data(as_text=True),
        client.get("/me/profile", headers=headers).get_data(as_text=True),
    ]
    for text in payloads:
        for secret in secrets:
            assert secret not in text

    # Another user in the same challenge gets their own row; context never crosses users.
    mine_before = _logs(user_id)
    other_headers, other_id, other_missions = _user_with_missions(client, "CtxOther")
    other = client.post(f"/me/missions/{other_missions['main']}/done", json={}, headers=other_headers)
    assert other.status_code == 200
    assert other.get_json()["mission"]["context"] is None
    assert all(log[column] is None for log in _logs(other_id) for column in CONTEXT_COLUMNS)
    assert _logs(user_id) == mine_before
    for secret in secrets:
        assert secret not in other.get_data(as_text=True)


def test_migration_is_idempotent(client):
    import database

    database.init_db()
    database.init_db()
    conn = database.get_db_connection()
    try:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(mission_logs)").fetchall()}
        checkin_columns = {row["name"] for row in conn.execute("PRAGMA table_info(checkins)").fetchall()}
    finally:
        conn.close()
    assert set(CONTEXT_COLUMNS) <= columns
    assert not {"performed_at", "mode", "place_key", "feeling_key", "duration_seconds"} & checkin_columns


def test_parse_checkin_context_unit():
    now = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    assert parse_checkin_context({}, now) == (None, None)
    assert parse_checkin_context(None, now) == (None, None)
    assert parse_checkin_context({"note": "   "}, now) == (None, None)
    context, error = parse_checkin_context({"mode": "now", "performed_at": "2026-10-20T01:00:00Z"}, now)
    assert error is None and context["performed_at"] == "2026-10-20T12:00:00Z"  # server time for "now"
    context, error = parse_checkin_context({"mode": "earlier", "performed_at": "2026-10-20T12:00:30Z"}, now)
    assert error is None and context["performed_at"] == "2026-10-20T12:00:00Z"  # small clock skew clamps to now
    assert parse_checkin_context({"mode": "earlier", "performed_at": "2026-10-20T12:02:00Z"}, now)[1] == "performed_at_in_future"
    assert parse_checkin_context({"mode": "earlier", "performed_at": "2026-10-19T23:59:59Z"}, now)[1] == "performed_at_not_today"
    assert parse_checkin_context({"mode": "earlier", "performed_at": "2026-10-20T03:00:00+03:30"}, now)[1] == "performed_at_not_today"
    assert parse_checkin_context({"note": "x" * 280}, now)[0]["notes"] == "x" * 280
    assert set(FEELING_KEYS) == {"light", "good", "okay", "hard_but_done", "tired"}
    assert set(PLACE_KEYS) == {"home", "work_school", "gym", "outside", "cafe", "on_the_way", "other"}

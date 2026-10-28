from datetime import date, timedelta

import database
from helpers import auth_headers, register_user
from utils.date_utils import utc_today_iso


def _join_two(client, headers):
    items = client.get("/challenges", headers=headers).get_json()["items"]
    public = [item for item in items if item["visibility"] == "public" and not item["is_joined"]][:2]
    enrollments = []
    for challenge in public:
        data = client.post(f"/challenges/{challenge['challenge_id']}/join", json={}, headers=headers).get_json()
        assert data["ok"] is True
        enrollments.append((data["enrollment_id"], challenge["challenge_id"]))
    assert len(enrollments) == 2
    return enrollments


def _user_id(client, headers):
    me = client.get("/me", headers=headers).get_json()
    return me.get("user_id") or me.get("user", {}).get("id") or me.get("id")


def _checkin(user_id, enrollment, day, status="Done", counted=1):
    enrollment_id, challenge_id = enrollment
    conn = database.get_db_connection()
    try:
        conn.execute(
            "INSERT INTO checkins (enrollment_id, user_id, challenge_id, date, status, is_counted) VALUES (?, ?, ?, ?, ?, ?)",
            (enrollment_id, user_id, challenge_id, day, status, counted),
        )
        conn.commit()
    finally:
        conn.close()


def _days_ago(n):
    return (date.fromisoformat(utc_today_iso()) - timedelta(days=n)).isoformat()


def _stats(client, headers):
    res = client.get("/me/stats", headers=headers)
    assert res.status_code == 200
    return res.get_json()["stats"]


def test_total_days_is_zero_without_checkins(client):
    headers = auth_headers(register_user(client, username="DaysNone")["access_token"])
    stats = _stats(client, headers)
    assert stats["total_days"] == 0
    assert stats["total_checkins"] == 0


def test_two_checkins_on_one_day_count_once(client):
    headers = auth_headers(register_user(client, username="DaysSame")["access_token"])
    first, second = _join_two(client, headers)
    user_id = _user_id(client, headers)
    today = utc_today_iso()
    _checkin(user_id, first, today)
    _checkin(user_id, second, today)
    stats = _stats(client, headers)
    assert stats["total_checkins"] == 2
    assert stats["total_days"] == 1


def test_total_days_counts_gaps_and_ignores_uncounted_rows(client):
    headers = auth_headers(register_user(client, username="DaysGaps")["access_token"])
    first, second = _join_two(client, headers)
    user_id = _user_id(client, headers)
    for n in (0, 1, 5, 9):
        _checkin(user_id, first, _days_ago(n))
    _checkin(user_id, second, _days_ago(3), counted=0)
    _checkin(user_id, second, _days_ago(4), status="Missed")
    stats = _stats(client, headers)
    assert stats["total_days"] == 4
    assert stats["current_streak"] == 2


def test_total_days_covers_history_older_than_140_days(client):
    headers = auth_headers(register_user(client, username="DaysOld")["access_token"])
    first, _ = _join_two(client, headers)
    user_id = _user_id(client, headers)
    for n in (0, 150, 300, 400):
        _checkin(user_id, first, _days_ago(n))
    assert _stats(client, headers)["total_days"] == 4


def test_other_users_rows_never_count(client):
    other_headers = auth_headers(register_user(client, username="DaysOther")["access_token"])
    other_first, other_second = _join_two(client, other_headers)
    other_id = _user_id(client, other_headers)
    for n in (0, 1, 2):
        _checkin(other_id, other_first, _days_ago(n))
    _checkin(other_id, other_second, _days_ago(7))

    client.delete_cookie("ringo_token")
    headers = auth_headers(register_user(client, username="DaysMine")["access_token"])
    mine, _ = _join_two(client, headers)
    _checkin(_user_id(client, headers), mine, _days_ago(1))
    assert _stats(client, headers)["total_days"] == 1
    client.delete_cookie("ringo_token")
    assert _stats(client, other_headers)["total_days"] == 4

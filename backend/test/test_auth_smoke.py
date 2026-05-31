import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_users.db"

    monkeypatch.setenv("DB_PATH", str(test_db))
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("LOCAL_LOGIN_ENABLED", "True")
    monkeypatch.setenv("JWT_COOKIE_SECURE", "0")
    monkeypatch.setenv("JWT_COOKIE_SAMESITE", "Lax")

    import auth
    import app as app_module
    import database

    auth.JWT_SECRET = "test-jwt-secret"
    database.DB_NAME = str(test_db)

    flask_app = app_module.create_app()
    flask_app.config.update(TESTING=True)

    with flask_app.test_client() as test_client:
        yield test_client


def register_user(client, username="SmokeUser", password="secret123"):
    res = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "name": username,
            "email": f"{username.lower()}@example.com",
        },
    )

    assert res.status_code == 201
    data = res.get_json()
    assert data["ok"] is True
    assert data["access_token"]

    return data


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json() == {"ok": True}


def test_register_login_and_me_with_bearer(client):
    register_data = register_user(client)

    assert register_data["username"] == "smokeuser"

    login_res = client.post(
        "/auth/login",
        json={
            "username": "smokeuser",
            "password": "secret123",
        },
    )

    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert login_data["ok"] is True
    assert login_data["access_token"]

    me_res = client.get(
        "/me",
        headers=auth_headers(login_data["access_token"]),
    )

    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["ok"] is True
    assert me_data["username"] == "smokeuser"
    assert me_data["auth_method"] == "local"


def test_join_checkin_duplicate_and_stats_core_loop(client):
    user = register_user(client, username="LoopUser")
    headers = auth_headers(user["access_token"])

    challenges_res = client.get("/challenges", headers=headers)

    assert challenges_res.status_code == 200
    challenges_data = challenges_res.get_json()
    assert challenges_data["ok"] is True
    assert len(challenges_data["items"]) > 0

    public_challenge = next(
        item for item in challenges_data["items"]
        if item["visibility"] == "public" and not item["is_joined"]
    )

    join_res = client.post(
        f"/challenges/{public_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )

    assert join_res.status_code == 200
    join_data = join_res.get_json()
    assert join_data["ok"] is True
    assert join_data["mode"] == "created"
    assert join_data["enrollment_id"]

    enrollment_id = join_data["enrollment_id"]

    enrollment_res = client.get(
        f"/me/enrollments/{enrollment_id}",
        headers=headers,
    )

    assert enrollment_res.status_code == 200
    enrollment_data = enrollment_res.get_json()
    assert enrollment_data["ok"] is True
    assert enrollment_data["enrollment"]["enrollment_id"] == enrollment_id
    assert enrollment_data["enrollment"]["today_checked"] is False
    assert enrollment_data["enrollment"]["next_reset_at"]
    assert enrollment_data["enrollment"]["reset_timezone"] == "UTC"

    checkin_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert checkin_res.status_code in (200, 201)
    checkin_data = checkin_res.get_json()
    assert checkin_data["ok"] is True

    after_checkin_res = client.get(
        f"/me/enrollments/{enrollment_id}",
        headers=headers,
    )

    assert after_checkin_res.status_code == 200
    after_checkin_data = after_checkin_res.get_json()
    assert after_checkin_data["ok"] is True
    assert after_checkin_data["enrollment"]["today_checked"] is True
    assert after_checkin_data["enrollment"]["total_checkins"] >= 1

    duplicate_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert duplicate_res.status_code in (200, 409)
    duplicate_data = duplicate_res.get_json()
    assert duplicate_data["ok"] in (True, False)

    stats_res = client.get("/me/stats", headers=headers)

    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["ok"] is True
    assert stats_data["stats"]["total_checkins"] >= 1
    assert stats_data["stats"]["current_streak"] >= 1
    assert stats_data["stats"]["total_points"] >= 10


def test_public_profile_visibility_privacy_flow(client):
    user = register_user(client, username="PrivacyUser")
    headers = auth_headers(user["access_token"])

    public_res = client.get("/api/public/profile/privacyuser")

    assert public_res.status_code == 200
    public_data = public_res.get_json()
    assert public_data["ok"] is True
    assert public_data["profile"]["username"] == "privacyuser"
    assert public_data["profile"]["name"] == "PrivacyUser"

    private_res = client.patch(
        "/api/profile/visibility",
        json={"visibility": "private"},
        headers=headers,
    )

    assert private_res.status_code == 200
    private_data = private_res.get_json()
    assert private_data["ok"] is True

    blocked_public_res = client.get("/api/public/profile/privacyuser")

    assert blocked_public_res.status_code == 403
    blocked_public_data = blocked_public_res.get_json()
    assert blocked_public_data["ok"] is False
    assert blocked_public_data["error"] == "profile_private"

    me_profile_res = client.get("/me/profile", headers=headers)

    assert me_profile_res.status_code == 200
    me_profile_data = me_profile_res.get_json()
    assert me_profile_data["ok"] is True
    assert me_profile_data["profile"]["username"] == "privacyuser"
    assert me_profile_data["profile"]["profile_visibility"] == "private"

    public_again_res = client.patch(
        "/api/profile/visibility",
        json={"visibility": "public"},
        headers=headers,
    )

    assert public_again_res.status_code == 200
    public_again_data = public_again_res.get_json()
    assert public_again_data["ok"] is True

    restored_public_res = client.get("/api/public/profile/privacyuser")

    assert restored_public_res.status_code == 200
    restored_public_data = restored_public_res.get_json()
    assert restored_public_data["ok"] is True
    assert restored_public_data["profile"]["username"] == "privacyuser"


def test_achievement_unlocks_after_first_checkin(client):
    user = register_user(client, username="AchievementUser")
    headers = auth_headers(user["access_token"])

    before_res = client.get("/me/achievements", headers=headers)

    assert before_res.status_code == 200
    before_data = before_res.get_json()
    assert before_data["ok"] is True

    before_map = {
        achievement["key"]: achievement
        for achievement in before_data["achievements"]
    }

    assert before_map["first_checkin"]["unlocked"] is False
    assert before_map["first_challenge_completed"]["unlocked"] is False

    challenges_res = client.get("/challenges", headers=headers)

    assert challenges_res.status_code == 200
    challenges_data = challenges_res.get_json()
    assert challenges_data["ok"] is True

    public_challenge = next(
        item for item in challenges_data["items"]
        if item["visibility"] == "public" and not item["is_joined"]
    )

    join_res = client.post(
        f"/challenges/{public_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )

    assert join_res.status_code == 200
    join_data = join_res.get_json()
    assert join_data["ok"] is True

    enrollment_id = join_data["enrollment_id"]

    checkin_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert checkin_res.status_code == 200
    checkin_data = checkin_res.get_json()
    assert checkin_data["ok"] is True

    reward_keys = {
        achievement["key"]
        for achievement in checkin_data["rewards"]["achievements"]
    }

    assert "first_checkin" in reward_keys
    assert "first_challenge_completed" in reward_keys
    assert checkin_data["rewards"]["achievement_xp_reward"] >= 25

    after_res = client.get("/me/achievements", headers=headers)

    assert after_res.status_code == 200
    after_data = after_res.get_json()
    assert after_data["ok"] is True

    after_map = {
        achievement["key"]: achievement
        for achievement in after_data["achievements"]
    }

    assert after_map["first_checkin"]["unlocked"] is True
    assert after_map["first_checkin"]["unlocked_at"]

    assert after_map["first_challenge_completed"]["unlocked"] is True
    assert after_map["first_challenge_completed"]["unlocked_at"]

    duplicate_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert duplicate_res.status_code in (200, 409)
    duplicate_data = duplicate_res.get_json()

    if duplicate_data.get("ok") is True:
        duplicate_reward_keys = {
            achievement["key"]
            for achievement in duplicate_data["rewards"]["achievements"]
        }

        assert "first_checkin" not in duplicate_reward_keys
        assert "first_challenge_completed" not in duplicate_reward_keys
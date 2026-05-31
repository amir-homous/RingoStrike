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


def test_profile_update_validation(client):
    user = register_user(client, username="ProfileValidationUser")
    headers = auth_headers(user["access_token"])

    invalid_name_res = client.patch(
        "/api/profile",
        json={"name": 123},
        headers=headers,
    )

    assert invalid_name_res.status_code == 400
    invalid_name_data = invalid_name_res.get_json()
    assert invalid_name_data["ok"] is False
    assert invalid_name_data["error"] == "invalid_name_type"

    long_bio_res = client.patch(
        "/api/me/profile/settings",
        json={"bio": "x" * 281},
        headers=headers,
    )

    assert long_bio_res.status_code == 400
    long_bio_data = long_bio_res.get_json()
    assert long_bio_data["ok"] is False
    assert long_bio_data["error"] == "bio_too_long"

    invalid_avatar_res = client.patch(
        "/api/me/profile/settings",
        json={"avatar_url": "javascript:alert(1)"},
        headers=headers,
    )

    assert invalid_avatar_res.status_code == 400
    invalid_avatar_data = invalid_avatar_res.get_json()
    assert invalid_avatar_data["ok"] is False
    assert invalid_avatar_data["error"] == "invalid_avatar_url"

    valid_settings_res = client.patch(
        "/api/me/profile/settings",
        json={
            "bio": "Building consistency.",
            "avatar_url": "/avatars/avatar-1.png",
            "profile_visibility": "private",
        },
        headers=headers,
    )

    assert valid_settings_res.status_code == 200
    valid_settings_data = valid_settings_res.get_json()
    assert valid_settings_data["ok"] is True

    settings_res = client.get(
        "/api/me/profile/settings",
        headers=headers,
    )

    assert settings_res.status_code == 200
    settings_data = settings_res.get_json()
    assert settings_data["ok"] is True
    assert settings_data["settings"]["bio"] == "Building consistency."
    assert settings_data["settings"]["avatar_url"] == "/avatars/avatar-1.png"
    assert settings_data["settings"]["profile_visibility"] == "private"

def test_username_validation_register_flow(client):
    invalid_cases = [
        ("ab", "invalid_username"),
        ("thisusernameiswaytoolongforrules", "invalid_username"),
        ("bad-name", "invalid_username"),
        ("bad name", "invalid_username"),
        ("admin", "invalid_username"),
        ("api", "invalid_username"),
        ("login", "invalid_username"),
        ("me", "invalid_username"),
    ]

    for username, expected_error in invalid_cases:
        safe_email_username = (
            username
            .replace(" ", "_")
            .replace("-", "_")
        )

        res = client.post(
            "/auth/register",
            json={
                "username": username,
                "password": "secret123",
                "name": "Invalid User",
                "email": f"{safe_email_username}@example.com",
            },
        )

        assert res.status_code == 400
        data = res.get_json()
        assert data["ok"] is False
        assert data["error"] == expected_error

    valid_res = client.post(
        "/auth/register",
        json={
            "username": "Valid_User_01",
            "password": "secret123",
            "name": "Valid User",
            "email": "valid_user_01@example.com",
        },
    )

    assert valid_res.status_code == 201
    valid_data = valid_res.get_json()
    assert valid_data["ok"] is True
    assert valid_data["username"] == "valid_user_01"

    duplicate_res = client.post(
        "/auth/register",
        json={
            "username": "valid_user_01",
            "password": "secret123",
            "name": "Duplicate User",
            "email": "duplicate@example.com",
        },
    )

    assert duplicate_res.status_code == 409
    duplicate_data = duplicate_res.get_json()
    assert duplicate_data["ok"] is False


def test_logout_clears_cookie_session(client):
    register_data = register_user(client, username="LogoutUser")

    cookie_me_res = client.get("/me")

    assert cookie_me_res.status_code == 200
    cookie_me_data = cookie_me_res.get_json()
    assert cookie_me_data["ok"] is True
    assert cookie_me_data["username"] == "logoutuser"

    logout_res = client.post("/auth/logout")

    assert logout_res.status_code == 200
    logout_data = logout_res.get_json()
    assert logout_data["ok"] is True

    after_logout_res = client.get("/me")

    assert after_logout_res.status_code == 401
    after_logout_data = after_logout_res.get_json()
    assert after_logout_data["ok"] is False
    assert after_logout_data["error"] == "unauthorized"

    bearer_me_res = client.get(
        "/me",
        headers=auth_headers(register_data["access_token"]),
    )

    assert bearer_me_res.status_code == 200
    bearer_me_data = bearer_me_res.get_json()
    assert bearer_me_data["ok"] is True
    assert bearer_me_data["username"] == "logoutuser"


def test_invite_only_challenge_join_flow(client):
    user = register_user(client, username="InviteUser")
    headers = auth_headers(user["access_token"])

    import database

    conn = database.get_db_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO challenges (
                name,
                description,
                visibility,
                status,
                duration_days,
                join_code,
                max_members,
                requires_proof,
                checkin_method,
                goal_type,
                tags
            )
            VALUES (
                'Invite Only Test',
                'Private launch test challenge',
                'Invite-only',
                'Active',
                14,
                'SECRET123',
                0,
                0,
                'Manual',
                'Daily',
                'test,invite'
            )
            """
        )
        invite_challenge_id = cur.lastrowid
        conn.commit()
    finally:
        conn.close()

    list_res = client.get("/challenges", headers=headers)

    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert list_data["ok"] is True

    invite_item = next(
        item for item in list_data["items"]
        if item["challenge_id"] == invite_challenge_id
    )

    assert invite_item["visibility"] == "invite-only"
    assert invite_item["needs_code"] is True
    assert invite_item["is_joined"] is False

    missing_code_res = client.post(
        f"/challenges/{invite_challenge_id}/join",
        json={},
        headers=headers,
    )

    assert missing_code_res.status_code == 400
    missing_code_data = missing_code_res.get_json()
    assert missing_code_data["ok"] is False
    assert missing_code_data["error"] == "join_code_required"

    invalid_code_res = client.post(
        f"/challenges/{invite_challenge_id}/join",
        json={"join_code": "WRONG"},
        headers=headers,
    )

    assert invalid_code_res.status_code == 403
    invalid_code_data = invalid_code_res.get_json()
    assert invalid_code_data["ok"] is False
    assert invalid_code_data["error"] == "invalid_join_code"

    invalid_type_res = client.post(
        f"/challenges/{invite_challenge_id}/join",
        json={"join_code": 123},
        headers=headers,
    )

    assert invalid_type_res.status_code == 400
    invalid_type_data = invalid_type_res.get_json()
    assert invalid_type_data["ok"] is False
    assert invalid_type_data["error"] == "invalid_join_code_type"

    too_long_res = client.post(
        f"/challenges/{invite_challenge_id}/join",
        json={"join_code": "x" * 65},
        headers=headers,
    )

    assert too_long_res.status_code == 400
    too_long_data = too_long_res.get_json()
    assert too_long_data["ok"] is False
    assert too_long_data["error"] == "join_code_too_long"

    valid_join_res = client.post(
        f"/challenges/{invite_challenge_id}/join",
        json={"join_code": "SECRET123"},
        headers=headers,
    )

    assert valid_join_res.status_code == 200
    valid_join_data = valid_join_res.get_json()
    assert valid_join_data["ok"] is True
    assert valid_join_data["mode"] == "created"
    assert valid_join_data["challenge_id"] == invite_challenge_id
    assert valid_join_data["enrollment_id"]

    second_join_res = client.post(
        f"/challenges/{invite_challenge_id}/join",
        json={"join_code": "SECRET123"},
        headers=headers,
    )

    assert second_join_res.status_code == 200
    second_join_data = second_join_res.get_json()
    assert second_join_data["ok"] is True
    assert second_join_data["mode"] == "existing"
    assert second_join_data["challenge_id"] == invite_challenge_id
    assert second_join_data["enrollment_id"] == valid_join_data["enrollment_id"]

def test_public_consistency_and_achievements_respect_profile_privacy(client):
    user = register_user(client, username="PublicPrivacyUser")
    headers = auth_headers(user["access_token"])

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

    public_consistency_res = client.get(
        "/api/public/profile/publicprivacyuser/consistency"
    )

    assert public_consistency_res.status_code == 200
    public_consistency_data = public_consistency_res.get_json()
    assert public_consistency_data["ok"] is True
    assert len(public_consistency_data["days"]) >= 1

    public_achievements_res = client.get(
        "/api/public/profile/publicprivacyuser/achievements"
    )

    assert public_achievements_res.status_code == 200
    public_achievements_data = public_achievements_res.get_json()
    assert public_achievements_data["ok"] is True

    achievement_keys = {
        achievement["key"]
        for achievement in public_achievements_data["achievements"]
    }

    assert "first_checkin" in achievement_keys
    assert "first_challenge_completed" in achievement_keys

    private_res = client.patch(
        "/api/profile/visibility",
        json={"visibility": "private"},
        headers=headers,
    )

    assert private_res.status_code == 200
    private_data = private_res.get_json()
    assert private_data["ok"] is True

    blocked_consistency_res = client.get(
        "/api/public/profile/publicprivacyuser/consistency"
    )

    assert blocked_consistency_res.status_code == 403
    blocked_consistency_data = blocked_consistency_res.get_json()
    assert blocked_consistency_data["ok"] is False
    assert blocked_consistency_data["error"] == "profile_private"

    blocked_achievements_res = client.get(
        "/api/public/profile/publicprivacyuser/achievements"
    )

    assert blocked_achievements_res.status_code == 403
    blocked_achievements_data = blocked_achievements_res.get_json()
    assert blocked_achievements_data["ok"] is False
    assert blocked_achievements_data["error"] == "profile_private"

def test_leaderboard_rank_and_enrollment_reset_metadata(client):
    first_user = register_user(client, username="RankUserOne")
    first_headers = auth_headers(first_user["access_token"])

    second_user = register_user(client, username="RankUserTwo")
    second_headers = auth_headers(second_user["access_token"])
    client.delete_cookie("ringo_token")

    challenges_res = client.get("/challenges", headers=first_headers)

    assert challenges_res.status_code == 200
    challenges_data = challenges_res.get_json()
    assert challenges_data["ok"] is True

    public_challenge = next(
        item for item in challenges_data["items"]
        if item["visibility"] == "public" and not item["is_joined"]
    )

    challenge_id = public_challenge["challenge_id"]

    first_join_res = client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=first_headers,
    )

    assert first_join_res.status_code == 200
    first_join_data = first_join_res.get_json()
    assert first_join_data["ok"] is True
    first_enrollment_id = first_join_data["enrollment_id"]

    second_join_res = client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=second_headers,
    )

    assert second_join_res.status_code == 200
    second_join_data = second_join_res.get_json()
    assert second_join_data["ok"] is True
    second_enrollment_id = second_join_data["enrollment_id"]

    first_enrollment_res = client.get(
        f"/me/enrollments/{first_enrollment_id}",
        headers=first_headers,
    )

    assert first_enrollment_res.status_code == 200
    first_enrollment_data = first_enrollment_res.get_json()
    assert first_enrollment_data["ok"] is True

    first_enrollment = first_enrollment_data["enrollment"]

    assert first_enrollment["today_date"]
    assert first_enrollment["next_reset_at"]
    assert first_enrollment["reset_timezone"] == "UTC"

    first_checkin_res = client.post(
        f"/me/challenges/{first_enrollment_id}/checkin",
        headers=first_headers,
    )

    assert first_checkin_res.status_code == 200
    first_checkin_data = first_checkin_res.get_json()
    assert first_checkin_data["ok"] is True

    leaderboard_res = client.get(
        f"/me/enrollments/{first_enrollment_id}/leaderboard",
        headers=first_headers,
    )

    assert leaderboard_res.status_code == 200
    leaderboard_data = leaderboard_res.get_json()
    assert leaderboard_data["ok"] is True

    assert "overall" in leaderboard_data
    assert "today" in leaderboard_data
    assert "tie_breakers" in leaderboard_data

    assert leaderboard_data["tie_breakers"]["overall"] == [
        "total_checkins_desc",
        "current_streak_desc",
        "name_asc",
        "enrollment_id_asc",
    ]

    assert leaderboard_data["tie_breakers"]["today"] == [
        "current_streak_desc",
        "total_checkins_desc",
        "name_asc",
        "enrollment_id_asc",
    ]

    overall = leaderboard_data["overall"]
    today = leaderboard_data["today"]

    assert len(overall) >= 2
    assert len(today) >= 1

    first_row = next(
        row for row in overall
        if row["enrollment_id"] == first_enrollment_id
    )

    second_row = next(
        row for row in overall
        if row["enrollment_id"] == second_enrollment_id
    )

    assert first_row["rank"] == 1
    assert first_row["today_checked"] is True
    assert first_row["total_checkins"] >= 1
    assert first_row["current_streak"] >= 1

    assert second_row["rank"] >= 2
    assert second_row["today_checked"] is False
    assert second_row["total_checkins"] == 0
    assert second_row["current_streak"] == 0

    today_row = next(
        row for row in today
        if row["enrollment_id"] == first_enrollment_id
    )

    assert today_row["rank"] == 1
    assert today_row["today_checked"] is True

def test_challenge_access_rules_for_private_archived_and_missing(client):
    user = register_user(client, username="ChallengeAccessUser")
    headers = auth_headers(user["access_token"])

    import database

    conn = database.get_db_connection()
    try:
        private_cur = conn.execute(
            """
            INSERT INTO challenges (
                name,
                description,
                visibility,
                status,
                duration_days,
                join_code,
                max_members,
                requires_proof,
                checkin_method,
                goal_type,
                tags
            )
            VALUES (
                'Private Test Challenge',
                'Should not be joinable directly',
                'Private',
                'Active',
                14,
                NULL,
                0,
                0,
                'Manual',
                'Daily',
                'test,private'
            )
            """
        )
        private_challenge_id = private_cur.lastrowid

        archived_cur = conn.execute(
            """
            INSERT INTO challenges (
                name,
                description,
                visibility,
                status,
                duration_days,
                join_code,
                max_members,
                requires_proof,
                checkin_method,
                goal_type,
                tags
            )
            VALUES (
                'Archived Test Challenge',
                'Should not appear in discovery or allow join',
                'Public',
                'Archived',
                14,
                NULL,
                0,
                0,
                'Manual',
                'Daily',
                'test,archived'
            )
            """
        )
        archived_challenge_id = archived_cur.lastrowid

        public_cur = conn.execute(
            """
            INSERT INTO challenges (
                name,
                description,
                visibility,
                status,
                duration_days,
                join_code,
                max_members,
                requires_proof,
                checkin_method,
                goal_type,
                tags
            )
            VALUES (
                'Readable Public Challenge',
                'Public challenge detail should be readable',
                'Public',
                'Active',
                7,
                NULL,
                0,
                0,
                'Manual',
                'Daily',
                'test,public'
            )
            """
        )
        public_challenge_id = public_cur.lastrowid

        conn.commit()
    finally:
        conn.close()

    list_res = client.get("/challenges", headers=headers)

    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert list_data["ok"] is True

    challenge_ids = {
        item["challenge_id"]
        for item in list_data["items"]
    }

    assert private_challenge_id not in challenge_ids
    assert archived_challenge_id not in challenge_ids
    assert public_challenge_id in challenge_ids

    private_join_res = client.post(
        f"/challenges/{private_challenge_id}/join",
        json={},
        headers=headers,
    )

    assert private_join_res.status_code == 403
    private_join_data = private_join_res.get_json()
    assert private_join_data["ok"] is False
    assert private_join_data["error"] == "challenge_private"

    archived_join_res = client.post(
        f"/challenges/{archived_challenge_id}/join",
        json={},
        headers=headers,
    )

    assert archived_join_res.status_code == 403
    archived_join_data = archived_join_res.get_json()
    assert archived_join_data["ok"] is False
    assert archived_join_data["error"] == "challenge_inactive"

    public_detail_res = client.get(
        f"/challenges/{public_challenge_id}",
        headers=headers,
    )

    assert public_detail_res.status_code == 200
    public_detail_data = public_detail_res.get_json()
    assert public_detail_data["ok"] is True
    assert public_detail_data["item"]["challenge_id"] == public_challenge_id
    assert public_detail_data["item"]["visibility"] == "Public"
    assert public_detail_data["item"]["status"] == "Active"

    missing_detail_res = client.get("/challenges/999999", headers=headers)

    assert missing_detail_res.status_code == 404
    missing_detail_data = missing_detail_res.get_json()
    assert missing_detail_data["ok"] is False
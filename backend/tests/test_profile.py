from helpers import auth_headers, insert_challenge, register_user


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


def test_public_profile_username_lookup_is_normalized(client):
    user = register_user(client, username="NormalizedPublicUser")
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

    checkin_res = client.post(
        f"/me/challenges/{join_data['enrollment_id']}/checkin",
        headers=headers,
    )

    assert checkin_res.status_code == 200

    spaced_username = "%20NormalizedPublicUser%20"

    profile_res = client.get(f"/api/public/profile/{spaced_username}")
    consistency_res = client.get(
        f"/api/public/profile/{spaced_username}/consistency"
    )
    achievements_res = client.get(
        f"/api/public/profile/{spaced_username}/achievements"
    )

    assert profile_res.status_code == 200
    profile_data = profile_res.get_json()
    assert profile_data["ok"] is True
    assert profile_data["profile"]["username"] == "normalizedpublicuser"

    assert consistency_res.status_code == 200
    consistency_data = consistency_res.get_json()
    assert consistency_data["ok"] is True

    assert achievements_res.status_code == 200
    achievements_data = achievements_res.get_json()
    assert achievements_data["ok"] is True


def test_profile_visibility_validation(client):
    user = register_user(client, username="VisibilityValidationUser")
    headers = auth_headers(user["access_token"])

    normalized_res = client.patch(
        "/api/profile/visibility",
        json={"visibility": " Private "},
        headers=headers,
    )

    assert normalized_res.status_code == 200
    normalized_data = normalized_res.get_json()
    assert normalized_data["ok"] is True
    assert normalized_data["visibility"] == "private"

    invalid_type_res = client.patch(
        "/api/profile/visibility",
        json={"visibility": 123},
        headers=headers,
    )

    assert invalid_type_res.status_code == 400
    invalid_type_data = invalid_type_res.get_json()
    assert invalid_type_data["ok"] is False
    assert invalid_type_data["error"] == "invalid_visibility_type"

    invalid_value_res = client.patch(
        "/api/profile/visibility",
        json={"visibility": "friends"},
        headers=headers,
    )

    assert invalid_value_res.status_code == 400
    invalid_value_data = invalid_value_res.get_json()
    assert invalid_value_data["ok"] is False
    assert invalid_value_data["error"] == "invalid_visibility"

    invalid_body_res = client.patch(
        "/api/profile/visibility",
        json=[],
        headers=headers,
    )

    assert invalid_body_res.status_code == 400
    invalid_body_data = invalid_body_res.get_json()
    assert invalid_body_data["ok"] is False
    assert invalid_body_data["error"] == "invalid_json_body"


def test_profile_visibility_updates_user_timestamp(client):
    user = register_user(client, username="VisibilityTimestampUser")
    headers = auth_headers(user["access_token"])

    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            UPDATE users
            SET updated_at = ?
            WHERE id = ?
            """,
            (
                "2000-01-01 00:00:00",
                user["user_id"],
            ),
        )
        conn.commit()
    finally:
        conn.close()

    res = client.patch(
        "/api/profile/visibility",
        json={"visibility": "private"},
        headers=headers,
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True

    conn = database.get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT profile_visibility, updated_at
            FROM users
            WHERE id = ?
            """,
            (user["user_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert row["profile_visibility"] == "private"
    assert row["updated_at"] != "2000-01-01 00:00:00"


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

    protocol_relative_avatar_res = client.patch(
        "/api/me/profile/settings",
        json={"avatar_url": "//example.com/avatar.png"},
        headers=headers,
    )

    assert protocol_relative_avatar_res.status_code == 400
    protocol_relative_avatar_data = protocol_relative_avatar_res.get_json()
    assert protocol_relative_avatar_data["ok"] is False
    assert protocol_relative_avatar_data["error"] == "invalid_avatar_url"

    protocol_relative_profile_res = client.patch(
        "/api/profile",
        json={"avatar_url": "//example.com/avatar.png"},
        headers=headers,
    )

    assert protocol_relative_profile_res.status_code == 400
    protocol_relative_profile_data = protocol_relative_profile_res.get_json()
    assert protocol_relative_profile_data["ok"] is False
    assert protocol_relative_profile_data["error"] == "invalid_avatar_url"

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


def test_profile_update_preserves_omitted_fields(client):
    user = register_user(client, username="PartialProfileUser")
    headers = auth_headers(user["access_token"])

    full_update_res = client.patch(
        "/api/profile",
        json={
            "name": "Partial Player",
            "bio": "Original bio.",
            "avatar_url": "/avatars/avatar-2.png",
        },
        headers=headers,
    )

    assert full_update_res.status_code == 200
    full_update_data = full_update_res.get_json()
    assert full_update_data["ok"] is True

    partial_update_res = client.patch(
        "/api/profile",
        json={
            "bio": "Updated bio only.",
        },
        headers=headers,
    )

    assert partial_update_res.status_code == 200
    partial_update_data = partial_update_res.get_json()
    assert partial_update_data["ok"] is True

    profile_res = client.get("/me/profile", headers=headers)

    assert profile_res.status_code == 200
    profile_data = profile_res.get_json()
    assert profile_data["ok"] is True
    assert profile_data["profile"]["name"] == "Partial Player"
    assert profile_data["profile"]["bio"] == "Updated bio only."
    assert profile_data["profile"]["avatar_url"] == "/avatars/avatar-2.png"


def test_profile_update_rejects_non_object_json(client):
    user = register_user(client, username="ProfileBodyUser")
    headers = auth_headers(user["access_token"])

    res = client.patch(
        "/api/profile",
        json=[],
        headers=headers,
    )

    assert res.status_code == 400
    data = res.get_json()
    assert data["ok"] is False
    assert data["error"] == "invalid_json_body"


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


def test_public_identity_endpoints_block_private_profile_with_normalized_username(client):
    user = register_user(client, username="PrivateNormalizedUser")
    headers = auth_headers(user["access_token"])

    private_res = client.patch(
        "/api/profile/visibility",
        json={"visibility": "private"},
        headers=headers,
    )

    assert private_res.status_code == 200

    spaced_username = "%20PrivateNormalizedUser%20"
    endpoints = [
        f"/api/public/profile/{spaced_username}",
        f"/api/public/profile/{spaced_username}/consistency",
        f"/api/public/profile/{spaced_username}/achievements",
    ]

    for endpoint in endpoints:
        res = client.get(endpoint)
        data = res.get_json()

        assert res.status_code == 403
        assert data == {
            "ok": False,
            "error": "profile_private",
        }


def test_public_identity_endpoints_share_not_found_response_shape(client):
    endpoints = [
        "/api/public/profile/%20missing_identity_user%20",
        "/api/public/profile/%20missing_identity_user%20/consistency",
        "/api/public/profile/%20missing_identity_user%20/achievements",
    ]

    for endpoint in endpoints:
        res = client.get(endpoint)
        data = res.get_json()

        assert res.status_code == 404
        assert data == {
            "ok": False,
            "error": "profile_not_found",
        }


def test_public_consistency_returns_unique_dates(client):
    user = register_user(client, username="UniqueConsistencyUser")
    today = "2026-01-15"
    challenge_one_id = insert_challenge(
        name="Unique Consistency One",
        description="First same-day public consistency challenge.",
        visibility="Public",
    )
    challenge_two_id = insert_challenge(
        name="Unique Consistency Two",
        description="Second same-day public consistency challenge.",
        visibility="Public",
    )

    import database

    conn = database.get_db_connection()
    try:
        for challenge_id in (
            challenge_one_id,
            challenge_two_id,
        ):
            cur = conn.execute(
                """
                INSERT INTO enrollments (
                    user_id,
                    challenge_id,
                    status
                )
                VALUES (?, ?, 'Active')
                """,
                (
                    user["user_id"],
                    challenge_id,
                ),
            )
            conn.execute(
                """
                INSERT INTO checkins (
                    enrollment_id,
                    user_id,
                    challenge_id,
                    date,
                    status,
                    is_counted
                )
                VALUES (?, ?, ?, ?, 'Done', 1)
                """,
                (
                    cur.lastrowid,
                    user["user_id"],
                    challenge_id,
                    today,
                ),
            )
        conn.commit()
    finally:
        conn.close()

    res = client.get(
        "/api/public/profile/uniqueconsistencyuser/consistency"
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["days"].count(today) == 1


def test_public_profile_not_found_returns_404(client):
    res = client.get("/api/public/profile/does_not_exist_user")

    assert res.status_code == 404

    data = res.get_json()

    assert data["ok"] is False
    assert data["error"] == "profile_not_found"


def test_public_consistency_not_found_returns_404(client):
    res = client.get("/api/public/profile/does_not_exist_user/consistency")

    assert res.status_code == 404

    data = res.get_json()

    assert data["ok"] is False
    assert data["error"] == "profile_not_found"


def test_public_achievements_not_found_returns_404(client):
    res = client.get("/api/public/profile/does_not_exist_user/achievements")

    assert res.status_code == 404

    data = res.get_json()

    assert data["ok"] is False
    assert data["error"] == "profile_not_found"

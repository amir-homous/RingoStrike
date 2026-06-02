from datetime import datetime, timedelta

from helpers import auth_headers, insert_challenge, register_user
from utils.date_utils import utc_today_iso


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


def test_uncounted_checkins_do_not_affect_progress_surfaces(client):
    user = register_user(client, username="UncountedProgressUser")
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
    challenge_id = public_challenge["challenge_id"]

    checkin_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert checkin_res.status_code == 200
    checkin_data = checkin_res.get_json()
    assert checkin_data["ok"] is True

    today = utc_today_iso()
    yesterday = (
        datetime.strptime(today, "%Y-%m-%d").date()
        - timedelta(days=1)
    ).isoformat()
    two_days_ago = (
        datetime.strptime(today, "%Y-%m-%d").date()
        - timedelta(days=2)
    ).isoformat()

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
                is_counted
            )
            VALUES (?, ?, ?, ?, 'Done', 0)
            """,
            (
                enrollment_id,
                user["user_id"],
                challenge_id,
                yesterday,
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
            VALUES (?, ?, ?, ?, 'Skipped', 1)
            """,
            (
                enrollment_id,
                user["user_id"],
                challenge_id,
                two_days_ago,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    enrollment_res = client.get(
        f"/me/enrollments/{enrollment_id}",
        headers=headers,
    )

    assert enrollment_res.status_code == 200
    enrollment_data = enrollment_res.get_json()
    assert enrollment_data["ok"] is True
    assert enrollment_data["enrollment"]["total_checkins"] == 1
    assert enrollment_data["enrollment"]["current_streak"] == 1

    recent_log_dates = {
        item["date"]
        for item in enrollment_data["recent_logs"]
    }

    assert today in recent_log_dates
    assert yesterday not in recent_log_dates

    stats_res = client.get("/me/stats", headers=headers)

    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["ok"] is True
    assert stats_data["stats"]["total_checkins"] == 1
    assert stats_data["stats"]["current_streak"] == 1

    consistency_res = client.get("/me/consistency", headers=headers)

    assert consistency_res.status_code == 200
    consistency_data = consistency_res.get_json()
    assert consistency_data["ok"] is True

    consistency_dates = {
        item["date"]
        for item in consistency_data["days"]
    }

    assert today in consistency_dates
    assert yesterday not in consistency_dates
    assert two_days_ago not in consistency_dates

    public_consistency_res = client.get(
        "/api/public/profile/uncountedprogressuser/consistency"
    )

    assert public_consistency_res.status_code == 200
    public_consistency_data = public_consistency_res.get_json()
    assert public_consistency_data["ok"] is True
    assert today in public_consistency_data["days"]
    assert yesterday not in public_consistency_data["days"]
    assert two_days_ago not in public_consistency_data["days"]

    leaderboard_res = client.get(
        f"/me/enrollments/{enrollment_id}/leaderboard",
        headers=headers,
    )

    assert leaderboard_res.status_code == 200
    leaderboard_data = leaderboard_res.get_json()
    assert leaderboard_data["ok"] is True

    leaderboard_row = next(
        item
        for item in leaderboard_data["overall"]
        if item["enrollment_id"] == enrollment_id
    )

    assert leaderboard_row["total_checkins"] == 1
    assert leaderboard_row["current_streak"] == 1

    history_res = client.get(
        f"/me/challenges/{enrollment_id}/history?days=3",
        headers=headers,
    )

    assert history_res.status_code == 200
    history_data = history_res.get_json()
    assert history_data["ok"] is True
    assert history_data["summary"]["checked_days"] == 1

    history_by_date = {
        item["date"]: item
        for item in history_data["items"]
    }

    assert history_by_date[today]["status"] == "Done"
    assert history_by_date[today]["is_counted"] is True
    assert history_by_date[yesterday]["status"] == "Done"
    assert history_by_date[yesterday]["is_counted"] is False
    assert history_by_date[two_days_ago]["status"] == "Skipped"
    assert history_by_date[two_days_ago]["is_counted"] is False


def test_invite_only_challenge_join_flow(client):
    user = register_user(client, username="InviteUser")
    headers = auth_headers(user["access_token"])

    invite_challenge_id = insert_challenge(
        name="Invite Only Test",
        description="Private launch test challenge",
        visibility="Invite-only",
        status="Active",
        duration_days=14,
        join_code="SECRET123",
        tags="test,invite",
    )

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


def test_challenge_access_rules_for_private_archived_and_missing(client):
    user = register_user(client, username="ChallengeAccessUser")
    headers = auth_headers(user["access_token"])

    private_challenge_id = insert_challenge(
        name="Private Test Challenge",
        description="Should not be joinable directly",
        visibility="Private",
        status="Active",
        duration_days=14,
        tags="test,private",
    )

    archived_challenge_id = insert_challenge(
        name="Archived Test Challenge",
        description="Should not appear in discovery or allow join",
        visibility="Public",
        status="Archived",
        duration_days=14,
        tags="test,archived",
    )

    public_challenge_id = insert_challenge(
        name="Readable Public Challenge",
        description="Public challenge detail should be readable",
        visibility="Public",
        status="Active",
        duration_days=7,
        tags="test,public",
    )

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

    private_detail_res = client.get(
        f"/challenges/{private_challenge_id}",
        headers=headers,
    )

    assert private_detail_res.status_code == 403
    private_detail_data = private_detail_res.get_json()
    assert private_detail_data["ok"] is False
    assert private_detail_data["error"] == "challenge_private"

    private_members_res = client.get(
        f"/challenges/{private_challenge_id}/members",
        headers=headers,
    )

    assert private_members_res.status_code == 403
    private_members_data = private_members_res.get_json()
    assert private_members_data["ok"] is False
    assert private_members_data["error"] == "challenge_private"

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

    public_join_res = client.post(
        f"/challenges/{public_challenge_id}/join",
        json={},
        headers=headers,
    )

    assert public_join_res.status_code == 200
    public_join_data = public_join_res.get_json()
    assert public_join_data["ok"] is True

    public_members_res = client.get(
        f"/challenges/{public_challenge_id}/members",
        headers=headers,
    )

    assert public_members_res.status_code == 200
    public_members_data = public_members_res.get_json()
    assert public_members_data["ok"] is True

    public_member = next(
        item
        for item in public_members_data["items"]
        if item["user_id"] == user["user_id"]
    )

    assert public_member["username"] == "challengeaccessuser"
    assert public_member["telegram_username"] == "challengeaccessuser"

    missing_detail_res = client.get("/challenges/999999", headers=headers)

    assert missing_detail_res.status_code == 404
    missing_detail_data = missing_detail_res.get_json()
    assert missing_detail_data["ok"] is False

    missing_members_res = client.get("/challenges/999999/members", headers=headers)

    assert missing_members_res.status_code == 404
    missing_members_data = missing_members_res.get_json()
    assert missing_members_data["ok"] is False
    assert missing_members_data["error"] == "challenge_not_found"


def test_challenge_members_pagination_reports_real_next_page(client):
    user_one = register_user(client, username="MembersPageOne")
    user_two = register_user(client, username="MembersPageTwo")
    user_three = register_user(client, username="MembersPageThree")

    challenge_id = insert_challenge(
        name="Members Pagination Challenge",
        description="Used to verify public member pagination.",
        visibility="Public",
        status="Active",
    )

    import database

    conn = database.get_db_connection()
    try:
        for user_id in (
            user_one["user_id"],
            user_two["user_id"],
        ):
            conn.execute(
                """
                INSERT INTO enrollments (
                    user_id,
                    challenge_id,
                    status
                )
                VALUES (?, ?, 'Active')
                """,
                (
                    user_id,
                    challenge_id,
                ),
            )
        conn.commit()
    finally:
        conn.close()

    exact_page_res = client.get(
        f"/challenges/{challenge_id}/members?limit=2"
    )

    assert exact_page_res.status_code == 200
    exact_page_data = exact_page_res.get_json()
    assert exact_page_data["ok"] is True
    assert len(exact_page_data["items"]) == 2
    assert exact_page_data["has_more"] is False

    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO enrollments (
                user_id,
                challenge_id,
                status
            )
            VALUES (?, ?, 'Active')
            """,
            (
                user_three["user_id"],
                challenge_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    first_page_res = client.get(
        f"/challenges/{challenge_id}/members?limit=2"
    )
    negative_offset_res = client.get(
        f"/challenges/{challenge_id}/members?limit=2&offset=-10"
    )

    assert first_page_res.status_code == 200
    first_page_data = first_page_res.get_json()
    assert first_page_data["ok"] is True
    assert len(first_page_data["items"]) == 2
    assert first_page_data["has_more"] is True

    assert negative_offset_res.status_code == 200
    negative_offset_data = negative_offset_res.get_json()
    assert negative_offset_data["ok"] is True
    assert negative_offset_data["items"] == first_page_data["items"]


def test_challenge_discovery_ignores_left_enrollments(client):
    user = register_user(client, username="LeftEnrollmentUser")
    headers = auth_headers(user["access_token"])
    user_id = user["user_id"]

    private_challenge_id = insert_challenge(
        name="Left Private Challenge",
        description="Left private enrollment should not reveal challenge.",
        visibility="Private",
        status="Active",
        duration_days=14,
        tags="test,left,private",
    )

    public_challenge_id = insert_challenge(
        name="Left Public Challenge",
        description="Left public enrollment should not look joined.",
        visibility="Public",
        status="Active",
        duration_days=14,
        tags="test,left,public",
    )

    import database

    conn = database.get_db_connection()
    try:
        for challenge_id in (
            private_challenge_id,
            public_challenge_id,
        ):
            conn.execute(
                """
                INSERT INTO enrollments (
                    user_id,
                    challenge_id,
                    status
                )
                VALUES (?, ?, 'Left')
                """,
                (
                    user_id,
                    challenge_id,
                ),
            )
        conn.commit()
    finally:
        conn.close()

    list_res = client.get("/challenges", headers=headers)

    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert list_data["ok"] is True

    items_by_id = {
        item["challenge_id"]: item
        for item in list_data["items"]
    }

    assert private_challenge_id not in items_by_id
    assert public_challenge_id in items_by_id
    assert items_by_id[public_challenge_id]["is_joined"] is False
    assert items_by_id[public_challenge_id]["enrollment_id"] is None


def test_challenge_join_rejects_non_object_json(client):
    user = register_user(
        client,
        username="ChallengeJsonUser",
    )

    challenge_id = insert_challenge(
        name="Malformed Join Payload Challenge",
        description="Used to verify malformed join playload handling",
        visibility="Public",
    )

    res = client.post(
        f"/challenges/{challenge_id}/join",
        json=["not", "an", "object"],
        headers=auth_headers(user["access_token"]),
    )

    assert res.status_code == 400
    data = res.get_json()
    assert data["ok"] is False
    assert data["error"] == "invalid_json_body"

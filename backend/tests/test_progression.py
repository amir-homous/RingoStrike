from helpers import auth_headers, insert_challenge, register_user
from utils.date_utils import utc_today_iso


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
    assert checkin_data["rewards"]["xp_total"] >= (
        10 + checkin_data["rewards"]["achievement_xp_reward"]
    )

    stats_res = client.get("/me/stats", headers=headers)

    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["ok"] is True
    assert stats_data["stats"]["total_points"] >= (
        10 + checkin_data["rewards"]["achievement_xp_reward"]
    )

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


def test_checkin_requires_active_enrollment(client):
    user = register_user(client, username="InactiveCheckinUser")
    headers = auth_headers(user["access_token"])
    challenge_id = insert_challenge(
        name="Inactive Checkin Challenge",
        description="Used to verify inactive enrollment check-ins.",
        visibility="Public",
    )

    import database

    conn = database.get_db_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO enrollments (
                user_id,
                challenge_id,
                status
            )
            VALUES (?, ?, 'Left')
            """,
            (
                user["user_id"],
                challenge_id,
            ),
        )
        enrollment_id = cur.lastrowid
        conn.commit()
    finally:
        conn.close()

    res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert res.status_code == 403
    data = res.get_json()
    assert data["ok"] is False
    assert data["error"] == "enrollment_inactive"

    conn = database.get_db_connection()
    try:
        checkin_count = conn.execute(
            "SELECT COUNT(*) AS n FROM checkins WHERE enrollment_id = ?",
            (enrollment_id,),
        ).fetchone()["n"]
    finally:
        conn.close()

    assert checkin_count == 0


def test_checkin_recovers_existing_uncounted_today_row(client):
    user = register_user(client, username="RecoveredCheckinUser")
    headers = auth_headers(user["access_token"])
    challenge_id = insert_challenge(
        name="Recovered Checkin Challenge",
        description="Used to verify existing same-day check-ins are counted.",
        visibility="Public",
    )
    today = utc_today_iso()

    import database

    conn = database.get_db_connection()
    try:
        enrollment_cur = conn.execute(
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
        enrollment_id = enrollment_cur.lastrowid
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
            VALUES (?, ?, ?, ?, 'Skipped', 0)
            """,
            (
                enrollment_id,
                user["user_id"],
                challenge_id,
                today,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True

    conn = database.get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT status, is_counted
            FROM checkins
            WHERE enrollment_id = ? AND date = ?
            """,
            (
                enrollment_id,
                today,
            ),
        ).fetchone()
    finally:
        conn.close()

    assert row["status"] == "Done"
    assert row["is_counted"] == 1

    stats_res = client.get("/me/stats", headers=headers)

    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["ok"] is True
    assert stats_data["stats"]["total_checkins"] == 1


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

    unauthorized_leaderboard_res = client.get(
        f"/me/enrollments/{first_enrollment_id}/leaderboard",
        headers=second_headers,
    )

    assert unauthorized_leaderboard_res.status_code == 404
    unauthorized_leaderboard_data = unauthorized_leaderboard_res.get_json()
    assert unauthorized_leaderboard_data["ok"] is False
    assert unauthorized_leaderboard_data["error"] == "not_found"

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

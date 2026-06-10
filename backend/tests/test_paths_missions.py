from datetime import datetime, timedelta, timezone

from helpers import auth_headers, register_user


def test_paths_seed_does_not_create_legacy_unlinked_challenges(client):
    import database

    conn = database.get_db_connection()
    try:
        active_unlinked = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM challenges
            WHERE status = 'Active'
              AND path_id IS NULL
            """
        ).fetchone()["count"]
        active_without_missions = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM challenges
            WHERE status = 'Active'
              AND NOT EXISTS (
                SELECT 1
                FROM missions
                WHERE missions.challenge_id = challenges.id
                  AND missions.status = 'Active'
              )
            """
        ).fetchone()["count"]
        canonical_seeded = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM challenges
            WHERE status = 'Active'
              AND path_id IS NOT NULL
            """
        ).fetchone()["count"]
    finally:
        conn.close()

    assert active_unlinked == 0
    assert active_without_missions == 0
    assert canonical_seeded == 15


def test_paths_seed_and_start_user_path(client):
    user = register_user(client, username="PathStarter")
    headers = auth_headers(user["access_token"])

    paths_res = client.get("/paths", headers=headers)

    assert paths_res.status_code == 200
    paths_data = paths_res.get_json()
    assert paths_data["ok"] is True
    assert len(paths_data["items"]) >= 5

    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    challenges_res = client.get(f"/paths/{fitness_path['path_id']}/challenges")

    assert challenges_res.status_code == 200
    challenges_data = challenges_res.get_json()
    assert challenges_data["ok"] is True
    assert len(challenges_data["items"]) >= 3
    assert all(item["difficulty"] for item in challenges_data["items"])
    assert all(item["missions"] for item in challenges_data["items"])

    start_res = client.post(
        f"/paths/{fitness_path['path_id']}/start",
        headers=headers,
    )

    assert start_res.status_code == 200
    start_data = start_res.get_json()
    assert start_data["ok"] is True
    assert start_data["mode"] == "created"
    assert start_data["path"]["key"] == "fitness"

    repeat_res = client.post(
        f"/paths/{fitness_path['path_id']}/start",
        headers=headers,
    )

    assert repeat_res.status_code == 200
    repeat_data = repeat_res.get_json()
    assert repeat_data["ok"] is True
    assert repeat_data["mode"] == "existing"


def test_today_missions_trigger_checkin_safely(client):
    user = register_user(client, username="MissionUser")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    learning_path = next(item for item in paths_data["items"] if item["key"] == "learning")

    client.post(f"/paths/{learning_path['path_id']}/start", headers=headers)
    path_challenges = client.get(
        f"/paths/{learning_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"]

    challenge_id = path_challenges[0]["challenge_id"]

    join_res = client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    assert join_res.status_code == 200
    enrollment_id = join_res.get_json()["enrollment_id"]

    day_one_progress = client.get(
        f"/paths/{learning_path['path_id']}/challenges",
        headers=headers,
    ).get_json()
    day_one_challenge = next(
        item for item in day_one_progress["items"]
        if item["challenge_id"] == challenge_id
    )

    assert day_one_challenge["today_missions_total"] == 1
    assert day_one_challenge["missions"][0]["available_today"] is True
    assert day_one_challenge["missions"][0]["today_status"] == "pending"
    assert day_one_challenge["missions"][1]["available_today"] is False
    assert day_one_challenge["missions"][1]["today_status"] == "locked"
    assert day_one_challenge["missions"][1]["unlocks_in_days"] == 1

    enrollment_detail = client.get(
        f"/me/enrollments/{enrollment_id}",
        headers=headers,
    ).get_json()

    assert enrollment_detail["mission_summary"]["today_missions_total"] == 1
    assert enrollment_detail["mission_summary"]["future_missions_total"] >= 1
    assert enrollment_detail["missions"][0]["available_today"] is True
    assert enrollment_detail["missions"][1]["today_status"] == "locked"

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

    missions_res = client.get("/me/today-missions", headers=headers)

    assert missions_res.status_code == 200
    missions_data = missions_res.get_json()
    assert missions_data["ok"] is True
    assert missions_data["ringo"]["sprite"] in {
        "idle",
        "welcome",
        "talking",
        "explaining",
        "thinking",
        "encouraging",
        "warning",
        "concerned",
        "happy",
        "celebration",
        "achievement",
        "proud",
        "sad",
        "sleeping",
        "focus",
        "victory",
    }
    assert len(missions_data["missions"]) >= 3

    first, second, third = missions_data["missions"][:3]

    done_res = client.post(
        f"/me/missions/{first['mission_id']}/done",
        headers=headers,
    )

    assert done_res.status_code == 200
    done_data = done_res.get_json()
    assert done_data["ok"] is True
    assert done_data["mission"]["status"] == "done"
    assert done_data["mission"]["xp_earned"] == first["xp_reward"]
    assert done_data["mission"]["enrollment_id"] == enrollment_id
    assert done_data["checkin"]["ok"] is True
    assert done_data["checkin"]["mode"] == "created"
    assert done_data["checkin"]["already_checked"] is False

    progress_res = client.get(
        f"/paths/{learning_path['path_id']}/challenges",
        headers=headers,
    )
    progress_data = progress_res.get_json()
    joined_challenge = next(
        item for item in progress_data["items"]
        if item["challenge_id"] == challenge_id
    )

    assert progress_res.status_code == 200
    assert progress_data["summary"]["joined_challenges"] == 1
    assert progress_data["summary"]["today_checked_challenges"] == 1
    assert progress_data["summary"]["today_missions_done"] == 1
    assert joined_challenge["is_joined"] is True
    assert joined_challenge["enrollment_id"] == enrollment_id
    assert joined_challenge["today_checked"] is True
    assert joined_challenge["today_missions_done"] == 1
    assert joined_challenge["missions"][0]["today_status"] == "done"

    repeat_done_res = client.post(
        f"/me/missions/{first['mission_id']}/done",
        headers=headers,
    )

    assert repeat_done_res.status_code == 200
    repeat_done_data = repeat_done_res.get_json()
    assert repeat_done_data["ok"] is True
    assert repeat_done_data["checkin"]["ok"] is True
    assert repeat_done_data["checkin"]["mode"] == "existing"
    assert repeat_done_data["checkin"]["already_checked"] is True

    reminder_at = (
        datetime.now(timezone.utc) + timedelta(hours=2)
    ).isoformat()
    remind_res = client.post(
        f"/me/missions/{second['mission_id']}/remind-later",
        json={"reminder_at": reminder_at},
        headers=headers,
    )

    assert remind_res.status_code == 200
    remind_data = remind_res.get_json()
    assert remind_data["ok"] is True
    assert remind_data["mission"]["status"] == "remind_later"
    assert remind_data["mission"]["reminder_at"] == reminder_at

    skip_res = client.post(
        f"/me/missions/{third['mission_id']}/skip",
        headers=headers,
    )

    assert skip_res.status_code == 200
    skip_data = skip_res.get_json()
    assert skip_data["ok"] is True
    assert skip_data["mission"]["status"] == "skipped"
    assert skip_data["mission"]["xp_earned"] == 0

    stats_res = client.get("/me/stats", headers=headers)

    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["ok"] is True
    assert stats_data["stats"]["total_checkins"] == 1
    assert stats_data["stats"]["total_points"] >= 10


def test_legacy_challenge_checkin_syncs_first_today_mission(client):
    user = register_user(client, username="LegacyMissionSync")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]

    join_res = client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )
    enrollment_id = join_res.get_json()["enrollment_id"]

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

    checkin_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert checkin_res.status_code == 200
    checkin_data = checkin_res.get_json()
    assert checkin_data["ok"] is True
    assert checkin_data["mode"] == "created"
    assert checkin_data["synced_mission_id"] is not None

    missions_data = client.get("/me/today-missions", headers=headers).get_json()
    mission_statuses = [mission["status"] for mission in missions_data["missions"][:3]]

    assert mission_statuses.count("done") == 1
    assert mission_statuses.count("pending") == 2

    repeat_checkin_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert repeat_checkin_res.status_code == 200
    repeat_checkin_data = repeat_checkin_res.get_json()
    assert repeat_checkin_data["mode"] == "existing"
    assert repeat_checkin_data["synced_mission_id"] is None

    repeat_missions_data = client.get("/me/today-missions", headers=headers).get_json()
    repeat_statuses = [mission["status"] for mission in repeat_missions_data["missions"][:3]]

    assert repeat_statuses.count("done") == 1
    assert repeat_statuses.count("pending") == 2


def test_today_missions_are_not_truncated_after_many_active_challenges(client):
    user = register_user(client, username="ManyMissions")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    challenge_ids = []

    for path in paths_data["items"]:
        challenges = client.get(
            f"/paths/{path['path_id']}/challenges",
            headers=headers,
        ).get_json()["items"]
        challenge_ids.extend(item["challenge_id"] for item in challenges)

    selected_ids = challenge_ids[:10]

    for challenge_id in selected_ids:
        join_res = client.post(
            f"/challenges/{challenge_id}/join",
            json={},
            headers=headers,
        )
        assert join_res.status_code == 200

    missions_res = client.get("/me/today-missions", headers=headers)

    assert missions_res.status_code == 200
    missions_data = missions_res.get_json()
    challenge_names = {mission["challenge_name"] for mission in missions_data["missions"]}

    assert len(missions_data["missions"]) == len(selected_ids)
    assert "Creative Spark" in challenge_names

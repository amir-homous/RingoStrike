from datetime import datetime, timedelta, timezone

from helpers import auth_headers, insert_challenge, register_user
from services.stats_service import build_level_progress
from utils.date_utils import ringo_day_metadata


def _before_next_reset_at():
    next_reset = datetime.fromisoformat(
        ringo_day_metadata()["next_reset_at"].replace("Z", "+00:00"),
    )
    target = min(
        datetime.now(timezone.utc) + timedelta(hours=2),
        next_reset - timedelta(seconds=1),
    )
    return target.isoformat()


def _after_next_reset_at():
    next_reset = datetime.fromisoformat(
        ringo_day_metadata()["next_reset_at"].replace("Z", "+00:00"),
    )
    return (next_reset + timedelta(minutes=1)).isoformat()


def _start_first_fitness_challenge(client, headers):
    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    join_data = client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    ).get_json()

    return {
        "path_id": fitness_path["path_id"],
        "challenge_id": challenge_id,
        "enrollment_id": join_data["enrollment_id"],
        "missions": client.get("/me/today-missions", headers=headers).get_json()["missions"],
    }


def _set_mission_xp(mission_id, xp_reward):
    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            "UPDATE missions SET xp_reward = ? WHERE id = ?",
            (xp_reward, mission_id),
        )
        conn.commit()
    finally:
        conn.close()


def _insert_counted_checkin(user_id, enrollment_id, challenge_id):
    import database
    from utils.date_utils import utc_today_iso

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
            VALUES (?, ?, ?, ?, 'Done', 1)
            ON CONFLICT(enrollment_id, date) DO UPDATE SET
                status = 'Done',
                is_counted = 1
            """,
            (enrollment_id, user_id, challenge_id, utc_today_iso()),
        )
        conn.commit()
    finally:
        conn.close()


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


def test_seeded_missions_include_linked_intensity_variants(client):
    import database

    conn = database.get_db_connection()
    try:
        intensity_counts = {
            row["mission_intensity"]: row["count"]
            for row in conn.execute(
                """
                SELECT COALESCE(mission_intensity, 'main') AS mission_intensity,
                       COUNT(*) AS count
                FROM missions
                WHERE status = 'Active'
                GROUP BY COALESCE(mission_intensity, 'main')
                """
            ).fetchall()
        }
        tiny_links = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM missions tiny
            JOIN missions parent ON parent.id = tiny.parent_mission_id
            WHERE tiny.status = 'Active'
              AND tiny.mission_intensity = 'tiny'
              AND parent.mission_intensity = 'main'
              AND tiny.estimated_minutes BETWEEN 1 AND 3
            """
        ).fetchone()["count"]
        bonus_links = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM missions bonus
            JOIN missions parent ON parent.id = bonus.parent_mission_id
            WHERE bonus.status = 'Active'
              AND bonus.mission_intensity = 'bonus'
              AND parent.mission_intensity = 'main'
            """
        ).fetchone()["count"]
    finally:
        conn.close()

    assert intensity_counts["main"] >= 45
    assert intensity_counts["tiny"] >= 15
    assert intensity_counts["bonus"] >= 5
    assert tiny_links >= 15
    assert bonus_links >= 5


def test_seeded_missions_have_planner_metadata(client):
    import database

    valid_suggested_times = {"morning", "midday", "afternoon", "evening", "night", "anytime"}
    valid_difficulties = {"easy", "medium", "hard"}

    conn = database.get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                key,
                title,
                difficulty,
                suggested_time,
                COALESCE(mission_intensity, 'main') AS mission_intensity,
                estimated_minutes
            FROM missions
            WHERE status = 'Active'
            """
        ).fetchall()
    finally:
        conn.close()

    assert rows
    assert all(row["estimated_minutes"] is not None for row in rows)
    assert all(int(row["estimated_minutes"]) > 0 for row in rows)
    assert all(row["suggested_time"] in valid_suggested_times for row in rows)
    assert all(row["suggested_time"] != "Anytime today" for row in rows)
    assert all(row["difficulty"] in valid_difficulties for row in rows)

    tiny_rows = [row for row in rows if row["mission_intensity"] == "tiny"]
    main_rows = [row for row in rows if row["mission_intensity"] == "main"]
    bonus_rows = [row for row in rows if row["mission_intensity"] == "bonus"]

    assert tiny_rows
    assert main_rows
    assert bonus_rows
    assert all(1 <= int(row["estimated_minutes"]) <= 5 for row in tiny_rows)
    assert all(1 <= int(row["estimated_minutes"]) <= 25 for row in main_rows)
    assert all(1 <= int(row["estimated_minutes"]) <= 15 for row in bonus_rows)


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

    assert day_one_challenge["today_missions_total"] == 3
    assert day_one_challenge["missions"][0]["available_today"] is True
    assert day_one_challenge["missions"][0]["today_status"] == "pending"
    assert day_one_challenge["missions"][0]["mission_intensity"] == "main"
    assert "estimated_minutes" in day_one_challenge["missions"][0]
    assert "parent_mission_id" in day_one_challenge["missions"][0]

    available_day_one = [
        mission for mission in day_one_challenge["missions"]
        if mission["available_today"]
    ]

    assert {mission["mission_intensity"] for mission in available_day_one} == {"main", "tiny", "bonus"}

    bonus_mission = next(
        mission for mission in available_day_one
        if mission["mission_intensity"] == "bonus"
    )
    assert bonus_mission["parent_mission_id"] is not None
    assert bonus_mission["parent_mission_id"] is not None
    tiny_mission = next(
        mission for mission in available_day_one
        if mission["mission_intensity"] == "tiny"
    )
    assert tiny_mission["parent_mission_id"] == day_one_challenge["missions"][0]["mission_id"]
    assert tiny_mission["estimated_minutes"] in {1, 2, 3}
    assert day_one_challenge["missions"][1]["available_today"] is False
    assert day_one_challenge["missions"][1]["today_status"] == "locked"
    assert day_one_challenge["missions"][1]["unlocks_in_days"] == 1

    enrollment_detail = client.get(
        f"/me/enrollments/{enrollment_id}",
        headers=headers,
    ).get_json()

    assert enrollment_detail["mission_summary"]["today_missions_total"] == 3
    assert enrollment_detail["mission_summary"]["future_missions_total"] >= 1
    assert enrollment_detail["missions"][0]["available_today"] is True
    assert enrollment_detail["missions"][1]["today_status"] == "locked"
    assert enrollment_detail["missions"][0]["mission_intensity"] == "main"

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
    assert first["mission_intensity"] == "main"
    assert "estimated_minutes" in first
    assert "parent_mission_id" in first

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
    assert "reward_sequence" in done_data
    assert [step["type"] for step in done_data["reward_sequence"]] == [
        "ringo_message",
        "mission_completed",
        "xp_earned",
        "today_saved",
        "next_choice",
    ]
    assert done_data["reward_sequence"][1]["title"] == first["title"]
    assert done_data["reward_sequence"][2]["amount"] == first["xp_reward"]

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
    assert "reward_sequence" in repeat_done_data
    assert repeat_done_data["mission"]["status"] == "done"
    assert not any(
        step["type"] == "today_saved"
        for step in repeat_done_data["reward_sequence"]
    )
    assert any(
        step["title"] == "Bonus momentum."
        and "optional extra progress" in step["text"]
        for step in repeat_done_data["reward_sequence"]
    )

    reminder_at = _before_next_reset_at()
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
    assert skip_data["mission"]["skip_reason"] is None

    updated_missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    completed_mission = next(
        item for item in updated_missions
        if item["mission_id"] == first["mission_id"]
    )
    reminded_mission = next(
        item for item in updated_missions
        if item["mission_id"] == second["mission_id"]
    )
    skipped_mission = next(
        item for item in updated_missions
        if item["mission_id"] == third["mission_id"]
    )

    assert completed_mission["done_at"].endswith("Z")
    assert completed_mission["status_updated_at"] == completed_mission["done_at"]
    assert reminded_mission["reminder_at"] == reminder_at
    assert reminded_mission["reminder_set_at"].endswith("Z")
    assert reminded_mission["status_updated_at"] == reminded_mission["reminder_set_at"]
    assert skipped_mission["skipped_at"].endswith("Z")
    assert skipped_mission["status_updated_at"] == skipped_mission["skipped_at"]

    stats_res = client.get("/me/stats", headers=headers)

    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["ok"] is True
    assert stats_data["stats"]["total_checkins"] == 1
    assert stats_data["stats"]["total_points"] >= 10


def test_main_mission_awards_mission_xp_without_old_fixed_double_award(client):
    user = register_user(client, username="MainMissionXp")
    headers = auth_headers(user["access_token"])
    setup = _start_first_fitness_challenge(client, headers)
    main_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "main"
    )
    _set_mission_xp(main_mission["mission_id"], 17)

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )

    assert done_res.status_code == 200
    done_data = done_res.get_json()
    achievement_xp = done_data["checkin"]["rewards"]["achievement_xp_reward"]

    assert done_data["mission"]["xp_earned"] == 17
    assert done_data["mission"]["xp_awarded"] == 17
    assert done_data["checkin"]["mode"] == "created"

    stats_data = client.get("/me/stats", headers=headers).get_json()
    progress = build_level_progress(17 + achievement_xp)

    assert stats_data["stats"]["total_checkins"] == 1
    assert stats_data["stats"]["current_streak"] == 1
    assert stats_data["stats"]["total_points"] == 17 + achievement_xp
    assert stats_data["stats"]["level"] == progress["level"]
    assert stats_data["stats"]["progress_percent"] == progress["progress_percent"]


def test_legacy_only_checkin_still_awards_fixed_xp(client):
    user = register_user(client, username="LegacyOnlyXp")
    headers = auth_headers(user["access_token"])
    challenge_id = insert_challenge(
        name="Legacy Only XP Challenge",
        description="No missions are attached to this challenge.",
        visibility="Public",
    )

    join_data = client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    ).get_json()
    checkin_res = client.post(
        f"/me/challenges/{join_data['enrollment_id']}/checkin",
        headers=headers,
    )

    assert checkin_res.status_code == 200
    checkin_data = checkin_res.get_json()
    achievement_xp = checkin_data["rewards"]["achievement_xp_reward"]

    assert checkin_data["synced_mission_id"] is None
    assert client.get("/me/stats", headers=headers).get_json()["stats"]["total_points"] == 10 + achievement_xp


def test_tiny_mission_awards_mission_xp_and_satisfies_today_once(client):
    user = register_user(client, username="TinyMissionXp")
    headers = auth_headers(user["access_token"])
    setup = _start_first_fitness_challenge(client, headers)
    main_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "main"
    )
    tiny_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "tiny"
        and mission["parent_mission_id"] == main_mission["mission_id"]
    )
    _set_mission_xp(tiny_mission["mission_id"], 7)

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )

    assert done_res.status_code == 200
    done_data = done_res.get_json()
    achievement_xp = done_data["checkin"]["rewards"]["achievement_xp_reward"]

    assert done_data["mission"]["xp_earned"] == 7
    assert done_data["mission"]["xp_awarded"] == 7
    assert done_data["checkin"]["mode"] == "created"
    assert any(step["type"] == "today_saved" for step in done_data["reward_sequence"])

    stats_data = client.get("/me/stats", headers=headers).get_json()
    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    updated_main = next(m for m in missions if m["mission_id"] == main_mission["mission_id"])
    updated_tiny = next(m for m in missions if m["mission_id"] == tiny_mission["mission_id"])

    assert stats_data["stats"]["total_checkins"] == 1
    assert stats_data["stats"]["total_points"] == 7 + achievement_xp
    assert updated_main["status"] == "pending"
    assert updated_tiny["status"] == "done"


def test_bonus_mission_does_not_suppress_same_enrollment_legacy_checkin_xp(client):
    user = register_user(client, username="BonusKeepsLegacyXp")
    headers = auth_headers(user["access_token"])
    setup = _start_first_fitness_challenge(client, headers)
    bonus_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "bonus"
    )
    _set_mission_xp(bonus_mission["mission_id"], 6)
    _insert_counted_checkin(
        user["user_id"],
        setup["enrollment_id"],
        setup["challenge_id"],
    )

    done_res = client.post(
        f"/me/missions/{bonus_mission['mission_id']}/done",
        headers=headers,
    )

    assert done_res.status_code == 200
    done_data = done_res.get_json()
    achievement_xp = done_data["checkin"]["rewards"]["achievement_xp_reward"]

    assert done_data["mission"]["xp_awarded"] == 6
    assert done_data["checkin"]["mode"] == "not_applicable"
    assert client.get("/me/stats", headers=headers).get_json()["stats"]["total_points"] == 16 + achievement_xp


def test_bonus_mission_awards_xp_without_checkin_or_streak_ownership(client):
    user = register_user(client, username="BonusMissionXp")
    headers = auth_headers(user["access_token"])
    setup = _start_first_fitness_challenge(client, headers)
    bonus_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "bonus"
    )
    _set_mission_xp(bonus_mission["mission_id"], 6)

    done_res = client.post(
        f"/me/missions/{bonus_mission['mission_id']}/done",
        headers=headers,
    )

    assert done_res.status_code == 200
    done_data = done_res.get_json()

    assert done_data["mission"]["xp_earned"] == 6
    assert done_data["mission"]["xp_awarded"] == 6
    assert done_data["checkin"]["mode"] == "not_applicable"
    assert done_data["checkin"]["rewards"]["achievement_xp_reward"] == 0

    stats_data = client.get("/me/stats", headers=headers).get_json()
    activity_data = client.get("/me/activity", headers=headers).get_json()

    assert stats_data["stats"]["total_points"] == 6
    assert stats_data["stats"]["total_checkins"] == 0
    assert stats_data["stats"]["current_streak"] == 0
    assert [event for event in activity_data["events"] if event["type"] == "checkin"] == []


def test_mission_completion_does_not_suppress_other_enrollment_legacy_xp(client):
    user = register_user(client, username="MissionAndOtherLegacyXp")
    headers = auth_headers(user["access_token"])
    setup = _start_first_fitness_challenge(client, headers)
    path_challenges = client.get(
        f"/paths/{setup['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"]
    other_challenge = next(
        item for item in path_challenges
        if item["challenge_id"] != setup["challenge_id"]
    )
    other_join = client.post(
        f"/challenges/{other_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    ).get_json()
    main_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "main"
    )
    _set_mission_xp(main_mission["mission_id"], 17)

    done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    done_data = done_res.get_json()
    achievement_xp = done_data["checkin"]["rewards"]["achievement_xp_reward"]
    _insert_counted_checkin(
        user["user_id"],
        other_join["enrollment_id"],
        other_challenge["challenge_id"],
    )

    assert done_res.status_code == 200
    assert done_data["mission"]["xp_awarded"] == 17
    assert client.get("/me/stats", headers=headers).get_json()["stats"]["total_points"] == 27 + achievement_xp


def test_missing_mission_xp_uses_intensity_fallback(client):
    user = register_user(client, username="MissionFallbackXp")
    headers = auth_headers(user["access_token"])
    setup = _start_first_fitness_challenge(client, headers)
    main_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "main"
    )
    tiny_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "tiny"
        and mission["parent_mission_id"] == main_mission["mission_id"]
    )
    _set_mission_xp(tiny_mission["mission_id"], 0)

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )

    assert done_res.status_code == 200
    done_data = done_res.get_json()
    achievement_xp = done_data["checkin"]["rewards"]["achievement_xp_reward"]

    assert done_data["mission"]["xp_earned"] == 5
    assert done_data["mission"]["xp_awarded"] == 5
    assert client.get("/me/stats", headers=headers).get_json()["stats"]["total_points"] == 5 + achievement_xp


def test_repeated_mission_done_is_idempotent_for_xp_activity_and_achievements(client):
    user = register_user(client, username="MissionXpIdempotent")
    headers = auth_headers(user["access_token"])
    setup = _start_first_fitness_challenge(client, headers)
    main_mission = next(
        mission for mission in setup["missions"]
        if mission["mission_intensity"] == "main"
    )
    _set_mission_xp(main_mission["mission_id"], 17)

    first_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    first_data = first_res.get_json()
    first_stats = client.get("/me/stats", headers=headers).get_json()["stats"]
    first_activity = client.get("/me/activity", headers=headers).get_json()["events"]
    first_achievements = client.get("/me/achievements", headers=headers).get_json()["achievements"]

    repeat_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    repeat_data = repeat_res.get_json()
    repeat_stats = client.get("/me/stats", headers=headers).get_json()["stats"]
    repeat_activity = client.get("/me/activity", headers=headers).get_json()["events"]
    repeat_achievements = client.get("/me/achievements", headers=headers).get_json()["achievements"]

    first_checkin_events = [event for event in first_activity if event["type"] == "checkin"]
    repeat_checkin_events = [event for event in repeat_activity if event["type"] == "checkin"]

    assert first_res.status_code == 200
    assert first_data["mission"]["xp_awarded"] == 17
    assert repeat_res.status_code == 200
    assert repeat_data["mission"]["xp_earned"] == 17
    assert repeat_data["mission"]["xp_awarded"] == 0
    assert repeat_data["mission"]["already_done"] is True
    assert repeat_data["checkin"]["rewards"]["achievements"] == []
    assert repeat_stats["total_points"] == first_stats["total_points"]
    assert repeat_stats["total_checkins"] == first_stats["total_checkins"] == 1
    assert len(repeat_checkin_events) == len(first_checkin_events) == 1
    assert repeat_checkin_events[0]["xp_delta"] == 17
    assert {
        achievement["key"]: achievement["unlocked_at"]
        for achievement in repeat_achievements
    } == {
        achievement["key"]: achievement["unlocked_at"]
        for achievement in first_achievements
    }


def test_mission_reminder_rejects_time_after_next_daily_reset(client):
    user = register_user(client, username="ResetReminder")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    mission = client.get("/me/today-missions", headers=headers).get_json()["missions"][0]

    remind_res = client.post(
        f"/me/missions/{mission['mission_id']}/remind-later",
        json={"reminder_at": _after_next_reset_at()},
        headers=headers,
    )

    assert remind_res.status_code == 400
    assert remind_res.get_json()["error"] == "reminder_after_next_reset"

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    unchanged_mission = next(
        item for item in missions
        if item["mission_id"] == mission["mission_id"]
    )

    assert unchanged_mission["status"] == "pending"
    assert unchanged_mission["reminder_at"] is None


def test_today_missions_ringo_suggests_pending_after_future_reminder(client):
    user = register_user(client, username="ReminderNextAction")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

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

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    first = missions[0]
    next_pending = next(
        mission for mission in missions
        if mission["mission_id"] != first["mission_id"]
        and mission["status"] == "pending"
    )

    remind_res = client.post(
        f"/me/missions/{first['mission_id']}/remind-later",
        json={"reminder_at": _before_next_reset_at()},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload = client.get("/me/today-missions", headers=headers).get_json()

    assert payload["ok"] is True
    assert payload["ringo"]["state"] == "today_not_started"
    assert "I saved that reminder" in payload["ringo"]["message"]
    assert next_pending["title"] in payload["ringo"]["message"]
    assert payload["ringo"]["primary_action"]["mission_id"] == next_pending["mission_id"]


def test_today_missions_ringo_skips_parent_after_linked_tiny_reminder(client):
    user = register_user(client, username="TinyReminderNextAction")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenges = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"]
    first_challenge = challenges[0]
    second_challenge = challenges[1]
    client.post(
        f"/challenges/{first_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )
    client.post(
        f"/challenges/{second_challenge['challenge_id']}/join",
        json={},
        headers=headers,
    )

    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            "UPDATE missions SET unlock_after_days = 0 WHERE challenge_id IN (?, ?)",
            (first_challenge["challenge_id"], second_challenge["challenge_id"]),
        )
        conn.commit()
    finally:
        conn.close()

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    first_main = next(
        mission for mission in missions
        if mission["challenge_id"] == first_challenge["challenge_id"]
        and mission["mission_intensity"] == "main"
    )
    first_tiny = next(
        mission for mission in missions
        if mission["mission_intensity"] == "tiny"
        and mission["parent_mission_id"] == first_main["mission_id"]
    )
    second_main = next(
        mission for mission in missions
        if mission["challenge_id"] == second_challenge["challenge_id"]
        and mission["mission_intensity"] == "main"
    )

    remind_res = client.post(
        f"/me/missions/{first_tiny['mission_id']}/remind-later",
        json={"reminder_at": _before_next_reset_at()},
        headers=headers,
    )
    assert remind_res.status_code == 200

    payload = client.get("/me/today-missions", headers=headers).get_json()

    assert payload["ok"] is True
    assert payload["ringo"]["state"] == "today_not_started"
    assert "I saved that reminder" in payload["ringo"]["message"]
    assert second_main["title"] in payload["ringo"]["message"]
    assert first_main["title"] not in payload["ringo"]["message"]
    assert payload["ringo"]["primary_action"]["mission_id"] == second_main["mission_id"]


def test_plan_reminders_schedules_pending_only_before_reset(client):
    user = register_user(client, username="ReminderPlanner")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    learning_path = next(item for item in paths_data["items"] if item["key"] == "learning")

    client.post(f"/paths/{learning_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{learning_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

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

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    first, second, third = missions[:3]
    existing_reminder_at = _before_next_reset_at()

    client.post(
        f"/me/missions/{first['mission_id']}/remind-later",
        json={"reminder_at": existing_reminder_at},
        headers=headers,
    )
    client.post(
        f"/me/missions/{second['mission_id']}/done",
        headers=headers,
    )
    client.post(
        f"/me/missions/{third['mission_id']}/skip",
        headers=headers,
    )

    plan_res = client.post("/me/missions/plan-reminders", headers=headers)

    assert plan_res.status_code == 200
    plan_data = plan_res.get_json()
    assert plan_data["ok"] is True
    assert "scheduled" in plan_data
    assert "unscheduled" in plan_data
    assert plan_data["summary"]["scheduled_count"] == len(plan_data["scheduled"])
    assert plan_data["summary"]["unscheduled_count"] == len(plan_data["unscheduled"])

    next_reset = datetime.fromisoformat(
        plan_data["ringo_day"]["next_reset_at"].replace("Z", "+00:00"),
    )
    for item in plan_data["scheduled"]:
        reminder_at = datetime.fromisoformat(item["reminder_at"].replace("Z", "+00:00"))
        assert datetime.now(timezone.utc) < reminder_at < next_reset

    updated_missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    existing_reminder = next(
        item for item in updated_missions
        if item["mission_id"] == first["mission_id"]
    )
    done_mission = next(
        item for item in updated_missions
        if item["mission_id"] == second["mission_id"]
    )
    skipped_mission = next(
        item for item in updated_missions
        if item["mission_id"] == third["mission_id"]
    )

    assert existing_reminder["status"] == "remind_later"
    assert existing_reminder["reminder_at"] == existing_reminder_at
    assert done_mission["status"] == "done"
    assert skipped_mission["status"] == "skipped"


def test_plan_single_mission_reminder_applies_safe_future_time(client):
    user = register_user(client, username="SinglePlanner")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    learning_path = next(item for item in paths_data["items"] if item["key"] == "learning")

    client.post(f"/paths/{learning_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{learning_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    mission = client.get("/me/today-missions", headers=headers).get_json()["missions"][0]
    plan_res = client.post(
        f"/me/missions/{mission['mission_id']}/plan-reminder",
        headers=headers,
    )

    assert plan_res.status_code == 200
    plan_data = plan_res.get_json()
    assert plan_data["ok"] is True
    assert plan_data["mission"]["status"] == "remind_later"
    reminder_at = datetime.fromisoformat(
        plan_data["scheduled"]["reminder_at"].replace("Z", "+00:00"),
    )
    next_reset = datetime.fromisoformat(
        plan_data["ringo_day"]["next_reset_at"].replace("Z", "+00:00"),
    )
    assert datetime.now(timezone.utc) < reminder_at < next_reset


def test_plan_single_mission_reminder_can_replace_existing_reminder(client):
    user = register_user(client, username="SinglePlannerEdit")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    mission = client.get("/me/today-missions", headers=headers).get_json()["missions"][0]
    existing_reminder_at = _before_next_reset_at()
    client.post(
        f"/me/missions/{mission['mission_id']}/remind-later",
        json={"reminder_at": existing_reminder_at},
        headers=headers,
    )

    plan_res = client.post(
        f"/me/missions/{mission['mission_id']}/plan-reminder",
        headers=headers,
    )

    assert plan_res.status_code == 200
    plan_data = plan_res.get_json()
    assert plan_data["ok"] is True
    assert plan_data["mission"]["status"] == "remind_later"
    assert plan_data["mission"]["reminder_at"] != existing_reminder_at


def test_plan_single_mission_reminder_clamps_when_planned_time_crosses_reset(monkeypatch, client):
    from services import mission_service

    user = register_user(client, username="SinglePlannerNoTime")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    current = datetime.now(timezone.utc).replace(microsecond=0)
    next_reset = current + timedelta(minutes=5)
    monkeypatch.setattr(
        mission_service,
        "ringo_day_metadata",
        lambda: {
            "date": current.date().isoformat(),
            "next_reset_at": next_reset.isoformat().replace("+00:00", "Z"),
            "reset_basis": "utc",
            "server_now": current.isoformat().replace("+00:00", "Z"),
        },
    )

    mission = client.get("/me/today-missions", headers=headers).get_json()["missions"][0]
    plan_res = client.post(
        f"/me/missions/{mission['mission_id']}/plan-reminder",
        headers=headers,
    )

    assert plan_res.status_code == 200
    plan_data = plan_res.get_json()
    assert plan_data["ok"] is True
    reminder_at = datetime.fromisoformat(
        plan_data["scheduled"]["reminder_at"].replace("Z", "+00:00"),
    )
    assert current < reminder_at < next_reset
    assert reminder_at == next_reset - timedelta(seconds=1)


def test_today_missions_ignore_previous_day_event_timestamps(client):
    import database

    user = register_user(client, username="YesterdayLog")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    mission = client.get("/me/today-missions", headers=headers).get_json()["missions"][0]
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO mission_logs (
                user_id,
                enrollment_id,
                challenge_id,
                mission_id,
                date,
                status,
                xp_earned,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, 'done', ?, ?)
            """,
            (
                user["user_id"],
                mission["enrollment_id"],
                mission["challenge_id"],
                mission["mission_id"],
                yesterday,
                mission["xp_reward"],
                f"{yesterday} 12:00:00",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    today_mission = next(
        item for item in missions
        if item["mission_id"] == mission["mission_id"]
    )

    assert today_mission["status"] == "pending"
    assert today_mission["done_at"] is None
    assert today_mission["skipped_at"] is None
    assert today_mission["reminder_set_at"] is None
    assert today_mission["status_updated_at"] is None


def test_mission_skip_reason_is_optional_and_persisted(client):
    user = register_user(client, username="SkipReason")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    mission = client.get("/me/today-missions", headers=headers).get_json()["missions"][0]

    skip_res = client.post(
        f"/me/missions/{mission['mission_id']}/skip",
        json={"reason": "too_tired"},
        headers=headers,
    )

    assert skip_res.status_code == 200
    skip_data = skip_res.get_json()
    assert skip_data["ok"] is True
    assert skip_data["mission"]["status"] == "skipped"
    assert skip_data["mission"]["skip_reason"] == "too_tired"
    assert skip_data["mission"]["xp_earned"] == 0

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    skipped_mission = next(
        item for item in missions
        if item["mission_id"] == mission["mission_id"]
    )

    assert skipped_mission["status"] == "skipped"
    assert skipped_mission["skip_reason"] == "too_tired"

    stats_data = client.get("/me/stats", headers=headers).get_json()

    assert stats_data["ok"] is True
    assert stats_data["stats"]["total_checkins"] == 0


def test_mission_skip_rejects_invalid_reason_payload(client):
    user = register_user(client, username="SkipReasonInvalid")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    mission = client.get("/me/today-missions", headers=headers).get_json()["missions"][0]

    invalid_type_res = client.post(
        f"/me/missions/{mission['mission_id']}/skip",
        json={"reason": 123},
        headers=headers,
    )
    unsupported_res = client.post(
        f"/me/missions/{mission['mission_id']}/skip",
        json={"reason": "not_a_reason"},
        headers=headers,
    )

    assert invalid_type_res.status_code == 400
    assert invalid_type_res.get_json()["error"] == "invalid_skip_reason"
    assert unsupported_res.status_code == 400
    assert unsupported_res.get_json()["error"] == "unsupported_skip_reason"


def test_linked_tiny_mission_completion_reward_sequence_saves_today(client):
    user = register_user(client, username="TinyReward")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]

    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    main_mission = next(
        mission for mission in missions
        if mission["mission_intensity"] == "main"
    )
    tiny_mission = next(
        mission for mission in missions
        if mission["mission_intensity"] == "tiny"
        and mission["parent_mission_id"] == main_mission["mission_id"]
    )

    done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )

    assert done_res.status_code == 200
    done_data = done_res.get_json()
    step_types = [step["type"] for step in done_data["reward_sequence"]]

    assert done_data["mission"]["mission_id"] == tiny_mission["mission_id"]
    assert "today_saved" in step_types
    assert done_data["reward_sequence"][1]["title"] == tiny_mission["title"]

    updated_missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    updated_main = next(
        mission for mission in updated_missions
        if mission["mission_id"] == main_mission["mission_id"]
    )
    updated_tiny = next(
        mission for mission in updated_missions
        if mission["mission_id"] == tiny_mission["mission_id"]
    )

    assert updated_tiny["status"] == "done"
    assert updated_main["status"] == "pending"


def test_completion_after_today_saved_gets_bonus_reward_copy(client):
    user = register_user(client, username="BonusReward")
    headers = auth_headers(user["access_token"])

    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]

    client.post(
        f"/challenges/{challenge_id}/join",
        json={},
        headers=headers,
    )

    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    main_mission = next(
        mission for mission in missions
        if mission["mission_intensity"] == "main"
    )
    tiny_mission = next(
        mission for mission in missions
        if mission["mission_intensity"] == "tiny"
        and mission["parent_mission_id"] == main_mission["mission_id"]
    )

    first_done_res = client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    )
    assert first_done_res.status_code == 200
    first_done_data = first_done_res.get_json()
    assert any(
        step["type"] == "today_saved"
        for step in first_done_data["reward_sequence"]
    )

    extra_done_res = client.post(
        f"/me/missions/{tiny_mission['mission_id']}/done",
        headers=headers,
    )

    assert extra_done_res.status_code == 200
    extra_done_data = extra_done_res.get_json()
    assert extra_done_data["ok"] is True
    assert "mission" in extra_done_data
    assert "checkin" in extra_done_data
    assert "checkin_status_code" in extra_done_data
    assert "reward_sequence" in extra_done_data
    assert not any(
        step["type"] == "today_saved"
        for step in extra_done_data["reward_sequence"]
    )
    assert any(
        step["type"] == "ringo_message"
        and step["title"] == "Bonus momentum."
        and "optional extra progress" in step["text"]
        for step in extra_done_data["reward_sequence"]
    )


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
    mission_statuses = [mission["status"] for mission in missions_data["missions"]]

    assert mission_statuses.count("done") == 1
    assert mission_statuses.count("pending") >= 2

    repeat_checkin_res = client.post(
        f"/me/challenges/{enrollment_id}/checkin",
        headers=headers,
    )

    assert repeat_checkin_res.status_code == 200
    repeat_checkin_data = repeat_checkin_res.get_json()
    assert repeat_checkin_data["mode"] == "existing"
    assert repeat_checkin_data["synced_mission_id"] is None

    repeat_missions_data = client.get("/me/today-missions", headers=headers).get_json()
    repeat_statuses = [mission["status"] for mission in repeat_missions_data["missions"]]

    assert repeat_statuses.count("done") == 1
    assert repeat_statuses.count("pending") >= 2


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

    assert len(missions_data["missions"]) >= len(selected_ids)
    assert "Creative Spark" in challenge_names

from helpers import register_user


FIRST_PATH_REWARDS = {
    "career": "career_planner",
    "creativity": "creativity_sketchbook",
    "fitness": "fitness_water_bottle",
    "learning": "learning_first_book",
    "sleep": "sleep_pillow",
}


def test_living_space_reward_definitions_seed_idempotently(client):
    import database

    conn = database.get_db_connection()
    try:
        first_count = conn.execute(
            "SELECT CAST(COUNT(*) AS INTEGER) AS n FROM reward_definitions"
        ).fetchone()["n"]
        first_path_reward_count = conn.execute(
            """
            SELECT CAST(COUNT(*) AS INTEGER) AS n
            FROM reward_definitions
            WHERE unlock_condition_type = 'first_path_mission_done'
            """
        ).fetchone()["n"]
    finally:
        conn.close()

    database.init_db()

    conn = database.get_db_connection()
    try:
        second_count = conn.execute(
            "SELECT CAST(COUNT(*) AS INTEGER) AS n FROM reward_definitions"
        ).fetchone()["n"]
        keys_count = conn.execute(
            "SELECT CAST(COUNT(DISTINCT key) AS INTEGER) AS n FROM reward_definitions"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert first_count == 25
    assert first_path_reward_count == 5
    assert second_count == 25
    assert keys_count == 25


def test_living_space_service_unlocks_first_reward_for_each_path(client):
    import database
    from services.living_space_service import (
        get_user_space_state,
        unlock_first_path_reward_for_mission,
    )

    user = register_user(client, username="LivingSpaceAllPathsUser")
    user_id = user["user_id"]

    conn = database.get_db_connection()
    try:
        missions = conn.execute(
            """
            SELECT p.key AS path_key, MIN(m.id) AS mission_id
            FROM paths p
            JOIN challenges c ON c.path_id = p.id
            JOIN missions m ON m.challenge_id = c.id
            WHERE p.key IN ('career', 'creativity', 'fitness', 'learning', 'sleep')
              AND m.status = 'Active'
              AND COALESCE(m.mission_intensity, 'main') = 'main'
            GROUP BY p.key
            """
        ).fetchall()
    finally:
        conn.close()

    mission_by_path = {row["path_key"]: row["mission_id"] for row in missions}
    assert set(mission_by_path) == set(FIRST_PATH_REWARDS)

    unlocked_keys = {}
    for path_key, mission_id in mission_by_path.items():
        first_payload, first_status = unlock_first_path_reward_for_mission(
            user_id,
            mission_id,
        )
        repeat_payload, repeat_status = unlock_first_path_reward_for_mission(
            user_id,
            mission_id,
        )

        assert first_status == 200
        assert first_payload["ok"] is True
        assert first_payload["newly_unlocked"] is True
        assert first_payload["reward"]["path_key"] == path_key
        assert first_payload["reward"]["key"] == FIRST_PATH_REWARDS[path_key]
        assert first_payload["reward"]["source_type"] == "mission_reward"
        assert first_payload["reward"]["source_id"] == mission_id
        assert repeat_status == 200
        assert repeat_payload["ok"] is True
        assert repeat_payload["newly_unlocked"] is False
        unlocked_keys[path_key] = first_payload["reward"]["key"]

    state_payload, state_status = get_user_space_state(user_id)
    unlocked = [
        reward for reward in state_payload["rewards"]
        if reward["unlocked"]
    ]
    unlocked_by_path = {
        reward["path_key"]: reward["key"]
        for reward in unlocked
    }

    assert state_status == 200
    assert unlocked_keys == FIRST_PATH_REWARDS
    assert unlocked_by_path == FIRST_PATH_REWARDS
    assert len(state_payload["unlocked_objects"]) == 5
    assert len(state_payload["locked_preview_objects"]) == 20
    assert len(state_payload["next_rewards"]) == 5
    assert state_payload["has_unseen_rewards"] is True


def test_living_space_service_unlocks_reward_idempotently(client):
    from services.living_space_service import (
        get_user_space_state,
        list_reward_definitions,
        unlock_reward,
    )

    user = register_user(client, username="LivingSpaceUser")
    user_id = user["user_id"]

    definitions = list_reward_definitions()
    reward = next(
        item
        for item in definitions
        if item["key"] == "creativity_sketchbook"
    )

    first_payload, first_status = unlock_reward(
        user_id,
        reward["id"],
        source_type="mission_reward",
        source_id=123,
    )
    repeat_payload, repeat_status = unlock_reward(
        user_id,
        reward["id"],
        source_type="mission_reward",
        source_id=123,
    )
    state_payload, state_status = get_user_space_state(user_id)

    unlocked_rewards = [
        item
        for item in state_payload["rewards"]
        if item["unlocked"]
    ]

    assert first_status == 200
    assert first_payload["ok"] is True
    assert first_payload["newly_unlocked"] is True
    assert repeat_status == 200
    assert repeat_payload["ok"] is True
    assert repeat_payload["newly_unlocked"] is False
    assert state_status == 200
    assert state_payload["space"]["theme"] == "default"
    assert state_payload["space"]["current_stage"] == 1
    assert len(state_payload["rewards"]) == 25
    assert [item["key"] for item in unlocked_rewards] == ["creativity_sketchbook"]
    assert unlocked_rewards[0]["source_type"] == "mission_reward"
    assert unlocked_rewards[0]["source_id"] == 123

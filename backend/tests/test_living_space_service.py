from helpers import register_user


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

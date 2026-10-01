from helpers import auth_headers, register_user


def _complete_first_fitness_mission(client, headers):
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

    return client.post(
        f"/me/missions/{main_mission['mission_id']}/done",
        headers=headers,
    ).get_json()


def test_living_space_state_endpoint_returns_locked_previews(client):
    user = register_user(client, username="SpaceStateUser")
    headers = auth_headers(user["access_token"])

    res = client.get("/me/space", headers=headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["space"]["theme"] == "default"
    assert data["space"]["current_stage"] == 1
    assert len(data["zones"]) == 5
    assert len(data["rewards"]) == 25
    assert len(data["unlocked_objects"]) == 0
    assert len(data["locked_preview_objects"]) == 25
    assert len(data["next_rewards"]) == 5
    assert data["has_unseen_rewards"] is False


def test_living_space_reward_seen_endpoint_preserves_unlock(client):
    user = register_user(client, username="SpaceSeenUser")
    headers = auth_headers(user["access_token"])

    done_data = _complete_first_fitness_mission(client, headers)
    reward_id = done_data["living_space_reward"]["id"]

    rewards_res = client.get("/me/space/rewards", headers=headers)
    seen_res = client.post(
        f"/me/space/rewards/{reward_id}/seen",
        headers=headers,
    )
    space_res = client.get("/me/space", headers=headers)

    rewards_data = rewards_res.get_json()
    seen_data = seen_res.get_json()
    space_data = space_res.get_json()
    unlocked = [
        reward for reward in space_data["rewards"]
        if reward["unlocked"]
    ]

    assert rewards_res.status_code == 200
    assert rewards_data["ok"] is True
    assert rewards_data["has_unseen_rewards"] is True
    assert len(rewards_data["rewards"]) == 25
    assert seen_res.status_code == 200
    assert seen_data["reward"]["key"] == "fitness_water_bottle"
    assert seen_data["reward"]["is_seen"] is True
    assert space_res.status_code == 200
    assert space_data["has_unseen_rewards"] is False
    assert [reward["key"] for reward in unlocked] == ["fitness_water_bottle"]
    assert unlocked[0]["is_seen"] is True


def test_living_space_seen_rejects_locked_reward(client):
    user = register_user(client, username="SpaceLockedSeenUser")
    headers = auth_headers(user["access_token"])

    space_data = client.get("/me/space", headers=headers).get_json()
    locked_reward = space_data["locked_preview_objects"][0]

    res = client.post(
        f"/me/space/rewards/{locked_reward['id']}/seen",
        headers=headers,
    )

    assert res.status_code == 404
    assert res.get_json()["error"] == "reward_not_unlocked"

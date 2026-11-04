from helpers import auth_headers, register_user


def _join_first_fitness_challenge(client, headers):
    paths_data = client.get("/paths", headers=headers).get_json()
    fitness_path = next(item for item in paths_data["items"] if item["key"] == "fitness")

    client.post(f"/paths/{fitness_path['path_id']}/start", headers=headers)
    challenge_id = client.get(
        f"/paths/{fitness_path['path_id']}/challenges",
        headers=headers,
    ).get_json()["items"][0]["challenge_id"]
    join_data = client.post(f"/challenges/{challenge_id}/join", json={}, headers=headers).get_json()

    return fitness_path["path_id"], challenge_id, join_data["enrollment_id"]


def _today(client, headers):
    return client.get("/me/today-missions", headers=headers).get_json()["missions"]


def _family(missions):
    main = next(m for m in missions if m["mission_intensity"] == "main" and m["unlock_after_days"] == 0)
    tiny = next(
        m for m in missions
        if m["mission_intensity"] == "tiny" and m["parent_mission_id"] == main["mission_id"]
    )
    bonus = next(
        m for m in missions
        if m["mission_intensity"] == "bonus" and m["parent_mission_id"] == main["mission_id"]
    )
    return main, tiny, bonus


def _by_id(missions, mission):
    return next(m for m in missions if m["mission_id"] == mission["mission_id"])


def _setup(client, username):
    user = register_user(client, username=username)
    headers = auth_headers(user["access_token"])
    path_id, challenge_id, enrollment_id = _join_first_fitness_challenge(client, headers)
    main, tiny, bonus = _family(_today(client, headers))
    return headers, path_id, challenge_id, enrollment_id, main, tiny, bonus


def test_family_closed_is_false_for_an_open_family(client):
    headers, _, _, _, main, tiny, bonus = _setup(client, "FamilyOpen")

    missions = _today(client, headers)

    assert all(mission["family_closed"] is False for mission in missions)
    assert {_by_id(missions, m)["status"] for m in (main, tiny, bonus)} == {"pending"}


def test_main_done_closes_its_tiny_on_every_payload(client):
    headers, path_id, challenge_id, enrollment_id, main, tiny, bonus = _setup(client, "FamilyMainDone")

    client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)

    missions = _today(client, headers)
    assert _by_id(missions, main)["family_closed"] is False
    assert _by_id(missions, tiny)["family_closed"] is True
    assert _by_id(missions, bonus)["family_closed"] is False

    path_items = client.get(f"/paths/{path_id}/challenges", headers=headers).get_json()["items"]
    path_missions = next(c for c in path_items if c["challenge_id"] == challenge_id)["missions"]
    assert _by_id(path_missions, tiny)["family_closed"] is True
    assert _by_id(path_missions, main)["family_closed"] is False

    enrollment = client.get(f"/me/enrollments/{enrollment_id}", headers=headers).get_json()
    enrollment_missions = enrollment["missions"]
    assert _by_id(enrollment_missions, tiny)["family_closed"] is True
    assert _by_id(enrollment_missions, bonus)["family_closed"] is False


def test_tiny_done_closes_its_main(client):
    headers, _, _, _, main, tiny, bonus = _setup(client, "FamilyTinyDone")

    client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers)

    missions = _today(client, headers)
    assert _by_id(missions, main)["family_closed"] is True
    assert _by_id(missions, tiny)["family_closed"] is False
    assert _by_id(missions, bonus)["family_closed"] is False


def test_skip_on_either_member_closes_the_family(client):
    headers, _, _, _, main, tiny, _ = _setup(client, "FamilySkipMain")
    client.post(f"/me/missions/{main['mission_id']}/skip", headers=headers)
    missions = _today(client, headers)
    assert _by_id(missions, tiny)["family_closed"] is True
    assert _by_id(missions, main)["family_closed"] is False

    headers, _, _, _, main, tiny, _ = _setup(client, "FamilySkipTiny")
    client.post(f"/me/missions/{tiny['mission_id']}/skip", headers=headers)
    missions = _today(client, headers)
    assert _by_id(missions, main)["family_closed"] is True


def test_bonus_done_does_not_close_the_family(client):
    headers, _, _, _, main, tiny, bonus = _setup(client, "FamilyBonusDone")

    client.post(f"/me/missions/{bonus['mission_id']}/done", headers=headers)

    missions = _today(client, headers)
    assert _by_id(missions, main)["family_closed"] is False
    assert _by_id(missions, tiny)["family_closed"] is False


def test_family_closed_helper_ignores_other_families_and_bonus():
    from services.mission_service import _family_closed

    missions = [
        {"mission_id": 1, "mission_intensity": "main", "status": "pending"},
        {"mission_id": 2, "mission_intensity": "tiny", "parent_mission_id": 1, "status": "pending"},
        {"mission_id": 3, "mission_intensity": "bonus", "parent_mission_id": 1, "status": "done"},
        {"mission_id": 4, "mission_intensity": "main", "status": "done"},
        {"mission_id": 5, "mission_intensity": "tiny", "parent_mission_id": 4, "today_status": "skipped"},
    ]

    assert _family_closed(missions, missions[0]) is False
    assert _family_closed(missions, missions[1]) is False
    assert _family_closed(missions, missions[2]) is False
    assert _family_closed(missions, missions[3]) is True
    assert _family_closed(missions, missions[4]) is True
    assert _family_closed(missions, None) is False


def _log_rows(mission_id):
    import database

    conn = database.get_db_connection()
    try:
        return conn.execute(
            "SELECT status, xp_earned FROM mission_logs WHERE mission_id = ?",
            (mission_id,),
        ).fetchall()
    finally:
        conn.close()


def _stats(client, headers):
    return client.get("/me/stats", headers=headers).get_json()["stats"]


def test_second_member_done_earns_no_xp_and_writes_no_log(client):
    headers, _, _, _, main, tiny, _ = _setup(client, "FamilySecondDone")
    client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)
    before = _stats(client, headers)

    res = client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["mission"]["already_done"] is True
    assert data["mission"]["family_closed"] is True
    assert data["mission"]["xp_awarded"] == 0
    assert data["mission"]["status"] == "pending"
    assert data["checkin"]["already_checked"] is True
    assert data["reward_sequence"] == []
    assert _log_rows(tiny["mission_id"]) == []
    after = _stats(client, headers)
    assert after["total_points"] == before["total_points"]
    assert after["total_checkins"] == before["total_checkins"] == 1


def test_main_after_tiny_done_is_already_counted(client):
    headers, _, _, _, main, tiny, _ = _setup(client, "FamilyMainAfterTiny")
    client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers)
    before = _stats(client, headers)

    data = client.post(f"/me/missions/{main['mission_id']}/done", headers=headers).get_json()

    assert data["mission"]["already_done"] is True
    assert data["mission"]["xp_awarded"] == 0
    assert _log_rows(main["mission_id"]) == []
    assert _stats(client, headers)["total_points"] == before["total_points"]


def test_skip_on_a_closed_member_writes_no_log(client):
    headers, _, _, _, main, tiny, _ = _setup(client, "FamilySkipClosed")
    client.post(f"/me/missions/{main['mission_id']}/done", headers=headers)

    res = client.post(f"/me/missions/{tiny['mission_id']}/skip", json={"reason": "no_time"}, headers=headers)

    assert res.status_code == 200
    assert res.get_json()["mission"]["family_closed"] is True
    assert _log_rows(tiny["mission_id"]) == []
    assert _by_id(_today(client, headers), main)["status"] == "done"


def test_main_skipped_then_tiny_done_is_already_counted(client):
    headers, _, _, _, main, tiny, _ = _setup(client, "FamilySkipThenTiny")
    client.post(f"/me/missions/{main['mission_id']}/skip", headers=headers)

    data = client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers).get_json()

    assert data["mission"]["already_done"] is True
    assert data["mission"]["xp_awarded"] == 0
    assert _log_rows(tiny["mission_id"]) == []
    assert _stats(client, headers)["total_checkins"] == 0


def test_the_skipped_member_itself_can_still_be_done(client):
    headers, _, _, _, main, tiny, _ = _setup(client, "FamilySkipUndo")
    client.post(f"/me/missions/{main['mission_id']}/skip", headers=headers)

    data = client.post(f"/me/missions/{main['mission_id']}/done", headers=headers).get_json()

    assert data["mission"]["status"] == "done"
    assert data["mission"]["xp_awarded"] > 0
    missions = _today(client, headers)
    assert _by_id(missions, tiny)["family_closed"] is True


def test_bonus_is_unchanged_by_the_family_rule(client):
    headers, _, _, _, main, tiny, bonus = _setup(client, "FamilyBonusAfter")
    client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers)

    data = client.post(f"/me/missions/{bonus['mission_id']}/done", headers=headers).get_json()

    assert data["mission"]["status"] == "done"
    assert data["mission"]["xp_awarded"] > 0
    assert "family_closed" not in data["mission"]
    assert [row["status"] for row in _log_rows(bonus["mission_id"])] == ["done"]


def test_ringo_does_not_offer_a_closed_member(client):
    from services.ringo_brain_service import get_today_ringo_guidance

    user = register_user(client, username="FamilyRingoSkip")
    headers = auth_headers(user["access_token"])
    _join_first_fitness_challenge(client, headers)
    main, tiny, _ = _family(_today(client, headers))

    client.post(f"/me/missions/{main['mission_id']}/skip", headers=headers)
    payload, code = get_today_ringo_guidance(user["user_id"])

    assert code == 200
    assert payload["agenda"]["next_mission_id"] != tiny["mission_id"]
    assert (payload.get("mission") or {}).get("mission_id") != tiny["mission_id"]
    assert payload["progress"]["today_saved"] is False


def test_ringo_today_saved_by_a_tiny_still_counts_once(client):
    from services.ringo_brain_service import get_today_ringo_guidance

    user = register_user(client, username="FamilyRingoTiny")
    headers = auth_headers(user["access_token"])
    _join_first_fitness_challenge(client, headers)
    main, tiny, _ = _family(_today(client, headers))

    first = client.post(f"/me/missions/{tiny['mission_id']}/done", headers=headers).get_json()
    second = client.post(f"/me/missions/{main['mission_id']}/done", headers=headers).get_json()
    payload, _ = get_today_ringo_guidance(user["user_id"])

    assert [step["type"] for step in first["reward_sequence"]].count("today_saved") == 1
    assert second["reward_sequence"] == []
    assert payload["progress"]["today_saved"] is True
    assert _stats(client, headers)["total_checkins"] == 1

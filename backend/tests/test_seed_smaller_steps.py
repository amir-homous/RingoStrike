import copy
from datetime import datetime, timedelta, timezone

import database
from helpers import auth_headers, register_user
from services import path_seed_service as seed
from utils.date_utils import utc_today_iso

# #410: the 30 smaller steps for the day-2 and day-3 Main missions.
NEW_PARENTS = [
    "drink-water", "energy-note", "warm-up", "cool-down", "posture-check", "mobility-note",
    "capture-note", "apply-small", "highlight-one", "share-insight", "choose-drill", "review-progress",
    "define-output", "close-loop", "collect-proof", "next-edit", "update-context", "next-contact",
    "make-small", "archive-spark", "polish-one-pass", "share-or-save", "remix-it", "save-version",
    "clear-one-thing", "soft-close", "prepare-room", "sleep-note", "no-rush-start", "energy-check",
]
NEW_KEYS = {f"{parent}-tiny" for parent in NEW_PARENTS}
# The seed as shipped (with the 30), kept before any test swaps MVP_PATHS.
FULL_PATHS = copy.deepcopy(seed.MVP_PATHS)


def _seed_entries():
    """(challenge name, payload) for every seeded mission, in list order."""
    out = []
    for path in FULL_PATHS:
        for challenge in path["challenges"]:
            for index, mission in enumerate(challenge["missions"], start=1):
                out.append((challenge["name"], seed._mission_seed_payload(mission, index)))
    return out


def _old_paths():
    """The seed as it was before #410: the same lists without the 30 appended smaller steps."""
    paths = copy.deepcopy(FULL_PATHS)
    for path in paths:
        for challenge in path["challenges"]:
            challenge["missions"] = [m for m in challenge["missions"] if m[0] not in NEW_KEYS]
    return paths


def _snapshot(conn):
    rows = conn.execute(
        """
        SELECT m.id, m.key, c.name AS challenge, m.title, m.description, m.xp_reward, m.order_index,
               m.unlock_after_days, m.mission_intensity, m.estimated_minutes, m.parent_mission_id, m.status
        FROM missions m JOIN challenges c ON c.id = m.challenge_id
        ORDER BY m.id
        """
    ).fetchall()
    return {(r["challenge"], r["key"]): dict(r) for r in rows}


def _counts(conn):
    return {
        table: conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
        for table in ("mission_logs", "checkins", "missions", "challenges", "paths")
    }


def test_new_seed_entries_are_appended_with_parent_day():
    entries = _seed_entries()
    by_key = {(name, p["key"]): p for name, p in entries}
    new = [(name, p) for name, p in entries if p["key"] in NEW_KEYS]
    assert len(new) == 30
    # Keys are unique per challenge (the DB rule); the 30 new keys are unique across the whole seed.
    assert len({(name, p["key"]) for name, p in entries}) == len(entries)
    all_keys = [p["key"] for _, p in entries]
    assert all(all_keys.count(key) == 1 for key in NEW_KEYS)

    for name, p in new:
        parent = by_key[(name, p["parent_mission_key"])]
        assert parent["mission_intensity"] == "main"
        assert p["mission_intensity"] == "tiny"
        assert p["xp_reward"] == 3
        assert p["unlock_after_days"] == parent["unlock_after_days"] in (1, 2)
        assert p["estimated_minutes"] <= parent["estimated_minutes"]

    # Appended: in every challenge the new rows come after all the existing ones.
    for path in FULL_PATHS:
        for challenge in path["challenges"]:
            keys = [m[0] for m in challenge["missions"]]
            flags = [key in NEW_KEYS for key in keys]
            assert flags == sorted(flags), f"{challenge['name']}: a new smaller step is not at the end"

    # The 15 day-1 smaller steps keep day 0.
    old_tinies = [p for _, p in entries if p["mission_intensity"] == "tiny" and p["key"] not in NEW_KEYS]
    assert len(old_tinies) == 15
    assert all(p["unlock_after_days"] == 0 for p in old_tinies)


def test_seed_update_keeps_existing_rows_and_is_idempotent(client, monkeypatch, tmp_path):
    # 1) A fresh database seeded before #410 (the client fixture's own DB already has the new seed),
    #    with a user who has logs and check-ins.
    monkeypatch.setattr(database, "DB_NAME", str(tmp_path / "before_410.db"))
    monkeypatch.setattr(seed, "MVP_PATHS", _old_paths())
    database.init_db()
    conn = database.get_db_connection()
    try:
        before = _snapshot(conn)
    finally:
        conn.close()
    assert not any(key in NEW_KEYS for _, key in before)

    user = register_user(client, username="SeedKeeper")
    headers = auth_headers(user["access_token"])
    items = client.get("/challenges", headers=headers).get_json()["items"]
    joined = next(item for item in items if item["name"] == "Move Your Body")
    enrollment_id = client.post(f"/challenges/{joined['challenge_id']}/join", json={}, headers=headers).get_json()["enrollment_id"]
    missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
    main = next(m for m in missions if m.get("key") == "move-10")
    assert client.post(f"/me/missions/{main['mission_id']}/done", json={}, headers=headers).status_code == 200

    conn = database.get_db_connection()
    try:
        counts_before = _counts(conn)
        assert counts_before["mission_logs"] >= 1 and counts_before["checkins"] >= 1

        # 2) The new seed, twice (as two restarts would run it).
        monkeypatch.setattr(seed, "MVP_PATHS", copy.deepcopy(FULL_PATHS))
        seed.ensure_mvp_paths_and_missions(conn)
        conn.commit()
        first = _snapshot(conn)
        seed.ensure_mvp_paths_and_missions(conn)
        conn.commit()
        second = _snapshot(conn)
        counts_after = _counts(conn)
    finally:
        conn.close()

    # Every existing mission keeps its id, order, day, text, XP and parent.
    for key, row in before.items():
        assert first[key] == row, f"{key} changed"

    # The 30 new rows exist exactly once, linked to the right parent, with its day and their minutes.
    added = {key: row for key, row in first.items() if key not in before}
    assert {key for _, key in added} == NEW_KEYS
    assert len(added) == 30
    by_id = {row["id"]: row for row in first.values()}
    expected = {p["key"]: (name, p) for name, p in _seed_entries() if p["key"] in NEW_KEYS}
    for (challenge, key), row in added.items():
        name, payload = expected[key]
        parent = by_id[row["parent_mission_id"]]
        assert challenge == name
        assert parent["key"] == payload["parent_mission_key"] and parent["mission_intensity"] == "main"
        assert row["unlock_after_days"] == parent["unlock_after_days"]
        assert row["estimated_minutes"] == payload["estimated_minutes"]
        assert row["xp_reward"] == 3 and row["mission_intensity"] == "tiny" and row["status"] == "Active"

    # A second run changes nothing; logs and check-ins are untouched.
    assert second == first
    assert counts_after["mission_logs"] == counts_before["mission_logs"]
    assert counts_after["checkins"] == counts_before["checkins"]
    assert counts_after["missions"] == counts_before["missions"] + 30
    assert enrollment_id


def test_no_smaller_step_shows_before_its_parent(client):
    user = register_user(client, username="SeedDays")
    headers = auth_headers(user["access_token"])
    items = client.get("/challenges", headers=headers).get_json()["items"]
    names = {"Move Your Body", "Deep Work Sprint", "Morning Recovery"}
    enrollment_ids = []
    for item in items:
        if item["name"] in names:
            data = client.post(f"/challenges/{item['challenge_id']}/join", json={}, headers=headers).get_json()
            enrollment_ids.append(data["enrollment_id"])
    assert len(enrollment_ids) == 3

    for days_ago in (0, 1, 2):
        joined = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        conn = database.get_db_connection()
        try:
            conn.executemany("UPDATE enrollments SET joined_at = ? WHERE id = ?", [(joined, e) for e in enrollment_ids])
            conn.commit()
        finally:
            conn.close()
        missions = client.get("/me/today-missions", headers=headers).get_json()["missions"]
        visible = {m["mission_id"]: m for m in missions}
        tinies = [m for m in missions if m.get("mission_intensity") == "tiny"]
        for tiny in tinies:
            assert tiny.get("parent_mission_id") in visible, f"day {days_ago + 1}: {tiny.get('key')} shows without its parent"
        new_open = {m.get("key") for m in tinies if m.get("key") in NEW_KEYS}
        mains_open = {m.get("key") for m in missions if m.get("mission_intensity", "main") == "main"}
        assert new_open == {f"{key}-tiny" for key in mains_open if f"{key}-tiny" in NEW_KEYS}, f"day {days_ago + 1}"
        assert len(new_open) == {0: 0, 1: 3, 2: 6}[days_ago], f"day {days_ago + 1}: {sorted(new_open)}"
    assert utc_today_iso()

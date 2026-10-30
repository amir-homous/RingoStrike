import database
from helpers import auth_headers
from services.username_service import display_name, member_display_name, stored_display_name


def _register(client, username, name):
    res = client.post(
        "/auth/register",
        json={"username": username, "password": "secret123", "name": name, "email": f"{username}@example.com"},
    )
    assert res.status_code == 201
    client.delete_cookie("ringo_token")
    return res.get_json()


def _db_user(username):
    conn = database.get_db_connection()
    try:
        return conn.execute("SELECT id, name, username FROM users WHERE username = ?", (username,)).fetchone()
    finally:
        conn.close()


def _set(username, **fields):
    # Test database only: simulate an older row (a name with "@", a private profile).
    conn = database.get_db_connection()
    try:
        for key, value in fields.items():
            conn.execute(f"UPDATE users SET {key} = ? WHERE username = ?", (value, username))
        conn.commit()
    finally:
        conn.close()


def _join_first(client, headers, name="Move Your Body"):
    items = client.get("/challenges", headers=headers).get_json()["items"]
    challenge = next(item for item in items if item["name"] == name)
    data = client.post(f"/challenges/{challenge['challenge_id']}/join", json={}, headers=headers).get_json()
    return challenge["challenge_id"], data["enrollment_id"]


def test_helper_rules():
    assert display_name("Sara", "sara1") == "Sara"
    assert display_name("sara@example.com", "sara1") == "sara1"
    assert display_name("  ", "sara1") == "sara1"
    assert display_name(None, None) == "Player"
    assert display_name("a@b", "x@y") == "Player"
    assert member_display_name("Sara", "sara1", "public") == "Sara"
    assert member_display_name("Sara", "sara1", None) == "Sara", "no setting means public"
    assert member_display_name("Sara", "sara1", "private") == "S."
    assert member_display_name("sara@example.com", "nima", "private") == "N.", "the initial never comes from an email"
    assert stored_display_name("Sara", "sara1") == "Sara"
    assert stored_display_name("sara@example.com", "sara1") == "sara1"
    assert stored_display_name("", "sara1") == "sara1"


def test_register_never_stores_a_name_with_at(client):
    _register(client, "regemail", "me@example.com")
    assert _db_user("regemail")["name"] == "regemail"
    _register(client, "regplain", "Sara Plain")
    assert _db_user("regplain")["name"] == "Sara Plain"


def test_own_surfaces_never_return_a_name_with_at(client):
    data = _register(client, "ownleak", "Own Name")
    headers = auth_headers(data["access_token"])
    _set("ownleak", name="own@example.com")
    responses = [
        client.get("/me", headers=headers).get_json(),
        client.get("/me/stats", headers=headers).get_json(),
        client.get("/me/profile", headers=headers).get_json(),
        client.get("/api/public/profile/ownleak").get_json(),
    ]
    for payload in responses:
        assert "own@example.com" not in str(payload)
    assert responses[0]["name"] == "ownleak"
    assert responses[1]["user"]["name"] == "ownleak"
    assert responses[2]["profile"]["name"] == "ownleak"
    # Shapes are unchanged: the same keys are still there.
    assert {"user_id", "username", "name", "email"} <= set(responses[0])


def test_member_surfaces_respect_visibility_and_hide_at(client):
    viewer = _register(client, "viewerone", "Viewer One")
    viewer_headers = auth_headers(viewer["access_token"])

    public = _register(client, "publicsara", "Sara Public")
    private = _register(client, "privatenima", "Nima Private")
    emailer = _register(client, "emailbo", "Bo")
    _set("privatenima", profile_visibility="private")
    _set("emailbo", name="bo@example.com")

    challenge_id = None
    for user in (public, private, emailer):
        challenge_id, _ = _join_first(client, auth_headers(user["access_token"]))
    _, viewer_enrollment = _join_first(client, viewer_headers)

    # /challenges (members_preview), /challenges/:id/members (login required) and the leaderboard.
    items = client.get("/challenges", headers=viewer_headers).get_json()["items"]
    preview = next(item for item in items if item["challenge_id"] == challenge_id)["members_preview"]
    members = client.get(f"/challenges/{challenge_id}/members", headers=viewer_headers).get_json()["items"]
    board = client.get(f"/me/enrollments/{viewer_enrollment}/leaderboard", headers=viewer_headers).get_json()

    names_seen = list(preview) + [m["user_name"] for m in members] + [r["name"] for r in board["overall"]]
    assert all("@" not in name for name in names_seen), names_seen
    assert "Nima Private" not in str(preview) + str(members) + str(board)

    # Public members are unchanged; a private member is an initial only (no user_id or username).
    public_row = next(m for m in members if m["username"] == "publicsara")
    assert public_row["user_name"] == "Sara Public"
    assert isinstance(public_row["user_id"], int) and public_row["telegram_username"] == "publicsara"
    assert next(m for m in members if m["username"] == "emailbo")["user_name"] == "emailbo"
    private_rows = [m for m in members if m["user_name"] == "N."]
    assert len(private_rows) == 1
    assert {k: private_rows[0][k] for k in ("user_id", "username", "telegram_username")} == {
        "user_id": None, "username": None, "telegram_username": None,
    }
    assert set(private_rows[0]) == set(public_row), "same keys for private and public rows"
    assert "privatenima" not in str(members)

    board_names = {r["name"]: r["username"] for r in board["overall"]}
    assert board_names["N."] is None, "leaderboard: private member has no username"
    assert board_names["Sara Public"] == "publicsara"
    assert board_names["emailbo"] == "emailbo"
    assert "privatenima" not in str(board)
    # members_preview keeps its shape: a list of strings (at most three).
    assert isinstance(preview, list) and all(isinstance(name, str) for name in preview)
    assert len(preview) <= 3


def test_existing_rows_are_not_modified(client):
    data = _register(client, "rowkeeper", "Row Keeper")
    _set("rowkeeper", name="row@example.com")
    client.get("/me", headers=auth_headers(data["access_token"]))
    client.get("/me/profile", headers=auth_headers(data["access_token"]))
    assert _db_user("rowkeeper")["name"] == "row@example.com", "reading never rewrites the stored name"


def test_profile_update_follows_the_register_rule(client):
    data = _register(client, "patchrule", "Patch Rule")
    headers = auth_headers(data["access_token"])

    res = client.patch("/api/profile", json={"name": "me@example.com"}, headers=headers)
    assert res.status_code == 200
    assert res.get_json() == {"ok": True}, "response shape unchanged"
    assert _db_user("patchrule")["name"] == "patchrule", "a name with @ is stored as the username"

    res = client.patch("/api/profile", json={"name": "  New Name  "}, headers=headers)
    assert res.get_json() == {"ok": True}
    assert _db_user("patchrule")["name"] == "New Name"

    client.patch("/api/profile", json={"bio": "hello"}, headers=headers)
    assert _db_user("patchrule")["name"] == "New Name", "updating only the bio leaves the name"

    res = client.patch("/api/profile", json={"name": "x" * 61}, headers=headers)
    assert res.status_code == 400 and res.get_json()["error"] == "name_too_long", "existing validation unchanged"


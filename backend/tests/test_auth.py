from helpers import auth_headers, register_user


def test_health(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json() == {"ok": True}


def test_register_login_and_me_with_bearer(client):
    register_data = register_user(client)

    assert register_data["username"] == "smokeuser"

    login_res = client.post(
        "/auth/login",
        json={
            "username": "smokeuser",
            "password": "secret123",
        },
    )

    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert login_data["ok"] is True
    assert login_data["access_token"]

    me_res = client.get(
        "/me",
        headers=auth_headers(login_data["access_token"]),
    )

    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["ok"] is True
    assert me_data["username"] == "smokeuser"
    assert me_data["auth_method"] == "local"


def test_username_validation_register_flow(client):
    invalid_cases = [
        ("ab", "invalid_username"),
        ("thisusernameiswaytoolongforrules", "invalid_username"),
        ("bad-name", "invalid_username"),
        ("bad name", "invalid_username"),
        ("admin", "invalid_username"),
        ("api", "invalid_username"),
        ("login", "invalid_username"),
        ("me", "invalid_username"),
    ]

    for username, expected_error in invalid_cases:
        safe_email_username = (
            username
            .replace(" ", "_")
            .replace("-", "_")
        )

        res = client.post(
            "/auth/register",
            json={
                "username": username,
                "password": "secret123",
                "name": "Invalid User",
                "email": f"{safe_email_username}@example.com",
            },
        )

        assert res.status_code == 400
        data = res.get_json()
        assert data["ok"] is False
        assert data["error"] == expected_error

    valid_res = client.post(
        "/auth/register",
        json={
            "username": "Valid_User_01",
            "password": "secret123",
            "name": "Valid User",
            "email": "valid_user_01@example.com",
        },
    )

    assert valid_res.status_code == 201
    valid_data = valid_res.get_json()
    assert valid_data["ok"] is True
    assert valid_data["username"] == "valid_user_01"

    duplicate_res = client.post(
        "/auth/register",
        json={
            "username": "valid_user_01",
            "password": "secret123",
            "name": "Duplicate User",
            "email": "duplicate@example.com",
        },
    )

    assert duplicate_res.status_code == 409
    duplicate_data = duplicate_res.get_json()
    assert duplicate_data["ok"] is False


def test_logout_clears_cookie_session(client):
    register_data = register_user(client, username="LogoutUser")

    cookie_me_res = client.get("/me")

    assert cookie_me_res.status_code == 200
    cookie_me_data = cookie_me_res.get_json()
    assert cookie_me_data["ok"] is True
    assert cookie_me_data["username"] == "logoutuser"

    logout_res = client.post("/auth/logout")

    assert logout_res.status_code == 200
    logout_data = logout_res.get_json()
    assert logout_data["ok"] is True

    after_logout_res = client.get("/me")

    assert after_logout_res.status_code == 401
    after_logout_data = after_logout_res.get_json()
    assert after_logout_data["ok"] is False
    assert after_logout_data["error"] == "unauthorized"

    bearer_me_res = client.get(
        "/me",
        headers=auth_headers(register_data["access_token"]),
    )

    assert bearer_me_res.status_code == 200
    bearer_me_data = bearer_me_res.get_json()
    assert bearer_me_data["ok"] is True
    assert bearer_me_data["username"] == "logoutuser"
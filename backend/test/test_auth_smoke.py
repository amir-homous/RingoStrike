import os
import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_users.db"

    monkeypatch.setenv("DB_PATH", str(test_db))
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("LOCAL_LOGIN_ENABLED", "True")
    monkeypatch.setenv("JWT_COOKIE_SECURE", "0")
    monkeypatch.setenv("JWT_COOKIE_SAMESITE", "Lax")

    import auth
    import app as app_module
    import database

    auth.JWT_SECRET = "test-jwt-secret"
    database.DB_NAME = str(test_db)

    flask_app = app_module.create_app()
    flask_app.config.update(TESTING=True)

    with flask_app.test_client() as test_client:
        yield test_client


def test_health(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json() == {"ok": True}


def test_register_login_and_me_with_bearer(client):
    register_res = client.post(
        "/auth/register",
        json={
            "username": "SmokeUser",
            "password": "secret123",
            "name": "Smoke User",
            "email": "smoke@example.com",
        },
    )

    assert register_res.status_code == 201
    register_data = register_res.get_json()
    assert register_data["ok"] is True
    assert register_data["username"] == "smokeuser"
    assert register_data["access_token"]

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
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )

    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["ok"] is True
    assert me_data["username"] == "smokeuser"
    assert me_data["auth_method"] == "local"
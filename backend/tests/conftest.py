import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent

for path in (BACKEND_DIR, TESTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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
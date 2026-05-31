import importlib

import pytest


def test_config_requires_secret_key_outside_development(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "")
    monkeypatch.setenv("JWT_SECRET", "production-jwt-secret")

    import config

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        importlib.reload(config)


def test_config_requires_jwt_secret_outside_development(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "production-secret-key")
    monkeypatch.setenv("JWT_SECRET", "")

    import config

    with pytest.raises(RuntimeError, match="JWT_SECRET must be set"):
        importlib.reload(config)


def test_config_allows_development_secret_fallbacks(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("SECRET_KEY", "")
    monkeypatch.setenv("JWT_SECRET", "")

    import config

    reloaded = importlib.reload(config)

    assert reloaded.Config.SECRET_KEY
    assert reloaded.Config.JWT_SECRET
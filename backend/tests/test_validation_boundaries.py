from flask import Flask, request

from helpers import auth_headers, register_user
from utils.validation_utils import parse_json_object_payload


def test_parse_json_object_payload_defaults_missing_body_to_empty_object():
    app = Flask(__name__)

    with app.test_request_context(method="PATCH"):
        payload, error = parse_json_object_payload(request)

    assert payload == {}
    assert error is None


def test_parse_json_object_payload_rejects_json_array():
    app = Flask(__name__)

    with app.test_request_context(method="PATCH", json=["bad"]):
        payload, error = parse_json_object_payload(request)

    assert payload is None
    assert error == "invalid_json_body"


def test_profile_settings_rejects_non_object_json_at_route_boundary(client):
    user = register_user(client, username="SettingsBoundaryUser")

    res = client.patch(
        "/api/me/profile/settings",
        json=["not", "an", "object"],
        headers=auth_headers(user["access_token"]),
    )

    assert res.status_code == 400
    data = res.get_json()
    assert data == {
        "ok": False,
        "error": "invalid_json_body",
    }

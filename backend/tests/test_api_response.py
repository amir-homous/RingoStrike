from flask import Flask

from utils.api_response import (
    error_response,
    ok_response,
)


def test_ok_response_shape():
    app = Flask(__name__)

    with app.app_context():
        response, status = ok_response(
            {
                "value": 123,
            },
            status_code=201,
        )

    assert status == 201

    data = response.get_json()

    assert data == {
        "ok": True,
        "value": 123,
    }


def test_error_response_minimal_shape():
    app = Flask(__name__)

    with app.app_context():
        response, status = error_response(
            "invalid_payload",
            400,
        )

    assert status == 400

    data = response.get_json()

    assert data == {
        "ok": False,
        "error": "invalid_payload",
    }


def test_error_response_optional_message_and_details():
    app = Flask(__name__)

    with app.app_context():
        response, status = error_response(
            "rate_limited",
            429,
            message="Too many attempts.",
            details={
                "window_seconds": 60,
            },
        )

    assert status == 429

    data = response.get_json()

    assert data == {
        "ok": False,
        "error": "rate_limited",
        "message": "Too many attempts.",
        "details": {
            "window_seconds": 60,
        },
    }
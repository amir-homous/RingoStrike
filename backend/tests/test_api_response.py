from flask import Flask

from utils.api_response import (
    API_ERROR_CONVENTION,
    error_response,
    ok_response,
    service_response,
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


def test_api_error_convention_documents_required_and_optional_fields():
    assert API_ERROR_CONVENTION == {
        "required": [
            "ok",
            "error",
        ],
        "optional": [
            "message",
            "details",
        ],
    }


def test_service_response_preserves_success_payload_shape():
    app = Flask(__name__)

    with app.app_context():
        response, status = service_response(
            {
                "ok": True,
                "items": [
                    "one",
                ],
            },
            200,
        )

    assert status == 200
    assert response.get_json() == {
        "ok": True,
        "items": [
            "one",
        ],
    }


def test_service_response_normalizes_error_payload_shape():
    app = Flask(__name__)

    with app.app_context():
        response, status = service_response(
            {
                "ok": False,
                "error": "invalid_payload",
                "message": "Invalid payload.",
                "details": {
                    "field": "name",
                },
            },
            400,
        )

    assert status == 400
    assert response.get_json() == {
        "ok": False,
        "error": "invalid_payload",
        "message": "Invalid payload.",
        "details": {
            "field": "name",
        },
    }

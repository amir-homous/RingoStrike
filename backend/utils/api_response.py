from __future__ import annotations

from flask import jsonify


API_ERROR_CONVENTION = {
    "required": [
        "ok",
        "error",
    ],
    "optional": [
        "message",
        "details",
    ],
}


def ok_response(
    payload: dict | None = None,
    status_code: int = 200,
):
    body = {
        "ok": True,
    }

    if payload:
        body.update(payload)

    return jsonify(body), status_code


def error_response(
    error: str,
    status_code: int = 400,
    *,
    message: str | None = None,
    details: dict | None = None,
):
    body = {
        "ok": False,
        "error": error,
    }

    if message:
        body["message"] = message

    if details:
        body["details"] = details

    return jsonify(body), status_code


def service_response(
    payload: dict,
    status_code: int,
    *,
    fallback_error: str = "api_error",
):
    if not payload.get("ok"):
        return error_response(
            payload.get("error", fallback_error),
            status_code,
            message=payload.get("message"),
            details=payload.get("details"),
        )

    clean_payload = {
        key: value
        for key, value in payload.items()
        if key != "ok"
    }

    return ok_response(clean_payload, status_code)

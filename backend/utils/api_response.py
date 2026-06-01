from __future__ import annotations

from flask import jsonify


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
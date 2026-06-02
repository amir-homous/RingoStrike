import os

from flask import Blueprint

from services.debug_service import sqlite_counts, sqlite_schema
from utils.api_response import error_response, service_response

debug_bp = Blueprint("debug_bp", __name__)


def _debug_enabled():
    return os.getenv("FLASK_ENV", "development") == "development"


def _debug_disabled_response():
    return error_response("debug_disabled", 403)


@debug_bp.get("/debug/sqlite/schema/<table>")
def debug_sqlite_schema(table):
    if not _debug_enabled():
        return _debug_disabled_response()

    payload, code = sqlite_schema(table)
    return service_response(
        payload,
        code,
        fallback_error="debug_error",
    )


@debug_bp.get("/debug/sqlite/counts")
def debug_sqlite_counts():
    if not _debug_enabled():
        return _debug_disabled_response()

    payload, code = sqlite_counts()
    return service_response(
        payload,
        code,
        fallback_error="debug_error",
    )

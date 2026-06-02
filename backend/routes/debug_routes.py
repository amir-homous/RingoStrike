import os

from flask import Blueprint, jsonify

from services.debug_service import sqlite_counts, sqlite_schema

debug_bp = Blueprint("debug_bp", __name__)


def _debug_enabled():
    return os.getenv("FLASK_ENV", "development") == "development"


def _debug_disabled_response():
    return jsonify({"ok": False, "error": "debug_disabled"}), 403


@debug_bp.get("/debug/sqlite/schema/<table>")
def debug_sqlite_schema(table):
    if not _debug_enabled():
        return _debug_disabled_response()

    payload, code = sqlite_schema(table)
    return jsonify(payload), code


@debug_bp.get("/debug/sqlite/counts")
def debug_sqlite_counts():
    if not _debug_enabled():
        return _debug_disabled_response()

    payload, code = sqlite_counts()
    return jsonify(payload), code

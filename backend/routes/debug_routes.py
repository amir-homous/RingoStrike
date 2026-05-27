from flask import Blueprint, jsonify
from services.debug_service import sqlite_counts, sqlite_schema

debug_bp = Blueprint('debug_bp', __name__)

@debug_bp.get('/debug/sqlite/schema/<table>')
def debug_sqlite_schema(table):
    payload, code = sqlite_schema(table)
    return jsonify(payload), code

@debug_bp.get('/debug/sqlite/counts')
def debug_sqlite_counts():
    payload, code = sqlite_counts()
    return jsonify(payload), code
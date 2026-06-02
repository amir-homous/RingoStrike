from __future__ import annotations

from database import get_db_connection
from services.public_activity_service import get_public_activity_feed
from services.profile_service import get_profile
from services.username_service import normalize_username


def get_public_profile(username: str):
    username = normalize_username(username)
    conn = get_db_connection()

    try:
        user = conn.execute(
            """
            SELECT id, username, profile_visibility
            FROM users
            WHERE lower(username) = lower(?)
            """,
            (username,),
        ).fetchone()

        if not user:
            return {"ok": False, "error": "profile_not_found"}, 404

        if user["profile_visibility"] != "public":
            return {"ok": False, "error": "profile_private"}, 403

        profile_payload, profile_code = get_profile(user["id"])

        if profile_code != 200:
            return profile_payload, profile_code

        activity_payload, _ = get_public_activity_feed(user["id"])

        profile = profile_payload.get("profile", {})

        public_profile = {
            "id": profile.get("id"),
            "name": profile.get("name"),
            "username": profile.get("username"),
            "avatar_url": profile.get("avatar_url"),
            "joined_date": profile.get("joined_date"),
            "title": profile.get("title"),
            "tagline": profile.get("tagline"),
            "bio": profile.get("bio", ""),
            "stats": profile.get("stats"),
            "recent_activity": activity_payload.get("events", []),
        }

        return {
            "ok": True,
            "profile": public_profile,
        }, 200

    finally:
        conn.close()

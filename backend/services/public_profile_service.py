from __future__ import annotations

from database import get_db_connection
from services.public_activity_service import get_public_activity_feed
from services.public_identity_service import get_public_identity
from services.profile_service import get_profile


def get_public_profile(username: str):
    conn = get_db_connection()

    try:
        user, error_payload, code = get_public_identity(username, conn=conn)
        if error_payload:
            return error_payload, code

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

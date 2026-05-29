from __future__ import annotations

from services.activity_service import get_activity_feed


PUBLIC_ALLOWED_EVENT_TYPES = {
    "checkin",
    "streak",
    "level_up",
    "achievement",
}


def get_public_activity_feed(user_id: int, limit: int = 20):
    payload, code = get_activity_feed(user_id, limit)

    if code != 200:
        return payload, code

    filtered_events = []

    for event in payload.get("events", []):
        event_type = event.get("type")

        if event_type not in PUBLIC_ALLOWED_EVENT_TYPES:
            continue

        filtered_events.append({
            "id": event.get("id"),
            "type": event.get("type"),
            "title": event.get("title"),
            "subtitle": event.get("subtitle"),
            "icon": event.get("icon"),
            "rarity": event.get("rarity"),
            "created_at": event.get("created_at"),
        })

    return {
        "ok": True,
        "events": filtered_events,
    }, 200
"""B26: optional check-in context for a done mission (#383).

When the user really did it, where (a place they pick, never GPS), how it felt, a short note,
and, for "Do it now", how long it took. Stored on mission_logs only (checkins stays the
counted record). Context never changes XP, rewards or streaks, and it is private to the owner:
no public payload, feed or log reads these fields.

Validation runs before any write; any invalid field rejects the whole request.
"""

from datetime import datetime, timedelta, timezone

from utils.date_utils import utc_iso_z, utc_now

MODES = ("now", "earlier")
PLACE_KEYS = ("home", "work_school", "gym", "outside", "cafe", "on_the_way", "other")
# Matches the approved B27 chips: سبک / خوب / معمولی / سخت ولی انجامش دادم / خسته.
FEELING_KEYS = ("light", "good", "okay", "hard_but_done", "tired")
FIELDS = ("mode", "performed_at", "place_key", "place_label", "feeling_key", "note", "duration_seconds")

PLACE_LABEL_MAX = 40
NOTE_MAX = 280
DURATION_MAX_SECONDS = 24 * 60 * 60
# Client clocks drift a little; a performed_at up to this far ahead of the server is accepted.
FUTURE_SKEW = timedelta(seconds=60)


def _text(value, field, max_length):
    if value is None:
        return None, None
    if not isinstance(value, str):
        return None, f"invalid_{field}"
    value = value.strip()
    if not value:
        return None, None
    if len(value) > max_length:
        return None, f"{field}_too_long"
    return value, None


def _choice(value, field, choices):
    if value is None:
        return None, None
    if not isinstance(value, str) or value not in choices:
        return None, f"invalid_{field}"
    return value, None


def _performed_at(value, now):
    """ISO time on today's UTC date (the app's day boundary, utc_today_iso), not in the future."""
    if value is None:
        return None, None
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        return None, "invalid_performed_at"
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None, "invalid_performed_at"
    parsed = parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    if parsed > now + FUTURE_SKEW:
        return None, "performed_at_in_future"
    if parsed.date() != now.date():
        return None, "performed_at_not_today"
    return utc_iso_z(min(parsed, now)), None


def parse_checkin_context(body, now=None):
    """Return (context, error). context is None when the body carries no context fields.

    context keys are the mission_logs columns: mode, performed_at, place_key, place_label,
    feeling_key, notes, duration_seconds.
    """
    if body is None:
        return None, None
    if not isinstance(body, dict):
        return None, "invalid_json_body"

    unknown = sorted(set(body) - set(FIELDS))
    if unknown:
        return None, "unknown_context_field"
    if not body:
        return None, None

    now = (now or utc_now()).astimezone(timezone.utc)
    context = {}

    for field, parse in (
        ("mode", lambda v: _choice(v, "mode", MODES)),
        ("place_key", lambda v: _choice(v, "place_key", PLACE_KEYS)),
        ("feeling_key", lambda v: _choice(v, "feeling_key", FEELING_KEYS)),
        ("place_label", lambda v: _text(v, "place_label", PLACE_LABEL_MAX)),
        ("notes", lambda v: _text(v, "note", NOTE_MAX)),
    ):
        source = "note" if field == "notes" else field
        value, error = parse(body.get(source))
        if error:
            return None, error
        context[field] = value

    if context["place_label"] and context["place_key"] != "other":
        return None, "place_label_requires_other"

    duration = body.get("duration_seconds")
    if duration is not None:
        if isinstance(duration, bool) or not isinstance(duration, int):
            return None, "invalid_duration_seconds"
        if context["mode"] != "now":
            return None, "duration_requires_now"
        if not 1 <= duration <= DURATION_MAX_SECONDS:
            return None, "invalid_duration_seconds"
    context["duration_seconds"] = duration

    if context["mode"] == "now":
        # "Do it now" happens at save time: the server's clock, not the client's.
        context["performed_at"] = utc_iso_z(now)
    else:
        value, error = _performed_at(body.get("performed_at"), now)
        if error:
            return None, error
        context["performed_at"] = value

    if not any(value is not None for value in context.values()):
        return None, None
    return context, None


def public_context(context):
    """Owner-only echo in the done response (the note text itself is not echoed)."""
    if not context:
        return None
    return {
        "mode": context.get("mode"),
        "performed_at": context.get("performed_at"),
        "place_key": context.get("place_key"),
        "place_label": context.get("place_label"),
        "feeling_key": context.get("feeling_key"),
        "has_note": bool(context.get("notes")),
        "duration_seconds": context.get("duration_seconds"),
    }

def safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def safe_bool(value) -> bool:
    s = str(value or "").strip().lower()
    return s in ("1", "true", "yes", "on")


def parse_json_object_payload(request, *, default_empty=True):
    payload = request.get_json(silent=True)

    if payload is None and default_empty:
        return {}, None

    if not isinstance(payload, dict):
        return None, "invalid_json_body"

    return payload, None

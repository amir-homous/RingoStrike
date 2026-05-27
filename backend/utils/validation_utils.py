def safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def safe_bool(value) -> bool:
    s = str(value or "").strip().lower()
    return s in ("1", "true", "yes", "on")
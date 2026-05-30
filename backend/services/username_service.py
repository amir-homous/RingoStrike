import re

RESERVED_USERNAMES = {
    "admin",
    "api",
    "auth",
    "dashboard",
    "settings",
    "profile",
    "profiles",
    "public",
    "login",
    "register",
    "logout",
    "me",
    "u",
}


def normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def is_valid_username(username: str) -> bool:
    if not username:
        return False

    if len(username) < 3 or len(username) > 24:
        return False

    if username in RESERVED_USERNAMES:
        return False

    pattern = r"^[a-z0-9_]+$"

    return re.match(pattern, username) is not None
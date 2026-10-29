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

# Display names (one rule for every API response that shows a name):
# - a name that contains "@" (an email typed into the free-text name field) is never returned;
#   the username is shown instead, then "Player";
# - other users see a private profile only as an initial ("S."), never the full name.
DISPLAY_NAME_FALLBACK = "Player"


def display_name(name, username=None) -> str:
    value = (name or "").strip()
    if value and "@" not in value:
        return value
    fallback = (username or "").strip()
    if fallback and "@" not in fallback:
        return fallback
    return DISPLAY_NAME_FALLBACK


def member_display_name(name, username=None, profile_visibility=None) -> str:
    shown = display_name(name, username)
    if (profile_visibility or "public") != "public":
        return f"{shown[:1].upper()}."
    return shown


def stored_display_name(name, username) -> str:
    """The name to store at sign-up: the typed name, or the username when it is empty or has "@"."""
    value = (name or "").strip()
    return value if value and "@" not in value else username

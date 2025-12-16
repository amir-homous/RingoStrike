import hashlib
import hmac
import time
from urllib.parse import unquote_plus

def verify_telegram_login(data: dict, bot_token: str, max_age_seconds: int = 86400) -> bool:
    """
    Telegram Login Widget verification:
    - Build data_check_string from sorted key=val (excluding 'hash')
    - secret_key = sha256(bot_token)
    - compare HMAC-SHA256(data_check_string, secret_key) with received hash
    - optionally validate auth_date freshness
    """
    if "hash" not in data:
        return False

    recv_hash = data["hash"]
    check_items = []
    for k in sorted(data.keys()):
        if k == "hash":
            continue
        v = data[k]
        if isinstance(v, str):
            v = unquote_plus(v)
        check_items.append(f"{k}={v}")
    data_check_string = "\n".join(check_items)

    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    if calc_hash != recv_hash:
        return False

    # optional auth_date freshness
    try:
        auth_date = int(data.get("auth_date", "0"))
        if auth_date and (time.time() - auth_date) > max_age_seconds:
            return False
    except ValueError:
        return False

    return True

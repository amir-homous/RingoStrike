from datetime import datetime, timedelta, timezone


def utc_today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def date_range_days(days: int) -> list[str]:
    today = datetime.now(timezone.utc).date()
    return [(today - timedelta(days=(days - 1 - i))).isoformat() for i in range(days)]
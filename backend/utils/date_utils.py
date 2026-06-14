from datetime import datetime, time, timedelta, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_today_iso() -> str:
    return utc_now().date().isoformat()


def ringo_day_metadata(now: datetime | None = None) -> dict:
    current = (now or utc_now()).astimezone(timezone.utc)
    next_reset = datetime.combine(
        current.date() + timedelta(days=1),
        time.min,
        tzinfo=timezone.utc,
    )

    return {
        "date": current.date().isoformat(),
        "next_reset_at": utc_iso_z(next_reset),
        "reset_basis": "utc",
        "server_now": utc_iso_z(current),
    }


def date_range_days(days: int) -> list[str]:
    today = utc_now().date()
    return [(today - timedelta(days=(days - 1 - i))).isoformat() for i in range(days)]

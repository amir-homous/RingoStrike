from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque


_attempts: dict[str, Deque[float]] = defaultdict(deque)


def is_rate_limited(
    key: str,
    *,
    limit: int = 10,
    window_seconds: int = 60,
) -> bool:
    now = time.time()
    bucket = _attempts[key]

    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()

    if len(bucket) >= limit:
        return True

    bucket.append(now)
    return False


def reset_rate_limits() -> None:
    _attempts.clear()
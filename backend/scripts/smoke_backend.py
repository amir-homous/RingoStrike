from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_TIMEOUT = 10


def fetch_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "RingoStrike-SmokeCheck/1.0",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except HTTPError as exc:
        raise RuntimeError(
            f"HTTP {exc.code} while requesting {url}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"Network error while requesting {url}: {exc.reason}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON response from {url}"
        ) from exc


def assert_ok(payload: dict, label: str) -> None:
    if payload.get("ok") is not True:
        raise RuntimeError(
            f"{label} check failed: {payload}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run RingoStrike backend deployment smoke checks."
    )

    parser.add_argument(
        "--base-url",
        default="http://localhost:5005",
        help="Backend base URL, e.g. https://api.ringostrike.com",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds.",
    )

    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    checks = [
        ("health", f"{base_url}/health"),
        ("config", f"{base_url}/health/config"),
    ]

    try:
        for label, url in checks:
            payload = fetch_json(
                url,
                timeout=args.timeout,
            )

            assert_ok(payload, label)

            print(
                f"[PASS] {label}: "
                f"{json.dumps(payload, sort_keys=True)}"
            )

    except RuntimeError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    print("[PASS] Backend smoke checks completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
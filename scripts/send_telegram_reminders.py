#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.reminder_service import (
    send_due_mission_telegram_reminders,
    send_unchecked_telegram_reminders,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Send Telegram reminders for active enrollments not checked in today.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Select reminder targets without sending Telegram messages.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of selected enrollments to process.",
    )
    parser.add_argument(
        "--due-missions",
        action="store_true",
        help="Send due mission-level reminders instead of unchecked enrollment reminders.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.due_missions:
        result = send_due_mission_telegram_reminders(
            dry_run=args.dry_run,
            limit=args.limit,
        )

        logging.info(
            "mission reminders dry_run=%s checked=%s due=%s sent=%s skipped=%s failed=%s",
            result["dry_run"],
            result["checked"],
            result["due"],
            result["sent"],
            result["skipped"],
            result["failed"],
        )

        for item in result["items"]:
            logging.info(
                "mission_log=%s user=%s mission=%s status=%s reason=%s error=%s",
                item.get("mission_log_id"),
                item.get("user_id"),
                item.get("mission_id"),
                item.get("status"),
                item.get("reason", ""),
                item.get("error", ""),
            )

        return 1 if result["failed"] else 0

    result = send_unchecked_telegram_reminders(
        dry_run=args.dry_run,
        limit=args.limit,
    )

    logging.info(
        "telegram reminders date=%s dry_run=%s selected=%s sent=%s skipped=%s failed=%s",
        result["date"],
        result["dry_run"],
        result["selected"],
        result["sent"],
        result["skipped"],
        result["failed"],
    )

    for item in result["items"]:
        logging.info(
            "enrollment=%s user=%s challenge=%s status=%s reason=%s error=%s",
            item.get("enrollment_id"),
            item.get("user_id"),
            item.get("challenge_id"),
            item.get("status"),
            item.get("reason", ""),
            item.get("error", ""),
        )

    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

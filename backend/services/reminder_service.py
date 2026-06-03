from database import get_db_connection
from utils.date_utils import utc_today_iso
from services.telegram_service import send_telegram_message
from config import Config


def find_unchecked_active_enrollments(today_iso=None):
    today = today_iso or utc_today_iso()
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                e.id AS enrollment_id,
                e.user_id,
                tc.telegram_chat_id,
                tc.telegram_username,
                u.username,
                u.name,
                c.id AS challenge_id,
                c.name AS challenge_name
            FROM enrollments e
            JOIN users u ON u.id = e.user_id
            JOIN challenges c ON c.id = e.challenge_id
            JOIN telegram_connections tc
                ON tc.id = (
                    SELECT latest_tc.id
                    FROM telegram_connections latest_tc
                    WHERE latest_tc.user_id = e.user_id
                      AND latest_tc.status = 'connected'
                      AND latest_tc.telegram_chat_id IS NOT NULL
                      AND latest_tc.reminders_enabled = 1
                      AND latest_tc.daily_checkin_enabled = 1
                    ORDER BY
                        COALESCE(
                            latest_tc.connected_at,
                            latest_tc.updated_at,
                            latest_tc.created_at
                        ) DESC,
                        latest_tc.id DESC
                    LIMIT 1
                )
            LEFT JOIN checkins ci
                ON ci.enrollment_id = e.id
                AND ci.date = ?
                AND ci.status = 'Done'
                AND ci.is_counted = 1
            WHERE e.status = 'Active'
              AND c.status = 'Active'
              AND ci.id IS NULL
            ORDER BY u.name, u.username, c.name, e.id
            """,
            (today,),
        ).fetchall()
    finally:
        conn.close()

    return [dict(row) for row in rows]


def build_unchecked_summary(today_iso=None):
    today = today_iso or utc_today_iso()
    return today, find_unchecked_active_enrollments(today)


def build_reminder_text(item, today_iso=None):
    today = today_iso or utc_today_iso()
    name = item.get("name") or item.get("username") or "there"
    challenge = item.get("challenge_name") or "your challenge"

    return (
        f"🔥 RingoStrike reminder\n\n"
        f"Hi {name}, your daily strike for {challenge} is still waiting today ({today}).\n"
        "Check in before reset to protect your momentum."
    )


def _safe_item_for_log(item):
    return {
        "enrollment_id": item.get("enrollment_id"),
        "user_id": item.get("user_id"),
        "challenge_id": item.get("challenge_id"),
        "has_telegram_chat_id": bool(item.get("telegram_chat_id")),
    }


def send_unchecked_telegram_reminders(
    *,
    dry_run=False,
    limit=None,
    today_iso=None,
    sender=send_telegram_message,
):
    today = today_iso or utc_today_iso()
    items = find_unchecked_active_enrollments(today)

    if limit is not None:
        items = items[: max(0, int(limit))]

    result = {
        "ok": True,
        "date": today,
        "dry_run": bool(dry_run),
        "selected": len(items),
        "sent": 0,
        "skipped": 0,
        "failed": 0,
        "items": [],
    }

    for item in items:
        log_item = _safe_item_for_log(item)

        if not item.get("telegram_chat_id"):
            result["skipped"] += 1
            result["items"].append({
                **log_item,
                "status": "skipped",
                "reason": "telegram_chat_id_missing",
            })
            continue

        text = build_reminder_text(item, today)

        if dry_run:
            result["items"].append({
                **log_item,
                "status": "dry_run",
            })
            continue

        try:
            send_result = sender(item["telegram_chat_id"], text) or {}
        except Exception as exc:
            send_result = {
                "ok": False,
                "error": "telegram_sender_exception",
                "message": str(exc),
            }

        if send_result.get("ok") is True:
            result["sent"] += 1
            result["items"].append({
                **log_item,
                "status": "sent",
            })
        else:
            result["failed"] += 1
            result["items"].append({
                **log_item,
                "status": "failed",
                "error": send_result.get("error") or "telegram_send_failed",
            })

    return result


def send_unchecked_test_reminder():
    today, items = build_unchecked_summary()

    if not items:
        text = f"✅ RingoStrike reminder check\n\nAll active enrollments are checked in for {today}."
    else:
        lines = [
            f"🔥 RingoStrike reminder check",
            f"Date: {today}",
            "",
            f"Unchecked enrollments: {len(items)}",
            "",
        ]

        for item in items[:20]:
            name = item.get("name") or item.get("username") or "User"
            challenge = item.get("challenge_name") or "Challenge"
            lines.append(f"• {name} — {challenge}")

        if len(items) > 20:
            lines.append(f"\n…and {len(items) - 20} more")

        text = "\n".join(lines)

    return send_telegram_message(
        Config.TELEGRAM_TEST_CHAT_ID,
        text,
    )

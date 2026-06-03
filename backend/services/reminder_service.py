from database import get_db_connection
from utils.date_utils import utc_today_iso
from services.telegram_service import send_telegram_message
from config import Config


def build_unchecked_summary():
    today = utc_today_iso()

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT
            e.id AS enrollment_id,
            u.username,
            u.name,
            c.name AS challenge_name
        FROM enrollments e
        JOIN users u ON u.id = e.user_id
        JOIN challenges c ON c.id = e.challenge_id
        LEFT JOIN checkins ci
            ON ci.enrollment_id = e.id
            AND ci.date = ?
            AND ci.status = 'Done'
            AND ci.is_counted = 1
        WHERE e.status = 'Active'
          AND c.status = 'Active'
          AND ci.id IS NULL
        ORDER BY u.name, c.name
        """,
        (today,),
    ).fetchall()
    conn.close()

    return today, [dict(row) for row in rows]


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
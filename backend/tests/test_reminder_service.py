from helpers import insert_challenge
from utils.date_utils import utc_today_iso


def _create_user(username, telegram_id=None):
    import database

    return database.create_user(
        username=username,
        password="secret123",
        name=username,
        email=f"{username.lower()}@example.com",
        telegram_id=telegram_id,
    )


def _connect_telegram(user_id, chat_id, reminders_enabled=1, daily_checkin_enabled=1):
    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO telegram_connections (
                user_id,
                code,
                status,
                telegram_chat_id,
                reminders_enabled,
                daily_checkin_enabled,
                streak_risk_enabled,
                weekly_summary_enabled,
                connected_at,
                updated_at
            )
            VALUES (?, ?, 'connected', ?, ?, ?, 1, 0, datetime('now'), datetime('now'))
            """,
            (
                user_id,
                f"TEST-{user_id}-{chat_id}",
                str(chat_id),
                reminders_enabled,
                daily_checkin_enabled,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _create_enrollment(user_id, challenge_id, status="Active"):
    import database

    conn = database.get_db_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO enrollments (user_id, challenge_id, status, role)
            VALUES (?, ?, ?, 'Member')
            """,
            (user_id, challenge_id, status),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_checkin(
    *,
    enrollment_id,
    user_id,
    challenge_id,
    date,
    status="Done",
    is_counted=1,
):
    import database

    conn = database.get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO checkins (
                enrollment_id,
                user_id,
                challenge_id,
                date,
                status,
                is_counted
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                enrollment_id,
                user_id,
                challenge_id,
                date,
                status,
                is_counted,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def test_unchecked_active_enrollment_is_selected(client):
    from services.reminder_service import find_unchecked_active_enrollments

    user_id = _create_user("ReminderUncheckedUser")
    _connect_telegram(user_id, "10001")
    challenge_id = insert_challenge(
        name="Reminder Active Challenge",
        description="Reminder selection test",
    )
    enrollment_id = _create_enrollment(user_id, challenge_id)

    items = find_unchecked_active_enrollments(utc_today_iso())

    assert [item["enrollment_id"] for item in items] == [enrollment_id]
    assert items[0]["user_id"] == user_id
    assert items[0]["telegram_chat_id"] == "10001"
    assert items[0]["challenge_id"] == challenge_id


def test_checked_in_enrollment_is_skipped(client):
    from services.reminder_service import find_unchecked_active_enrollments

    today = utc_today_iso()
    user_id = _create_user("ReminderCheckedUser")
    _connect_telegram(user_id, "10002")
    challenge_id = insert_challenge(
        name="Reminder Checked Challenge",
        description="Reminder checked skip test",
    )
    enrollment_id = _create_enrollment(user_id, challenge_id)

    _insert_checkin(
        enrollment_id=enrollment_id,
        user_id=user_id,
        challenge_id=challenge_id,
        date=today,
        status="Done",
        is_counted=1,
    )

    items = find_unchecked_active_enrollments(today)

    assert enrollment_id not in {item["enrollment_id"] for item in items}


def test_inactive_or_left_enrollment_is_skipped(client):
    from services.reminder_service import find_unchecked_active_enrollments

    left_user_id = _create_user("ReminderLeftUser")
    archived_user_id = _create_user("ReminderArchivedUser")
    _connect_telegram(left_user_id, "10003")
    _connect_telegram(archived_user_id, "10004")
    active_challenge_id = insert_challenge(
        name="Reminder Left Challenge",
        description="Reminder left skip test",
    )
    archived_challenge_id = insert_challenge(
        name="Reminder Archived Challenge",
        description="Reminder archived skip test",
        status="Archived",
    )
    left_enrollment_id = _create_enrollment(
        left_user_id,
        active_challenge_id,
        status="Left",
    )
    archived_enrollment_id = _create_enrollment(
        archived_user_id,
        archived_challenge_id,
    )

    items = find_unchecked_active_enrollments(utc_today_iso())
    enrollment_ids = {item["enrollment_id"] for item in items}

    assert left_enrollment_id not in enrollment_ids
    assert archived_enrollment_id not in enrollment_ids


def test_missing_telegram_identity_is_not_selected(client):
    from services.reminder_service import send_unchecked_telegram_reminders

    user_id = _create_user("ReminderMissingTelegramUser")
    challenge_id = insert_challenge(
        name="Reminder Missing Telegram Challenge",
        description="Reminder missing Telegram test",
    )
    enrollment_id = _create_enrollment(user_id, challenge_id)

    def fail_sender(chat_id, text):
        raise AssertionError("sender should not be called without telegram_chat_id")

    result = send_unchecked_telegram_reminders(sender=fail_sender)

    assert result["ok"] is True
    assert result["selected"] == 0
    assert result["sent"] == 0
    assert result["skipped"] == 0
    assert result["failed"] == 0
    assert result["items"] == []


def test_reminders_disabled_user_is_not_selected(client):
    from services.reminder_service import find_unchecked_active_enrollments

    user_id = _create_user("ReminderDisabledUser")
    _connect_telegram(user_id, "10007", reminders_enabled=0)
    challenge_id = insert_challenge(
        name="Reminder Disabled Challenge",
        description="Reminder disabled test",
    )
    enrollment_id = _create_enrollment(user_id, challenge_id)

    items = find_unchecked_active_enrollments(utc_today_iso())

    assert enrollment_id not in {item["enrollment_id"] for item in items}


def test_dry_run_does_not_send_telegram_messages(client):
    from services.reminder_service import send_unchecked_telegram_reminders

    user_id = _create_user("ReminderDryRunUser")
    _connect_telegram(user_id, "10005")
    challenge_id = insert_challenge(
        name="Reminder Dry Run Challenge",
        description="Reminder dry-run test",
    )
    enrollment_id = _create_enrollment(user_id, challenge_id)

    def fail_sender(chat_id, text):
        raise AssertionError("sender should not be called during dry-run")

    result = send_unchecked_telegram_reminders(
        dry_run=True,
        sender=fail_sender,
    )

    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["selected"] == 1
    assert result["sent"] == 0
    assert result["skipped"] == 0
    assert result["failed"] == 0
    assert result["items"] == [
        {
            "enrollment_id": enrollment_id,
            "user_id": user_id,
            "challenge_id": challenge_id,
            "has_telegram_chat_id": True,
            "status": "dry_run",
        }
    ]


def test_send_unchecked_telegram_reminders_calls_sender(client):
    from services.reminder_service import send_unchecked_telegram_reminders

    user_id = _create_user("ReminderSendUser")
    _connect_telegram(user_id, "10006")
    challenge_id = insert_challenge(
        name="Reminder Send Challenge",
        description="Reminder send test",
    )
    enrollment_id = _create_enrollment(user_id, challenge_id)
    sent_messages = []

    def fake_sender(chat_id, text):
        sent_messages.append((chat_id, text))
        return {"ok": True}

    result = send_unchecked_telegram_reminders(sender=fake_sender)

    assert result["ok"] is True
    assert result["selected"] == 1
    assert result["sent"] == 1
    assert result["skipped"] == 0
    assert result["failed"] == 0
    assert result["items"] == [
        {
            "enrollment_id": enrollment_id,
            "user_id": user_id,
            "challenge_id": challenge_id,
            "has_telegram_chat_id": True,
            "status": "sent",
        }
    ]
    assert sent_messages[0][0] == "10006"
    assert "Reminder Send Challenge" in sent_messages[0][1]

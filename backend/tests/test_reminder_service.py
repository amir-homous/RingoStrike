from datetime import datetime, timedelta, timezone

from helpers import insert_challenge
from utils.date_utils import utc_iso_z, utc_today_iso


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


def _create_mission(
    challenge_id,
    *,
    key,
    title="Mission reminder test",
    status="Active",
    estimated_minutes=5,
    difficulty="easy",
    mission_intensity="main",
):
    import database

    conn = database.get_db_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO missions (
                challenge_id,
                key,
                title,
                description,
                mission_type,
                difficulty,
                is_core,
                xp_reward,
                order_index,
                suggested_time,
                unlock_after_days,
                mission_intensity,
                estimated_minutes,
                status
            )
            VALUES (?, ?, ?, 'Mission reminder description', 'daily', ?, 1, 10, 1, 'afternoon', 0, ?, ?, ?)
            """,
            (
                challenge_id,
                key,
                title,
                difficulty,
                mission_intensity,
                estimated_minutes,
                status,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _insert_mission_log(
    *,
    user_id,
    enrollment_id,
    challenge_id,
    mission_id,
    status="remind_later",
    reminder_at=None,
    reminder_sent_at=None,
):
    import database

    conn = database.get_db_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO mission_logs (
                user_id,
                enrollment_id,
                challenge_id,
                mission_id,
                date,
                status,
                reminder_at,
                reminder_sent_at,
                xp_earned,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                user_id,
                enrollment_id,
                challenge_id,
                mission_id,
                utc_today_iso(),
                status,
                reminder_at,
                reminder_sent_at,
                utc_iso_z(datetime.now(timezone.utc)),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _mission_reminder_fixture(
    username,
    *,
    chat_id="20001",
    reminders_enabled=1,
    enrollment_status="Active",
    challenge_status="Active",
    mission_status="Active",
    log_status="remind_later",
    reminder_at=None,
    reminder_sent_at=None,
):
    user_id = _create_user(username)
    if chat_id is not None:
        _connect_telegram(user_id, chat_id, reminders_enabled=reminders_enabled)
    challenge_id = insert_challenge(
        name=f"{username} Challenge",
        description="Mission reminder selection test",
        status=challenge_status,
    )
    enrollment_id = _create_enrollment(user_id, challenge_id, status=enrollment_status)
    mission_id = _create_mission(
        challenge_id,
        key=f"{username.lower()}-mission",
        title=f"{username} mission",
        status=mission_status,
    )
    mission_log_id = _insert_mission_log(
        user_id=user_id,
        enrollment_id=enrollment_id,
        challenge_id=challenge_id,
        mission_id=mission_id,
        status=log_status,
        reminder_at=reminder_at or utc_iso_z(datetime.now(timezone.utc) - timedelta(minutes=1)),
        reminder_sent_at=reminder_sent_at,
    )

    return {
        "user_id": user_id,
        "challenge_id": challenge_id,
        "enrollment_id": enrollment_id,
        "mission_id": mission_id,
        "mission_log_id": mission_log_id,
        "chat_id": chat_id,
    }


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


def test_due_mission_reminder_is_selected_and_sent(client):
    from services.reminder_service import (
        find_due_mission_reminders,
        send_due_mission_telegram_reminders,
    )

    fixture = _mission_reminder_fixture("MissionDueUser", chat_id="20002")
    sent_messages = []

    def fake_sender(chat_id, text):
        sent_messages.append((chat_id, text))
        return {"ok": True}

    due_items = find_due_mission_reminders()
    assert fixture["mission_log_id"] in {item["mission_log_id"] for item in due_items}

    result = send_due_mission_telegram_reminders(sender=fake_sender)

    assert result["ok"] is True
    assert result["due"] == 1
    assert result["sent"] == 1
    assert result["failed"] == 0
    assert result["items"][0]["status"] == "sent"
    assert sent_messages[0][0] == "20002"
    assert "MissionDueUser mission" in sent_messages[0][1]
    assert "~5 min" in sent_messages[0][1]


def test_future_mission_reminder_is_not_selected(client):
    from services.reminder_service import find_due_mission_reminders

    fixture = _mission_reminder_fixture(
        "MissionFutureUser",
        reminder_at=utc_iso_z(datetime.now(timezone.utc) + timedelta(hours=1)),
    )

    due_items = find_due_mission_reminders()

    assert fixture["mission_log_id"] not in {item["mission_log_id"] for item in due_items}


def test_done_and_skipped_mission_reminders_are_not_sent(client):
    from services.reminder_service import send_due_mission_telegram_reminders

    done = _mission_reminder_fixture("MissionDoneUser", log_status="done", chat_id="20003")
    skipped = _mission_reminder_fixture("MissionSkippedUser", log_status="skipped", chat_id="20004")

    def fail_sender(chat_id, text):
        raise AssertionError("done/skipped mission reminders should not send")

    result = send_due_mission_telegram_reminders(sender=fail_sender)
    sent_ids = {item["mission_log_id"] for item in result["items"]}

    assert result["due"] == 0
    assert done["mission_log_id"] not in sent_ids
    assert skipped["mission_log_id"] not in sent_ids


def test_due_mission_reminder_is_not_sent_twice(client):
    from services.reminder_service import send_due_mission_telegram_reminders

    fixture = _mission_reminder_fixture("MissionOnceUser", chat_id="20005")
    sends = []

    def fake_sender(chat_id, text):
        sends.append(chat_id)
        return {"ok": True}

    first = send_due_mission_telegram_reminders(sender=fake_sender)
    second = send_due_mission_telegram_reminders(sender=fake_sender)

    assert first["sent"] == 1
    assert second["due"] == 0
    assert sends == ["20005"]

    import database

    conn = database.get_db_connection()
    try:
        row = conn.execute(
            "SELECT reminder_sent_at FROM mission_logs WHERE id = ?",
            (fixture["mission_log_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert row["reminder_sent_at"]


def test_due_mission_reminder_marks_sent_only_after_success(client):
    from services.reminder_service import send_due_mission_telegram_reminders

    fixture = _mission_reminder_fixture("MissionFailedUser", chat_id="20006")

    def failing_sender(chat_id, text):
        return {"ok": False, "error": "telegram_test_failure"}

    result = send_due_mission_telegram_reminders(sender=failing_sender)

    assert result["sent"] == 0
    assert result["failed"] == 1

    import database

    conn = database.get_db_connection()
    try:
        row = conn.execute(
            "SELECT reminder_sent_at FROM mission_logs WHERE id = ?",
            (fixture["mission_log_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert row["reminder_sent_at"] is None


def test_due_mission_reminder_dry_run_does_not_mark_sent(client):
    from services.reminder_service import send_due_mission_telegram_reminders

    fixture = _mission_reminder_fixture("MissionDryRunUser", chat_id="20007")

    def fail_sender(chat_id, text):
        raise AssertionError("dry-run should not send mission reminders")

    result = send_due_mission_telegram_reminders(dry_run=True, sender=fail_sender)

    assert result["dry_run"] is True
    assert result["due"] == 1
    assert result["sent"] == 0
    assert result["items"][0]["status"] == "dry_run"

    import database

    conn = database.get_db_connection()
    try:
        row = conn.execute(
            "SELECT reminder_sent_at FROM mission_logs WHERE id = ?",
            (fixture["mission_log_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert row["reminder_sent_at"] is None


def test_due_mission_reminder_marker_resets_when_reminder_changes(client):
    from services.mission_service import remind_mission_later
    from utils.date_utils import ringo_day_metadata

    next_reset = datetime.fromisoformat(
        ringo_day_metadata()["next_reset_at"].replace("Z", "+00:00"),
    )
    future = utc_iso_z(
        min(
            datetime.now(timezone.utc) + timedelta(minutes=30),
            next_reset - timedelta(minutes=1),
        ),
    )
    fixture = _mission_reminder_fixture(
        "MissionResetUser",
        chat_id="20008",
        reminder_sent_at=utc_iso_z(datetime.now(timezone.utc) - timedelta(minutes=1)),
    )

    payload, code = remind_mission_later(
        fixture["user_id"],
        fixture["mission_id"],
        future,
    )

    assert code == 200
    assert payload["ok"] is True

    import database

    conn = database.get_db_connection()
    try:
        row = conn.execute(
            "SELECT reminder_at, reminder_sent_at FROM mission_logs WHERE id = ?",
            (fixture["mission_log_id"],),
        ).fetchone()
    finally:
        conn.close()

    assert row["reminder_at"] == future
    assert row["reminder_sent_at"] is None


def test_due_mission_reminder_user_without_telegram_is_skipped(client):
    from services.reminder_service import send_due_mission_telegram_reminders

    fixture = _mission_reminder_fixture("MissionNoTelegramUser", chat_id=None)

    def fail_sender(chat_id, text):
        raise AssertionError("sender should not be called without Telegram")

    result = send_due_mission_telegram_reminders(sender=fail_sender)

    assert result["due"] == 1
    assert result["sent"] == 0
    assert result["skipped"] == 1
    assert result["items"] == [
        {
            "mission_log_id": fixture["mission_log_id"],
            "user_id": fixture["user_id"],
            "mission_id": fixture["mission_id"],
            "title": "MissionNoTelegramUser mission",
            "has_telegram_chat_id": False,
            "status": "skipped",
            "reason": "telegram_chat_id_missing",
        }
    ]


def test_due_mission_reminder_disabled_user_is_skipped(client):
    from services.reminder_service import send_due_mission_telegram_reminders

    fixture = _mission_reminder_fixture(
        "MissionDisabledUser",
        chat_id="20009",
        reminders_enabled=0,
    )

    def fail_sender(chat_id, text):
        raise AssertionError("sender should not be called when reminders are disabled")

    result = send_due_mission_telegram_reminders(sender=fail_sender)

    assert result["due"] == 1
    assert result["sent"] == 0
    assert result["skipped"] == 1
    assert result["items"][0]["mission_log_id"] == fixture["mission_log_id"]
    assert result["items"][0]["reason"] == "reminders_disabled"


def test_reminder_diagnostics_requires_admin_token(client):
    res = client.get("/api/telegram/reminder-diagnostics")

    assert res.status_code == 401
    assert res.get_json()["error"] == "unauthorized"


def test_reminder_diagnostics_returns_safe_operational_state(client, monkeypatch):
    from routes import telegram_routes

    monkeypatch.setattr(telegram_routes.Config, "REMINDER_ADMIN_TOKEN", "test-reminder-token")
    due = _mission_reminder_fixture("DiagDueUser", chat_id="30001")
    future = _mission_reminder_fixture(
        "DiagFutureUser",
        chat_id="30002",
        reminder_at=utc_iso_z(datetime.now(timezone.utc) + timedelta(hours=1)),
    )
    sent = _mission_reminder_fixture(
        "DiagSentUser",
        chat_id="30003",
        reminder_sent_at=utc_iso_z(datetime.now(timezone.utc) - timedelta(minutes=2)),
    )
    missing = _mission_reminder_fixture("DiagNoTelegramUser", chat_id=None)

    res = client.get(
        "/api/telegram/reminder-diagnostics",
        headers={"X-Reminder-Token": "test-reminder-token"},
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["server_now"]
    assert data["summary"]["due_count"] == 1
    assert data["summary"]["scheduled_future_count"] == 1
    assert data["summary"]["already_sent_count"] == 1
    assert data["summary"]["missing_telegram_count"] == 1

    assert [item["mission_log_id"] for item in data["due_reminders"]] == [due["mission_log_id"]]
    assert [item["mission_log_id"] for item in data["scheduled_future_reminders"]] == [future["mission_log_id"]]
    assert [item["mission_log_id"] for item in data["already_sent_reminders"]] == [sent["mission_log_id"]]
    assert [item["mission_log_id"] for item in data["missing_telegram_reminders"]] == [missing["mission_log_id"]]

    sent_item = data["already_sent_reminders"][0]
    assert sent_item["delivery_state"] == "sent"
    assert sent_item["reminder_sent_at"]
    assert sent_item not in data["due_reminders"]

    missing_item = data["missing_telegram_reminders"][0]
    assert missing_item["has_telegram_chat_id"] is False
    assert missing_item["delivery_state"] == "missing_telegram"

    serialized = repr(data)
    assert "test-reminder-token" not in serialized
    assert "30001" not in serialized
    assert "'telegram_chat_id':" not in serialized


def test_reminder_diagnostics_recent_limit(client, monkeypatch):
    from routes import telegram_routes

    monkeypatch.setattr(telegram_routes.Config, "REMINDER_ADMIN_TOKEN", "test-reminder-token")
    _mission_reminder_fixture("DiagLimitOne", chat_id="30004")
    _mission_reminder_fixture("DiagLimitTwo", chat_id="30005")

    res = client.get(
        "/api/telegram/reminder-diagnostics?recent_limit=1",
        headers={"X-Reminder-Token": "test-reminder-token"},
    )

    assert res.status_code == 200
    data = res.get_json()
    assert len(data["recent_reminder_logs"]) == 1

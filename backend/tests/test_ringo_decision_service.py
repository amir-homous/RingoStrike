from datetime import datetime, timedelta, timezone

from services.ringo_decision_service import decide_ringo_state


def _mission(status="pending", title="Capture one idea", mission_id=10, **overrides):
    mission = {
        "mission_id": mission_id,
        "title": title,
        "status": status,
        "enrollment_id": 20,
    }
    mission.update(overrides)
    return mission


def test_completed_state_dismisses_instead_of_looping_to_paths():
    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[_mission("done")],
        checkins_total=1,
        current_streak=1,
    )

    assert state["state"] == "today_completed"
    assert state["primary_action"]["type"] == "dismiss"
    assert state["secondary_action"]["to"] == "/paths"


def test_in_progress_action_names_the_next_mission():
    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission("done", "Capture one idea", 10),
            _mission("pending", "Make one small thing", 11),
        ],
        checkins_total=1,
        current_streak=1,
    )

    assert state["state"] == "today_in_progress"
    assert "Make one small thing" in state["message"]
    assert state["primary_action"]["label"] == "Finish: Make one small thing"
    assert state["primary_action"]["mission_id"] == 11


def test_reminded_state_offers_another_path_instead_of_repeat_reminder():
    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[_mission("remind_later", "Make one small thing", 11)],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_reminded"
    assert state["primary_action"]["label"] == "Do it now: Make one small thing"
    assert state["secondary_action"]["to"] == "/paths"


def test_future_reminder_does_not_block_next_pending_mission():
    reminder_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "remind_later",
                "First mission",
                10,
                reminder_at=reminder_at,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "pending",
                "Second mission",
                11,
                order_index=2,
                mission_intensity="main",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_not_started"
    assert "I saved that reminder" in state["message"]
    assert "Second mission" in state["message"]
    assert state["primary_action"]["mission_id"] == 11


def test_due_reminder_can_beat_pending_mission():
    reminder_at = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()

    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "remind_later",
                "Due mission",
                10,
                reminder_at=reminder_at,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "pending",
                "Second mission",
                11,
                order_index=2,
                mission_intensity="main",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_not_started"
    assert "Due mission" in state["message"]
    assert state["primary_action"]["mission_id"] == 10


def test_future_tiny_reminder_covers_parent_main_for_next_action():
    reminder_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "pending",
                "Move for 10 minutes",
                10,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "remind_later",
                "Move for 2 minutes",
                11,
                reminder_at=reminder_at,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
            _mission(
                "pending",
                "Send one signal",
                12,
                order_index=3,
                mission_intensity="main",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_not_started"
    assert "I saved that reminder" in state["message"]
    assert "Send one signal" in state["message"]
    assert "Move for 10 minutes" not in state["message"]
    assert state["primary_action"]["mission_id"] == 12


def test_future_main_reminder_covers_linked_tiny_for_next_action():
    reminder_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "remind_later",
                "Move for 10 minutes",
                10,
                reminder_at=reminder_at,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "pending",
                "Move for 2 minutes",
                11,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
            _mission(
                "pending",
                "Send one signal",
                12,
                order_index=3,
                mission_intensity="main",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_not_started"
    assert "I saved that reminder" in state["message"]
    assert "Send one signal" in state["message"]
    assert "Move for 2 minutes" not in state["message"]
    assert state["primary_action"]["mission_id"] == 12


def test_tiny_completion_does_not_suggest_bonus_next():
    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "pending",
                "Move for 10 minutes",
                10,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "done",
                "Move for 2 minutes",
                11,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
            _mission(
                "pending",
                "Add one extra movement minute",
                12,
                parent_mission_id=10,
                order_index=3,
                mission_intensity="bonus",
            ),
        ],
        checkins_total=1,
        current_streak=1,
    )

    assert state["state"] == "today_completed"
    assert state["primary_action"]["type"] == "dismiss"


def test_main_completion_can_suggest_bonus_next():
    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "done",
                "Move for 10 minutes",
                10,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "pending",
                "Move for 2 minutes",
                11,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
            _mission(
                "pending",
                "Add one extra movement minute",
                12,
                parent_mission_id=10,
                order_index=3,
                mission_intensity="bonus",
            ),
        ],
        checkins_total=1,
        current_streak=1,
    )

    assert state["state"] == "today_in_progress"
    assert "Add one extra movement minute" in state["message"]
    assert state["primary_action"]["mission_id"] == 12


def test_due_tiny_reminder_still_wins_over_parent_and_pending_mission():
    reminder_at = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()

    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "pending",
                "Move for 10 minutes",
                10,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "remind_later",
                "Move for 2 minutes",
                11,
                reminder_at=reminder_at,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
            _mission(
                "pending",
                "Send one signal",
                12,
                order_index=3,
                mission_intensity="main",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_not_started"
    assert "Move for 2 minutes" in state["message"]
    assert state["primary_action"]["mission_id"] == 11


def test_future_tiny_reminder_without_other_pending_focuses_reminder():
    reminder_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "pending",
                "Move for 10 minutes",
                10,
                order_index=1,
                mission_intensity="main",
            ),
            _mission(
                "remind_later",
                "Move for 2 minutes",
                11,
                reminder_at=reminder_at,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_reminded"
    assert "Move for 2 minutes" in state["message"]
    assert state["primary_action"]["mission_id"] == 11

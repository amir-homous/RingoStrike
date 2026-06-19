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


def _future_today_reminder_at():
    next_reset = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) + timedelta(days=1)
    return min(
        datetime.now(timezone.utc) + timedelta(hours=1),
        next_reset - timedelta(seconds=1),
    ).isoformat()


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


def test_done_required_step_names_next_mission_as_optional_continuation():
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

    assert state["state"] == "today_completed"
    assert "Make one small thing" in state["message"]
    assert state["primary_action"]["type"] == "dismiss"
    assert state["secondary_action"]["label"] == "Optional: Make one small thing"
    assert state["secondary_action"]["mission_id"] == 11


def test_reminded_state_offers_another_path_instead_of_repeat_reminder():
    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "remind_later",
                "Make one small thing",
                11,
                reminder_at=_future_today_reminder_at(),
                mission_intensity="main",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_reminded"
    assert state["primary_action"]["label"] == "Do it now: Make one small thing"
    assert state["secondary_action"]["to"] == "/paths"


def test_future_reminder_does_not_block_next_pending_mission():
    reminder_at = _future_today_reminder_at()

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


def test_current_day_main_mission_outranks_unrelated_due_reminder():
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
    assert "Second mission" in state["message"]
    assert state["primary_action"]["mission_id"] == 11


def test_stale_due_reminder_does_not_dominate_current_day_main():
    reminder_at = (datetime.now(timezone.utc) - timedelta(days=1, minutes=5)).isoformat()

    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "remind_later",
                "Stale mission",
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
    assert "Stale mission" in state["message"]
    assert "I saved that reminder" not in state["message"]
    assert state["primary_action"]["mission_id"] == 10


def test_returning_user_defaults_to_main_when_tiny_is_available():
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
                "pending",
                "Move for 2 minutes",
                11,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
        ],
        checkins_total=2,
        current_streak=0,
    )

    assert state["state"] == "returning_after_break"
    assert "Move for 10 minutes" in state["message"]
    assert state["primary_action"]["mission_id"] == 10


def test_streak_risk_user_defaults_to_main_when_tiny_is_available():
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
                "pending",
                "Move for 2 minutes",
                11,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
        ],
        checkins_total=2,
        current_streak=1,
    )

    assert state["state"] == "streak_at_risk"
    assert "Move for 10 minutes" in state["message"]
    assert state["primary_action"]["mission_id"] == 10


def test_tiny_remains_fallback_when_no_main_is_available():
    state = decide_ringo_state(
        has_active_path=True,
        has_active_enrollment=True,
        missions=[
            _mission(
                "pending",
                "Move for 2 minutes",
                11,
                parent_mission_id=10,
                order_index=2,
                mission_intensity="tiny",
            ),
        ],
        checkins_total=2,
        current_streak=0,
    )

    assert state["state"] == "returning_after_break"
    assert "Move for 2 minutes" in state["message"]
    assert state["primary_action"]["mission_id"] == 11


def test_future_tiny_reminder_covers_parent_main_for_next_action():
    reminder_at = _future_today_reminder_at()

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
    reminder_at = _future_today_reminder_at()

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

    assert state["state"] == "today_completed"
    assert "Today is secured" in state["message"]
    assert "optional" in state["secondary_action"]["label"].lower()
    assert "Add one extra movement minute" in state["message"]
    assert state["primary_action"]["type"] == "dismiss"
    assert state["secondary_action"]["mission_id"] == 12


def test_main_completion_can_suggest_unrelated_pending_as_optional_continuation():
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
                "Read for 5 minutes",
                20,
                order_index=2,
                mission_intensity="main",
            ),
        ],
        checkins_total=1,
        current_streak=1,
    )

    assert state["state"] == "today_completed"
    assert "Read for 5 minutes" in state["message"]
    assert state["primary_action"]["type"] == "dismiss"
    assert state["secondary_action"]["mission_id"] == 20


def test_due_tiny_reminder_defers_parent_but_not_unrelated_main():
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
    assert "Send one signal" in state["message"]
    assert "Move for 10 minutes" not in state["message"]
    assert state["primary_action"]["mission_id"] == 12


def test_bonus_reminder_does_not_become_primary_before_today_is_saved():
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
                "Add one extra movement minute",
                12,
                reminder_at=reminder_at,
                parent_mission_id=10,
                order_index=3,
                mission_intensity="bonus",
            ),
        ],
        checkins_total=0,
        current_streak=0,
    )

    assert state["state"] == "today_not_started"
    assert "Move for 10 minutes" in state["message"]
    assert state["primary_action"]["mission_id"] == 10


def test_future_tiny_reminder_without_other_pending_focuses_reminder():
    reminder_at = _future_today_reminder_at()

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


def test_bonus_completion_does_not_chain_into_another_bonus():
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
                "done",
                "Add one extra movement minute",
                12,
                parent_mission_id=10,
                order_index=3,
                mission_intensity="bonus",
            ),
            _mission(
                "pending",
                "Save one extra idea",
                22,
                parent_mission_id=20,
                order_index=3,
                mission_intensity="bonus",
            ),
        ],
        checkins_total=2,
        current_streak=2,
    )

    assert state["state"] == "today_completed"
    assert state["primary_action"]["type"] == "dismiss"

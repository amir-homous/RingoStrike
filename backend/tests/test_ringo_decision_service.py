from services.ringo_decision_service import decide_ringo_state


def _mission(status="pending", title="Capture one idea", mission_id=10):
    return {
        "mission_id": mission_id,
        "title": title,
        "status": status,
        "enrollment_id": 20,
    }


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

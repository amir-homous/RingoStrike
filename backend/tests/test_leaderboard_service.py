from datetime import datetime, timedelta

from database import get_db_connection
from services.leaderboard_service import enrollment_leaderboard
from utils.date_utils import utc_today_iso


def create_user(conn, username, name):
    cursor = conn.execute(
        """
        INSERT INTO users (
            username,
            name,
            email,
            password_hash
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            name,
            f"{username}@example.com",
            "test-password-hash",
        ),
    )

    return cursor.lastrowid


def create_challenge(conn):
    cursor = conn.execute(
        """
        INSERT INTO challenges (
            name,
            description,
            visibility,
            status,
            duration_days
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Service Tie Challenge",
            "Used to verify leaderboard service tie ordering.",
            "Public",
            "Active",
            7,
        ),
    )

    return cursor.lastrowid


def create_enrollment(conn, user_id, challenge_id):
    cursor = conn.execute(
        """
        INSERT INTO enrollments (
            user_id,
            challenge_id,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            challenge_id,
            "Active",
        ),
    )

    return cursor.lastrowid


def add_checkin(conn, enrollment_id, user_id, challenge_id, date):
    conn.execute(
        """
        INSERT INTO checkins (
            enrollment_id,
            user_id,
            challenge_id,
            date,
            is_counted
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            enrollment_id,
            user_id,
            challenge_id,
            date,
            1,
        ),
    )


def add_checkins(conn, enrollment_id, user_id, challenge_id, dates):
    for date in dates:
        add_checkin(conn, enrollment_id, user_id, challenge_id, date)


def days_ago(days):
    today = datetime.strptime(utc_today_iso(), "%Y-%m-%d").date()
    return (today - timedelta(days=days)).isoformat()


def test_leaderboard_service_orders_overall_and_today_by_documented_tie_breakers(client):
    conn = get_db_connection()

    try:
        challenge_id = create_challenge(conn)

        volume_user_id = create_user(
            conn,
            "tievolumeuser",
            "Tie Volume User",
        )
        streak_user_id = create_user(
            conn,
            "tiestreakuser",
            "Tie Streak User",
        )
        alpha_user_id = create_user(
            conn,
            "tiealphaorder",
            "Tie Alpha Order",
        )
        beta_user_id = create_user(
            conn,
            "tiebetaorder",
            "Tie Beta Order",
        )

        volume_enrollment_id = create_enrollment(
            conn,
            volume_user_id,
            challenge_id,
        )
        streak_enrollment_id = create_enrollment(
            conn,
            streak_user_id,
            challenge_id,
        )
        beta_enrollment_id = create_enrollment(
            conn,
            beta_user_id,
            challenge_id,
        )
        alpha_enrollment_id = create_enrollment(
            conn,
            alpha_user_id,
            challenge_id,
        )

        add_checkins(
            conn,
            volume_enrollment_id,
            volume_user_id,
            challenge_id,
            [days_ago(0), days_ago(7), days_ago(8)],
        )
        add_checkins(
            conn,
            streak_enrollment_id,
            streak_user_id,
            challenge_id,
            [days_ago(0), days_ago(1)],
        )

        for enrollment_id, user_id in (
            (beta_enrollment_id, beta_user_id),
            (alpha_enrollment_id, alpha_user_id),
        ):
            add_checkins(
                conn,
                enrollment_id,
                user_id,
                challenge_id,
                [days_ago(12)],
            )

        conn.commit()

    finally:
        conn.close()

    payload, code = enrollment_leaderboard(volume_enrollment_id)

    assert code == 200
    assert payload["ok"] is True
    assert payload["tie_breakers"] == {
        "overall": [
            "total_checkins_desc",
            "current_streak_desc",
            "name_asc",
            "enrollment_id_asc",
        ],
        "today": [
            "current_streak_desc",
            "total_checkins_desc",
            "name_asc",
            "enrollment_id_asc",
        ],
    }

    assert [row["username"] for row in payload["overall"]] == [
        "tievolumeuser",
        "tiestreakuser",
        "tiealphaorder",
        "tiebetaorder",
    ]
    assert [row["rank"] for row in payload["overall"]] == [1, 2, 3, 4]

    assert [row["username"] for row in payload["today"]] == [
        "tiestreakuser",
        "tievolumeuser",
    ]
    assert [row["rank"] for row in payload["today"]] == [1, 2]


def test_leaderboard_service_exact_tie_orders_by_name(client):
    conn = get_db_connection()

    try:
        challenge_id = create_challenge(conn)

        beta_user_id = create_user(
            conn,
            "tiebetauser",
            "Tie Beta User",
        )
        alpha_user_id = create_user(
            conn,
            "tiealphauser",
            "Tie Alpha User",
        )

        beta_enrollment_id = create_enrollment(
            conn,
            beta_user_id,
            challenge_id,
        )
        alpha_enrollment_id = create_enrollment(
            conn,
            alpha_user_id,
            challenge_id,
        )

        for enrollment_id, user_id in (
            (beta_enrollment_id, beta_user_id),
            (alpha_enrollment_id, alpha_user_id),
        ):
            add_checkin(
                conn,
                enrollment_id,
                user_id,
                challenge_id,
                "2026-06-01",
            )

        conn.commit()

    finally:
        conn.close()

    payload, code = enrollment_leaderboard(beta_enrollment_id)

    assert code == 200
    assert payload["ok"] is True

    overall = payload["overall"]

    tied_users = [
        row
        for row in overall
        if row["username"] in {
            "tiealphauser",
            "tiebetauser",
        }
    ]

    assert len(tied_users) == 2

    assert tied_users[0]["username"] == "tiealphauser"
    assert tied_users[0]["rank"] == 1

    assert tied_users[1]["username"] == "tiebetauser"
    assert tied_users[1]["rank"] == 2


def test_leaderboard_service_exact_tie_falls_back_to_enrollment_id(client):
    conn = get_db_connection()

    try:
        challenge_id = create_challenge(conn)

        user_one_id = create_user(
            conn,
            "sameone",
            "Same Name",
        )
        user_two_id = create_user(
            conn,
            "sametwo",
            "Same Name",
        )

        enrollment_one_id = create_enrollment(
            conn,
            user_one_id,
            challenge_id,
        )
        enrollment_two_id = create_enrollment(
            conn,
            user_two_id,
            challenge_id,
        )

        for enrollment_id, user_id in (
            (enrollment_one_id, user_one_id),
            (enrollment_two_id, user_two_id),
        ):
            add_checkin(
                conn,
                enrollment_id,
                user_id,
                challenge_id,
                "2026-06-01",
            )

        conn.commit()

    finally:
        conn.close()

    payload, code = enrollment_leaderboard(enrollment_two_id)

    assert code == 200
    assert payload["ok"] is True

    same_name_rows = [
        row
        for row in payload["overall"]
        if row["name"] == "Same Name"
    ]

    assert len(same_name_rows) == 2

    assert same_name_rows[0]["enrollment_id"] == enrollment_one_id
    assert same_name_rows[0]["rank"] == 1

    assert same_name_rows[1]["enrollment_id"] == enrollment_two_id
    assert same_name_rows[1]["rank"] == 2

from database import get_db_connection
from services.leaderboard_service import enrollment_leaderboard


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
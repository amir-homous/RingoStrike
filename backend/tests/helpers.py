def register_user(client, username="SmokeUser", password="secret123"):
    res = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "name": username,
            "email": f"{username.lower()}@example.com",
        },
    )

    assert res.status_code == 201
    data = res.get_json()
    assert data["ok"] is True
    assert data["access_token"]

    return data


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def insert_challenge(
    *,
    name,
    description,
    visibility="Public",
    status="Active",
    duration_days=14,
    join_code=None,
    tags="test",
):
    import database

    conn = database.get_db_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO challenges (
                name,
                description,
                visibility,
                status,
                duration_days,
                join_code,
                max_members,
                requires_proof,
                checkin_method,
                goal_type,
                tags
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, 0, 'Manual', 'Daily', ?)
            """,
            (
                name,
                description,
                visibility,
                status,
                duration_days,
                join_code,
                tags,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
from database import get_db_connection
from utils.date_utils import utc_today_iso
from services.stats_service import calculate_current_streak


def _with_ranks(items):
    return [
        {
            **item,
            "rank": index + 1,
        }
        for index, item in enumerate(items)
    ]


def enrollment_leaderboard(
    enrollment_id: int,
    user_id: int | None = None,
):
    conn = get_db_connection()

    try:
        enroll = conn.execute(
            "SELECT challenge_id, user_id FROM enrollments WHERE id = ?",
            (enrollment_id,),
        ).fetchone()

        if not enroll:
            return {"ok": False, "error": "not_found"}, 404

        if user_id is not None and int(enroll["user_id"]) != int(user_id):
            return {"ok": False, "error": "not_found"}, 404

        rows = conn.execute(
            """
            SELECT
                e.id AS enrollment_id,
                u.name,
                u.username
            FROM enrollments e
            JOIN users u ON e.user_id = u.id
            WHERE e.challenge_id = ?
              AND e.status = 'Active'
            """,
            (enroll["challenge_id"],),
        ).fetchall()

        today = utc_today_iso()
        board = []
        today_board = []

        for row in rows:
            eid = row["enrollment_id"]

            total = conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM checkins
                WHERE enrollment_id = ?
                  AND is_counted = 1
                """,
                (eid,),
            ).fetchone()["n"]

            dates = conn.execute(
                """
                SELECT date
                FROM checkins
                WHERE enrollment_id = ?
                  AND is_counted = 1
                ORDER BY date DESC
                """,
                (eid,),
            ).fetchall()

            streak = calculate_current_streak(
                [item["date"] for item in dates if item["date"]],
                today,
            )

            today_checked = (
                conn.execute(
                    """
                    SELECT 1
                    FROM checkins
                    WHERE enrollment_id = ?
                      AND date = ?
                      AND is_counted = 1
                    LIMIT 1
                    """,
                    (eid, today),
                ).fetchone()
                is not None
            )

            item = {
                "name": row["name"],
                "username": row["username"],
                "enrollment_id": eid,
                "total_checkins": int(total),
                "current_streak": int(streak),
                "today_checked": bool(today_checked),
            }

            board.append(item)

            if today_checked:
                today_board.append(item.copy())

        # Tie-breaker:
        # 1. total_checkins DESC
        # 2. current_streak DESC
        # 3. name ASC
        # 4. enrollment_id ASC
        board.sort(
            key=lambda item: (
                -item["total_checkins"],
                -item["current_streak"],
                (item["name"] or "").lower(),
                item["enrollment_id"],
            )
        )

        # Today board tie-breaker:
        # 1. current_streak DESC
        # 2. total_checkins DESC
        # 3. name ASC
        # 4. enrollment_id ASC
        today_board.sort(
            key=lambda item: (
                -item["current_streak"],
                -item["total_checkins"],
                (item["name"] or "").lower(),
                item["enrollment_id"],
            )
        )

        return {
            "ok": True,
            "overall": _with_ranks(board),
            "today": _with_ranks(today_board),
            "tie_breakers": {
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
            },
        }, 200

    finally:
        conn.close()

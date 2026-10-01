from __future__ import annotations

REWARD_DEFS = [
    ("career", "work_desk", "career_planner", "Career Planner", "Unlocked because you completed your first Career mission.", "planner", "career_planner", "common", "first_path_mission_done", None, 1, "work_desk_first_reward"),
    ("career", "work_desk", "career_desk_lamp", "Desk Lamp", "A calm work light for early Career consistency.", "lamp", "career_desk_lamp", "common", "early_consistency", None, 1, "work_desk_consistency"),
    ("career", "work_desk", "career_monitor", "Focus Monitor", "A clearer workspace for Career progress milestones.", "monitor", "career_monitor", "rare", "path_progress_milestone", None, 1, "work_desk_progress"),
    ("career", "work_desk", "career_project_board", "Project Board", "A visible board for Career achievements.", "wall_board", "career_project_board", "rare", "achievement_unlocked", None, 1, "work_desk_achievement"),
    ("career", "work_desk", "career_trophy", "Career Trophy", "A major Career milestone marker.", "trophy", "career_trophy", "epic", "major_path_milestone", None, 1, "work_desk_major"),
    ("creativity", "creative_corner", "creativity_sketchbook", "Sketchbook", "Unlocked because you completed your first Creativity mission.", "book", "creativity_sketchbook", "common", "first_path_mission_done", None, 1, "creative_corner_first_reward"),
    ("creativity", "creative_corner", "creativity_desk_lamp", "Creative Lamp", "A warm light for early Creativity consistency.", "lamp", "creativity_desk_lamp", "common", "early_consistency", None, 1, "creative_corner_consistency"),
    ("creativity", "creative_corner", "creativity_easel_upgrade", "Easel Upgrade", "A stronger creative setup for path progress.", "easel", "creativity_easel_upgrade", "rare", "path_progress_milestone", None, 1, "creative_corner_progress"),
    ("creativity", "creative_corner", "creativity_art_wall", "Art Wall", "A wall that reflects your creative achievements.", "wall_art", "creativity_art_wall", "rare", "achievement_unlocked", None, 1, "creative_corner_achievement"),
    ("creativity", "creative_corner", "creativity_trophy", "Creativity Trophy", "A major Creativity milestone marker.", "trophy", "creativity_trophy", "epic", "major_path_milestone", None, 1, "creative_corner_major"),
    ("fitness", "fitness_corner", "fitness_water_bottle", "Water Bottle", "Unlocked because you completed your first Fitness mission.", "bottle", "fitness_water_bottle", "common", "first_path_mission_done", None, 1, "fitness_corner_first_reward"),
    ("fitness", "fitness_corner", "fitness_dumbbells", "Dumbbells", "A steady Fitness consistency reward.", "weights", "fitness_dumbbells", "common", "early_consistency", None, 1, "fitness_corner_consistency"),
    ("fitness", "fitness_corner", "fitness_better_mat", "Better Mat", "A more grounded Fitness setup for path progress.", "mat", "fitness_better_mat", "rare", "path_progress_milestone", None, 1, "fitness_corner_progress"),
    ("fitness", "fitness_corner", "fitness_training_bench", "Training Bench", "A visible marker for Fitness achievements.", "bench", "fitness_training_bench", "rare", "achievement_unlocked", None, 1, "fitness_corner_achievement"),
    ("fitness", "fitness_corner", "fitness_trophy", "Fitness Trophy", "A major Fitness milestone marker.", "trophy", "fitness_trophy", "epic", "major_path_milestone", None, 1, "fitness_corner_major"),
    ("learning", "learning_corner", "learning_first_book", "First Book", "Unlocked because you completed your first Learning mission.", "book", "learning_first_book", "common", "first_path_mission_done", None, 1, "learning_corner_first_reward"),
    ("learning", "learning_corner", "learning_study_lamp", "Study Lamp", "A steady Learning consistency reward.", "lamp", "learning_study_lamp", "common", "early_consistency", None, 1, "learning_corner_consistency"),
    ("learning", "learning_corner", "learning_book_stack", "Book Stack", "A visible stack for Learning progress.", "books", "learning_book_stack", "rare", "path_progress_milestone", None, 1, "learning_corner_progress"),
    ("learning", "learning_corner", "learning_bookshelf", "Bookshelf", "A shelf that reflects Learning achievements.", "shelf", "learning_bookshelf", "rare", "achievement_unlocked", None, 1, "learning_corner_achievement"),
    ("learning", "learning_corner", "learning_trophy", "Learning Trophy", "A major Learning milestone marker.", "trophy", "learning_trophy", "epic", "major_path_milestone", None, 1, "learning_corner_major"),
    ("sleep", "sleep_corner", "sleep_pillow", "Pillow", "Unlocked because you completed your first Sleep mission.", "pillow", "sleep_pillow", "common", "first_path_mission_done", None, 1, "sleep_corner_first_reward"),
    ("sleep", "sleep_corner", "sleep_bedside_lamp", "Bedside Lamp", "A soft Sleep consistency reward.", "lamp", "sleep_bedside_lamp", "common", "early_consistency", None, 1, "sleep_corner_consistency"),
    ("sleep", "sleep_corner", "sleep_blanket", "Blanket", "A cozy marker for Sleep path progress.", "blanket", "sleep_blanket", "rare", "path_progress_milestone", None, 1, "sleep_corner_progress"),
    ("sleep", "sleep_corner", "sleep_moon_decoration", "Moon Decoration", "A calm decoration for Sleep achievements.", "wall_art", "sleep_moon_decoration", "rare", "achievement_unlocked", None, 1, "sleep_corner_achievement"),
    ("sleep", "sleep_corner", "sleep_trophy", "Recovery Trophy", "A major Sleep milestone marker.", "trophy", "sleep_trophy", "epic", "major_path_milestone", None, 1, "sleep_corner_major"),
]


def ensure_reward_definitions(conn):
    for reward in REWARD_DEFS:
        path_key = reward[0]
        path_row = conn.execute("SELECT id FROM paths WHERE key = ?", (path_key,)).fetchone()
        if not path_row:
            continue

        conn.execute(
            """
            INSERT INTO reward_definitions (
                path_id,
                zone_key,
                key,
                title,
                description,
                object_type,
                asset_key,
                rarity,
                unlock_condition_type,
                unlock_condition_value,
                stage,
                slot_key,
                status,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', datetime('now'))
            ON CONFLICT(key) DO UPDATE SET
                path_id = excluded.path_id,
                zone_key = excluded.zone_key,
                title = excluded.title,
                description = excluded.description,
                object_type = excluded.object_type,
                asset_key = excluded.asset_key,
                rarity = excluded.rarity,
                unlock_condition_type = excluded.unlock_condition_type,
                unlock_condition_value = excluded.unlock_condition_value,
                stage = excluded.stage,
                slot_key = excluded.slot_key,
                status = 'Active',
                updated_at = datetime('now')
            """,
            (
                path_row["id"],
                reward[1],
                reward[2],
                reward[3],
                reward[4],
                reward[5],
                reward[6],
                reward[7],
                reward[8],
                reward[9],
                reward[10],
                reward[11],
            ),
        )


def list_reward_definitions():
    from database import get_db_connection

    conn = get_db_connection()
    try:
        ensure_reward_definitions(conn)
        conn.commit()
        rows = conn.execute(
            """
            SELECT
                rd.id,
                rd.key,
                rd.title,
                rd.description,
                p.key AS path_key,
                rd.zone_key,
                rd.object_type,
                rd.asset_key,
                rd.rarity,
                rd.unlock_condition_type,
                rd.unlock_condition_value,
                rd.stage,
                rd.slot_key,
                rd.status
            FROM reward_definitions rd
            JOIN paths p ON p.id = rd.path_id
            WHERE rd.status = 'Active'
            ORDER BY p.sort_order ASC, rd.stage ASC, rd.id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def unlock_reward(user_id: int, reward_id: int, *, source_type: str | None = None, source_id: int | None = None):
    from database import get_db_connection

    conn = get_db_connection()
    try:
        reward = conn.execute(
            """
            SELECT rd.*, p.key AS path_key
            FROM reward_definitions rd
            JOIN paths p ON p.id = rd.path_id
            WHERE rd.id = ? AND rd.status = 'Active'
            """,
            (reward_id,),
        ).fetchone()
        if not reward:
            return {"ok": False, "error": "reward_not_found"}, 404

        conn.execute(
            """
            INSERT OR IGNORE INTO user_space (user_id)
            VALUES (?)
            """,
            (user_id,),
        )
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO user_rewards (
                user_id,
                reward_id,
                source_type,
                source_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (user_id, reward_id, source_type, source_id),
        )
        conn.commit()

        reward_payload = _reward_payload(reward)
        reward_payload.update({
            "source_type": source_type,
            "source_id": source_id,
            "is_seen": False,
        })

        return {
            "ok": True,
            "reward": reward_payload,
            "newly_unlocked": cursor.rowcount == 1,
        }, 200
    finally:
        conn.close()


def unlock_first_path_reward_for_mission(user_id: int, mission_id: int):
    from database import get_db_connection

    conn = get_db_connection()
    try:
        ensure_reward_definitions(conn)
        mission = conn.execute(
            """
            SELECT
                m.id AS mission_id,
                m.mission_intensity,
                c.path_id,
                p.key AS path_key
            FROM missions m
            JOIN challenges c ON c.id = m.challenge_id
            JOIN paths p ON p.id = c.path_id
            WHERE m.id = ?
            """,
            (mission_id,),
        ).fetchone()
        if not mission:
            return {"ok": False, "error": "mission_not_found"}, 404

        if (mission["mission_intensity"] or "main") == "bonus":
            return {
                "ok": True,
                "reward": None,
                "newly_unlocked": False,
            }, 200

        reward = conn.execute(
            """
            SELECT rd.*, p.key AS path_key
            FROM reward_definitions rd
            JOIN paths p ON p.id = rd.path_id
            WHERE rd.path_id = ?
              AND rd.unlock_condition_type = 'first_path_mission_done'
              AND rd.status = 'Active'
            ORDER BY rd.stage ASC, rd.id ASC
            LIMIT 1
            """,
            (mission["path_id"],),
        ).fetchone()
        if not reward:
            return {"ok": True, "reward": None, "newly_unlocked": False}, 200

        conn.execute(
            """
            INSERT OR IGNORE INTO user_space (user_id)
            VALUES (?)
            """,
            (user_id,),
        )
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO user_rewards (
                user_id,
                reward_id,
                source_type,
                source_id
            )
            VALUES (?, ?, 'mission_reward', ?)
            """,
            (user_id, reward["id"], mission_id),
        )
        conn.commit()

        reward_payload = _reward_payload(reward)
        reward_payload.update({
            "source_type": "mission_reward",
            "source_id": mission_id,
            "is_seen": False,
        })

        return {
            "ok": True,
            "reward": reward_payload,
            "newly_unlocked": cursor.rowcount == 1,
        }, 200
    finally:
        conn.close()


def get_user_space_state(user_id: int):
    from database import get_db_connection

    conn = get_db_connection()
    try:
        ensure_reward_definitions(conn)
        conn.execute(
            """
            INSERT OR IGNORE INTO user_space (user_id)
            VALUES (?)
            """,
            (user_id,),
        )
        conn.commit()

        space = conn.execute(
            """
            SELECT user_id, theme, current_stage, updated_at
            FROM user_space
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        reward_rows = conn.execute(
            """
            SELECT
                rd.*,
                p.key AS path_key,
                ur.unlocked_at,
                ur.source_type,
                ur.source_id,
                ur.is_seen
            FROM reward_definitions rd
            JOIN paths p ON p.id = rd.path_id
            LEFT JOIN user_rewards ur
              ON ur.reward_id = rd.id
             AND ur.user_id = ?
            WHERE rd.status = 'Active'
            ORDER BY p.sort_order ASC, rd.stage ASC, rd.id ASC
            """,
            (user_id,),
        ).fetchall()

        return {
            "ok": True,
            "space": {
                "user_id": space["user_id"],
                "theme": space["theme"],
                "current_stage": int(space["current_stage"] or 1),
                "updated_at": space["updated_at"],
            },
            "rewards": [_user_reward_payload(row) for row in reward_rows],
        }, 200
    finally:
        conn.close()


def _reward_payload(row):
    return {
        "id": row["id"],
        "key": row["key"],
        "title": row["title"],
        "description": row["description"],
        "path_key": row["path_key"],
        "zone_key": row["zone_key"],
        "object_type": row["object_type"],
        "asset_key": row["asset_key"],
        "rarity": row["rarity"],
        "unlock_condition_type": row["unlock_condition_type"],
        "unlock_condition_value": row["unlock_condition_value"],
        "stage": int(row["stage"] or 1),
        "slot_key": row["slot_key"],
    }


def _user_reward_payload(row):
    payload = _reward_payload(row)
    payload.update({
        "unlocked": bool(row["unlocked_at"]),
        "unlocked_at": row["unlocked_at"],
        "source_type": row["source_type"],
        "source_id": row["source_id"],
        "is_seen": bool(row["is_seen"]),
    })
    return payload

def _tiny_mission(parent_key, key, title, description, *, minutes=2, xp_reward=3):
    return (
        key,
        title,
        description,
        xp_reward,
        {
            "mission_intensity": "tiny",
            "estimated_minutes": minutes,
            "parent_mission_key": parent_key,
            "unlock_after_days": 0,
        },
    )


def _bonus_mission(parent_key, key, title, description, *, minutes=5, xp_reward=5, unlock_after_days=0):
    return (
        key,
        title,
        description,
        xp_reward,
        {
            "mission_intensity": "bonus",
            "estimated_minutes": minutes,
            "parent_mission_key": parent_key,
            "unlock_after_days": unlock_after_days,
        },
    )


MISSION_METADATA = {
    "move-10": {"estimated_minutes": 10, "suggested_time": "morning", "difficulty": "easy"},
    "drink-water": {"estimated_minutes": 1, "suggested_time": "anytime", "difficulty": "easy"},
    "energy-note": {"estimated_minutes": 3, "suggested_time": "evening", "difficulty": "easy"},
    "bodyweight-set": {"estimated_minutes": 10, "suggested_time": "morning", "difficulty": "easy"},
    "warm-up": {"estimated_minutes": 2, "suggested_time": "morning", "difficulty": "easy"},
    "cool-down": {"estimated_minutes": 1, "suggested_time": "evening", "difficulty": "easy"},
    "stretch-focus": {"estimated_minutes": 8, "suggested_time": "evening", "difficulty": "easy"},
    "posture-check": {"estimated_minutes": 1, "suggested_time": "midday", "difficulty": "easy"},
    "mobility-note": {"estimated_minutes": 3, "suggested_time": "evening", "difficulty": "easy"},
    "learn-one-thing": {"estimated_minutes": 10, "suggested_time": "midday", "difficulty": "easy"},
    "capture-note": {"estimated_minutes": 5, "suggested_time": "afternoon", "difficulty": "easy"},
    "apply-small": {"estimated_minutes": 8, "suggested_time": "afternoon", "difficulty": "medium"},
    "read-five-pages": {"estimated_minutes": 12, "suggested_time": "evening", "difficulty": "easy"},
    "highlight-one": {"estimated_minutes": 3, "suggested_time": "evening", "difficulty": "easy"},
    "share-insight": {"estimated_minutes": 5, "suggested_time": "evening", "difficulty": "easy"},
    "practice-15": {"estimated_minutes": 15, "suggested_time": "afternoon", "difficulty": "medium"},
    "choose-drill": {"estimated_minutes": 3, "suggested_time": "afternoon", "difficulty": "easy"},
    "review-progress": {"estimated_minutes": 4, "suggested_time": "evening", "difficulty": "easy"},
    "deep-work-block": {"estimated_minutes": 25, "suggested_time": "morning", "difficulty": "medium"},
    "define-output": {"estimated_minutes": 3, "suggested_time": "morning", "difficulty": "easy"},
    "close-loop": {"estimated_minutes": 5, "suggested_time": "afternoon", "difficulty": "easy"},
    "improve-asset": {"estimated_minutes": 20, "suggested_time": "afternoon", "difficulty": "medium"},
    "collect-proof": {"estimated_minutes": 5, "suggested_time": "afternoon", "difficulty": "easy"},
    "next-edit": {"estimated_minutes": 3, "suggested_time": "evening", "difficulty": "easy"},
    "send-signal": {"estimated_minutes": 5, "suggested_time": "afternoon", "difficulty": "easy"},
    "update-context": {"estimated_minutes": 3, "suggested_time": "afternoon", "difficulty": "easy"},
    "next-contact": {"estimated_minutes": 3, "suggested_time": "evening", "difficulty": "easy"},
    "capture-idea": {"estimated_minutes": 5, "suggested_time": "anytime", "difficulty": "easy"},
    "make-small": {"estimated_minutes": 15, "suggested_time": "afternoon", "difficulty": "medium"},
    "archive-spark": {"estimated_minutes": 3, "suggested_time": "evening", "difficulty": "easy"},
    "draft-small": {"estimated_minutes": 15, "suggested_time": "afternoon", "difficulty": "medium"},
    "polish-one-pass": {"estimated_minutes": 8, "suggested_time": "evening", "difficulty": "medium"},
    "share-or-save": {"estimated_minutes": 5, "suggested_time": "evening", "difficulty": "easy"},
    "choose-source": {"estimated_minutes": 3, "suggested_time": "anytime", "difficulty": "easy"},
    "remix-it": {"estimated_minutes": 12, "suggested_time": "afternoon", "difficulty": "medium"},
    "save-version": {"estimated_minutes": 3, "suggested_time": "evening", "difficulty": "easy"},
    "mind-reset": {"estimated_minutes": 7, "suggested_time": "evening", "difficulty": "easy"},
    "clear-one-thing": {"estimated_minutes": 5, "suggested_time": "evening", "difficulty": "easy"},
    "soft-close": {"estimated_minutes": 5, "suggested_time": "night", "difficulty": "easy"},
    "dim-inputs": {"estimated_minutes": 5, "suggested_time": "night", "difficulty": "easy"},
    "prepare-room": {"estimated_minutes": 5, "suggested_time": "night", "difficulty": "easy"},
    "sleep-note": {"estimated_minutes": 3, "suggested_time": "night", "difficulty": "easy"},
    "morning-light": {"estimated_minutes": 5, "suggested_time": "morning", "difficulty": "easy"},
    "no-rush-start": {"estimated_minutes": 1, "suggested_time": "morning", "difficulty": "easy"},
    "energy-check": {"estimated_minutes": 2, "suggested_time": "morning", "difficulty": "easy"},
}

VALID_SUGGESTED_TIMES = {"morning", "midday", "afternoon", "evening", "night", "anytime"}
VALID_MISSION_DIFFICULTIES = {"easy", "medium", "hard"}


MVP_PATHS = [
    {
        "key": "fitness",
        "title": "Fitness",
        "description": "Build energy and body momentum through small movement missions.",
        "icon": "activity",
        "color": "#4ade80",
        "challenges": [
            {
                "name": "Move Your Body",
                "description": "Create physical momentum with a daily walk, workout, stretch, or movement session.",
                "duration_days": 21,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "fitness,movement,energy",
                "ringo_intro": "Start small. One movement session is enough to protect today's rhythm.",
                "missions": [
                    ("move-10", "Move for 10 minutes", "Walk, stretch, or do a light workout for ten minutes.", 10),
                    ("drink-water", "Drink water", "Hydrate once before or after your movement session.", 5),
                    ("energy-note", "Notice your energy", "Write one short note about how your body feels today.", 5),
                    _tiny_mission("move-10", "move-10-tiny", "Move for 2 minutes", "Walk, stretch, or shake out tension for just two minutes.", minutes=2),
                    _bonus_mission("move-10", "move-10-bonus", "Add one extra movement minute", "If you feel good, add one extra minute after the main movement mission.", minutes=1),
                ],
            },
            {
                "name": "Strength Starter",
                "description": "Begin a simple strength rhythm with light bodyweight work.",
                "duration_days": 14,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "fitness,strength,starter",
                "ringo_intro": "No heroic session needed. A few honest reps count.",
                "missions": [
                    ("bodyweight-set", "Complete one bodyweight set", "Do one simple set of squats, pushups, or core work.", 10),
                    ("warm-up", "Warm up gently", "Spend two minutes preparing your body before the set.", 5),
                    ("cool-down", "Cool down", "Take one calm minute to breathe and reset.", 5),
                    _tiny_mission("bodyweight-set", "bodyweight-set-tiny", "Do three honest reps", "Do three calm reps of any bodyweight movement.", minutes=2),
                    _bonus_mission(
                        "bodyweight-set",
                        "bodyweight-set-bonus",
                        "Add one steady set",
                        "If the first set felt okay, add one extra calm set or hold.",
                        minutes=3,
                    ),
                ],
            },
            {
                "name": "Mobility Reset",
                "description": "Keep your body loose with a daily mobility pause.",
                "duration_days": 10,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "fitness,mobility,reset",
                "ringo_intro": "A flexible body starts with one quiet reset.",
                "missions": [
                    ("stretch-focus", "Stretch one tight area", "Pick one tight area and stretch it calmly.", 10),
                    ("posture-check", "Check your posture", "Reset your posture once during the day.", 5),
                    ("mobility-note", "Log a mobility note", "Record one sentence about what improved.", 5),
                    _tiny_mission("stretch-focus", "stretch-focus-tiny", "Stretch for one minute", "Pick one tight area and give it one calm minute.", minutes=1),
                    _bonus_mission(
                        "stretch-focus",
                        "stretch-focus-bonus",
                        "Stretch one more area",
                        "If your body wants more room, choose one more tight area and stretch it gently.",
                        minutes=3,
                    ),
                ],
            },
        ],
    },
    {
        "key": "learning",
        "title": "Learning",
        "description": "Turn curiosity into visible daily learning progress.",
        "icon": "book",
        "color": "#6ee5ff",
        "challenges": [
            {
                "name": "Learn One Thing",
                "description": "Learn, read, watch, practice, or document one useful thing every day.",
                "duration_days": 30,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "learning,growth,knowledge",
                "ringo_intro": "One useful thing today is enough to keep your learning identity alive.",
                "missions": [
                    ("learn-one-thing", "Learn one useful thing", "Read, watch, practice, or document one useful idea.", 10),
                    ("capture-note", "Capture one note", "Write the idea in your own words.", 5),
                    ("apply-small", "Apply it once", "Use the idea in a tiny real action if possible.", 10),
                    _tiny_mission("learn-one-thing", "learn-one-thing-tiny", "Learn one tiny idea", "Read or watch one small piece and name the useful idea.", minutes=2),
                    _bonus_mission("learn-one-thing", "learn-one-thing-bonus", "Save a second useful idea", "If curiosity is alive, capture one more useful idea.", minutes=5),
                ],
            },
            {
                "name": "Read Five Pages",
                "description": "Build a calm reading rhythm with a small daily page target.",
                "duration_days": 21,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "learning,reading,books",
                "ringo_intro": "Five pages can change the tone of a day.",
                "missions": [
                    ("read-five-pages", "Read five pages", "Read five pages from any useful book or article.", 10),
                    ("highlight-one", "Highlight one idea", "Choose one sentence or idea worth keeping.", 5),
                    ("share-insight", "Explain the insight", "Explain the idea briefly to yourself or someone else.", 5),
                    _tiny_mission("read-five-pages", "read-five-pages-tiny", "Read one page", "Read one page or one short section. That still keeps the thread alive.", minutes=3),
                    _bonus_mission(
                        "read-five-pages",
                        "read-five-pages-bonus",
                        "Save one extra idea",
                        "If the reading has momentum, save one more useful idea before you stop.",
                        minutes=4,
                    ),
                ],
            },
            {
                "name": "Practice Skill",
                "description": "Make skill growth visible through one focused practice block.",
                "duration_days": 14,
                "difficulty": "medium",
                "stage": 2,
                "tags": "learning,practice,skill",
                "ringo_intro": "Practice becomes identity when it survives ordinary days.",
                "missions": [
                    ("practice-15", "Practice for 15 minutes", "Spend fifteen focused minutes on one skill.", 15),
                    ("choose-drill", "Choose one drill", "Pick one small drill instead of practicing everything.", 5),
                    ("review-progress", "Review one improvement", "Name one thing that felt better than before.", 5),
                    _tiny_mission("practice-15", "practice-15-tiny", "Practice for three minutes", "Do one tiny drill for three focused minutes.", minutes=3),
                    _bonus_mission(
                        "practice-15",
                        "practice-15-bonus",
                        "Repeat one small drill",
                        "If practice feels alive, repeat one tiny drill once more with attention.",
                        minutes=5,
                    ),
                ],
            },
        ],
    },
    {
        "key": "career",
        "title": "Career",
        "description": "Protect focused work and career momentum with small daily wins.",
        "icon": "briefcase",
        "color": "#c35ad6",
        "challenges": [
            {
                "name": "Deep Work Sprint",
                "description": "Protect focused time and complete one meaningful deep-work session per day.",
                "duration_days": 14,
                "difficulty": "medium",
                "stage": 1,
                "tags": "career,focus,work",
                "ringo_intro": "Your career path starts with one protected focus block.",
                "missions": [
                    ("deep-work-block", "Complete one focus block", "Work without switching context for one focused block.", 15),
                    ("define-output", "Define the output", "Write what finished means before you begin.", 5),
                    ("close-loop", "Close the loop", "Record the outcome or next step after the session.", 5),
                    _tiny_mission("deep-work-block", "deep-work-block-tiny", "Focus for three minutes", "Protect three minutes for one task without switching tabs.", minutes=3),
                    _bonus_mission("deep-work-block", "deep-work-block-bonus", "Add one closing note", "If the focus block went well, write one extra note about the next step.", minutes=3),
                ],
            },
            {
                "name": "Portfolio Pulse",
                "description": "Move one professional asset forward every day.",
                "duration_days": 21,
                "difficulty": "medium",
                "stage": 2,
                "tags": "career,portfolio,progress",
                "ringo_intro": "A visible career identity is built one proof at a time.",
                "missions": [
                    ("improve-asset", "Improve one asset", "Improve a portfolio, resume, case study, or profile item.", 15),
                    ("collect-proof", "Collect proof", "Save one screenshot, metric, note, or example.", 5),
                    ("next-edit", "Name the next edit", "Write the next small improvement to make.", 5),
                    _tiny_mission("improve-asset", "improve-asset-tiny", "Make one tiny edit", "Change one line, one word, one image, or one detail on a career asset.", minutes=3),
                    _bonus_mission(
                        "improve-asset",
                        "improve-asset-bonus",
                        "Save one proof",
                        "If the asset moved forward, save one screenshot, note, or before-after proof.",
                        minutes=4,
                    ),
                ],
            },
            {
                "name": "Network Signal",
                "description": "Create one small professional signal or connection.",
                "duration_days": 10,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "career,network,signal",
                "ringo_intro": "Connection does not need pressure. One thoughtful signal is enough.",
                "missions": [
                    ("send-signal", "Send one signal", "Message, thank, comment, or follow up with one person.", 10),
                    ("update-context", "Update context", "Write one note about the relationship or opportunity.", 5),
                    ("next-contact", "Choose next contact", "Pick who you might reach out to next.", 5),
                    _tiny_mission("send-signal", "send-signal-tiny", "Draft one sentence", "Write one sentence you could send later, even if you do not send it now.", minutes=2),
                    _bonus_mission(
                        "improve-asset",
                        "improve-asset-bonus",
                        "Save one proof",
                        "If the asset moved forward, save one screenshot, note, or before-after proof.",
                        minutes=4,
                    ),
                ],
            },
        ],
    },
    {
        "key": "creativity",
        "title": "Creativity",
        "description": "Keep creative identity alive through small making rituals.",
        "icon": "sparkles",
        "color": "#f7d774",
        "challenges": [
            {
                "name": "Creative Spark",
                "description": "Make or capture one small creative idea each day.",
                "duration_days": 14,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "creativity,ideas,making",
                "ringo_intro": "Creativity likes a low-pressure doorway.",
                "missions": [
                    ("capture-idea", "Capture one idea", "Save one sketch, phrase, melody, image, or concept.", 10),
                    ("make-small", "Make one small thing", "Turn the idea into a tiny artifact.", 10),
                    ("archive-spark", "Archive the spark", "Put today's idea somewhere you can find it again.", 5),
                    _tiny_mission("capture-idea", "capture-idea-tiny", "Capture one tiny spark", "Save one phrase, shape, color, sound, or rough thought.", minutes=1),
                    _bonus_mission("capture-idea", "capture-idea-bonus", "Add one detail", "If the idea has energy, add one extra detail before you archive it.", minutes=3),
                ],
            },
            {
                "name": "Publish Tiny",
                "description": "Practice sharing one small piece of creative output.",
                "duration_days": 10,
                "difficulty": "medium",
                "stage": 2,
                "tags": "creativity,publishing,sharing",
                "ringo_intro": "Sharing can be quiet. Tiny publishing still counts.",
                "missions": [
                    ("draft-small", "Draft a tiny piece", "Create a small publishable draft.", 10),
                    ("polish-one-pass", "Polish once", "Make one improvement pass, then stop.", 5),
                    ("share-or-save", "Share or save it", "Publish it or save it to a ready folder.", 10),
                    _tiny_mission("draft-small", "draft-small-tiny", "Write one rough line", "Create one rough line, beat, frame, or sentence for the draft.", minutes=2),
                    _bonus_mission(
                        "draft-small",
                        "draft-small-bonus",
                        "Create one extra version",
                        "If the draft has energy, make one small alternate version before you stop.",
                        minutes=5,
                    ),
                ],
            },
            {
                "name": "Idea Remix",
                "description": "Train creative range by remixing one existing idea.",
                "duration_days": 7,
                "difficulty": "easy",
                "stage": 1,
                "tags": "creativity,remix,practice",
                "ringo_intro": "A remix is a safe way to start moving.",
                "missions": [
                    ("choose-source", "Choose one source", "Pick one idea, reference, or prompt to remix.", 5),
                    ("remix-it", "Remix it", "Change the format, audience, mood, or constraint.", 10),
                    ("save-version", "Save the version", "Keep the remix as proof of practice.", 5),
                    _tiny_mission("choose-source", "choose-source-tiny", "Pick one reference", "Choose one reference or prompt and stop there if that is enough.", minutes=1),
                    _bonus_mission(
                        "choose-source",
                        "choose-source-bonus",
                        "Try one alternate angle",
                        "If the source feels interesting, write one different angle, mood, or constraint for the remix.",
                        minutes=4,
                    ),
                ],
            },
        ],
    },
    {
        "key": "sleep",
        "title": "Sleep",
        "description": "Create calmer nights and better recovery through small reset missions.",
        "icon": "moon",
        "color": "#818cf8",
        "challenges": [
            {
                "name": "Mind Reset",
                "description": "Take a short daily reset for reflection, breathing, journaling, or mental clarity.",
                "duration_days": 7,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "sleep,reset,calm",
                "ringo_intro": "A calmer night starts before the moment you need sleep.",
                "missions": [
                    ("mind-reset", "Take a reset moment", "Pause for breathing, journaling, or quiet reflection.", 10),
                    ("clear-one-thing", "Clear one loose end", "Write down one worry or next action before it follows you.", 5),
                    ("soft-close", "Create a soft close", "Do one small action that tells your day it can end.", 5),
                    _tiny_mission("mind-reset", "mind-reset-tiny", "Take three calm breaths", "Pause and take three slow breaths without fixing anything.", minutes=1),
                    _bonus_mission("mind-reset", "mind-reset-bonus", "Write one calm sentence", "If your mind is still noisy, write one sentence to park it for tomorrow.", minutes=3),
                ],
            },
            {
                "name": "Sleep Wind Down",
                "description": "Build a simple evening wind-down ritual.",
                "duration_days": 14,
                "difficulty": "beginner",
                "stage": 1,
                "tags": "sleep,evening,recovery",
                "ringo_intro": "The wind-down is the mission. Sleep can follow.",
                "missions": [
                    ("dim-inputs", "Reduce inputs", "Lower one source of stimulation before bed.", 10),
                    ("prepare-room", "Prepare the room", "Make one small change that helps sleep feel easier.", 5),
                    ("sleep-note", "Write a sleep note", "Record what helped or got in the way tonight.", 5),
                    _tiny_mission("dim-inputs", "dim-inputs-tiny", "Dim one input", "Lower one light, one sound, or one screen for a minute.", minutes=1),
                    _bonus_mission(
                        "dim-inputs",
                        "dim-inputs-bonus",
                        "Add one calm cue",
                        "If the night still feels noisy, add one small cue that tells your body it can slow down.",
                        minutes=3,
                    ),
                ],
            },
            {
                "name": "Morning Recovery",
                "description": "Start the day with one recovery-friendly signal.",
                "duration_days": 10,
                "difficulty": "easy",
                "stage": 1,
                "tags": "sleep,morning,recovery",
                "ringo_intro": "Recovery continues in the first minutes of the morning.",
                "missions": [
                    ("morning-light", "Get morning light", "Step near light or outside for a short reset.", 10),
                    ("no-rush-start", "Start without rushing", "Take one calm minute before diving into tasks.", 5),
                    ("energy-check", "Check energy", "Notice your energy level without judging it.", 5),
                    _tiny_mission("morning-light", "morning-light-tiny", "Find light for one minute", "Stand near a window or step outside for one minute.", minutes=1),
                    _bonus_mission(
                        "morning-light",
                        "morning-light-bonus",
                        "Add one calm breath",
                        "If the morning feels okay, take one slow breath after finding light.",
                        minutes=2,
                    ),
                ],
            },
        ],
    },
]


def _mission_seed_payload(mission, mission_index):
    key, title, description, xp_reward = mission[:4]
    options = mission[4] if len(mission) > 4 and isinstance(mission[4], dict) else {}
    metadata = MISSION_METADATA.get(key, {})
    intensity = options.get("mission_intensity") or options.get("intensity") or "main"
    estimated_minutes = options.get("estimated_minutes") or metadata.get("estimated_minutes")
    suggested_time = options.get("suggested_time") or metadata.get("suggested_time") or "anytime"
    difficulty = options.get("difficulty") or metadata.get("difficulty")

    if not estimated_minutes:
        estimated_minutes = 2 if intensity == "tiny" else 5 if intensity == "bonus" else 10
    if suggested_time not in VALID_SUGGESTED_TIMES:
        suggested_time = "anytime"
    if difficulty not in VALID_MISSION_DIFFICULTIES:
        difficulty = "easy" if intensity == "tiny" else "medium" if intensity == "bonus" else "easy"

    return {
        "key": key,
        "title": title,
        "description": description,
        "xp_reward": xp_reward,
        "difficulty": difficulty,
        "suggested_time": suggested_time,
        "mission_intensity": intensity,
        "estimated_minutes": estimated_minutes,
        "parent_mission_key": options.get("parent_mission_key"),
        "order_index": mission_index,
        "unlock_after_days": max(0, options.get("unlock_after_days", mission_index - 1)),
    }


def ensure_mvp_paths_and_missions(conn):
    for path_index, path in enumerate(MVP_PATHS, start=1):
        conn.execute(
            """
            INSERT INTO paths (
                key, title, description, icon, color, sort_order, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Active')
            ON CONFLICT(key) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                icon = excluded.icon,
                color = excluded.color,
                sort_order = excluded.sort_order,
                status = 'Active'
            """,
            (
                path["key"],
                path["title"],
                path["description"],
                path["icon"],
                path["color"],
                path_index,
            ),
        )

        path_id = conn.execute(
            "SELECT id FROM paths WHERE key = ?",
            (path["key"],),
        ).fetchone()["id"]

        for challenge in path["challenges"]:
            existing = conn.execute(
                "SELECT id FROM challenges WHERE name = ? LIMIT 1",
                (challenge["name"],),
            ).fetchone()

            if existing:
                challenge_id = existing["id"]
                conn.execute(
                    """
                    UPDATE challenges
                    SET
                        description = COALESCE(description, ?),
                        path_id = ?,
                        difficulty = ?,
                        stage = ?,
                        estimated_days = ?,
                        ringo_intro = ?,
                        tags = COALESCE(tags, ?),
                        status = 'Active'
                    WHERE id = ?
                    """,
                    (
                        challenge["description"],
                        path_id,
                        challenge["difficulty"],
                        challenge["stage"],
                        challenge["duration_days"],
                        challenge["ringo_intro"],
                        challenge["tags"],
                        challenge_id,
                    ),
                )
            else:
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
                        tags,
                        path_id,
                        difficulty,
                        stage,
                        estimated_days,
                        ringo_intro
                    )
                    VALUES (?, ?, 'Public', 'Active', ?, NULL, 0, 0, 'Manual', 'Daily', ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        challenge["name"],
                        challenge["description"],
                        challenge["duration_days"],
                        challenge["tags"],
                        path_id,
                        challenge["difficulty"],
                        challenge["stage"],
                        challenge["duration_days"],
                        challenge["ringo_intro"],
                    ),
                )
                challenge_id = cur.lastrowid

            seeded_mission_ids = {}

            for mission_index, mission in enumerate(challenge["missions"], start=1):
                mission_payload = _mission_seed_payload(mission, mission_index)
                conn.execute(
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
                        ringo_message,
                        status
                    )
                    VALUES (?, ?, ?, ?, 'daily', ?, 1, ?, ?, ?, ?, ?, ?, ?, 'Active')
                    ON CONFLICT(challenge_id, key) DO UPDATE SET
                        title = excluded.title,
                        description = excluded.description,
                        difficulty = excluded.difficulty,
                        xp_reward = excluded.xp_reward,
                        order_index = excluded.order_index,
                        suggested_time = excluded.suggested_time,
                        unlock_after_days = excluded.unlock_after_days,
                        mission_intensity = COALESCE(excluded.mission_intensity, missions.mission_intensity, 'main'),
                        estimated_minutes = excluded.estimated_minutes,
                        ringo_message = excluded.ringo_message,
                        status = 'Active'
                    """,
                    (
                        challenge_id,
                        mission_payload["key"],
                        mission_payload["title"],
                        mission_payload["description"],
                        mission_payload["difficulty"],
                        mission_payload["xp_reward"],
                        mission_payload["order_index"],
                        mission_payload["suggested_time"],
                        mission_payload["unlock_after_days"],
                        mission_payload["mission_intensity"],
                        mission_payload["estimated_minutes"],
                        f"Ringo says: {mission_payload['title']} is enough for today's mission.",
                    ),
                )
                row = conn.execute(
                    "SELECT id FROM missions WHERE challenge_id = ? AND key = ?",
                    (challenge_id, mission_payload["key"]),
                ).fetchone()
                if row:
                    seeded_mission_ids[mission_payload["key"]] = row["id"]

            for mission_index, mission in enumerate(challenge["missions"], start=1):
                mission_payload = _mission_seed_payload(mission, mission_index)
                parent_key = mission_payload.get("parent_mission_key")
                parent_id = seeded_mission_ids.get(parent_key) if parent_key else None
                if parent_id:
                    conn.execute(
                        """
                        UPDATE missions
                        SET parent_mission_id = ?
                        WHERE challenge_id = ? AND key = ?
                        """,
                        (parent_id, challenge_id, mission_payload["key"]),
                    )


def archive_legacy_unlinked_challenges(conn):
    conn.execute(
        """
        UPDATE challenges
        SET status = 'Archived'
        WHERE status = 'Active'
          AND (
            path_id IS NULL
            OR NOT EXISTS (
                SELECT 1
                FROM missions
                WHERE missions.challenge_id = challenges.id
                  AND missions.status = 'Active'
            )
          )
        """
    )

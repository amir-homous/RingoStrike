import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone,timedelta
from services.path_seed_service import (
    archive_legacy_unlinked_challenges,
    ensure_mvp_paths_and_missions,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.getenv("DB_PATH") or os.path.join(BASE_DIR, "users.db")

def get_db_connection():
    """Get database connection with row factory and FK enforcement"""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _table_columns(cursor, table_name):
    return [row[1] for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]


def _add_column_if_missing(cursor, table_name, column_name, ddl):
    columns = _table_columns(cursor, table_name)

    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def init_db():
    """Initialize database with all necessary tables"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              telegram_id TEXT UNIQUE, 
              username TEXT UNIQUE, 
              password_hash TEXT, 
              name TEXT,
              email TEXT UNIQUE,
              avatar_url TEXT,
              bio TEXT DEFAULT '',
              profile_visibility TEXT DEFAULT 'public',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
        # ===== Users table migrations =====

    user_columns = [r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()]

    if "avatar_url" not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")

    if "bio" not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")

    if "profile_visibility" not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN profile_visibility TEXT DEFAULT 'public'")
        
    
    # User stats table for tracking streaks and check-ins
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL UNIQUE,
                  total_checkins INTEGER DEFAULT 0,
                  current_streak INTEGER DEFAULT 0,
                  longest_streak INTEGER DEFAULT 0,
                  total_points INTEGER DEFAULT 0,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    
    c.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                visibility TEXT CHECK(visibility IN ('Public', 'Invite-only', 'Private')) DEFAULT 'Public',
                status TEXT CHECK(status IN ('Active', 'Archived')) DEFAULT 'Active',
                duration_days INTEGER,
                join_code TEXT,
                max_members INTEGER DEFAULT 0,
                requires_proof INTEGER DEFAULT 0, -- 0 for False, 1 for True
                checkin_method TEXT DEFAULT 'Manual', -- Manual, Auto, etc.
                goal_type TEXT, -- e.g., 'Daily', 'Weekly'
                tags TEXT -- ذخیره به صورت رشته کاما‌دار (Tag1,Tag2)
            )
            """)

    _add_column_if_missing(c, "challenges", "path_id", "path_id INTEGER")
    _add_column_if_missing(
        c,
        "challenges",
        "difficulty",
        "difficulty TEXT DEFAULT 'beginner'",
    )
    _add_column_if_missing(c, "challenges", "stage", "stage INTEGER DEFAULT 1")
    _add_column_if_missing(c, "challenges", "estimated_days", "estimated_days INTEGER")
    _add_column_if_missing(c, "challenges", "ringo_intro", "ringo_intro TEXT")

    c.execute("CREATE INDEX IF NOT EXISTS idx_challenges_path_status ON challenges(path_id, status)")

    c.execute("""
    CREATE TABLE IF NOT EXISTS paths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        description TEXT,
        icon TEXT,
        color TEXT,
        sort_order INTEGER NOT NULL DEFAULT 0,
        status TEXT CHECK(status IN ('Active', 'Archived')) DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenge_id INTEGER NOT NULL,
        key TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        mission_type TEXT CHECK(mission_type IN ('daily', 'weekly', 'one_time', 'bonus')) DEFAULT 'daily',
        difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')) DEFAULT 'easy',
        is_core INTEGER NOT NULL DEFAULT 1,
        xp_reward INTEGER NOT NULL DEFAULT 0,
        order_index INTEGER NOT NULL DEFAULT 0,
        suggested_time TEXT,
        unlock_after_days INTEGER NOT NULL DEFAULT 0,
        ringo_message TEXT,
        status TEXT CHECK(status IN ('Active', 'Archived')) DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(challenge_id, key),
        FOREIGN KEY(challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS mission_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        enrollment_id INTEGER NOT NULL,
        challenge_id INTEGER NOT NULL,
        mission_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT CHECK(status IN ('pending', 'done', 'skipped', 'remind_later')) DEFAULT 'pending',
        reminder_at TEXT,
        notes TEXT,
        xp_earned INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT,
        UNIQUE(user_id, mission_id, date),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
        FOREIGN KEY(challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
        FOREIGN KEY(mission_id) REFERENCES missions(id) ON DELETE CASCADE
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_paths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        path_id INTEGER NOT NULL,
        status TEXT CHECK(status IN ('Active', 'Paused', 'Completed', 'Left')) DEFAULT 'Active',
        current_stage INTEGER NOT NULL DEFAULT 1,
        started_at TEXT NOT NULL DEFAULT (datetime('now')),
        completed_at TEXT,
        updated_at TEXT,
        UNIQUE(user_id, path_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(path_id) REFERENCES paths(id) ON DELETE CASCADE
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_paths_status_sort ON paths(status, sort_order)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_missions_challenge_status ON missions(challenge_id, status, order_index)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_mission_logs_user_date ON mission_logs(user_id, date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_mission_logs_enrollment_date ON mission_logs(enrollment_id, date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_user_paths_user_status ON user_paths(user_id, status)")


    # در تابع init_db جدول enrollments رو به این صورت اصلاح کن:
    c.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('Active', 'Left')) DEFAULT 'Active',
            role TEXT DEFAULT 'Member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, challenge_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(challenge_id) REFERENCES challenges(id)
        )
        """)
    
    c.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_user_status ON enrollments(user_id, status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_challenge_status ON enrollments(challenge_id, status)")





    c.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        description TEXT,
        icon TEXT,
        category TEXT NOT NULL,
        condition_type TEXT NOT NULL,
        condition_value INTEGER NOT NULL,
        xp_reward INTEGER NOT NULL DEFAULT 0,
        rarity TEXT NOT NULL DEFAULT 'common',
        is_hidden INTEGER NOT NULL DEFAULT 0,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        achievement_id INTEGER NOT NULL,
        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, achievement_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON user_achievements(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_user_achievements_achievement ON user_achievements(achievement_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_achievements_category ON achievements(category)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_achievements_condition ON achievements(condition_type, condition_value)")

    c.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        challenge_id INTEGER NOT NULL,
        date TEXT NOT NULL,              -- YYYY-MM-DD (UTC)
        status TEXT DEFAULT 'Done',
        notes TEXT,
        source TEXT,
        is_counted INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT,
        UNIQUE(enrollment_id, date),
        FOREIGN KEY(enrollment_id) REFERENCES enrollments(id),
        FOREIGN KEY(challenge_id) REFERENCES challenges(id)
        );
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_checkins_user_date ON checkins(user_id, date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_checkins_enrollment_date ON checkins(enrollment_id, date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_checkins_challenge ON checkins(challenge_id)")

    c.execute("""
    CREATE TABLE IF NOT EXISTS telegram_connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        code TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'pending'
            CHECK(status IN ('pending', 'connected', 'expired', 'disconnected')),
        telegram_chat_id TEXT,
        telegram_username TEXT,
        reminders_enabled INTEGER NOT NULL DEFAULT 0,
        daily_checkin_enabled INTEGER NOT NULL DEFAULT 1,
        streak_risk_enabled INTEGER NOT NULL DEFAULT 1,
        weekly_summary_enabled INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        expires_at TEXT,
        connected_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_telegram_connections_user ON telegram_connections(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_telegram_connections_code ON telegram_connections(code)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_telegram_connections_status ON telegram_connections(status)")

    # Paths/Missions are now the canonical MVP seed. Keeping challenge-only
    # seed rows here creates stale unlinked challenges in fresh databases.
    ensure_mvp_paths_and_missions(conn)
    archive_legacy_unlinked_challenges(conn)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# ==================== USER OPERATIONS ====================

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, name, username, email, created_at FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, name, username, email, created_at FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, name, username, email, created_at FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_user_by_telegram_id(telegram_id):
    """Get user by Telegram ID"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, name, username, email FROM users WHERE telegram_id=?", (str(telegram_id),))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_user(username=None, password=None, name=None, email=None, telegram_id=None):
    """
    Create a new user. 
    For Telegram login: provide telegram_id
    For password login: provide username, password, and optionally name/email
    """
    if not username and not telegram_id:
        raise ValueError("Either username or telegram_id must be provided")
    
    pwd_hash = None
    if password:
        pwd_hash = generate_password_hash(password)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute(
            """INSERT INTO users 
               (telegram_id, username, password_hash, name, email, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
            (str(telegram_id) if telegram_id else None, username, pwd_hash, name, email)
        )
        conn.commit()
        user_id = c.lastrowid
        
        # Create user_stats entry (WITHOUT created_at, it doesn't exist in schema)
        c.execute(
            """INSERT INTO user_stats (user_id, updated_at) 
               VALUES (?, CURRENT_TIMESTAMP)""",
            (user_id,)
        )
        conn.commit()
        
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        raise ValueError(f"User already exists: {str(e)}")

def verify_password(username, password):
    """Verify user password. Returns user dict if valid, None otherwise"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, name, email FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row and row['password_hash']:
        if check_password_hash(row['password_hash'], password):
            return dict(row)
    return None

def update_user(user_id, name=None, email=None):
    """Update user information"""
    conn = get_db_connection()
    c = conn.cursor()
    
    if name:
        c.execute("UPDATE users SET name=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (name, user_id))
    if email:
        c.execute("UPDATE users SET email=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (email, user_id))
    
    conn.commit()
    conn.close()

def update_user_stats(user_id, total_checkins=None, current_streak=None, longest_streak=None, total_points=None):
    """Update user stats"""
    conn = get_db_connection()
    c = conn.cursor()
    
    updates = []
    params = []
    
    if total_checkins is not None:
        updates.append("total_checkins=?")
        params.append(total_checkins)
    if current_streak is not None:
        updates.append("current_streak=?")
        params.append(current_streak)
    if longest_streak is not None:
        updates.append("longest_streak=?")
        params.append(longest_streak)
    if total_points is not None:
        updates.append("total_points=?")
        params.append(total_points)
    
    if updates:
        updates.append("updated_at=CURRENT_TIMESTAMP")
        params.append(user_id)
        query = f"UPDATE user_stats SET {', '.join(updates)} WHERE user_id=?"
        c.execute(query, params)
        conn.commit()
    
    conn.close()

def get_user_stats(user_id):
    """Get user stats"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

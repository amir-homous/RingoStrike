import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone,timedelta

DB_NAME = os.getenv("DB_PATH", "users.db")

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all necessary tables"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table with both Telegram and local auth support
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  telegram_id TEXT UNIQUE, 
                  username TEXT UNIQUE, 
                  password_hash TEXT, 
                  name TEXT,
                  email TEXT UNIQUE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Sessions table for token management
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  token TEXT UNIQUE NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  expires_at TIMESTAMP NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    
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


#     # این تابع رو اضافه کن تا توی app.py استفاده کنی
# def get_user_challenges(user_id):
#     conn = get_db_connection()
#     conn.row_factory = sqlite3.Row
#     cur = conn.cursor()
#     cur.execute('''SELECT e.id as enrollment_id, c.id as challenge_id, c.name as challenge_name, e.status 
#                    FROM enrollments e 
#                    JOIN challenges c ON e.challenge_id = c.id 
#                    WHERE e.user_id = ?''', (user_id,))
#     rows = cur.fetchall()
#     conn.close()
#     return rows
def get_user_challenges(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT e.id as enrollment_id, c.id as challenge_id, c.name as challenge_name, e.status
        FROM enrollments e
        JOIN challenges c ON e.challenge_id = c.id
        WHERE e.user_id = ?
    ''', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# # این تابع رو برای روتِ /me/challenges استفاده کن
# def get_user_enrollments(user_id):
#     conn = get_db_connection()
#     # کوئری مشابه ساختار Notion برای برگردوندن آبجکت‌های مورد نیاز فرانت‌اند
#     rows = conn.execute('''SELECT e.id as enrollment_id, c.id as challenge_id, c.name as challenge_name, e.status 
#                            FROM enrollments e JOIN challenges c ON e.challenge_id = c.id 
#                            WHERE e.user_id = ? AND e.status = 'Active' ''', (user_id,)).fetchall()
#     conn.close()
#     return rows

def get_user_enrollments(user_id):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT e.id as enrollment_id, c.id as challenge_id, c.name as challenge_name, e.status
        FROM enrollments e
        JOIN challenges c ON e.challenge_id = c.id
        WHERE e.user_id = ? AND e.status = 'Active'
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_db_conn():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    return conn

# یک تابع جدید برای ثبت Checkin مطمئن
def add_checkin(enrollment_id, user_id, challenge_id, date, notes=None):
    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO checkins (enrollment_id, user_id, challenge_id, date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (enrollment_id, user_id, challenge_id, date, notes))
        conn.commit()
        # بعد از ثبت، باید stats کاربر آپدیت بشه
        update_user_stats_after_checkin(user_id)
        return True
    except sqlite3.IntegrityError:
        return False # یعنی قبلاً ثبت شده
    finally:
        conn.close()

def get_leaderboard(challenge_id):
    conn = get_db_connection()
    query = """
    SELECT
        u.id AS user_id,
        u.name,
        u.username,
        us.current_streak,
        us.longest_streak,
        us.total_checkins,
        us.total_points
    FROM enrollments e
    JOIN users u ON u.id = e.user_id
    LEFT JOIN user_stats us ON us.user_id = u.id
    WHERE e.challenge_id = ?
      AND e.status = 'Active'
    ORDER BY us.total_points DESC, us.current_streak DESC, us.total_checkins DESC, u.name ASC
    """
    rows = conn.execute(query, (challenge_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

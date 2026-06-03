# RingoStrike - Database Schema

## Source Of Truth

The schema is initialized in `backend/database.py` by `init_db()`.

Database engine: SQLite.

Default path behavior:

- If `DB_PATH` is provided, that value is used.
- If `DB_PATH` is not provided, SQLite uses `backend/users.db`, resolved relative to `backend/database.py`.

Every connection created by `get_db_connection()` enables SQLite foreign key enforcement with:

```sql
PRAGMA foreign_keys = ON

Local database files such as *.db, *.sqlite, and *.sqlite3 are ignored by Git and should not be committed.

Tables
Table	Purpose
users	Account identity, auth identity, and profile fields
user_stats	Cached stats derived from check-ins
challenges	Challenge definitions
enrollments	User participation in challenges
achievements	Achievement definitions
user_achievements	User achievement unlocks
checkins	Daily completion records
users
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  telegram_id TEXT UNIQUE,
  username TEXT UNIQUE,
  password_hash TEXT,
  name TEXT,
  email TEXT UNIQUE,
  avatar_url TEXT,
  bio TEXT DEFAULT '',
  profile_visibility TEXT DEFAULT 'public',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

Runtime migrations in init_db() add these columns if they are missing from older local databases:

avatar_url
bio
profile_visibility

Used by auth, profile, public profile, leaderboard, challenge member previews, and dashboard identity.

user_stats
CREATE TABLE IF NOT EXISTS user_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  total_checkins INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  total_points INTEGER DEFAULT 0,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)

stats_service.build_user_stats_payload() recalculates this table from checkins using INSERT ... ON CONFLICT(user_id) DO UPDATE.

Important:

checkins are the source of truth for check-in count and streaks.
user_stats is a cached aggregate table.
total_points currently reflects base XP derived from counted check-ins in the stats sync flow.
challenges
CREATE TABLE IF NOT EXISTS challenges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  visibility TEXT CHECK(visibility IN ('Public', 'Invite-only', 'Private')) DEFAULT 'Public',
  status TEXT CHECK(status IN ('Active', 'Archived')) DEFAULT 'Active',
  duration_days INTEGER,
  join_code TEXT,
  max_members INTEGER DEFAULT 0,
  requires_proof INTEGER DEFAULT 0,
  checkin_method TEXT DEFAULT 'Manual',
  goal_type TEXT,
  tags TEXT
)

Visibility and join behavior:

Public: join without code.
Invite-only: requires matching join_code if configured.
Private: join endpoint returns challenge_private.
enrollments
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

Enrollments link users to challenges and are used by dashboard, challenge detail, leaderboard, history, and check-in routes.

Indexes:

idx_enrollments_user_status on (user_id, status)
idx_enrollments_challenge_status on (challenge_id, status)
achievements
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

Seeded and updated by achievement_service.ensure_achievement_definitions().

Current condition types include:

total_checkins
active_challenge_checkins
streak
total_xp

Indexes:

idx_achievements_category on (category)
idx_achievements_condition on (condition_type, condition_value)
user_achievements
CREATE TABLE IF NOT EXISTS user_achievements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  achievement_id INTEGER NOT NULL,
  unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, achievement_id),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
)

Indexes:

idx_user_achievements_user on (user_id)
idx_user_achievements_achievement on (achievement_id)
checkins
CREATE TABLE IF NOT EXISTS checkins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  challenge_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  status TEXT DEFAULT 'Done',
  notes TEXT,
  source TEXT,
  is_counted INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  UNIQUE(enrollment_id, date),
  FOREIGN KEY(enrollment_id) REFERENCES enrollments(id),
  FOREIGN KEY(challenge_id) REFERENCES challenges(id)
)

date is expected as YYYY-MM-DD UTC from utils.date_utils.utc_today_iso().

Indexes:

idx_checkins_user_date on (user_id, date)
idx_checkins_enrollment_date on (enrollment_id, date)
idx_checkins_challenge on (challenge_id)
telegram_connections
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

Stores Telegram reminder connection state and user reminder preferences. The connect flow uses short-lived codes generated by authenticated users and redeemed by a bot-side bridge endpoint. `telegram_chat_id` is never collected by the frontend and is mirrored to `users.telegram_id` only for legacy compatibility.

Indexes:

idx_telegram_connections_user on (user_id)
idx_telegram_connections_code on (code)
idx_telegram_connections_status on (status)
Derived Logic
total_checkins: count of checkins where user_id = ? and status = 'Done'.
Base XP: total_checkins * 10 in stats_service.XP_PER_CHECKIN.
Current streak: consecutive dates anchored on today or yesterday.
Longest streak: longest consecutive date run.
Level: calculated from XP through stats_service.calculate_level().
Next level XP: calculated through stats_service.calculate_next_level_xp().
Progress percent: calculated through stats_service.calculate_progress_percent().
Current Auth Storage Model

The active auth flow uses stateless JWT tokens through:

HttpOnly auth cookie
Bearer token fallback

The old sessions table is no longer initialized by init_db().

Existing local databases may still contain an old sessions table from previous versions, but it is not part of the current active schema.

Schema Gaps And Risks
checkins.user_id has no foreign key in the current DDL, while enrollment_id and challenge_id do.
updated_at on checkins is not automatically maintained.
Existing local databases may still contain old tables such as sessions; init_db() no longer creates them.
There is no migrations framework; schema changes are embedded in init_db() and service helpers.
Runtime ALTER TABLE migrations are useful for local stabilization but should eventually be replaced by explicit migrations before production scale.
Future Migration Notes

Before launch or multi-user production growth, the project should add a real migration strategy.

Recommended future direction:

Keep SQLite for local development and early MVP stabilization.
Add explicit schema migration files before public launch.
Prepare PostgreSQL migration path before serious multi-user scale.
Avoid adding more ad hoc schema changes directly inside service functions.

بعدش تست:

```bash

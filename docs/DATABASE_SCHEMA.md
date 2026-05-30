# RingoStrike - Database Schema

## Source Of Truth

The schema is initialized in `backend/database.py` by `init_db()`. Services also perform a small runtime migration for `users.avatar_url` in `profile_service.py`.

Database engine: SQLite.

Default path: `DB_PATH` environment variable or `users.db` relative to the backend process working directory.

## Tables

| Table | Purpose |
| --- | --- |
| `users` | Account identity, auth identity, profile fields |
| `sessions` | Session-token table, currently not used by active JWT auth flow |
| `user_stats` | Cached stats derived from check-ins and achievement rewards |
| `challenges` | Challenge definitions |
| `enrollments` | User participation in challenges |
| `achievements` | Achievement definitions |
| `user_achievements` | User achievement unlocks |
| `checkins` | Daily completion records |

## `users`

```sql
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
```

Migrations add `avatar_url`, `bio`, and `profile_visibility` if missing.

Used by auth, profile, public profile, leaderboard, challenge member previews, and dashboard identity.

## `sessions`

```sql
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  token TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

Current status: present but not written by the active auth implementation. Auth uses JWT cookie/Bearer tokens.

## `user_stats`

```sql
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
```

`stats_service.build_user_stats_payload()` recalculates this table from `checkins` using `INSERT ... ON CONFLICT(user_id) DO UPDATE`.

Important: `checkins` are the source of truth for check-in count and streaks. `user_stats` is a cache plus current XP value after achievement rewards.

## `challenges`

```sql
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
```

Visibility and join behavior:

- `Public`: join without code.
- `Invite-only`: requires matching `join_code` if configured.
- `Private`: join endpoint returns `challenge_private`.

## `enrollments`

```sql
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
```

Enrollments link users to challenges and are used by dashboard, challenge detail, leaderboard, history, and check-in routes.

## `achievements`

```sql
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
```

Seeded/updated by `achievement_service.ensure_achievement_definitions()`.

Current condition types include `total_checkins`, `active_challenge_checkins`, `streak`, and `total_xp`.

## `user_achievements`

```sql
CREATE TABLE IF NOT EXISTS user_achievements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  achievement_id INTEGER NOT NULL,
  unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, achievement_id),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
)
```

Indexes:

- `idx_user_achievements_user`
- `idx_user_achievements_achievement`
- `idx_achievements_category`
- `idx_achievements_condition`

## `checkins`

```sql
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
```

`date` is expected as `YYYY-MM-DD` UTC from `utils.date_utils.utc_today_iso()`.

## Derived Logic

- `total_checkins`: count of `checkins` where `user_id = ?` and `status = 'Done'`.
- Base XP: `total_checkins * 10` in `stats_service.XP_PER_CHECKIN`.
- Achievement reward XP: added to `user_stats.total_points` after unlock, then stats are synced again by check-in flow. The exact persistence behavior should be reviewed because stats sync recalculates base points from check-ins.
- Current streak: consecutive dates anchored on today or yesterday.
- Longest streak: longest consecutive date run.

## Schema Gaps And Risks

- `sessions` is unused by the active auth flow.
- `checkins.user_id` has no foreign key in the current DDL, while `enrollment_id` and `challenge_id` do.
- `updated_at` on `checkins` is not automatically maintained.
- No indexes are defined on `checkins.user_id`, `checkins.enrollment_id`, `checkins.challenge_id`, or `checkins.date`, which are frequently queried.
- There is no migrations framework; schema changes are embedded in `init_db()` and service helpers.

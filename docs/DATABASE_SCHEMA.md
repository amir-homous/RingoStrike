# RingoStrike - Database Schema

## Source Of Truth

The schema is initialized in `backend/database.py` by `init_db()`.

Database engine: SQLite.

Default database path:

- `DB_PATH` is used when provided.
- Otherwise SQLite uses `backend/users.db`, resolved relative to `backend/database.py`.

Every connection created by `get_db_connection()` enables:

```sql
PRAGMA foreign_keys = ON;
```

Local database files such as `*.db`, `*.sqlite`, and `*.sqlite3` are ignored by Git and should not be committed.

## Table Summary

| Table | Purpose |
| --- | --- |
| `users` | Account identity, auth identity, and profile fields. |
| `user_stats` | Cached stats derived from counted check-ins and achievement XP. |
| `challenges` | Challenge definitions, now optionally linked to growth paths. |
| `paths` | Growth path definitions seeded for the guided mission experience. |
| `user_paths` | User path state, stage, and active/completed status. |
| `missions` | Path/challenge mission definitions. |
| `mission_logs` | Per-user daily mission status, reminder state, and mission XP display value. |
| `enrollments` | User participation in challenges. |
| `checkins` | Daily completion records. |
| `achievements` | Achievement definitions. |
| `user_achievements` | User achievement unlocks. |
| `telegram_connections` | Telegram reminder connection and preference state. |

## Guided Path/Mission Diagram

```txt
users
  -> user_paths -> paths
  -> enrollments -> challenges -> missions
  -> mission_logs
  -> checkins -> user_stats -> achievements/user_achievements
```

Mission completion writes `mission_logs` and then delegates to the existing check-in pipeline through `enrollment_service.checkin()`. `mission_logs.xp_earned` is mission display data; canonical progression XP still comes from stats/check-in/achievement services.

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
);
```

Runtime migrations add `avatar_url`, `bio`, and `profile_visibility` if missing from older local databases.

Used by auth, profile, public profile, leaderboard, challenge member previews, dashboard identity, and Telegram compatibility.

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
);
```

`checkins` are the source of truth. `user_stats` is a cached aggregate table refreshed by `stats_service.py`.

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
  tags TEXT,
  path_id INTEGER,
  difficulty TEXT DEFAULT 'beginner',
  stage INTEGER DEFAULT 1,
  estimated_days INTEGER,
  ringo_intro TEXT
);
```

`path_id`, `difficulty`, `stage`, `estimated_days`, and `ringo_intro` are runtime-added columns for the path/mission experience.

Indexes:

- `idx_challenges_path_status` on `(path_id, status)`

Visibility and join behavior:

- `Public`: join without code.
- `Invite-only`: requires matching `join_code` if configured.
- `Private`: join endpoint returns `challenge_private`.

## `paths`

```sql
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
);
```

Seeded by `services/path_seed_service.py`. Current MVP seed data includes movement, learning, career, social, creative, and recovery-oriented paths.

Indexes:

- `idx_paths_status_sort` on `(status, sort_order)`

## `user_paths`

```sql
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
);
```

Used by `/paths`, `/paths/:id/start`, and Ringo decision state.

Indexes:

- `idx_user_paths_user_status` on `(user_id, status)`

## `missions`

```sql
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
  mission_intensity TEXT CHECK(mission_intensity IN ('main', 'tiny', 'bonus')) DEFAULT 'main',
  estimated_minutes INTEGER,
  parent_mission_id INTEGER,
  ringo_message TEXT,
  status TEXT CHECK(status IN ('Active', 'Archived')) DEFAULT 'Active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(challenge_id, key),
  FOREIGN KEY(challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
  FOREIGN KEY(parent_mission_id) REFERENCES missions(id) ON DELETE SET NULL
);
```

Used by `/paths/:id/challenges` for mission previews and `/me/today-missions` for available daily missions. `unlock_after_days` is compared against days since enrollment join date.

`mission_intensity` supports `main`, `tiny`, and `bonus`. Existing rows default to `main`. `estimated_minutes` and `parent_mission_id` are optional metadata for lower-pressure tiny missions or bonus variants; they do not create a separate completion, XP, streak, or achievement system.

Indexes:

- `idx_missions_challenge_status` on `(challenge_id, status, order_index)`
- `idx_missions_intensity` on `(challenge_id, mission_intensity, status)`

## `mission_logs`

```sql
CREATE TABLE IF NOT EXISTS mission_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  enrollment_id INTEGER NOT NULL,
  challenge_id INTEGER NOT NULL,
  mission_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  status TEXT CHECK(status IN ('pending', 'done', 'skipped', 'remind_later')) DEFAULT 'pending',
  reminder_at TEXT,
  skip_reason TEXT,
  notes TEXT,
  xp_earned INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  UNIQUE(user_id, mission_id, date),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
  FOREIGN KEY(challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
  FOREIGN KEY(mission_id) REFERENCES missions(id) ON DELETE CASCADE
);
```

Status values:

- `pending`
- `done`
- `skipped`
- `remind_later`

`skip_reason` is optional metadata for skipped missions. Supported stable reason keys are `too_tired`, `no_time`, `too_hard`, `not_relevant`, `disliked`, and `other`. Skip reasons are future Ringo Brain context only; they do not affect XP, streak, achievements, or check-in logic.

Indexes:

- `idx_mission_logs_user_date` on `(user_id, date)`
- `idx_mission_logs_enrollment_date` on `(enrollment_id, date)`

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
);
```

Enrollments link users to challenges and are used by dashboard, MissionCenter, challenge detail, leaderboard, history, and check-in routes.

Indexes:

- `idx_enrollments_user_status` on `(user_id, status)`
- `idx_enrollments_challenge_status` on `(challenge_id, status)`

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
);
```

`date` is expected as `YYYY-MM-DD` UTC from `utils.date_utils.utc_today_iso()`.

Indexes:

- `idx_checkins_user_date` on `(user_id, date)`
- `idx_checkins_enrollment_date` on `(enrollment_id, date)`
- `idx_checkins_challenge` on `(challenge_id)`

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
);
```

Seeded and updated by `achievement_service.ensure_achievement_definitions()`.

Current condition types:

- `total_checkins`
- `active_challenge_checkins`
- `streak`
- `total_xp`

Indexes:

- `idx_achievements_category` on `(category)`
- `idx_achievements_condition` on `(condition_type, condition_value)`

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
);
```

Indexes:

- `idx_user_achievements_user` on `(user_id)`
- `idx_user_achievements_achievement` on `(achievement_id)`

## `telegram_connections`

```sql
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
);
```

Stores Telegram reminder connection state and user reminder preferences. The connect flow uses short-lived codes generated by authenticated users and redeemed by a bot-side bridge endpoint. `telegram_chat_id` is never collected by the frontend and is mirrored to `users.telegram_id` only for legacy compatibility.

Indexes:

- `idx_telegram_connections_user` on `(user_id)`
- `idx_telegram_connections_code` on `(code)`
- `idx_telegram_connections_status` on `(status)`

## Derived Logic

- `total_checkins`: count of counted check-ins with `status = 'Done'`.
- Base XP: `total_checkins * 10` in `stats_service.XP_PER_CHECKIN`.
- Achievement XP: included in persisted stats through the achievement/stats sync flow.
- Current streak: consecutive counted check-in dates anchored on today or yesterday.
- Longest streak: longest consecutive counted date run.
- Level, next-level XP, and progress percent: calculated in `stats_service.py`.
- Today's missions: active daily missions for active enrollments where `unlock_after_days` has elapsed since `enrollments.joined_at`.

## Seed And Migration Behavior

`init_db()` currently performs startup-time schema setup and lightweight migrations. It also calls:

- `ensure_mvp_paths_and_missions(conn)` to seed path/challenge/mission definitions.
- `archive_legacy_unlinked_challenges(conn)` to archive active challenges that are not linked to current seeded path/mission data.

This keeps local development databases moving, but it is not a replacement for a production migration system.

## Current Auth Storage Model

The active auth flow uses stateless JWT tokens through:

- HttpOnly auth cookie
- Bearer token fallback

The old `sessions` table is no longer initialized by `init_db()`. Existing local databases may still contain it, but it is not part of the current active schema.

## Schema Gaps And Risks

- There is no migrations framework; schema changes are embedded in `init_db()` and seed helpers.
- `checkins.user_id` has no foreign key in the current DDL, while `enrollment_id` and `challenge_id` do.
- `updated_at` is not automatically maintained on all tables.
- Mission XP and canonical progression XP are intentionally separate today, but this needs product clarity if mission-specific rewards later become independent of check-ins.
- Existing local databases may still contain old tables such as `sessions`.

## Future Migration Notes

Before launch or multi-user production growth, add an explicit migration strategy.

Recommended direction:

- Keep SQLite for local development and early MVP stabilization.
- Add explicit schema migration files before public launch.
- Prepare a PostgreSQL migration path before serious multi-user scale.
- Avoid adding more ad hoc schema changes directly inside service functions.

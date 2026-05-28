# RingoStrike — Database Schema

## Database Philosophy

RingoStrike uses a normalized, progression-oriented database architecture designed for:

* scalability
* future extensibility
* modular progression systems
* event-driven UX
* social progression evolution

The schema prioritizes:

* centralized progression logic
* normalized relationships
* future-safe extensibility
* migration safety
* emotional progression systems

The current database engine is:

* SQLite

However, the schema is intentionally designed to support future migration to:

* PostgreSQL
* MySQL
* managed cloud databases

with minimal architectural changes.

---

# Core Architecture Overview

The database currently contains systems for:

* authentication
* sessions
* progression tracking
* streak tracking
* challenge participation
* check-ins
* achievements
* profile identity
* activity generation foundations

---

# Table Overview

Current major tables:

| Table             | Purpose                          |
| ----------------- | -------------------------------- |
| users             | Core user identity               |
| sessions          | Auth/session management          |
| user_stats        | Cached progression aggregates    |
| challenges        | Challenge definitions            |
| enrollments       | User participation in challenges |
| checkins          | Daily progression actions        |
| achievements      | Achievement definitions          |
| user_achievements | User achievement unlocks         |

---

# USERS TABLE

## Purpose

Stores:

* account identity
* authentication identity
* future profile identity

Supports:

* local authentication
* Telegram authentication
* future OAuth/social auth systems

---

## Schema

```sql
users
```

| Column        | Type        | Description            |
| ------------- | ----------- | ---------------------- |
| id            | INTEGER PK  | Internal user ID       |
| telegram_id   | TEXT UNIQUE | Telegram auth identity |
| username      | TEXT UNIQUE | Public username        |
| password_hash | TEXT        | Hashed password        |
| name          | TEXT        | Display name           |
| email         | TEXT UNIQUE | User email             |
| created_at    | TIMESTAMP   | Account creation       |
| updated_at    | TIMESTAMP   | Last update            |

---

## Notes

This table intentionally separates:

* internal identity
* authentication systems
* public identity

Future-safe for:

* avatar systems
* profile customization
* public profile visibility
* social identity systems

---

# SESSIONS TABLE

## Purpose

Stores:

* authentication sessions
* token lifecycle management

Supports:

* persistent login
* future JWT refresh flows
* multi-device sessions

---

## Schema

```sql
sessions
```

| Column     | Type        | Description        |
| ---------- | ----------- | ------------------ |
| id         | INTEGER PK  | Session ID         |
| user_id    | INTEGER FK  | Owner user         |
| token      | TEXT UNIQUE | Session token      |
| created_at | TIMESTAMP   | Session creation   |
| expires_at | TIMESTAMP   | Session expiration |

---

## Relationships

```txt
sessions.user_id -> users.id
```

---

# USER_STATS TABLE

## Purpose

Stores cached progression aggregates for:

* fast dashboard rendering
* leaderboard queries
* progression summaries

This is a derived-state table.

It should NOT become the source of truth for progression history.

---

## Schema

```sql
user_stats
```

| Column         | Type              | Description                  |
| -------------- | ----------------- | ---------------------------- |
| id             | INTEGER PK        | Stats record                 |
| user_id        | INTEGER UNIQUE FK | User owner                   |
| total_checkins | INTEGER           | Lifetime completed check-ins |
| current_streak | INTEGER           | Current streak               |
| longest_streak | INTEGER           | Best streak                  |
| total_points   | INTEGER           | Current XP/points            |
| updated_at     | TIMESTAMP         | Last sync time               |

---

## Relationships

```txt
user_stats.user_id -> users.id
```

---

## Important Notes

This table acts as:

* progression cache
* dashboard optimization layer

The source of truth remains:

* checkins
* achievement unlocks
* future progression events

---

# CHALLENGES TABLE

## Purpose

Stores challenge definitions.

Challenges are:

* progression environments
* consistency spaces
* future social momentum hubs

---

## Schema

```sql
challenges
```

| Column         | Type       | Description                    |
| -------------- | ---------- | ------------------------------ |
| id             | INTEGER PK | Challenge ID                   |
| name           | TEXT       | Challenge title                |
| description    | TEXT       | Challenge details              |
| visibility     | TEXT       | Public / Invite-only / Private |
| status         | TEXT       | Active / Archived              |
| duration_days  | INTEGER    | Challenge duration             |
| join_code      | TEXT       | Invite system                  |
| max_members    | INTEGER    | Capacity                       |
| requires_proof | INTEGER    | Proof requirement              |
| checkin_method | TEXT       | Manual / Auto                  |
| goal_type      | TEXT       | Daily / Weekly                 |
| tags           | TEXT       | Comma-separated tags           |

---

## Design Philosophy

Challenges are intentionally future-safe for:

* public challenge discovery
* social participation
* seasonal systems
* challenge categories
* collaborative momentum

---

# ENROLLMENTS TABLE

## Purpose

Represents user participation in challenges.

Acts as:

* participation layer
* membership system
* progression ownership mapping

---

## Schema

```sql
enrollments
```

| Column       | Type       | Description   |
| ------------ | ---------- | ------------- |
| id           | INTEGER PK | Enrollment ID |
| user_id      | INTEGER FK | Participant   |
| challenge_id | INTEGER FK | Challenge     |
| status       | TEXT       | Active / Left |
| role         | TEXT       | Member role   |
| joined_at    | TIMESTAMP  | Join time     |

---

## Relationships

```txt
enrollments.user_id -> users.id
enrollments.challenge_id -> challenges.id
```

---

## Constraints

```sql
UNIQUE(user_id, challenge_id)
```

Prevents duplicate participation.

---

# CHECKINS TABLE

## Purpose

Core progression action system.

Every check-in represents:

* behavioral continuity
* progression reinforcement
* streak participation
* XP generation

This table is one of the most important systems in the platform.

---

## Schema

```sql
checkins
```

| Column        | Type       | Description           |
| ------------- | ---------- | --------------------- |
| id            | INTEGER PK | Check-in ID           |
| enrollment_id | INTEGER FK | Enrollment            |
| user_id       | INTEGER FK | Owner user            |
| challenge_id  | INTEGER FK | Challenge             |
| date          | TEXT       | YYYY-MM-DD            |
| status        | TEXT       | Done / future states  |
| notes         | TEXT       | Optional notes        |
| source        | TEXT       | Check-in source       |
| is_counted    | INTEGER    | Progression inclusion |
| created_at    | TEXT       | Creation time         |
| updated_at    | TEXT       | Last update           |

---

## Relationships

```txt
checkins.enrollment_id -> enrollments.id
checkins.user_id -> users.id
checkins.challenge_id -> challenges.id
```

---

## Constraints

```sql
UNIQUE(enrollment_id, date)
```

Prevents double check-ins for the same day.

---

## Future Direction

Future-safe for:

* proof systems
* AI validation
* media uploads
* check-in reactions
* social visibility
* smart reminders

---

# ACHIEVEMENTS TABLE

## Purpose

Stores achievement definitions.

Achievements are:

* progression milestones
* identity reinforcement systems
* emotional reward structures

---

## Schema

```sql
achievements
```

| Column          | Type        | Description           |
| --------------- | ----------- | --------------------- |
| id              | INTEGER PK  | Achievement ID        |
| key             | TEXT UNIQUE | Internal unique key   |
| title           | TEXT        | Achievement title     |
| description     | TEXT        | Achievement details   |
| icon            | TEXT        | Icon reference        |
| category        | TEXT        | Achievement category  |
| condition_type  | TEXT        | Unlock condition type |
| condition_value | INTEGER     | Unlock threshold      |
| xp_reward       | INTEGER     | XP reward             |
| rarity          | TEXT        | common/rare/etc       |
| is_hidden       | INTEGER     | Hidden achievement    |
| sort_order      | INTEGER     | UI ordering           |
| created_at      | TIMESTAMP   | Creation time         |

---

## Design Philosophy

Achievements are:

* emotionally meaningful
* identity reinforcing
* future social signals

NOT:

* collectible spam

---

# USER_ACHIEVEMENTS TABLE

## Purpose

Stores user achievement unlock history.

Represents:

* progression milestones
* identity progression memory
* future social progression visibility

---

## Schema

```sql
user_achievements
```

| Column         | Type       | Description |
| -------------- | ---------- | ----------- |
| id             | INTEGER PK | Unlock ID   |
| user_id        | INTEGER FK | Owner user  |
| achievement_id | INTEGER FK | Achievement |
| unlocked_at    | TIMESTAMP  | Unlock time |

---

## Relationships

```txt
user_achievements.user_id -> users.id
user_achievements.achievement_id -> achievements.id
```

---

## Constraints

```sql
UNIQUE(user_id, achievement_id)
```

Prevents duplicate unlocks.

---

# INDEXES

Current indexes:

```sql
idx_user_achievements_user
idx_user_achievements_achievement
idx_achievements_category
idx_achievements_condition
```

Purpose:

* faster achievement evaluation
* scalable unlock queries
* future leaderboard/social scaling

---

# Current Progression Flow

The current progression flow:

```txt
check-in
    ↓
stats sync
    ↓
achievement evaluation
    ↓
XP reward calculation
    ↓
timeline generation
    ↓
dashboard/profile rendering
```

This progression pipeline is intentionally centralized.

---

# Future Database Direction

The schema is intentionally preparing for future systems:

## Social Systems

Potential future tables:

* follows
* social_feed_events
* reactions
* comments
* profile_visibility

---

## AI Systems

Potential future tables:

* AI insights
* recommendation memory
* behavioral summaries
* streak risk analysis

---

## Seasonal Systems

Potential future tables:

* seasons
* seasonal_progress
* event_rewards

---

## Advanced Identity Systems

Potential future tables:

* titles
* cosmetics
* profile_themes
* prestige_levels

---

# Migration Philosophy

Future migrations should:

* preserve progression integrity
* avoid destructive rewrites
* keep event history safe
* maintain identity continuity

Progression data is emotionally valuable and should be treated carefully.

---

# Important Engineering Rules

## ALWAYS

* reuse centralized progression systems
* keep progression calculations consistent
* preserve normalized relationships
* design future-safe extensions
* maintain migration safety

---

## NEVER

* duplicate progression state
* duplicate streak calculations
* create disconnected event systems
* tightly couple frontend to schema
* bypass service-layer logic

---

# Final Database Goal

The database architecture should ultimately support:

* progression identity
* emotional continuity
* scalable social momentum
* AI-enhanced growth systems
* long-term behavioral visibility

while remaining:

* modular
* scalable
* maintainable
* future-safe

# RingoStrike - Frontend/API Contract

## API Client

Frontend API client: `frontend/src/lib/api.js`.

```js
baseURL = import.meta.env.VITE_API_BASE || "http://localhost:5005"
withCredentials = true
timeout = 15000
```

The backend supports HttpOnly cookie auth and Bearer token fallback. The frontend mainly relies on cookies because `withCredentials` is enabled.

Important mismatch: `frontend/src/stores/session.js` expects `api.setToken()`, but `lib/api.js` does not implement it.

## Auth Endpoints

### `POST /auth/register`

Auth: public.

Request:

```json
{
  "username": "player_name",
  "password": "secret123",
  "name": "Player Name",
  "email": "player@example.com"
}
```

Validation:

- username is normalized lowercase
- username must be 3-24 chars, `a-z`, `0-9`, underscore only
- reserved usernames are rejected
- password must be at least 6 chars
- email must contain `@` if provided

Success `201`:

```json
{
  "ok": true,
  "user_id": 1,
  "username": "player_name",
  "access_token": "jwt"
}
```

Also sets HttpOnly auth cookie.

### `POST /auth/login`

Auth: public.

Request:

```json
{
  "username": "player_name",
  "password": "secret123"
}
```

Success `200`: same shape as register and sets cookie.

### `POST /auth/logout`

Auth: public in route code; clears auth cookie.

Success:

```json
{ "ok": true }
```

### `GET /me`

Auth: required.

Local-auth success:

```json
{
  "ok": true,
  "user_id": 1,
  "username": "player_name",
  "name": "Player Name",
  "email": "player@example.com",
  "auth_method": "local",
  "registered": true
}
```

Telegram-shaped response exists in code for Telegram claims, but no active Telegram login route is registered.

## Health

### `GET /health`

Auth: public.

```json
{ "ok": true }
```

## Challenges

### `GET /challenges/public`

Auth: public.

Returns active public challenges:

```json
{
  "ok": true,
  "items": [
    {
      "challenge_id": 1,
      "name": "Challenge",
      "visibility": "Public",
      "status": "Active",
      "description": "...",
      "duration_days": 30
    }
  ]
}
```

### `GET /challenges`

Auth: required.

Returns active public/invite-only challenges plus joined private challenges visible to the user.

Item shape:

```json
{
  "challenge_id": 1,
  "name": "Challenge",
  "description": "...",
  "visibility": "public",
  "status": "active",
  "duration_days": 30,
  "members_count": 3,
  "members_preview": ["Alice"],
  "is_joined": true,
  "enrollment_id": 10,
  "needs_code": false
}
```

### `GET /challenges/:challenge_id`

Auth: public in route code.

Returns challenge details including visibility, status, duration, max members, proof flag, check-in method, goal type, tags, member count, and whether a join code is required.

### `GET /challenges/:challenge_id/members?limit=20&offset=0`

Auth: public in route code.

Returns active member rows:

```json
{
  "ok": true,
  "challenge_id": 1,
  "items": [
    {
      "enrollment_id": 10,
      "enrollment_status": "Active",
      "role": "Member",
      "user_id": 1,
      "user_name": "Alice",
      "telegram_username": "alice"
    }
  ],
  "has_more": false
}
```

### `POST /challenges/:challenge_id/join`

Auth: required.

Request:

```json
{ "join_code": "optional" }
```

Success:

```json
{
  "ok": true,
  "mode": "created",
  "enrollment_id": 10,
  "challenge_id": 1
}
```

`mode` can be `created`, `reactivated`, or `existing`.

## Enrollment, Check-ins, History, Leaderboard

### `GET /me/challenges`

Auth: required.

Dashboard challenge list response:

```json
{
  "ok": true,
  "date": "2026-05-30",
  "user": {
    "name": "Alice",
    "stats": {
      "total_points": 100,
      "current_streak": 3,
      "longest_streak": 7
    }
  },
  "challenges": [
    {
      "enrollment_id": 10,
      "enrollment_name": "Challenge",
      "status": "Active",
      "challenge_id": 1,
      "today_checked": false
    }
  ]
}
```

### `GET /me/enrollments/:enrollment_id`

Auth: required.

Returns enrollment summary, challenge details, recent logs, `today_checked`, `total_checkins`, and `current_streak`.

### `POST /me/challenges/:enrollment_id/checkin`

Auth: required.

Creates or updates today's check-in for the enrollment.

Success:

```json
{
  "ok": true,
  "message": "Check-in recorded",
  "rewards": {
    "xp_total": 100,
    "achievements": [],
    "achievement_xp_reward": 0
  }
}
```

### `GET /me/challenges/:enrollment_id/history?days=30`

Auth: required.

Returns up to 120 days of per-day status.

### `GET /me/enrollments/:enrollment_id/leaderboard`

Auth: required.

Returns leaderboard for the challenge connected to the enrollment:

```json
{
  "ok": true,
  "overall": [
    {
      "name": "Alice",
      "username": "alice",
      "enrollment_id": 10,
      "total_checkins": 12,
      "current_streak": 4
    }
  ],
  "today": []
}
```

## Stats, Activity, Achievements, Profile

### `GET /me/stats`

Auth: required.

Effective route is currently `dashboard_routes.py` because another duplicate route exists in `stats_routes.py`.

Response:

```json
{
  "ok": true,
  "stats": {
    "current_streak": 3,
    "level": 2,
    "longest_streak": 7,
    "next_level_xp": 200,
    "progress_percent": 20,
    "total_checkins": 12,
    "total_points": 120,
    "xp": 20
  },
  "user": { "id": 1, "name": "Alice" }
}
```

### `GET /me/activity`

Auth: required.

Returns derived events with types such as `checkin`, `streak`, `level_up`, and `achievement`.

### `GET /me/achievements`

Auth: required.

Returns all achievement definitions with `unlocked` and `unlocked_at` fields.

### `GET /me/profile`

Auth: required.

Returns private profile aggregate:

```json
{
  "ok": true,
  "profile": {
    "id": 1,
    "name": "Alice",
    "username": "alice",
    "avatar_url": "/avatars/avatar-1.png",
    "bio": "...",
    "joined_date": "2026-05-30",
    "profile_visibility": "public",
    "title": { "key": "beginner", "label": "Beginner" },
    "tagline": "Building consistency one strike at a time.",
    "stats": {}
  }
}
```

### `GET /me/consistency`

Auth: required.

Returns `days` as `{ date, count }` rows for the recent heatmap window.

## Profile Settings And Public Profile

### `GET /api/me/profile/settings`

Auth: required.

Returns `avatar_url`, `bio`, and `profile_visibility`.

### `PATCH /api/me/profile/settings`

Auth: required.

Request:

```json
{
  "avatar_url": "/avatars/avatar-1.png",
  "bio": "Short bio",
  "profile_visibility": "public"
}
```

Visibility values: `public`, `private`.

### `PATCH /api/profile/visibility`

Auth: required.

Request:

```json
{ "visibility": "private" }
```

### `PATCH /api/profile`

Auth: required.

Request fields: `name`, `bio`, `avatar_url`.

### `GET /api/public/profile/:username`

Auth: public.

Returns public-safe profile aggregate if `profile_visibility = 'public'`; otherwise `403 profile_private`.

### `GET /api/public/profile/:username/consistency`

Auth: public. Returns recent counted check-in dates for public profiles.

### `GET /api/public/profile/:username/achievements`

Auth: public. Returns up to 6 unlocked achievements for public profiles.

## Debug Endpoints

### `GET /debug/sqlite/schema/:table`

Auth: public in current code. Allowed tables: `users`, `challenges`, `enrollments`, `checkins`, `user_stats`, `sessions`.

### `GET /debug/sqlite/counts`

Auth: public in current code. Returns counts for users, challenges, enrollments, checkins, and user_stats.

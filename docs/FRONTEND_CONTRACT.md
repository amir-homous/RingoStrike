# RingoStrike - Frontend/API Contract

## API Client

Frontend API client: `frontend/src/lib/api.js`.

```js
baseURL = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? "http://localhost:5005" : "")
withCredentials = true
timeout = 15000
```

Production builds default to same-origin relative API requests when `VITE_API_BASE` is unset. Local development can still set `VITE_API_BASE=http://localhost:5005`. If a production build accidentally contains a loopback API base such as `http://localhost:5005` or `http://127.0.0.1:5005`, the client falls back to same-origin because browser loopback would point at the user's machine, not the VPS.

For the current VPS deployment at `http://82.115.24.10`, set:

```env
VITE_API_BASE=/api-proxy
VITE_BASE=/
```

Nginx should proxy `/api-proxy/` to Flask and rewrite the prefix away:

```nginx
location /api-proxy/ {
    rewrite ^/api-proxy/(.*)$ /$1 break;
    proxy_pass http://127.0.0.1:5005;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Vue routes should continue to use the SPA fallback:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

Only omit `VITE_API_BASE` when backend root routes do not conflict with frontend routes. This VPS requires `/api-proxy` because `/challenges` is both a frontend route and a backend API route; proxying `/challenges` directly returns backend JSON instead of the Vue page.

The backend supports HttpOnly cookie auth and Bearer token fallback. The frontend mainly relies on cookies because `withCredentials` is enabled.

`frontend/src/stores/session.js` is aligned with this cookie-based model and uses `/me` plus `/auth/logout`; it does not require `api.setToken()`.

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

### `GET /health/config`

Auth: public.

Returns a safe production-readiness snapshot with boolean/configuration flags. It must not expose secrets, tokens, full database paths, or integration credentials.

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
      "username": "alice",
      "telegram_username": "alice"
    }
  ],
  "has_more": false
}
```

`username` is the canonical local/public username. `telegram_username` is kept as a backward-compatible alias for older frontend/API consumers.

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

Frontend join UX currently consumes this same response to show JoinSuccessMoment before routing users to the dashboard or enrollment detail. Do not add a separate onboarding/recommendation endpoint for the v1 guided start flow; onboarding and challenge discovery both reuse this join contract.

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

Creates or updates today's check-in for an active enrollment.

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

Inactive enrollment error `403`:

```json
{ "ok": false, "error": "enrollment_inactive" }
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

Owned by `stats_routes.py` and generated through `stats_service.build_user_stats_payload()`.

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

## Telegram Reminder Settings

The frontend does not use Telegram Login and never sends or stores a bot token.

### `GET /api/me/telegram/settings`

Auth: required.

Returns:

```json
{
  "ok": true,
  "settings": {
    "connected": true,
    "telegram_username": "alice",
    "reminders_enabled": true,
    "daily_checkin_enabled": true,
    "streak_risk_enabled": true,
    "weekly_summary_enabled": false,
    "bot_username": "ringo_strike_bot",
    "bot_link": "https://t.me/ringo_strike_bot"
  }
}
```

### `POST /api/me/telegram/connect-code`

Auth: required.

Returns a short-lived code and optional bot deep link. A new pending code expires previous pending codes for the same user.

### `PATCH /api/me/telegram/settings`

Auth: required.

Request fields:

```json
{
  "reminders_enabled": true,
  "daily_checkin_enabled": true,
  "streak_risk_enabled": true,
  "weekly_summary_enabled": false
}
```

### `POST /api/me/telegram/disconnect`

Auth: required. Disconnects the user's Telegram chat and returns the updated settings.

### `POST /api/telegram/connect`

Auth: protected by `X-Reminder-Token`; intended for a bot-side bridge, n8n, or similar automation. The frontend must not call this endpoint.

Request:

```json
{
  "code": "RS-ABCDEFGH",
  "telegram_chat_id": "123456789",
  "telegram_username": "alice"
}
```

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

Auth: development-only endpoint. Outside development mode, returns `403 debug_disabled`.

Allowed tables: `users`, `challenges`, `enrollments`, `checkins`, `user_stats`.

### `GET /debug/sqlite/counts`

Auth: development-only endpoint. Outside development mode, returns `403 debug_disabled`.

Returns counts for users, challenges, enrollments, checkins, and user_stats.

# RingoStrike - Architecture

## Overview

RingoStrike is a two-tier web application:

```txt
Browser / Vue 3 SPA
  -> Axios API client with credentials
  -> Flask API on localhost:5005
  -> Service layer
  -> SQLite database
```

The codebase is organized around a modular Flask backend and component-driven Vue frontend.

## Repository Structure

```txt
backend/
  app.py
  auth.py
  auth_telegram.py
  config.py
  database.py
  routes/
  services/
  utils/
frontend/
  src/
    components/
    i18n/
    lib/api.js
    router/index.js
    stores/session.js
    styles/
    views/
docs/
```

Generated/dependency directories such as `backend/venv`, `backend/.venv`, `frontend/node_modules`, `__pycache__`, and the local SQLite file are not architecture source.

## Backend Runtime

`backend/app.py` creates the Flask application, loads config, enables credentialed CORS for local frontend origins plus env-driven `CORS_ORIGINS` / `FRONTEND_ORIGIN` / `FRONTEND_BASE_URL`, initializes SQLite tables, registers auth routes, registers blueprints, and exposes `/health`.

When run directly, `backend/app.py` reads runtime binding from:

- `FLASK_HOST` (default `127.0.0.1`)
- `PORT` (default `5005`)
- `FLASK_DEBUG` (`1` enables Flask debug/reloader)

The current VPS production-like runtime uses `systemd` service `ringostrike-backend`, working directory `/home/ringo/RingoStrike/backend`, virtualenv `/home/ringo/RingoStrike/backend/venv`, and:

```env
FLASK_HOST=127.0.0.1
PORT=5005
FLASK_DEBUG=0
```

Public access to the backend is through nginx `/api-proxy`, not a public Flask bind.

Registered route sources:

- `backend/auth.py` through `routes/auth_routes.py`
- `routes/challenge_routes.py`
- `routes/dashboard_routes.py`
- `routes/enrollment_routes.py`
- `routes/leaderboard_routes.py`
- `routes/history_routes.py`
- `routes/debug_routes.py`
- `routes/stats_routes.py`
- `routes/public_profile_routes.py`
- `routes/profile_settings_routes.py`
- `routes/telegram_routes.py`
- `routes/path_routes.py`
- `routes/mission_routes.py`
- `routes/health_routes.py`

## Backend Layering

```txt
Flask routes
  -> auth decorator / request validation
  -> service functions
  -> database helpers / SQLite queries
  -> JSON responses
```

Routes are mostly thin and defer to services. The main exception is `backend/auth.py`, which defines route handlers and auth utility logic in one file.

## Service Boundaries

- `challenge_service.py`: challenge discovery, detail, members, join, and enrollment detail.
- `enrollment_service.py`: daily check-in writes, stats sync, achievement evaluation.
- `path_seed_service.py`: seeded MVP growth paths, path-linked challenge definitions, mission definitions, and archiving of legacy unlinked active challenges.
- `path_service.py`: path listing, path challenge/missions projection, user path start/reactivation.
- `mission_service.py`: today's mission list, mission logs, remind-later/skip state, and mission completion through the existing check-in pipeline.
- `ringo_decision_service.py`: RingoCoach state, sprite key, message, and action decision from active path/enrollment/mission/stats context.
- `ringo_brain_service.py`: Ringo Brain v1 guidance contract for `/me/ringo/today`, using existing mission/path/stats data without owning mission completion or progression writes.
- `stats_service.py`: XP, level, streak, progress calculations, `user_stats` synchronization.
- `achievement_service.py`: achievement definition seeding, unlock evaluation, achievement list.
- `activity_service.py`: derived activity feed from check-ins, streaks, levels, achievements.
- `dashboard_service.py`: `/me`, dashboard challenges, dashboard stats.
- `profile_service.py`: private profile aggregation and title evaluation.
- `public_profile_service.py`: public profile aggregation with visibility checks.
- `public_activity_service.py`: public-safe activity projection.
- `public_consistency_service.py`: public consistency dates with visibility checks.
- `public_achievement_service.py`: public unlocked achievements with visibility checks.
- `profile_settings_service.py`: avatar, bio, and visibility settings.
- `profile_update_service.py`: name, bio, avatar update.
- `profile_visibility_service.py`: direct visibility update.
- `leaderboard_service.py`: leaderboard per enrollment/challenge.
- `history_service.py`: enrollment check-in history.
- `debug_service.py`: SQLite schema/count debug responses.
- `username_service.py`: username normalization and reserved-name validation.
- `telegram_connection_service.py`: Telegram connect codes, connected chat state, and reminder preference settings.
- `telegram_service.py`: shared Telegram Bot API message sender.
- `reminder_service.py`: unchecked enrollment reminders, due mission-level Telegram reminder selection/delivery, duplicate-prevention marking, and protected reminder diagnostics.

## Text Architecture Diagram

```txt
Vue views
  Dashboard/Paths/Challenges/Enrollment/Profile/PublicProfile
      |
      v
frontend/src/lib/api.js
      |
      v
Flask app.py + route modules
      |
      v
Service layer
  paths -> missions -> ringo decision
  stats -> achievements -> activity -> profile
  challenge -> enrollment -> history -> leaderboard
      |
      v
SQLite tables
  users, user_stats, challenges, enrollments,
  checkins, paths, user_paths, missions, mission_logs,
  achievements, user_achievements, telegram_connections
```

## Authentication Flow

Local auth is active:

1. `POST /auth/register` or `POST /auth/login` accepts JSON credentials.
2. Backend normalizes and validates usernames.
3. Passwords are hashed with Werkzeug.
4. Backend returns `access_token` and sets an HttpOnly `ringo_token` cookie.
5. `require_auth()` checks the cookie first, then `Authorization: Bearer`.
6. Protected routes receive decoded JWT claims.
7. `POST /auth/logout` clears the cookie.

Secret handling:

- `backend/config.py` owns `SECRET_KEY` and `JWT_SECRET` validation.
- Outside development, startup fails if either required secret is missing.
- `backend/auth.py` uses `Config.JWT_SECRET` for JWT signing and verification.

Telegram auth status:

- `backend/auth_telegram.py` can verify Telegram Login Widget payloads.
- `backend/config.py` defines Telegram config fields.
- No active `/auth/telegram` route is registered in the current app.

## Frontend Architecture

`frontend/src/main.js` installs Pinia and Vue Router, imports CSS tokens/base styles, and mounts `App.vue`.

It also installs `vue-i18n` from `frontend/src/i18n/index.js`. The i18n layer:

- loads English and Persian locale catalogs from `frontend/src/i18n/locales/`
- persists the selected locale in `localStorage.ringostrike_locale`
- sets `document.documentElement.lang`
- sets `document.documentElement.dir` to `rtl` for Persian and `ltr` for English
- keeps backend values as raw logic inputs while components translate display labels

Router paths:

- `/login`
- `/onboarding`
- `/auth/callback`
- `/dashboard`
- `/paths`
- `/challenges`
- `/profile`
- `/enrollment/:id`
- `/enrollment/:id/leaderboard`
- `/u/:username`
- `/docs`
- `/` redirects to `/dashboard`
- unknown paths redirect to `/dashboard`

Guided progression is now split between backend path/mission data and frontend presentation:

- `/onboarding` stores temporary completion/path state in `localStorage` and uses existing challenge list/join APIs.
- `frontend/src/views/challengeFlow.js` centralizes join payload handling and returns join success data so callers can decide whether to show JoinSuccessMoment or navigate.
- `/paths` uses `GET /paths`, `POST /paths/:id/start`, and `GET /paths/:id/challenges` to show active growth paths, challenge stages, mission previews, and path progress.
- Dashboard loads `MissionCenter` before legacy dashboard sections. `MissionCenter` calls `GET /me/today-missions`, renders `RingoCoach`, and writes mission state through `/me/missions/:id/...`.
- `POST /me/missions/:id/done` records the mission log and delegates to the existing enrollment check-in service, so XP, streaks, achievements, activity, and stats remain owned by the existing progression pipeline.
- RewardMoment and JoinSuccessMoment are display feedback components. RewardMoment consumes existing check-in reward data plus frontend-only feature unlock hints; JoinSuccessMoment consumes challenge/path start results.

## Ringo Helper Architecture

`backend/services/ringo_decision_service.py` returns a compact UI decision:

```json
{
  "state": "today_not_started",
  "sprite": "focus",
  "sprite_key": "focus",
  "message": "Today's mission is ready...",
  "primary_action": { "label": "Start: Mission", "type": "mission", "mission_id": 1 },
  "secondary_action": { "label": "View path details", "type": "route", "to": "/enrollment/1" }
}
```

`frontend/src/components/ringo/RingoCoach.vue` resolves `sprite_key` through `frontend/src/constants/ringoSprites.js` and emits action payloads for mission/reminder/dismiss behavior. Route actions render as `RouterLink`.

Current sprite asset set is under `frontend/src/assets/ringo/`. The frontend sprite map currently references `talking.png` and `victory.png`; those files are not present in the current working tree and should be restored or removed from the sprite map.

Router guard behavior:

- `requiresAuth: false` routes pass.
- All other routes call `GET /me`; failures redirect to `/login?next=...`.

## VPS Nginx/API Proxy Architecture

The current VPS deployment at `http://82.115.24.10` uses same-origin frontend/backend access:

```txt
Browser
  -> nginx at http://82.115.24.10
      -> frontend/dist for Vue routes
      -> /api-proxy/* to Flask on 127.0.0.1:5005
```

Production frontend builds for this deployment use:

```env
VITE_API_BASE=/api-proxy
VITE_BASE=/
```

Do not build the production frontend with `VITE_API_BASE=http://localhost:5005`; browser `localhost` would point at the user's machine.

The nginx API proxy should not use rewrite rules. A trailing slash on `proxy_pass` strips the `/api-proxy/` location prefix:

```nginx
location /api-proxy/ {
    proxy_pass http://127.0.0.1:5005/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

This maps:

- `/api-proxy/health` -> Flask `/health`
- `/api-proxy/api/telegram/remind-due-missions` -> Flask `/api/telegram/remind-due-missions`
- `/api-proxy/me` -> Flask `/me`

Vue routes stay on the SPA fallback:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

## Reminder Automation Architecture

Mission-level Telegram reminder delivery is backend-owned:

```txt
n8n/cron
  -> POST /api-proxy/api/telegram/remind-due-missions
  -> routes/telegram_routes.py
  -> services/reminder_service.py
  -> services/telegram_service.py
  -> Telegram Bot API
  -> mission_logs.reminder_sent_at
```

The endpoint is protected by `X-Reminder-Token`. n8n should trigger the backend endpoint; it should not send user Telegram messages directly.

Duplicate prevention uses `mission_logs.reminder_sent_at`: due reminders are selected only when `status = 'remind_later'`, `reminder_at <= now`, and `reminder_sent_at IS NULL`; the marker is set only after successful send.

Protected diagnostics live at `GET /api/telegram/reminder-diagnostics` and expose safe operational state only. They do not send messages and must not expose tokens, raw chat IDs, cookies, JWT secrets, or bot credentials.

## Frontend State Flow

The app mostly uses component-local state and direct API calls. Pinia exists and `stores/session.js` defines a small cookie-auth session store around `GET /me` and `POST /auth/logout`. The frontend relies on HttpOnly cookies through Axios `withCredentials`, while the backend still supports Bearer token fallback.

## Design System Architecture

Active global styles are:

- `frontend/src/styles/tokens.css`
- `frontend/src/styles/base.css`

`base.css` also defines the local Vazirmatn `@font-face` from `frontend/src/assets/fonts/Vazirmatn.woff2` and applies it only under `html[lang="fa"] body`. English keeps the default system font stack.

`frontend/src/style.css` and `frontend/src/assets/main.css` exist but are not imported by `main.js`.

The actual UI is implemented with Vue component CSS plus shared base primitives under `frontend/src/components/ui/`.

## Known Architecture Risks

- Auth route handlers still live in `backend/auth.py` rather than a cleaner route/service split.
- Auth remains stateless JWT; there is no token revocation or session blacklist.
- SQLite is suitable for local/MVP use but will need migrations and likely PostgreSQL before serious multi-user scale.
- Some read endpoints perform derived calculations or stats sync work, which can become expensive as data grows.
- Mission completion delegates to check-in, so duplicate mission/check-in submissions should continue to be tested around idempotency and reward display.
- API prefixes are mixed (`/me/...`, `/api/me/...`, `/api/profile...`) and should be normalized over time.
- Profile update responsibilities overlap across profile settings/update/visibility endpoints.

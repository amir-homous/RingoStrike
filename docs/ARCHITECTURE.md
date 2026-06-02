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
    lib/api.js
    router/index.js
    stores/session.js
    styles/
    views/
docs/
```

Generated/dependency directories such as `backend/venv`, `backend/.venv`, `frontend/node_modules`, `__pycache__`, and the local SQLite file are not architecture source.

## Backend Runtime

`backend/app.py` creates the Flask application, loads config, enables CORS for local frontend origins, initializes SQLite tables, registers auth routes, registers blueprints, and exposes `/health`.

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

## Text Architecture Diagram

```txt
Vue views
  Dashboard/Profile/Challenges/Enrollment/PublicProfile
      |
      v
frontend/src/lib/api.js
      |
      v
Flask app.py + route modules
      |
      v
Service layer
  stats -> achievements -> activity -> profile
  challenge -> enrollment -> history -> leaderboard
      |
      v
SQLite tables
  users, user_stats, challenges, enrollments,
  checkins, achievements, user_achievements
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

Router paths:

- `/login`
- `/auth/callback`
- `/dashboard`
- `/challenges`
- `/profile`
- `/enrollment/:id`
- `/enrollment/:id/leaderboard`
- `/u/:username`
- `/docs`
- `/` redirects to `/dashboard`
- unknown paths redirect to `/dashboard`

Router guard behavior:

- `requiresAuth: false` routes pass.
- All other routes call `GET /me`; failures redirect to `/login?next=...`.

## Frontend State Flow

The app mostly uses component-local state and direct API calls. Pinia exists and `stores/session.js` defines a small cookie-auth session store around `GET /me` and `POST /auth/logout`. The frontend relies on HttpOnly cookies through Axios `withCredentials`, while the backend still supports Bearer token fallback.

## Design System Architecture

Active global styles are:

- `frontend/src/styles/tokens.css`
- `frontend/src/styles/base.css`

`frontend/src/style.css` and `frontend/src/assets/main.css` exist but are not imported by `main.js`.

The actual UI is implemented with Vue component CSS plus shared base primitives under `frontend/src/components/ui/`.

## Known Architecture Risks

- Auth route handlers still live in `backend/auth.py` rather than a cleaner route/service split.
- Auth remains stateless JWT; there is no token revocation or session blacklist.
- SQLite is suitable for local/MVP use but will need migrations and likely PostgreSQL before serious multi-user scale.
- Some read endpoints perform derived calculations or stats sync work, which can become expensive as data grows.
- API prefixes are mixed (`/me/...`, `/api/me/...`, `/api/profile...`) and should be normalized over time.
- Profile update responsibilities overlap across profile settings/update/visibility endpoints.

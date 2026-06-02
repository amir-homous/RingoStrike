# RingoStrike - Project Overview

## What It Is

RingoStrike is a gamified consistency platform. Users join challenges, complete daily check-ins, build streaks, earn XP, unlock achievements, and shape a profile identity around their progress.

The current product is both private-progression focused and public-identity capable.

## Current Capabilities

- Local username/password authentication.
- JWT cookie auth with Bearer fallback.
- Challenge discovery and joining.
- Invite-only challenge join codes.
- Daily check-ins per enrollment.
- Enrollment history and challenge leaderboard.
- XP, level, current streak, longest streak, and progress calculations.
- Achievement definitions, unlock evaluation, and reward feedback.
- Activity feed derived from check-ins, streaks, level-ups, and achievements.
- Private profile page with title, stats, bio, avatar, and consistency heatmap.
- Public profiles at `/u/:username` backed by public API endpoints.
- Profile visibility controls: public/private.
- API docs page in the frontend.
- SQLite debug endpoints gated to development mode.
- Safe `/health/config` readiness endpoint.

## Technology

Backend:

- Flask
- Flask-CORS
- PyJWT
- Werkzeug password hashing
- SQLite
- python-dotenv

Frontend:

- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- Tailwind dependency present, but active global import is plain CSS tokens/base styles

## How The App Runs

Backend:

```bash
cd backend
python app.py
```

Default backend URL: `http://localhost:5005`.

Frontend:

```bash
cd frontend
npm run dev
```

Default Vite URL: `http://localhost:5173`.

Frontend API base is `VITE_API_BASE` or `http://localhost:5005`.

## User Flow

```txt
Register/Login
  -> Dashboard
  -> Join challenge
  -> Daily check-in
  -> Stats sync
  -> Achievement evaluation
  -> Activity feed/profile update
  -> Optional public profile sharing
```

## Current Architecture Strengths

- Clear route/service split for most backend features.
- Centralized stats and streak calculations in `stats_service.py`.
- Achievement and activity systems are reusable across dashboard/profile.
- Public profile endpoints enforce `profile_visibility`.
- Frontend is already organized by feature components and views.

## Current Product Stage

Based on git history, the project has progressed through:

1. Auth, dashboard, challenges, leaderboard, and API docs foundation.
2. Backend modularization and stats/streak fixes.
3. XP, dashboard progression UX, activity timeline, achievements, and profile identity hub.
4. Public identity foundations: public profiles, visibility, username normalization, avatar/profile settings, and shareable UX.

## Known Stabilization Needs

- Add a real migration strategy instead of startup-time schema changes.
- Normalize API naming conventions where practical (`/me/...` vs `/api/...`).
- Review overlapping profile update endpoints and choose one long-term contract.
- Review public challenge/member endpoint visibility before public launch.
- Continue expanding shared API response helper usage.
- Add frontend smoke tests for router guard, login, dashboard, challenge check-in, profile, and public profile rendering.

## Recently Stabilized

- Duplicate `/me/stats` route ownership was removed; `stats_routes.py` owns the endpoint.
- `frontend/src/stores/session.js` now follows cookie-based auth and no longer expects `api.setToken()`.
- SQLite debug endpoints are blocked outside development mode.
- Legacy `services/auth_service.py` and old `sessions` table initialization were removed.
- `backend/auth.py` now uses centralized `Config.JWT_SECRET` instead of a separate JWT fallback.
- Backend smoke coverage currently reports `34 passed` in the local `backend/venv` environment.

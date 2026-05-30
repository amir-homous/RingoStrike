# RingoStrike - AI Development Context

## Current State

RingoStrike is a Flask + Vue progression platform for challenges, daily check-ins, XP, streaks, achievements, profile identity, and public profile sharing.

This context reflects the code in this repository as of the current working tree, not only the earlier product roadmap.

## Product Identity

RingoStrike should feel like a premium consistency and progression system, not a generic habit tracker. The product direction remains:

- consistency becomes visible progress
- check-ins create momentum and identity
- achievements and XP reward consistency without casino-style noise
- public identity is shareable but privacy-aware
- social features should reinforce momentum, not toxic competition

## Implemented Backend Systems

- Flask app factory in `backend/app.py`.
- SQLite database initialized by `backend/database.py`.
- JWT auth in `backend/auth.py` with HttpOnly cookie and Bearer fallback.
- Modular route files in `backend/routes/`.
- Business logic split into `backend/services/`.
- Local username/password register, login, and logout endpoints.
- Telegram verification helper exists in `backend/auth_telegram.py`, but no active Telegram login route is registered in `backend/app.py`.
- Challenge listing, detail, members, join, enrollment detail, history, leaderboard, and check-in APIs.
- Stats engine with XP, level, current streak, longest streak, and progress percent.
- Achievement definitions and user unlock tracking.
- Activity feed derived from check-ins, streak moments, level-ups, and achievements.
- Private profile aggregation and public profile endpoints with visibility enforcement.
- Profile settings and profile update endpoints.
- Debug endpoints for SQLite schema and counts.

## Implemented Frontend Systems

- Vue 3 + Vite application in `frontend/`.
- Vue Router routes for login, auth callback, dashboard, challenges, profile, enrollment, leaderboard, public profile, API docs, and redirects.
- Axios API client in `frontend/src/lib/api.js` using `VITE_API_BASE` or `http://localhost:5005`, credentials enabled.
- Shared CSS tokens in `frontend/src/styles/tokens.css` and base styles in `frontend/src/styles/base.css`.
- Component groups for UI primitives, progress, achievements, activity, challenge cards, profile, and feedback.
- Public profile page consumes `/api/public/profile/:username`, `/consistency`, and `/achievements`.
- API docs view contains an older endpoint list and should be checked before relying on it as the source of truth.

## Source Of Truth Rules

- Database truth is in `backend/database.py`; service queries reveal actual field usage.
- API truth is in `backend/routes/*.py` plus endpoints registered directly by `backend/auth.py` and `backend/app.py`.
- Frontend route truth is in `frontend/src/router/index.js`.
- Frontend API usage truth is in `frontend/src/lib/api.js` and Vue views/components.
- Git timeline truth is in recent commits on `main` and `dev`.

## Critical Engineering Notes

- `frontend/src/stores/session.js` calls `api.setToken()`, but `frontend/src/lib/api.js` does not expose `setToken`. This store is currently inconsistent with the API client.
- Two route modules register `GET /me/stats`: `dashboard_routes.py` and `stats_routes.py`. Because `dashboard_bp` is registered before `stats_bp`, the dashboard implementation is the effective route in normal Flask dispatch order; the duplicate route should be removed or unified.
- `backend/services/auth_service.py` duplicates auth logic but is not used by `backend/routes/auth_routes.py`; active auth routes are registered through `backend/auth.py`.
- `sessions` table exists but active auth uses stateless JWT cookies and does not write session rows.
- Debug routes are unauthenticated and expose schema/count metadata.
- `JWT_SECRET` and `SECRET_KEY` have development fallbacks. Production must set secure environment values.
- `backend/users.db`, Python caches, `backend/venv`, `backend/.venv`, and `frontend/node_modules` are present in the working tree and should not be treated as application source.

## Current Roadmap Position

The project has moved beyond the older v0.3 dashboard/profile milestone. Public identity foundations are now implemented:

- username normalization and reserved names
- public-safe profile URLs at `/u/:username`
- visibility-controlled public profile endpoints
- profile settings and avatar/bio fields
- public consistency and public achievements endpoints

The next highest-value work is stabilization: remove duplicate/unused paths, fix frontend API client/session mismatch, harden auth/config, and align API docs with backend truth.

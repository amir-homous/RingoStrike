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
- Debug endpoints for SQLite schema and counts, blocked outside development mode.
- Safe `/health/config` endpoint that reports readiness flags without exposing secrets.

## Implemented Frontend Systems

- Vue 3 + Vite application in `frontend/`.
- Vue Router routes for login, auth callback, dashboard, challenges, profile, enrollment, leaderboard, public profile, API docs, and redirects.
- Axios API client in `frontend/src/lib/api.js` using `VITE_API_BASE` or `http://localhost:5005`, credentials enabled, and callback-token Bearer fallback support.
- Active local auth UI is `frontend/src/components/AuthForm.vue`; it uses the shared API client and honors the `next` redirect query.
- Shared CSS tokens in `frontend/src/styles/tokens.css` and base styles in `frontend/src/styles/base.css`.
- Component groups for UI primitives, progress, achievements, activity, challenge cards, profile, and feedback.
- Public profile page consumes `/api/public/profile/:username`, `/consistency`, and `/achievements`.
- API docs view has been brought closer to the backend contract, but route files remain the final source of truth.

## Source Of Truth Rules

- Database truth is in `backend/database.py`; service queries reveal actual field usage.
- API truth is in `backend/routes/*.py` plus endpoints registered directly by `backend/auth.py` and `backend/app.py`.
- Frontend route truth is in `frontend/src/router/index.js`.
- Frontend API usage truth is in `frontend/src/lib/api.js` and Vue views/components.
- Git timeline truth is in recent commits on `main` and `dev`.

## Critical Engineering Notes

- `frontend/src/stores/session.js` is aligned with cookie-based auth and no longer expects `api.setToken()`.
- Cookies remain the preferred auth path; `localStorage.ringo_token` is only a callback-token fallback and is cleared on logout.
- `frontend/src/components/AuthForm.vue` should stay aligned with `frontend/src/lib/api.js`; avoid hard-coded backend origins or auth payload logging.
- `frontend/src/views/Login.vue` is a Telegram-oriented view and is not the active `/login` route while local username/password auth remains the primary flow.
- `GET /me/stats` is owned by `stats_routes.py` and delegates to `stats_service.py`.
- `backend/services/auth_service.py` has been removed; active auth routes are still registered through `backend/auth.py`.
- The old `sessions` table is no longer initialized by `init_db()`; active auth uses stateless JWT cookies.
- Debug routes are development-only and return `debug_disabled` outside development mode.
- `SECRET_KEY` and `JWT_SECRET` are required outside development by `backend/config.py`.
- `backend/auth.py` uses centralized `Config.JWT_SECRET` for JWT signing and verification.
- `LOCAL_LOGIN_ENABLED=0` disables active username/password register and login routes.
- `stats_service.py` is the source of truth for total XP, including base check-in XP and unlocked achievement XP rewards.
- Progression surfaces should consistently filter counted check-ins with `status = 'Done' AND is_counted = 1`.
- Public profile, consistency, and achievement username lookups normalize route usernames before lookup.
- Private challenge detail/member endpoints and `/me/enrollments/:id/leaderboard` enforce privacy/ownership checks.
- `backend/users.db`, Python caches, `backend/venv`, `backend/.venv`, and `frontend/node_modules` are present in the working tree and should not be treated as application source.

## Current Roadmap Position

The project has moved beyond the older v0.3 dashboard/profile milestone. Public identity foundations are now implemented:

- username normalization and reserved names
- public-safe profile URLs at `/u/:username`
- visibility-controlled public profile endpoints
- profile settings and avatar/bio fields
- public consistency and public achievements endpoints

The next highest-value work is launch hardening: finalize production environment values, run the launch QA checklist, add frontend smoke tests, add a migration/backup plan, and continue reducing profile/API contract overlap.

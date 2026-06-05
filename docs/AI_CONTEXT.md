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

## Current Product UX Priority

Early tester feedback indicates that RingoStrike is valuable but feels too complex for first-time users.

The next product priority is to evolve the experience from a dashboard-heavy interface into a guided progression journey.

Primary target loop:

```txt
Today's Mission -> Check-in -> Reward -> Next Step
```

Implementation guidance:

- Prefer frontend-first UX simplification.
- Reuse existing challenge, enrollment, check-in, stats, achievement, and activity systems.
- Do not duplicate XP/streak/achievement logic.
- Do not rewrite the dashboard; evolve it into a guided mission surface.
- Delay complex social, mobile, widget, and advanced automation work until the guided loop is validated.

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
- Axios API client in `frontend/src/lib/api.js` using `VITE_API_BASE` when provided, `http://localhost:5005` only in Vite dev mode, and same-origin relative API paths in production by default. Credentials are enabled and callback-token Bearer fallback support remains.
- The current VPS same-origin deployment at `http://82.115.24.10` uses `VITE_API_BASE=/api-proxy` and Nginx rewrites `/api-proxy/*` to Flask on `http://127.0.0.1:5005`. Do not use `VITE_API_BASE=http://localhost:5005` in production browser builds.
- Active local auth UI is `frontend/src/components/AuthForm.vue`; it uses the shared API client and honors the `next` redirect query.
- Shared CSS tokens in `frontend/src/styles/tokens.css` and base styles in `frontend/src/styles/base.css`.
- Frontend i18n is implemented with `vue-i18n` in `frontend/src/i18n/`, currently supporting English (`en`) and Persian (`fa`).
- The language switcher lives in `frontend/src/components/i18n/LanguageSwitcher.vue`, persists the selected locale in `localStorage.ringostrike_locale`, and updates `document.documentElement.lang` and `dir`.
- Persian mode uses the local Vazirmatn variable WOFF2 font from `frontend/src/assets/fonts/Vazirmatn.woff2`; English mode keeps the existing system font stack.
- Component groups for UI primitives, progress, achievements, activity, challenge cards, profile, and feedback.
- Guided progression frontend surfaces now include a Today Mission dashboard focus, guided first-path empty state, lightweight `/onboarding` identity path flow, progressive dashboard disclosure, premium check-in RewardMoment, and JoinSuccessMoment after successful challenge joins.
- RewardMoment displays existing backend check-in rewards only and can surface frontend-only feature unlock hints for Activity, Achievements, and Public Profile. Leaderboard unlock hints are intentionally skipped for v1 because there is no dedicated global leaderboard route yet.
- JoinSuccessMoment keeps the join API unchanged and gives users a softer transition from onboarding/challenge discovery to the daily mission loop before they open dense enrollment details.
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
- Frontend translations should stay frontend-only. Do not change backend response shapes to support locale text; translate display labels at the component/i18n layer and keep raw backend values for logic.
- When adding Persian UI text, keep `lang="fa"`/`dir="rtl"` behavior centralized through `frontend/src/i18n/index.js`.
- Keep guided progression UX frontend-first while it is being validated. Reuse current challenge/enrollment/check-in responses; do not add onboarding, recommendation, XP, streak, or achievement backend logic unless a later issue explicitly requires it.
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
- For VPS same-origin deployment, use `/api-proxy` to avoid frontend/backend route collisions. Do not proxy backend root paths like `/challenges` directly because `/challenges` is also a Vue route and should render the SPA page.
- `backend/users.db`, Python caches, `backend/venv`, `backend/.venv`, and `frontend/node_modules` are present in the working tree and should not be treated as application source.

## Current Roadmap Position

The project has moved beyond the older v0.3 dashboard/profile milestone. Public identity foundations are now implemented:

- username normalization and reserved names
- public-safe profile URLs at `/u/:username`
- visibility-controlled public profile endpoints
- profile settings and avatar/bio fields
- public consistency and public achievements endpoints

The next highest-value work is launch hardening: finalize production environment values, run the launch QA checklist, add frontend smoke tests, add a migration/backup plan, and continue reducing profile/API contract overlap.

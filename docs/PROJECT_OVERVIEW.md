# RingoStrike - Project Overview

## What It Is

RingoStrike is a caring daily self-improvement companion centered around Ringo, a character who helps users take small guided actions, feel emotionally supported, and build visible progress over time.

Ringo is the emotional interface of the product. Paths, challenges, missions, streaks, XP, achievements, activity, and profiles are supporting infrastructure that help Ringo understand the user's context and guide the next small step.

The current product is both companion-first and progression-capable: it should feel warm, guided, and personal before it feels like a system dashboard.

Product direction source:

- [Product Direction Master Notes](product/PRODUCT_DIRECTION_MASTER_NOTES.md)
- [MVP Relaunch Phases](product/MVP_RELAUNCH_PHASES.md)
- [GitHub Issue Pack](product/GITHUB_ISSUE_PACK.md)

## Current Capabilities

- Local username/password authentication.
- JWT cookie auth with Bearer fallback.
- Challenge discovery and joining.
- Invite-only challenge join codes.
- Lightweight first-run onboarding with identity path selection and suggested first challenge.
- Guided join success moment after successful challenge joins, before users move into enrollment details.
- Backend-backed growth paths and daily missions.
- `/paths` and `/me/today-missions` APIs for path discovery, path start, mission status, reminders, skips, and mission completion.
- RingoCoach guidance states that choose message, sprite, and next action from the user's current path/enrollment/mission context.
- Daily check-ins per enrollment.
- Dashboard Mission Center that leads the daily loop and falls back to the legacy Today Mission card only when no mission is available.
- Full `/paths` page for path selection, challenge stage previews, mission previews, and per-path progress summary.
- Premium check-in reward moment with existing XP, streak, achievement, and frontend-only unlock hints.
- Frontend-only progressive disclosure for early dashboard sections based on existing check-in stats.
- Enrollment history and challenge leaderboard.
- XP, level, current streak, longest streak, and progress calculations.
- Achievement definitions, unlock evaluation, and reward feedback.
- Activity feed derived from check-ins, streaks, level-ups, and achievements.
- Private profile page with title, stats, bio, avatar, and consistency heatmap.
- Public profiles at `/u/:username` backed by public API endpoints.
- Profile visibility controls: public/private.
- Frontend Persian/English language switching with persisted locale and automatic `lang`/`dir` updates.
- Persian UI typography uses the local Vazirmatn variable WOFF2 font while English keeps the existing system font stack.
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
- vue-i18n
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

Frontend API base uses `VITE_API_BASE` when set. Without it, Vite dev mode falls back to `http://localhost:5005`; production builds use same-origin relative API paths for Nginx deployments.

The current VPS test deployment at `http://82.115.24.10` uses `VITE_API_BASE=/api-proxy` because backend routes such as `/challenges` conflict with Vue frontend routes when proxied at the root. Nginx rewrites `/api-proxy/*` to the local Flask backend on `http://127.0.0.1:5005`.

Selected frontend language is stored in `localStorage.ringostrike_locale`.

## User Flow

```txt
Register/Login
  -> Ringo welcomes and reads the user's current state
  -> Ringo suggests one clear daily mission
  -> User chooses the main step, a smaller step, or an optional extra
  -> User completes a small self-improvement action
  -> Existing check-in/stats/achievement pipeline
  -> Ringo reacts and rewards the moment
  -> Next gentle step or rest
```

## Guided User Flow

```txt
Register/Login
  -> Onboarding / Identity Path
  -> Suggested First Challenge or Growth Path
  -> Path Started Moment / JoinSuccessMoment
  -> Ringo-guided Today's Mission
  -> Mission Done / Check-in
  -> Ringo Moment / Reward Moment
  -> Next Step
  -> Paths/Dashboard/Profile as supporting surfaces
```

The product has shifted from a dashboard-based MVP toward a Ringo-first companion experience where the next action is emotionally clear and small enough to complete. The dashboard remains important, but it should feel like Ringo's home. MissionCenter, paths, challenges, stats, and profiles support the companion loop instead of competing with it.

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
5. Guided path/mission foundation: seeded MVP paths, path-specific challenges, daily missions, mission logs, RingoCoach state decisions, premium navigation, and Ringo helper sprites.

## Known Stabilization Needs

- Add a real migration strategy instead of startup-time schema changes.
- Normalize API naming conventions where practical (`/me/...` vs `/api/...`).
- Review overlapping profile update endpoints and choose one long-term contract.
- Review public challenge/member endpoint visibility before public launch.
- Continue expanding shared API response helper usage.
- Add frontend smoke tests for router guard, login, dashboard, challenge check-in, profile, and public profile rendering.
- Fix or remove missing Ringo sprite imports for `talking.png` and `victory.png`; the current frontend sprite map references these files, but they are absent from `frontend/src/assets/ringo/`.

## Recently Stabilized

- Duplicate `/me/stats` route ownership was removed; `stats_routes.py` owns the endpoint.
- `frontend/src/stores/session.js` now follows cookie-based auth and no longer expects `api.setToken()`.
- SQLite debug endpoints are blocked outside development mode.
- Legacy `services/auth_service.py` and old `sessions` table initialization were removed.
- `backend/auth.py` now uses centralized `Config.JWT_SECRET` instead of a separate JWT fallback.
- Local auth can be disabled through `LOCAL_LOGIN_ENABLED`.
- Profile, challenge, leaderboard, public identity, and progression privacy edge cases have been hardened.
- Progression surfaces consistently ignore uncounted check-ins.
- Achievement XP rewards are included in persisted stats.
- Backend smoke coverage currently reports `41 passed` in the local `backend/venv` environment.
- MVP paths and missions are seeded by `path_seed_service.py`, with legacy unlinked challenges archived when they have no active mission linkage.

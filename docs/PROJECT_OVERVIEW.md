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
- Frontend mission focus mode that keeps the dashboard centered on Ringo, the current mission/reminder/completion state, and a compact progress strip while the daily loop still needs attention.
- First-run staged reveal for the Mission Center so Ringo guidance, mission intro, mission card, and action education appear in a calm sequence.
- Rest Mode after `Finish for today`, with sleeping Ringo, safe-day copy, optional future reminder timing, and an explicit `Show dashboard` escape hatch.
- Post-safe optional explorer in MissionCenter with calm growth-map styling, path/challenge progress surfaces, icon progress rings, reward-ready/building display slots, earned/total XP summaries, mission-key icons, and status-aware mission rows.
- Mission Status details are collapsed by default during focus mode and can be revealed manually with `Show mission status`.
- Full `/paths` page for path selection, challenge stage previews, mission previews, and per-path progress summary.
- Premium check-in reward moment with existing XP, streak, achievement, and frontend-only unlock hints.
- Frontend-only Staged Mission Reward Sequence v2 after mission completion, reusing `RingoRewardSequence.vue` for mission, XP, strike/check-in, path, challenge, level, and final-choice presentation while falling back safely for already-done or no-XP responses.
- Frontend-only Daily Momentum Bar v1 as the compact daily strike/path/action dock, working alongside `compactProgressStrip` as the top/global XP-level/status strip.
- Today-only path progress rings with DB-backed path icons, path-color accents, contextual daily actions, and a lightweight Explore Paths action that routes to the existing Paths page.
- Action icon support from `frontend/src/assets/action-icons/`, including white-on-dark rendering for black PNG assets and safe text-only fallback.
- Reminder chip in `compactProgressStrip` only when existing frontend reminder count is greater than zero.
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
- Full-viewport dark root/app background coverage for stable LTR/RTL dashboard rendering.
- Frontend-only display localization for known seeded mission/path/challenge copy, improving Persian MissionCenter, onboarding, path/challenge preview, and Challenge Discovery surfaces while keeping backend seed data unchanged.
- Telegram reminder connection settings, mission-level reminder scheduling, n8n-triggered due reminder delivery, and protected reminder diagnostics.
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

The current VPS test deployment at `http://82.115.24.10` uses `VITE_API_BASE=/api-proxy` because backend routes such as `/challenges` conflict with Vue frontend routes when proxied at the root. Nginx serves `frontend/dist` and proxies `/api-proxy/` to the local Flask backend on `http://127.0.0.1:5005/` without rewrite rules.

Production-like VPS backend runtime is managed by `systemd` service `ringostrike-backend` from `/home/ringo/RingoStrike/backend`, using `/home/ringo/RingoStrike/backend/venv` and env-driven `backend/app.py` values:

```env
FLASK_HOST=127.0.0.1
PORT=5005
FLASK_DEBUG=0
```

Selected frontend language is stored in `localStorage.ringostrike_locale`.

## User Flow

```txt
Register/Login
  -> Ringo welcomes and reads the user's current state
  -> Ringo suggests one clear daily mission
  -> User chooses the main step, a smaller step, or an optional extra
  -> Known seeded mission/path/challenge copy is localized at the frontend display layer when available
  -> User completes a small self-improvement action
  -> Existing check-in/stats/achievement pipeline
  -> Ringo reacts and, when mission XP is earned, shows the Staged Mission Reward Sequence
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
  -> Staged Mission Reward Sequence / Ringo Moment
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
6. Mission-family, focus-mode, and optional-explorer polish: main/tiny substitute behavior, bonus-as-optional momentum, staged first-run reveal, post-first-win copy, compact focus progress, collapsed mission status details, Rest Mode, and post-safe optional growth-map exploration.
7. Mission Reward Moment v1: frontend-only mission completion feedback that reuses the existing reward sequence, differentiates main/tiny/bonus copy, skips full replay for already-done/no-XP responses, and keeps progression ownership in the existing backend systems.
8. Daily Momentum Bar v1: frontend-only compact daily strike/path/action dock that shows today safety, streak count, today-only path rings, contextual actions, Explore Paths navigation, and reminder chip display while preserving backend/API/schema/progression ownership.
9. Staged Mission Reward Sequence v2: frontend-only mission completion sequence that normalizes backend `reward_sequence`, uses before/after reward snapshots where available, guarantees fallback mission/XP/final-choice steps for newly completed XP missions, supports strike secured, level-up wrap, path/challenge strengthened, challenge secured, mission-key icons, legacy Dashboard reward-card suppression, EN/FA copy, RTL polish, and reduced-motion-safe behavior where implemented.

## Known Stabilization Needs

- Add a real migration strategy instead of startup-time schema changes.
- Normalize API naming conventions where practical (`/me/...` vs `/api/...`).
- Review overlapping profile update endpoints and choose one long-term contract.
- Review public challenge/member endpoint visibility before public launch.
- Continue expanding shared API response helper usage.
- Add frontend smoke tests for router guard, login, dashboard, challenge check-in, profile, and public profile rendering.
- Continue validating mission context clarity and seeded content localization. Mission focus mode, frontend-only seeded content display localization, and the staged mission reward sequence are implemented, but a full universal Mission Context UX layer, Telegram mission-specific deep-link restoration, and full custom-content localization remain planned work.

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
- Backend smoke coverage currently reports `153 passed` from `cd backend && ./venv/bin/pytest tests` in the local `backend/venv` environment.
- MVP paths and missions are seeded by `path_seed_service.py`, with legacy unlinked challenges archived when they have no active mission linkage.
- Mission-level Telegram reminder delivery is protected by `X-Reminder-Token`, safe for n8n/cron triggering, and prevents duplicate sends with `mission_logs.reminder_sent_at`.
- Protected reminder diagnostics expose due/scheduled/sent/missing-Telegram/reminders-disabled operational state without sending messages or exposing secrets.
- Mission-family agenda behavior treats linked `main` and `tiny` missions as substitutes while keeping `bonus` missions independently visible and optional.
- Dashboard mission focus mode hides secondary sections until the daily focus is resolved or the user explicitly chooses `Show dashboard`; focus mode remains frontend-only and does not alter progression writes.
- MissionCenter optional explorer progress-map polish remains frontend-only: completed groups can stay visible, due reminders still own focus, future reminders stay quiet until due, and reward-ready/building states do not imply backend reward claims.
- Staged Mission Reward Sequence v2 remains frontend-only: it consumes additive mission completion fields, backend `reward_sequence`, and frontend before/after snapshots where available, but does not change backend XP/stat/progression logic, mission mutation behavior, schema, API contracts, reminder delivery, or Ringo Brain policy.
- Daily Momentum Bar v1 remains frontend-only: it consumes existing mission/path/guidance data, centralizes daily action display in MissionCenter, hides duplicate optional continuation actions, and does not change backend XP/stat/progression logic, mission mutation behavior, schema, reminder delivery, API response shapes, path levels, historical analytics, or Ringo Brain policy.
- Persian/RTL root-background and layout stability were hardened by ensuring dark coverage for the full root/app shell.

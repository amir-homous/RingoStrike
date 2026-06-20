# RingoStrike - AI Development Context

## Current State

RingoStrike is a Flask + Vue caring daily self-improvement companion centered around Ringo, with progression systems for challenges, daily missions, check-ins, XP, streaks, achievements, profile identity, and public profile sharing.

This context reflects the code in this repository as of the current working tree, not only the earlier product roadmap.

## Product Identity

RingoStrike should feel like a companion-first self-improvement experience, not a generic habit tracker or cold productivity dashboard.

Core product rule:

```txt
First Ringo. Then system.
```

Ringo is the emotional interface. The technical systems exist to help Ringo feel alive, caring, useful, and personally aware.

Product direction references:

- [Product Direction Master Notes](product/PRODUCT_DIRECTION_MASTER_NOTES.md)
- [MVP Relaunch Phases](product/MVP_RELAUNCH_PHASES.md)
- [GitHub Issue Pack](product/GITHUB_ISSUE_PACK.md)

The supporting product principles remain:

- small daily actions create visible progress
- check-ins create momentum and identity
- achievements and XP reward consistency without casino-style noise
- public identity is shareable but privacy-aware
- social features should reinforce momentum, not toxic competition

## Current Product UX Priority

Early tester feedback indicates that RingoStrike is valuable but feels too complex for first-time users.

The next product priority is to evolve the experience from a dashboard-heavy interface into a Ringo-first companion journey.

Primary implemented loop:

```txt
Ringo guidance -> Today's Mission -> Mission Done / Check-in -> Ringo Moment / Reward -> Next gentle step
```

Implementation guidance:

- Lead with Ringo's emotional state, message, and one clear next step before exposing system detail.
- Prefer guided UX simplification that reuses the backend path/mission layer and existing progression services.
- Reuse existing challenge, enrollment, check-in, stats, achievement, and activity systems.
- Do not duplicate XP/streak/achievement logic.
- Do not rewrite the dashboard; MissionCenter is the primary daily surface and older sections are supporting/progressive surfaces.
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
- Growth path APIs: `GET /paths`, `GET /paths/:id/challenges`, and `POST /paths/:id/start`.
- Daily mission APIs: `GET /me/today-missions`, `POST /me/missions/:id/done`, `POST /me/missions/:id/remind-later`, and `POST /me/missions/:id/skip`.
- Seeded MVP path/challenge/mission data through `services/path_seed_service.py`.
- Ringo decision service that returns state, sprite key, message, and action payloads for RingoCoach.
- Stats engine with XP, level, current streak, longest streak, and progress percent.
- Achievement definitions and user unlock tracking.
- Activity feed derived from check-ins, streak moments, level-ups, and achievements.
- Private profile aggregation and public profile endpoints with visibility enforcement.
- Profile settings and profile update endpoints.
- Debug endpoints for SQLite schema and counts, blocked outside development mode.
- Safe `/health/config` endpoint that reports readiness flags without exposing secrets.

## Implemented Frontend Systems

- Vue 3 + Vite application in `frontend/`.
- Vue Router routes for login, auth callback, dashboard, paths, challenges, profile, enrollment, leaderboard, public profile, API docs, and redirects.
- Axios API client in `frontend/src/lib/api.js` using `VITE_API_BASE` when provided, `http://localhost:5005` only in Vite dev mode, and same-origin relative API paths in production by default. Credentials are enabled and callback-token Bearer fallback support remains.
- The current VPS same-origin deployment at `http://82.115.24.10` uses `VITE_API_BASE=/api-proxy`. Nginx serves `frontend/dist`, proxies `/api-proxy/` to Flask on `http://127.0.0.1:5005/` without rewrite rules, and keeps Vue routes on the SPA fallback. Do not use `VITE_API_BASE=http://localhost:5005` in production browser builds.
- Active local auth UI is `frontend/src/components/AuthForm.vue`; it uses the shared API client and honors the `next` redirect query.
- Shared CSS tokens in `frontend/src/styles/tokens.css` and base styles in `frontend/src/styles/base.css`.
- Frontend i18n is implemented with `vue-i18n` in `frontend/src/i18n/`, currently supporting English (`en`) and Persian (`fa`).
- The language switcher lives in `frontend/src/components/i18n/LanguageSwitcher.vue`, persists the selected locale in `localStorage.ringostrike_locale`, and updates `document.documentElement.lang` and `dir`.
- Persian mode uses the local Vazirmatn variable WOFF2 font from `frontend/src/assets/fonts/Vazirmatn.woff2`; English mode keeps the existing system font stack.
- Frontend-only seeded content display localization is implemented through helpers such as `frontend/src/lib/missionDisplayCopy.js` and `frontend/src/lib/ringoContentLocalization.js`. Known seeded mission/path/challenge copy can be localized for display while raw backend values remain logic inputs. Unknown or custom backend content falls back safely to backend-provided title/name/description.
- Component groups for UI primitives, progress, achievements, activity, challenge cards, profile, and feedback.
- Guided progression surfaces now include Dashboard MissionCenter, backend RingoCoach decisions, `/paths` path planning, path selection from MissionCenter, lightweight `/onboarding` identity path flow, progressive dashboard disclosure, premium check-in RewardMoment, and JoinSuccessMoment after successful challenge joins.
- `MissionCenter.vue` calls `/me/today-missions`; mission done calls `/me/missions/:id/done`, which writes a mission log and delegates to the existing check-in pipeline.
- Mission Reward Moment v1 is a frontend-only mission-completion enhancement. It reuses `RingoRewardSequence.vue` after mission completion when `mission.xp_awarded > 0` and `mission.already_done !== true`, and it falls back to calm completion copy for already-done, missing-XP, or zero-XP responses.
- Mission Reward Moment v1 consumes additive completion fields such as `mission.xp_awarded`, `mission.already_done`, and `mission.mission_intensity`. It does not own XP, streak, achievement, check-in, stats, reward economy, or mission mutation behavior.
- Daily Momentum Bar v1 is a frontend-only compact strike/path/action dock in MissionCenter. It uses existing mission, path catalog, and Ringo guidance data to show today safety, streak count, today-only path progress rings, path-color accents, contextual actions, and a lightweight Explore Paths entry that routes to the existing `/paths` page.
- Daily Momentum Bar v1 does not own XP, stats, streak, check-in, progression, reward economy, or mission mutation behavior. It orchestrates display/actions only, while `compactProgressStrip` remains the top/global XP-level/status strip.
- Daily Momentum Bar path icons prefer DB-backed path icon metadata where available. Action icons are resolved from `frontend/src/assets/action-icons/`, with black PNGs rendered white by CSS filtering and missing icons falling back to text-only buttons.
- The optional explorer remains available as content/status/path/challenge/mission information, but duplicate optional continuation footer actions are hidden while the Daily Momentum Bar owns the safe-state actions.
- `compactProgressStrip` can show a reminder chip only when the existing frontend reminder count is greater than zero; this uses current mission reminder state and does not add backend fields or endpoints.
- MissionCenter's post-safe optional explorer is a frontend-only growth-map surface. It groups existing mission data into path/challenge cards with progress surfaces, icon progress rings, reward-ready/building display slots, earned/total XP summaries, mission-key icons, and status-aware mission rows. These are display states only and do not imply backend reward claims or new progression ownership.
- `PathSelection.vue` starts a path and then joins the first related challenge when one is available. Path start and challenge join remain separate API operations.
- RewardMoment displays existing backend check-in rewards only and can surface frontend-only feature unlock hints for Activity, Achievements, and Public Profile. Leaderboard unlock hints are intentionally skipped for v1 because there is no dedicated global leaderboard route yet.
- JoinSuccessMoment keeps the join API unchanged and gives users a softer transition from onboarding/challenge discovery to the daily mission loop before they open dense enrollment details.
- Public profile page consumes `/api/public/profile/:username`, `/consistency`, and `/achievements`.
- API docs view has been brought closer to the backend contract, but route files remain the final source of truth.

## Source Of Truth Rules

- Product decision truth is in `docs/product/`, especially `PRODUCT_DIRECTION_MASTER_NOTES.md`, `MVP_RELAUNCH_PHASES.md`, and `GITHUB_ISSUE_PACK.md`.
- Database truth is in `backend/database.py`; service queries reveal actual field usage.
- API truth is in `backend/routes/*.py` plus endpoints registered directly by `backend/auth.py` and `backend/app.py`.
- Frontend route truth is in `frontend/src/router/index.js`.
- Frontend API usage truth is in `frontend/src/lib/api.js` and Vue views/components.
- Git timeline truth is in recent commits on `main` and `dev`.

## AI/Codex Working Rules

- Preserve existing working functionality.
- Make small, safe, reviewable changes.
- Extend existing services, routes, components, and data flows before creating replacements.
- Do not rewrite backend or frontend architecture unless an issue explicitly asks for it.
- Treat path, challenge, mission, check-in, stats, achievement, activity, and profile systems as supporting infrastructure for Ringo.
- For Ringo-related product behavior, follow `docs/product/` before inventing new direction.
- Keep deterministic product decisions in code and services. AI-assisted language should come later and remain structured, validated, and fallback-safe.

## Critical Engineering Notes

- `frontend/src/stores/session.js` is aligned with cookie-based auth and no longer expects `api.setToken()`.
- Cookies remain the preferred auth path; `localStorage.ringo_token` is only a callback-token fallback and is cleared on logout.
- `frontend/src/components/AuthForm.vue` should stay aligned with `frontend/src/lib/api.js`; avoid hard-coded backend origins or auth payload logging.
- Frontend translations should stay frontend-only. Do not change backend response shapes to support locale text; translate display labels at the component/i18n layer and keep raw backend values for logic.
- Known seeded content display localization should use frontend helpers such as `missionDisplayCopy.js` and `ringoContentLocalization.js`; do not change backend seed data for this phase. Unknown/custom content must fall back to backend values.
- When adding Persian UI text, keep `lang="fa"`/`dir="rtl"` behavior centralized through `frontend/src/i18n/index.js`.
- Keep guided progression UX frontend-first while it is being validated. Reuse current challenge/enrollment/check-in responses; do not add onboarding, recommendation, XP, streak, or achievement backend logic unless a later issue explicitly requires it.
- For path/mission work, keep mission state in `mission_logs` and canonical progression in check-ins/stats/achievements. Avoid adding a second progression economy.
- `frontend/src/constants/ringoSprites.js` resolves Ringo sprites from `frontend/src/assets/ringo/` with fallback aliases for missing or unknown keys. Keep `RINGO_SPRITE_KEYS`, backend `sprite_key` values, and actual asset filenames aligned.
- Dashboard mission focus mode is frontend-owned: `MissionCenter.vue` emits `focus-state-change`, `Dashboard.vue` hides secondary dashboard sections while focus is active, and `CompactProgressStrip.vue` provides minimal level/XP/streak context without duplicating progression calculations.
- `MissionCenter.vue` owns first-run staged reveal, mission status expansion, post-first-win copy, and Rest Mode. `Finish for today` enters the calm Rest Mode card; `Show dashboard` explicitly unlocks the full dashboard.
- Mission Reward Moment v1 should stay frontend-only. It may display mission XP, Today Safe / streak-protected language for main/tiny completions when appropriate, and bonus-complete XP language for bonus completions, but bonus rewards must not claim Today Safe or create a bonus chain.
- Daily Momentum Bar v1 should stay frontend-only. Keep Explore Paths v1 as lightweight navigation to `/paths` until a later issue explicitly designs a discovery modal or backend flow.
- The optional explorer must preserve MissionCenter's single-focus contract: due reminders still own focus, future reminders stay quiet until due, and post-safe optional exploration remains calm and non-blocking.
- Root/background coverage is part of RTL/LTR stability: `html`, `body`, `#app`, and `AppContainer` should keep the dark app background and full-height shell so uncovered points never expose a browser/light background.
- Mission focus mode is not the full Mission Context UX system. It improves dashboard focus and mission-family presentation, but complete path -> challenge -> mission breadcrumb/context clarity remains future product work unless code later proves otherwise.
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
- Production-like VPS runtime uses `systemd` service `ringostrike-backend`, working directory `/home/ringo/RingoStrike/backend`, Python venv `/home/ringo/RingoStrike/backend/venv`, and `backend/app.py` with env-driven `FLASK_HOST`, `PORT`, and `FLASK_DEBUG`. Use `FLASK_HOST=127.0.0.1`, `PORT=5005`, and `FLASK_DEBUG=0` on the VPS.
- Mission-level Telegram reminders are delivered by `POST /api/telegram/remind-due-missions`, normally reached publicly as `/api-proxy/api/telegram/remind-due-missions` with `X-Reminder-Token`. The backend selects due reminders, sends through `telegram_service.py`, and sets `mission_logs.reminder_sent_at` only after successful send.
- Reminder diagnostics are available through protected `GET /api/telegram/reminder-diagnostics`, normally reached publicly as `/api-proxy/api/telegram/reminder-diagnostics`. It is visibility-only and must not expose bot tokens, admin tokens, JWT secrets, cookies, raw chat IDs, or private credentials.

## Current Roadmap Position

The project has moved beyond the older v0.3 dashboard/profile milestone. Public identity foundations are now implemented:

- username normalization and reserved names
- public-safe profile URLs at `/u/:username`
- visibility-controlled public profile endpoints
- profile settings and avatar/bio fields
- public consistency and public achievements endpoints

The next highest-value work is launch hardening and operations polish plus QA/microcopy/localization polish for seeded Persian content display: keep reminder automation monitored, verify frontend production builds use `/api-proxy`, run the launch QA checklist, add/maintain mission-path-reminder smoke coverage, add a migration/backup plan, and continue reducing profile/API contract overlap.

# RingoStrike - Changelog

This changelog summarizes recent architecture, product, stabilization, and documentation changes.

---

## Current Development Stage

RingoStrike is currently in:

> Post-MVP Stabilization / Pre-Launch Hardening

The project has moved beyond raw MVP. Core progression identity is implemented. The current focus is reliability, security, testing, documentation, and launch readiness.

---

## Latest Launch-Hardening Updates

### Mission Family Agenda State Hardening

Hardened main/tiny mission family behavior before wider pre-launch testing:

- Treat linked `main` and `tiny` missions as one mission family in Ringo agenda selection.
- A reminded main mission now defers its linked tiny mission instead of immediately suggesting it.
- A reminded tiny mission now defers the parent main mission instead of suggesting the full version again.
- Completing a linked tiny mission keeps today safe without promoting the parent main as another active task.
- Completing a parent main mission suppresses linked tiny reminders from Ringo agenda, MissionCenter family display, and Telegram reminder delivery.
- Kept `bonus` missions separate from substitute-family suppression so bonus reminders/done states remain visible and deliverable.
- Bonus can be offered after completing the parent main mission, but completing the tiny substitute now lands on a calm done-for-today state instead of pushing bonus work.
- Kept raw `mission_logs` statuses intact and avoided schema changes; family state is computed in service/UI selection layers.

### Production Runtime And Reminder Automation Hardening

Documented and stabilized the current VPS launch pattern:

- Backend runs under `systemd` as `ringostrike-backend`.
- Production-like backend runtime uses env-driven `backend/app.py` values: `FLASK_HOST=127.0.0.1`, `PORT=5005`, and `FLASK_DEBUG=0`.
- Nginx serves the Vue production build from `frontend/dist`.
- Public backend access uses `/api-proxy`, with Flask bound to `127.0.0.1:5005`.
- Production frontend builds for the current VPS use `VITE_API_BASE=/api-proxy` and `VITE_BASE=/`.
- Production browser builds must not use `VITE_API_BASE=http://localhost:5005`.
- Added mission-level Telegram reminder delivery for due `mission_logs.status = 'remind_later'` rows.
- Added n8n/cron-compatible protected endpoint `POST /api/telegram/remind-due-missions`.
- Added protected operational diagnostics endpoint `GET /api/telegram/reminder-diagnostics`.
- Added duplicate-send prevention through `mission_logs.reminder_sent_at`.
- Reminder delivery sends through the existing Telegram service and marks `reminder_sent_at` only after successful send.
- Reminder diagnostics report due, scheduled future, already sent, missing Telegram, reminders-disabled, recent logs, and server time without exposing secrets.
- MissionCenter now prompts users to connect or enable Telegram after saving a mission reminder, uses the authenticated connect-code deep link, and shows compact reminder delivery status without exposing automation tokens.
- Stabilized first-run onboarding so incomplete users are routed back to the guided start, interrupted onboarding resumes from the safest useful step, path/challenge choice is intentionally one clear direction, and existing mission data leads to an explicit final handoff instead of silent completion.

### Backend-Backed Path And Mission System

Added the first backend-backed guided progression layer:

- Added `paths`, `user_paths`, `missions`, and `mission_logs` tables.
- Added seed data for MVP growth paths, path-linked challenges, mission definitions, challenge stage metadata, and Ringo intro copy.
- Added path APIs for listing paths, starting/reactivating a user path, and loading path challenges with mission previews and today progress.
- Added mission APIs for today's missions, mark done, remind later, and skip.
- Mission completion now records mission state and delegates to the existing check-in pipeline, preserving current XP, streak, achievement, activity, and stats ownership.
- Added Ringo decision service for state, sprite key, coaching message, and primary/secondary action selection.
- Added backend tests for path/mission behavior and Ringo decision states.

### Mission-Centered Frontend UX

Updated the frontend daily loop around paths and missions:

- Added `/paths` as a full path planning page with path picker, stage-based challenge panels, mission previews, daily summary, and current/secured challenge states.
- Added `MissionCenter.vue` as the first dashboard surface.
- Added `PathSelection.vue` for selecting a path directly from guided mission states.
- Kept the legacy Today Mission card as a fallback when MissionCenter errors or has no actionable mission.
- Mission actions support done, remind later, and skip states.
- RewardMoment now receives mission/check-in results through the dashboard reload path and shows XP, streak, achievements, and guided feature unlock hints.
- Updated navigation to include Paths, desktop/mobile guided nav hints, and a mobile bottom nav focused on Dashboard, Paths, Challenges, and Profile.
- Removed Settings from the visible navigation while profile/settings surfaces remain reachable from Profile.

### Ringo Helper Image Update

Updated Ringo helper presentation:

- Added/updated Ringo helper sprite assets under `frontend/src/assets/ringo/`.
- Added `RingoCoach.vue` as the guided coach component for sprite, message, and action rendering.
- Centralized sprite resolution in `frontend/src/constants/ringoSprites.js`.
- Simplified RewardMoment so it is a focused reward dialog rather than a Ringo image surface.

Known follow-up: `ringoSprites.js` currently references `talking.png` and `victory.png`, but those files are not present in the current asset folder. Restore the assets or remove those imports before production build verification.

### Documentation Refresh

Updated documentation for the latest committed state:

- Project overview now describes paths, missions, MissionCenter, RingoCoach, and the updated guided loop.
- Architecture docs now include `path_routes.py`, `mission_routes.py`, path/mission services, Ringo decisions, and the new data flow.
- Frontend/API contract now documents path and mission endpoints with response shapes.
- API endpoint ownership now records canonical owners for path and mission routes.
- Database schema docs now include path/mission tables, challenge metadata additions, and seed behavior.
- Design system and AI context now describe current navigation, path planning, Ringo helper assets, and mission-first dashboard behavior.

### Guided Progression Frontend Flow

Added the first frontend-only guided progression surfaces:

- Added a Today Mission dashboard focus and guided first-path empty state for users without active enrollments.
- Added lightweight onboarding with identity path selection and suggested challenge mapping.
- Added JoinSuccessMoment after successful challenge joins from onboarding or challenge discovery.
- Added a premium RewardMoment after successful check-ins using existing backend reward data.
- Added frontend-only progressive disclosure and unlock hints for Activity, Achievements, and Public Profile based on existing check-in stats.
- Kept backend APIs, database schema, XP, streak, and achievement logic unchanged.

### VPS API Proxy Deployment Fix

Documented the successful VPS deployment pattern:

- Frontend is served by Nginx from `/home/ringo/RingoStrike/frontend/dist`.
- Flask runs locally on `http://127.0.0.1:5005`.
- Public access is through `http://82.115.24.10`.
- Frontend production env uses `VITE_API_BASE=/api-proxy` and `VITE_BASE=/`.
- Nginx proxies `/api-proxy/` to Flask and keeps Vue routes on the `index.html` fallback.
- Avoided root proxy conflicts where `/challenges` returned backend JSON instead of the Vue route.
- Confirmed login/register, dashboard auth data, challenge list/join/check-in, logout, and API docs after the fix.

### Same-Origin Production API Routing

Hardened frontend/backend deployment configuration for VPS/Nginx serving:

- Updated the shared frontend API client to use same-origin relative requests in production when `VITE_API_BASE` is unset.
- Kept `http://localhost:5005` as a development-only fallback.
- Updated the API explorer to use the shared API client instead of rebuilding hard-coded URLs.
- Added `CORS_ORIGINS` support alongside `FRONTEND_ORIGIN` and `FRONTEND_BASE_URL`.
- Updated env examples and deployment docs to avoid baking localhost into production builds.

### Telegram Reminder Settings

Completed the first user-controlled Telegram reminder foundation:

- Added a `telegram_connections` table for connect codes, chat ids, connection status, and reminder preferences.
- Added authenticated settings endpoints for loading/updating reminder preferences, generating connect codes, and disconnecting Telegram.
- Added a protected bot-bridge endpoint for redeeming connect codes without Telegram Login.
- Updated unchecked enrollment reminders to send only to connected users with enabled daily check-in reminders.
- Added dry-run script support and backend tests for connection flow, preference filtering, checked/unchecked enrollments, and safe missing identity handling.
- Added Profile Settings UI controls and English/Persian translations for Telegram reminder settings.

### Frontend Persian/English i18n

Added frontend-only bilingual UI foundations:

- Installed `vue-i18n` and added English/Persian locale catalogs.
- Added a compact language switcher to the app header.
- Persisted the selected locale in `localStorage.ringostrike_locale`.
- Synced document `lang` and `dir` automatically (`fa` -> `rtl`, `en` -> `ltr`).
- Translated the main active frontend surfaces: auth, dashboard, challenges, enrollment, leaderboard, profile, public profile, and shared loading/error/empty states.
- Kept backend API contracts unchanged and preserved raw backend status values for logic.

### Persian Typography

Added Persian-only Vazirmatn font support:

- Added the local variable WOFF2 font at `frontend/src/assets/fonts/Vazirmatn.woff2`.
- Registered the font in the active global CSS layer.
- Applied Vazirmatn only for `html[lang="fa"] body`.
- Kept English/default typography on the existing system font stack.
- Made native buttons and form controls inherit the active body font.

### Public Identity Privacy Enforcement

Centralized public identity privacy enforcement:

- Added a shared public identity service gate for username normalization, not-found handling, and private-profile blocking.
- Migrated public profile, public consistency, and public achievements services to the shared gate.
- Preserved public endpoint response shapes.
- Added coverage for normalized private-profile blocking and shared not-found responses.

### Validation Boundary Ownership

Tightened mutation endpoint validation boundaries:

- Added a shared JSON-object payload parser for route-level request shape validation.
- Migrated auth, challenge join, profile settings, profile visibility, and profile update mutation routes to the shared parser.
- Kept domain/business validation in services.
- Added focused tests for non-object JSON payload rejection at route boundaries.

### Progression Calculation Ownership

Centralized level/progress calculations through `stats_service.py`:

- Added a canonical `build_level_progress` helper.
- Removed duplicate level/progress calculation logic from dashboard/profile services.
- Preserved existing response field names for active frontend surfaces.
- Added a guard test that catches local level/progress calculation drift in services.

### Duplicate Route Ownership Guard

Added backend route ownership tests that protect API reliability:

- The test fails if an active method/path is registered by more than one endpoint.
- Flask automatic `HEAD` and `OPTIONS` methods are ignored.
- Canonical owners for stats, leaderboard, public profile, and debug routes are asserted.
- This supports the endpoint ownership documentation and helps prevent future route drift.

### API Endpoint Ownership Documentation

Added `docs/API_ENDPOINT_OWNERSHIP.md` to clarify backend endpoint ownership:

- Inventoried public, authenticated, and development-only endpoints.
- Documented route owners, service owners, and active compatibility notes.
- Called out canonical owners for stats, leaderboard, profile settings, public profiles, and debug surfaces.
- Listed duplicate ownership risks to avoid as API reliability work continues.

### Shared API Error Response Convention

Defined and started migrating the shared API error response convention:

- Canonical API errors require `ok: false` and `error`.
- Optional frontend-safe fields are `message` and `details`.
- Added a shared `service_response` adapter for service payloads.
- Migrated selected challenge, stats, debug, leaderboard, and profile settings routes without changing active response shapes.

### Frontend Browser Console Pass

Added a headless browser console smoke pass for major frontend routes:

- Added a Chrome DevTools Protocol script that checks dashboard, challenges, enrollment, leaderboard, private profile, and public profile routes.
- The script provisions a temporary user and enrollment through the backend API.
- Verified the intended local frontend origin, `localhost:5173`, has no uncaught browser errors or failed route requests.
- Documented that Vite fallback ports such as `5174` are outside the backend default CORS allowlist.

### Frontend Responsive UI Hardening

Tightened responsive behavior across core frontend surfaces:

- Added shared min-width guards to app containers and cards.
- Made the consistency heatmap use a more readable mobile grid.
- Improved mobile challenge filters and invite-code controls.
- Let dashboard, private profile, and public profile action buttons wrap cleanly on narrow screens.

### Frontend Public Profile Smoke Coverage

Added a dependency-free frontend smoke test for public profile rendering behavior:

- Extracted public profile loading and display-state mapping into a testable module.
- Verified public profile, consistency, and achievement requests use the shared API client endpoints.
- Verified private and not-found API states map to stable display states.
- Verified representative public profile payloads preserve public activity and identity title data.

### Frontend Profile Loading Smoke Coverage

Added a dependency-free frontend smoke test for private profile loading and settings behavior:

- Extracted profile summary, identity status, and private profile loading logic into a testable module.
- Verified private profile requests use the shared API client endpoints.
- Verified profile settings load/save helpers preserve omitted fields in partial payloads.
- Verified empty and error profile data paths remain stable.

### Frontend Challenge Flow Smoke Coverage

Added a dependency-free frontend smoke test for challenge join and dashboard check-in behavior:

- Extracted join payload, invite-code validation, and join navigation behavior into a testable module.
- Verified challenge joins submit through the shared API client.
- Verified dashboard check-ins apply optimistic progress updates.
- Verified failed check-ins roll back optimistic state and preserve the previous activity feed.

### Frontend Dashboard Loading Smoke Coverage

Added a dependency-free frontend smoke test for dashboard loading behavior:

- Extracted dashboard data loading and summary logic into a testable module.
- Verified dashboard requests use the shared API client endpoints.
- Verified empty, error, ready, and completed challenge summary states.
- Verified representative challenge payloads hydrate card summary metadata.

### Frontend Login Flow Smoke Coverage

Added a dependency-free frontend smoke test for local auth flow behavior:

- Extracted login/register submission logic into a testable module.
- Verified local login posts through the shared API client.
- Verified successful auth redirects to a safe `next` path or dashboard fallback.
- Verified failed auth surfaces backend error text.
- Verified local login does not write tokens to local storage.

### Frontend Router Guard Smoke Coverage

Added a dependency-free frontend smoke test for router guard behavior:

- Extracted the guard into a small testable module.
- Verified explicit public routes skip `/me`.
- Verified authenticated protected routes continue.
- Verified unauthenticated protected routes redirect to `/login?next=...`.

### Leaderboard Ordering Coverage

Added service-level leaderboard tests that verify:

- Overall ordering uses total check-ins, current streak, name, then enrollment id.
- Today ordering uses current streak, total check-ins, name, then enrollment id.
- The documented `tie_breakers` metadata stays aligned with response ordering.

### Auth Callback Fallback Alignment

Updated the frontend auth callback path:

- `frontend/src/lib/api.js` now sends a stored callback token as a Bearer fallback when no explicit Authorization header is set.
- `frontend/src/views/AuthCallback.vue` accepts token/next data from hash or query params.
- Callback redirects are constrained to internal app paths.
- Logout clears the stored callback token along with the backend auth cookie request.

### Frontend Auth Form Hardening

Updated the active local auth form:

- Replaced hard-coded `http://localhost:5005` fetch calls with the shared frontend API client.
- Removed console logging of auth form payloads and responses.
- Preserved HttpOnly cookie-based auth behavior without writing local login tokens to local storage.
- Honored the `next` query parameter after successful login/register.
- Aligned client-side password validation with backend behavior: login requires a password, registration requires at least six characters.
- Removed a stale `frontend/src/views/Untitled` backend snippet and an unused router import.

### Production Readiness

Added production-readiness improvements:

- Updated active auth to use centralized `Config.JWT_SECRET` for JWT signing and verification.
- Added backend `.env.example` refresh for launch configuration.
- Added `docs/DEPLOYMENT_CHECKLIST.md`.
- Added safe `/health/config` endpoint.
- Moved `/health` into a dedicated health blueprint.
- Added environment-driven CORS origin configuration.
- Added production auth cookie configuration coverage.
- Added production secret requirement tests.
- Cleaned duplicated legacy auth logic from `config.py`.
- Added `scripts/smoke_backend.py` for deployment smoke checks.
- Added basic in-memory auth rate limiting for login/register endpoints.
- Added shared API response helper foundation.
- Added malformed JSON coverage for key endpoints.
- Added public profile not-found coverage.
- Enforced `LOCAL_LOGIN_ENABLED` in active local auth routes.
- Hardened profile PATCH behavior so omitted fields are preserved.
- Hardened profile visibility and avatar URL validation.
- Hardened private challenge detail/member visibility.
- Enforced enrollment ownership for leaderboard routes.
- Fixed challenge discovery joined-state behavior for left enrollments.
- Persisted achievement XP through derived stats.
- Made progression surfaces consistently respect `is_counted`.
- Preserved uncounted check-in state in enrollment history.
- Normalized public profile username lookup.

### Testing

Added backend smoke test coverage for:

- Health endpoint.
- Local register/login flow.
- Authenticated `/me`.
- Username validation.
- Reserved username rejection.
- Duplicate username rejection.
- Logout cookie-session clearing.
- Challenge listing.
- Public challenge join.
- Invite-only challenge join.
- Join payload validation for invite-only flow.
- Enrollment detail after join.
- Enrollment reset metadata.
- Daily check-in.
- Duplicate check-in behavior.
- Stats update after check-in.
- Leaderboard rank metadata.
- Leaderboard today status metadata.
- Leaderboard deterministic tie-breaker metadata.
- Public/private profile visibility.
- Public consistency privacy.
- Public achievements privacy.
- Achievement unlock after first check-in.
- Profile update validation.
- Safe config health endpoint.
- Production CORS origin behavior.
- Auth cookie Secure/SameSite/name behavior.
- Production secret requirements.
- Auth register/login rate limiting.
- Shared API response helper shape.
- Malformed JSON handling for auth, profile settings, and challenge join.
- Public profile, consistency, and achievements not-found behavior.
- Protected endpoint missing-auth behavior.
- Protected endpoint invalid bearer-token behavior.
- Profile settings unauthorized PATCH behavior.
- Local auth disabled behavior.
- Profile partial-update preservation.
- Profile visibility invalid payload behavior.
- Protocol-relative avatar URL rejection.
- Private challenge detail/member privacy.
- Leaderboard enrollment ownership.
- Left-enrollment discovery behavior.
- Achievement XP persistence in stats.
- Uncounted check-in handling across progress/history surfaces.
- Public profile username normalization.

Current backend test command:

```bash
./venv/bin/pytest backend/tests
```

Latest local result:

```txt
48 passed
```

### Profile Validation

Added validation for profile and profile settings inputs:

Reject non-string profile name.
Reject overly long bio.
Reject invalid avatar URL schemes.
Accept local avatar paths.
Validate profile visibility values.
Preserve public/private profile behavior.

### Challenge Join Validation

Added validation for challenge join payloads:

Empty JSON remains valid for public challenges.
Non-object JSON is rejected.
Non-string join_code is rejected.
Overly long join_code is rejected.
Existing public and invite-only join behavior is preserved.

### Launch QA Documentation

Added:

docs/LAUNCH_QA_CHECKLIST.md

The checklist covers:

Environment startup.
Backend tests.
Frontend build.
Auth flow.
Dashboard.
Challenge discovery.
Enrollment detail.
Daily reset UI.
Leaderboard.
Achievements.
Profile and public identity.
Activity and consistency.
API docs.
Security checks.
Database checks.
Responsive UI pass.
Browser console pass.
Pre-launch decision checklist.

### Product And UX Updates
#### Challenge Discovery
Updated challenge discovery experience:

Premium challenge discovery hero.
Default launch challenges.
Rich challenge cards.
Member count and member preview where available.
Access, duration, reward, and status metadata.
Invite-code UI preserved.
Dashboard-specific compact challenge card mode.

#### Enrollment Detail

Updated enrollment detail experience:

Premium command-center layout.
Challenge remaining time.
Timeline progress.
Start and end date display.
Daily reset rhythm panel.
Countdown until next reset.
Reset urgency states:
Open window.
Reset approaching.
Final window.
Today secured.
Future reminder-system note for:
Per-challenge reminder time.
Preferred daily window.
Late check-in status.
Normal vs late check-in distinction.
User timezone preferences.

#### Leaderboard

Updated leaderboard behavior and UI:

Overall leaderboard rows include rank.
Today leaderboard rows include rank.
Rows include today check-in status.
Deterministic tie-breakers are exposed.
Full leaderboard UI shows rank and today status.
Today leaderboard section added.
Embedded leaderboard preview remains supported.

#### Default Launch Challenges

Added default launch challenge seeding:

Daily Strike.
Deep Work Sprint.
Move Your Body.
Learn One Thing.
Mind Reset.

Default challenges are inserted only when missing and are not duplicated on repeated app startup.

### Backend Stabilization Updates

#### Stats Endpoint Ownership

Resolved duplicate /me/stats route ownership:

Removed duplicate route from dashboard routes.
Standardized /me/stats through stats_routes.py.
Centralized payload generation in stats_service.py.
#### Auth And Session Frontend Alignment

Aligned frontend session handling with current cookie-based auth behavior:

Removed frontend api.setToken() assumption.
Preserved backend support for cookie and Bearer token auth.
Added logout cookie-session behavior coverage.

#### Debug Endpoint Hardening

SQLite debug endpoints are development-only:

/debug/sqlite/schema/<table>
/debug/sqlite/counts

They are blocked outside development mode.

#### Production Secret Hardening

Production startup now requires safe secrets:

SECRET_KEY
JWT_SECRET

Unsafe fallback behavior was removed from active auth paths.

#### Database Reliability

Improved SQLite reliability:

DB_PATH is launch-location safe.
SQLite foreign keys are enabled per connection.
Frequent-query indexes added for enrollments and check-ins.
Unused sessions table initialization removed.
Legacy local database helpers removed.
Runtime database and Jupyter workspace files are ignored by git.
Test suite uses temporary SQLite databases.
#### Legacy Auth Cleanup

Removed unused duplicate auth-service path:

services/auth_service.py was removed because active route registration still uses backend/auth.py.
#### Documentation Sync

Updated documentation to reflect the actual codebase:

docs/DATABASE_SCHEMA.md
docs/FRONTEND_CONTRACT.md
docs/ROADMAP.md
docs/CHANGELOG.md
docs/LAUNCH_QA_CHECKLIST.md

Documentation now reflects:

Current backend routes.
Current frontend API usage.
Current database initialization behavior.
Stabilization progress.
Launch-readiness priorities.
Expanded backend smoke test coverage.

#### Public Profile And Identity Layer

Implemented and stabilized:

Public profile route /u/:username.
Public profile API /api/public/profile/<username>.
Public consistency API.
Public achievements API.
Profile visibility enforcement.
Avatar URL and bio profile fields.
Profile settings endpoint.
Username normalization.
Reserved username handling.
Public-safe activity filtering.
Privacy coverage for public profile, consistency, and achievements endpoints.

#### Progression System

Implemented:

XP and level calculations.
Dashboard progression stats.
Activity feed.
Achievement definitions.
User achievement unlock tracking.
Achievement XP rewards.
First-check-in achievements.
Streak-based achievement definitions.
Check-in-count achievement definitions.
XP milestone achievement definitions.
Achievement unlock smoke coverage.

#### Core App Foundation

Implemented:

Flask app factory.
Blueprint-based backend routing.
Service-layer backend structure.
Vue 3 + Vite frontend.
Modular frontend components.
JWT cookie/Bearer auth support.
SQLite schema initialization.
Challenges.
Enrollments.
Daily check-ins.
History.
Leaderboards.
Dashboard.
Profile.
Public identity.


Run full launch QA checklist.
Add rate limiting for auth endpoints.
Define shared API error response shape.
Add real migration strategy.
Add deployment/backup checklist.
Add production monitoring/error logging.
Review API naming consistency.
Review profile update endpoint overlap.
Resolve or document remaining GitHub Actions frontend build instability if it reappears.
Run production deployment smoke script after deploy.
Finalize backend/frontend production `.env` values.
Add private/archived challenge access tests.
Add malformed JSON tests for key endpoints.
Add public profile not-found tests.
Add leaderboard exact tie-ordering tests.

Expand shared API response helper usage across existing routes.
Investigate reliable service-level coverage for exact leaderboard tie-ordering.
docs/ROADMAP.md

### Future Product Expansion
Telegram reminders.
Telegram login if still desired.
Android app / widget support.
AI-generated progress insights.
Weekly summaries.
Streak-risk warnings.
Per-challenge reminder time.
Preferred daily check-in window.
Late check-in status.
Public share cards.
OpenGraph profile/achievement previews.
Social inspiration mechanics.

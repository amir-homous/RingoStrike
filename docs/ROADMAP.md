# RingoStrike - Roadmap

## Current Product Stage

RingoStrike is currently in:

> Post-MVP Stabilization / Pre-Launch Hardening

The product has moved beyond raw MVP. The core progression identity system is implemented, and the current priority is reliability, security, documentation, testing, and launch readiness before larger product expansion.

---

## Completed Foundations

### Core App

- Flask backend app factory and blueprint registration.
- Vue 3 + Vite frontend.
- Local auth with JWT cookie/Bearer support.
- SQLite schema initialization.
- Challenge listing, detail, join, enrollment, check-in, history, and leaderboard flows.
- Public and authenticated API surfaces.
- Frontend API docs surface.

### Progression

- XP per check-in.
- Current and longest streak calculations.
- Level and progress percent calculations.
- Dashboard stats.
- Activity feed.
- Achievement definitions and unlock tracking.
- First-check-in achievement rewards.
- Stats sync after check-in.
- Duplicate check-in handling.

### Profile And Public Identity

- Private profile aggregate.
- Dynamic profile title.
- Consistency heatmap data.
- Avatar URL and bio fields.
- Public profile endpoints.
- Public achievements and consistency endpoints.
- Public/private profile visibility.
- Public route `/u/:username`.
- Username normalization and reserved username list.
- Profile settings endpoint.
- Profile update validation for name, bio, avatar URL, and visibility.

### Challenge And Social Momentum

- Default launch challenge seeding.
- Challenge discovery UI polish.
- Challenge card compact mode for dashboard.
- Member count and member preview on challenge discovery.
- Leaderboard rank metadata.
- Deterministic leaderboard tie-breakers.
- Today leaderboard data.
- Leaderboard UI showing rank and today check-in status.
- Enrollment UI with challenge remaining time.
- Enrollment UI with daily reset rhythm and urgency states.

### Stabilization Progress Completed

- Removed duplicate `GET /me/stats` route ownership.
- Standardized `/me/stats` through `stats_routes.py` and `stats_service.py`.
- Aligned `frontend/src/stores/session.js` with cookie-based auth.
- Removed frontend `api.setToken()` assumption.
- Gated SQLite debug endpoints behind development environment config.
- Required production `SECRET_KEY` and `JWT_SECRET`.
- Centralized active JWT signing/verification on `Config.JWT_SECRET`.
- Removed unsafe JWT secret fallback from active auth code.
- Added frequent-query indexes for `checkins` and `enrollments`.
- Made SQLite `DB_PATH` launch-location safe.
- Enabled SQLite foreign key enforcement per database connection.
- Removed unused legacy `auth_service.py`.
- Removed unused legacy database helper functions.
- Removed unused `sessions` table initialization.
- Added `.gitignore` coverage for local runtime files.
- Synced `DATABASE_SCHEMA.md` with current database implementation.
- Synced `ApiDocsView.vue` with current backend endpoints.
- Added challenge join payload validation.
- Added profile update/profile settings validation.
- Added launch QA checklist.
- Added backend `.env.example` launch-ready environment documentation.
- Added deployment readiness checklist.
- Added safe `/health/config` production-readiness endpoint.
- Added environment-driven production CORS origin support.
- Added production auth cookie configuration coverage.
- Added production secret requirement tests.
- Cleaned duplicated legacy auth logic from `config.py`.
- Added backend deployment smoke script.
- Added basic in-memory auth rate limiting for login/register endpoints.
- Added shared API response helper foundation.
- Added malformed JSON handling coverage for key endpoints.
- Added public profile not-found coverage.
- Enforced local auth disable behavior through `LOCAL_LOGIN_ENABLED`.
- Preserved omitted profile fields on partial profile updates.
- Hardened profile visibility payload validation.
- Rejected protocol-relative avatar URLs.
- Blocked private challenge detail/member reads.
- Enforced enrollment ownership on leaderboard routes.
- Ignored left enrollments during challenge discovery joined-state checks.
- Included achievement XP rewards in persisted stats.
- Made progression surfaces consistently ignore uncounted check-ins.
- Preserved uncounted check-in state in enrollment history.
- Normalized public profile username lookups.
- Hardened the active local auth form to use the shared API client, remove auth payload console logging, honor post-login redirects, and match backend password validation.
- Removed stale frontend route/file clutter around the legacy login import and stray `Untitled` view snippet.
- Aligned auth callback token storage with the shared API client Bearer fallback, constrained callback redirects to internal paths, and cleared stored callback tokens on logout.


### Backend Test Coverage Added

- Health endpoint smoke test.
- Local register/login `/me` auth smoke test.
- Username validation and reserved username smoke test.
- Duplicate username smoke test.
- Logout cookie-session smoke test.
- Challenge list/join/check-in core loop smoke test.
- Invite-only challenge join smoke test.
- Duplicate check-in behavior smoke test.
- Stats update after check-in smoke test.
- Public/private profile visibility smoke test.
- Public consistency privacy smoke test.
- Public achievements privacy smoke test.
- Achievement unlock after first check-in smoke test.
- Profile validation smoke test.
- Enrollment reset metadata smoke test.
- Leaderboard rank/tie-breaker smoke test.
- Temporary SQLite test database setup.
- Safe `/health/config` smoke test.
- Production CORS origin smoke test.
- Production auth cookie configuration smoke tests.
- Production secret requirement tests.
- Auth register/login rate limiting smoke tests.
- Shared API response helper tests.
- Auth malformed JSON payload tests.
- Profile settings malformed JSON payload test.
- Challenge join malformed JSON payload test.
- Public profile not-found smoke tests.
- Protected endpoint missing-auth smoke tests.
- Protected endpoint invalid bearer-token smoke tests.
- Profile settings unauthorized PATCH smoke tests.
- Local auth disabled smoke test.
- Profile partial-update preservation smoke test.
- Profile visibility invalid payload smoke test.
- Private challenge detail/member privacy smoke tests.
- Leaderboard enrollment ownership smoke test.
- Left-enrollment challenge discovery smoke test.
- Achievement XP persistence smoke test.
- Uncounted check-in progression/history smoke tests.
- Public profile username normalization smoke test.
- Expand protected-endpoint auth failure coverage as new authenticated routes are added.



---

## Now: Stabilization Milestone

These items should happen before expanding product scope:

- Keep invalid challenge join payload coverage as route behavior evolves.
- Add tests for `/auth/logout` edge cases if token blacklist/session invalidation is introduced later.
- Resolve or document remaining GitHub Actions frontend build instability if it reappears.
- Run deployment smoke script after every production/pre-launch deployment.
- Finalize production `.env` values for backend and frontend.
- Normalize API naming conventions where practical (`/api/...` vs non-`/api/...`).
- Add a real migration strategy instead of ad hoc table changes in app startup.
- Review profile update endpoints and reduce overlap where possible.
- Public challenge/member endpoint visibility has been hardened for private challenges; keep intended policy documented as product scope evolves.
- Run full `docs/LAUNCH_QA_CHECKLIST.md` before release candidate.
- Expand shared API response helper usage across existing routes.
- Investigate reliable service-level coverage for exact leaderboard tie-ordering.


---

## Next Sprint: Quality And Reliability

### Backend Reliability

- Add tests for reset edge cases when user timezone support is introduced.
- Expand leaderboard ordering tests if tie-breaker behavior changes.
- Expand archived/private challenge tests if challenge lifecycle behavior changes.
- Expand profile visibility tests if new visibility states are added.
- Add tests for auth failure behavior on protected endpoints.
- Expand malformed JSON coverage to any remaining mutation endpoints.
- Add reliable service-level tests for leaderboard exact tie scenarios.



### Frontend Reliability

- Add smoke test for router guard.
- Add smoke test for login flow.
- Add smoke test for dashboard loading.
- Add smoke test for challenge join/check-in flow.
- Add smoke test for profile loading.
- Add smoke test for public profile rendering.
- Run responsive UI pass using launch QA checklist.
- Run browser console pass on major routes.

### API Reliability

- Define a shared API error response convention.
- Keep backward-compatible response shapes for active frontend usage.
- Document endpoint ownership clearly.
- Avoid duplicate route ownership.
- Avoid duplicate progression calculations outside `stats_service.py`.
- Keep validation close to route/service boundaries.
- Preserve privacy enforcement on public identity endpoints.

---

## Product Expansion: Social Momentum

After stabilization:

- Public share cards for profiles and achievements.
- Public profile OpenGraph metadata if server-side rendering or a share proxy is added.
- Challenge discovery improvements with categories/tags.
- Safer public activity controls.
- Social follow or inspiration mechanics that avoid toxic competition.
- Public achievement sharing.
- Profile identity polish for shareable progression.
- Better leaderboard identity states and optional public rank surfaces.

---

## Product Expansion: Automation And Insights

After launch-readiness foundations:

- Telegram login route if Telegram auth is still desired.
- Telegram reminders.
- Per-challenge reminder time.
- Preferred daily check-in window.
- Late check-in status.
- Normal vs late check-in distinction.
- User timezone preferences.
- Weekly summaries.
- Streak-risk warnings.
- AI-generated progress insights.
- n8n workflow integration hardening.
- Notification-ready check-in reminders.
- Progress recap automation.

---

## Launch Readiness

Before first public launch:

- Production deployment plan.
- Environment/config checklist.
- Database backup process.
- Database migration process.
- Monitoring and error logging.
- Privacy policy.
- Public profile visibility controls review.
- Demo data and onboarding.
- Performance pass for dashboard/profile query load.
- Security pass for auth, debug routes, validation, and public endpoints.
- Manual QA checklist pass for core user flow.
- Frontend production build verification.
- Backend smoke test verification.
- Safe config health verification.
- Production CORS origin verification.
- Auth cookie production settings verification.
- Deployment smoke script execution.

Required commands:

```bash
cd backend
py -m pytest -q
```

```bash
cd frontend
npm run build
```

```bash
python scripts/smoke_backend.py --base-url http://localhost:5005
```

## Recommended Next Issue

The next highest-value issue is:

Tests: investigate and add reliable leaderboard tie-ordering coverage.

Suggested target:

- Review `leaderboard_service.py` sorting behavior.
- Add service-level or database-level test coverage instead of brittle route-level assumptions.
- Verify exact tie ordering by total check-ins, current streak, name, and enrollment id.
- Preserve current route behavior and response shape.

---

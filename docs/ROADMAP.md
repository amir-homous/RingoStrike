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

---

## Now: Stabilization Milestone

These items should happen before expanding product scope:

- Add tests for invalid challenge join payloads if not already covered separately from invite-only flow.
- Add tests for `/auth/logout` edge cases if token blacklist/session invalidation is introduced later.
- Add frontend smoke tests or manual QA pass for router guard, login, dashboard, challenge join, check-in, profile, and public profile rendering.
- Add rate limiting for auth endpoints.
- Normalize API naming conventions where practical (`/api/...` vs non-`/api/...`).
- Add structured error codes and a shared API error shape.
- Add a real migration strategy instead of ad hoc table changes in app startup.
- Review profile update endpoints and reduce overlap where possible.
- Review public challenge/member endpoints and confirm intended visibility.
- Run full `docs/LAUNCH_QA_CHECKLIST.md` before release candidate.

---

## Next Sprint: Quality And Reliability

### Backend Reliability

- Add tests for reset edge cases when user timezone support is introduced.
- Add tests for leaderboard ordering with exact tie scenarios.
- Add tests for archived challenges and inactive challenge joins.
- Add tests for private challenge join rejection.
- Add tests for malformed JSON across important endpoints.
- Add tests for profile visibility invalid payloads.
- Add tests for public profile not-found behavior.
- Add tests for auth failure behavior on protected endpoints.

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

Required commands:

```bash
cd backend
py -m pytest -q
cd frontend
npm run build
Recommended Next Issue

The next highest-value issue is:

Tests: add private and inactive challenge access coverage.

Suggested target:

Private challenge appears only when already enrolled.
Private challenge join returns challenge_private.
Archived challenge join returns challenge_inactive.
Inactive/archived challenges do not appear in normal discovery.
Public challenge detail remains readable.

---
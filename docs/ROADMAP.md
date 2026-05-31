# RingoStrike - Roadmap

## Completed Foundations

### Core App

- Flask backend app factory and blueprint registration.
- Vue 3 + Vite frontend.
- Local auth with JWT cookie/Bearer support.
- SQLite schema initialization.
- Challenge, enrollment, check-in, history, and leaderboard flows.

### Progression

- XP per check-in.
- Current and longest streak calculations.
- Level and progress percent calculations.
- Dashboard stats.
- Activity feed.
- Achievement definitions and unlock tracking.

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

## Now: Stabilization Milestone

These items should happen before expanding product scope:

- Add backend tests for auth, username validation, challenge joining, duplicate check-ins, stats sync, achievements, and public profile privacy.
- Add frontend smoke tests for router guard, login, dashboard load, check-in flow, and public profile rendering.
- Add rate limiting for auth endpoints.
- Add input validation for profile avatar URLs and challenge join payloads.
- Normalize API naming conventions where practical (`/api/...` vs non-`/api/...`).
- Add structured error codes and a shared API error shape.
- Add a real migration strategy instead of ad hoc table changes in app startup.
- Review profile update endpoints and reduce overlap where possible.
- Review public challenge/member endpoints and confirm intended visibility.

## Next Sprint: Quality And Reliability

### Backend Reliability

- Add tests for `POST /auth/register`.
- Add tests for `POST /auth/login`.
- Add tests for `POST /auth/logout`.
- Add tests for username normalization and reserved username validation.
- Add tests for `POST /challenges/:id/join`.
- Add tests for duplicate daily check-ins.
- Add tests for stats sync after check-in.
- Add tests for achievement unlock evaluation.
- Add tests for public/private profile visibility.

### Frontend Reliability

- Add smoke test for router guard.
- Add smoke test for login flow.
- Add smoke test for dashboard loading.
- Add smoke test for challenge join/check-in flow.
- Add smoke test for profile loading.
- Add smoke test for public profile rendering.

### API Reliability

- Define a shared API error response convention.
- Keep backward-compatible response shapes for active frontend usage.
- Document endpoint ownership clearly.
- Avoid duplicate route ownership.
- Avoid duplicate progression calculations outside `stats_service.py`.

## Product Expansion: Social Momentum

After stabilization:

- Public share cards for profiles and achievements.
- Public profile OpenGraph metadata if server-side rendering or a share proxy is added.
- Challenge discovery improvements.
- Safer public activity controls.
- Social follow or inspiration mechanics that avoid toxic competition.
- Public achievement sharing.
- Profile identity polish for shareable progression.

## Product Expansion: Automation And Insights

After launch-readiness foundations:

- Telegram login route if Telegram auth is still desired.
- Telegram reminders.
- Weekly summaries.
- Streak-risk warnings.
- AI-generated progress insights.
- n8n workflow integration hardening.
- Notification-ready check-in reminders.
- Progress recap automation.

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
- Security pass for auth, debug routes, and public endpoints.
- Manual QA checklist for core user flow.

## Current Product Stage

RingoStrike is currently in:

> Post-MVP Stabilization / Pre-Launch Hardening

The product has moved beyond a raw MVP. The core progression identity system is implemented, and the current priority is making the architecture reliable, secure, documented, and testable before adding larger product expansion features.

## Recommended Next Issue

The next highest-value issue is:

> Add backend tests for auth and check-in reliability.

Suggested first testing target:

- Register
- Login
- `/me`
- Join challenge
- Check-in
- Duplicate check-in handling
- `/me/stats`

This gives the project a safety net before more refactors or product expansion.
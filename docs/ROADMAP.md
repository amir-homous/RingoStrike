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

## Now: Stabilization Milestone

These items should happen before expanding product scope:

- Remove or merge duplicate `GET /me/stats` route implementations.
- Fix `frontend/src/stores/session.js` by either adding `api.setToken()` or removing token-store assumptions.
- Decide whether `services/auth_service.py` replaces `backend/auth.py` or should be deleted.
- Gate `/debug/sqlite/*` behind development-only config or authentication.
- Require production `JWT_SECRET` and `SECRET_KEY`; remove unsafe fallback behavior for deploy builds.
- Add indexes for frequent `checkins` queries.
- Add a real migration strategy instead of ad hoc table changes in app startup.
- Align `frontend/src/views/ApiDocsView.vue` with current endpoints.

## Next Sprint: Quality And Reliability

- Add backend tests for auth, username validation, challenge joining, duplicate check-ins, stats sync, achievements, and public profile privacy.
- Add frontend smoke tests for router guard, login, dashboard load, check-in flow, and public profile rendering.
- Normalize API naming conventions (`/api/...` vs non-`/api/...`).
- Make `DB_PATH` launch-location safe by resolving a consistent absolute path.
- Add structured error codes and a shared API error shape.
- Add rate limiting for auth endpoints.
- Add input validation for profile avatar URLs and challenge join payloads.

## Product Expansion: Social Momentum

After stabilization:

- Public share cards for profiles and achievements.
- Public profile OpenGraph metadata if server-side rendering or a share proxy is added.
- Challenge discovery improvements.
- Safer public activity controls.
- Social follow or inspiration mechanics that avoid toxic competition.

## Product Expansion: Automation And Insights

- Telegram login route if Telegram auth is still desired.
- Telegram reminders.
- Weekly summaries.
- Streak-risk warnings.
- AI-generated progress insights.
- n8n workflow integration hardening.

## Launch Readiness

- Production deployment plan.
- Environment/config checklist.
- Database backup/migration process.
- Monitoring and error logging.
- Privacy policy and public profile controls.
- Demo data and onboarding.
- Performance pass for dashboard/profile query load.

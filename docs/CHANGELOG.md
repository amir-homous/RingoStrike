# RingoStrike - Changelog

This changelog summarizes recent architecture, product, stabilization, and documentation changes.

---

## Current Development Stage

RingoStrike is currently in:

> Post-MVP Stabilization / Pre-Launch Hardening

The project has moved beyond raw MVP. Core progression identity is implemented. The current focus is reliability, security, testing, documentation, and launch readiness.

---

## Latest Launch-Hardening Updates

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

Current backend test command:

```bash
cd backend
py -m pytest -q
Profile Validation

Added validation for profile and profile settings inputs:

Reject non-string profile name.
Reject overly long bio.
Reject invalid avatar URL schemes.
Accept local avatar paths.
Validate profile visibility values.
Preserve public/private profile behavior.
Challenge Join Validation

Added validation for challenge join payloads:

Empty JSON remains valid for public challenges.
Non-object JSON is rejected.
Non-string join_code is rejected.
Overly long join_code is rejected.
Existing public and invite-only join behavior is preserved.
Launch QA Documentation

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
Product And UX Updates
Challenge Discovery

Updated challenge discovery experience:

Premium challenge discovery hero.
Default launch challenges.
Rich challenge cards.
Member count and member preview where available.
Access, duration, reward, and status metadata.
Invite-code UI preserved.
Dashboard-specific compact challenge card mode.
Enrollment Detail

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
Leaderboard

Updated leaderboard behavior and UI:

Overall leaderboard rows include rank.
Today leaderboard rows include rank.
Rows include today check-in status.
Deterministic tie-breakers are exposed.
Full leaderboard UI shows rank and today status.
Today leaderboard section added.
Embedded leaderboard preview remains supported.
Default Launch Challenges

Added default launch challenge seeding:

Daily Strike.
Deep Work Sprint.
Move Your Body.
Learn One Thing.
Mind Reset.

Default challenges are inserted only when missing and are not duplicated on repeated app startup.

Backend Stabilization Updates
Stats Endpoint Ownership

Resolved duplicate /me/stats route ownership:

Removed duplicate route from dashboard routes.
Standardized /me/stats through stats_routes.py.
Centralized payload generation in stats_service.py.
Auth And Session Frontend Alignment

Aligned frontend session handling with current cookie-based auth behavior:

Removed frontend api.setToken() assumption.
Preserved backend support for cookie and Bearer token auth.
Added logout cookie-session behavior coverage.
Debug Endpoint Hardening

SQLite debug endpoints are development-only:

/debug/sqlite/schema/<table>
/debug/sqlite/counts

They are blocked outside development mode.

Production Secret Hardening

Production startup now requires safe secrets:

SECRET_KEY
JWT_SECRET

Unsafe fallback behavior was removed from active auth paths.

Database Reliability

Improved SQLite reliability:

DB_PATH is launch-location safe.
SQLite foreign keys are enabled per connection.
Frequent-query indexes added for enrollments and check-ins.
Unused sessions table initialization removed.
Legacy local database helpers removed.
Runtime database and Jupyter workspace files are ignored by git.
Test suite uses temporary SQLite databases.
Legacy Auth Cleanup

Removed unused duplicate auth-service path:

services/auth_service.py was removed because active route registration still uses backend/auth.py.
Documentation Sync

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
Public Profile And Identity Layer

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
Progression System

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
Core App Foundation

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
Remaining Known Work
Before First Public Launch
Run full launch QA checklist.
Add rate limiting for auth endpoints.
Define shared API error response shape.
Add real migration strategy.
Add deployment/backup checklist.
Add production monitoring/error logging.
Review API naming consistency.
Review profile update endpoint overlap.
Add frontend smoke tests or complete manual QA pass.
Add private/archived challenge access tests.
Add malformed JSON tests for key endpoints.
Add public profile not-found tests.
Add leaderboard exact tie-ordering tests.
Future Product Expansion
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
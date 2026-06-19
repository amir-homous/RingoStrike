# RingoStrike - Technical Analysis

## A) System Health

### Architecture Quality Score

Overall score: 8/10.

Rationale:

- Strong modular direction with Flask blueprints and service files.
- Progression, achievement, activity, profile, and public profile systems are mostly separated.
- Path/mission work follows the existing route/service pattern and correctly delegates mission completion to the existing check-in pipeline.
- Frontend component grouping is healthy and feature-oriented.
- Recent stabilization removed several transitional problems: duplicate stats route ownership, unused auth-service duplication, old session-table initialization, public debug exposure, and the broken Pinia session-store assumption.
- Recent privacy/progression fixes tightened profile validation, private challenge visibility, leaderboard ownership, left-enrollment discovery, uncounted-check-in handling, achievement XP persistence, local-login disabling, and public username lookup normalization.
- Remaining technical debt is mostly around auth route/service separation, API naming consistency, migration/backup strategy, and frontend smoke coverage.

### Coupling Issues

- `backend/auth.py` combines decorators, JWT helpers, cookie helpers, and route handlers.
- Public profile aggregation calls private `get_profile()`, which syncs stats and queries private profile data before projecting public fields.
- Activity feed is derived from check-ins and achievements on read rather than persisted as an event table; this is simple now but couples feed behavior to current query logic.
- Frontend views call backend endpoints directly; Pinia is not consistently used as a stable state boundary.
- Guided progression now spans path state, mission logs, enrollments, check-ins, and dashboard reward display. This is appropriate for the product, but it increases the need for end-to-end smoke coverage around duplicate mission/check-in submissions.

### Duplication Hotspots

- Active auth code still combines route handling and auth helpers in `backend/auth.py`.
- Profile update paths overlap: `/api/me/profile/settings`, `/api/profile/visibility`, and `/api/profile` update related user profile fields.
- API route naming is mixed across `/me/...`, `/api/me/...`, and `/api/profile...`.
- Ringo sprite resolution is split between backend decision keys and frontend asset imports. The current sprite assets include `talking.png` and `victory.png`; keep `frontend/src/constants/ringoSprites.js`, asset filenames, and backend `sprite_key` values aligned.

### Complexity Analysis

- Backend complexity is moderate. Services are understandable, but several endpoints trigger multiple per-item queries.
- Frontend complexity is moderate. Component split is good, but state ownership is inconsistent.
- Database complexity is low-to-moderate. Schema is small and indexed for common check-in/enrollment access, but lacks an explicit migration framework.

## B) Security Review

### Auth And Configuration

Recently fixed:

- `backend/auth.py` now uses centralized `Config.JWT_SECRET` for JWT signing and verification.
- `backend/config.py` requires `SECRET_KEY` and `JWT_SECRET` outside development.
- Active local register/login routes respect `LOCAL_LOGIN_ENABLED`.
- Login/register have basic in-memory rate limiting.
- Debug endpoints are blocked outside development mode.

Remaining risks:

- JWT sessions are stateless with no revocation list or server-side session invalidation.
- Auth helpers and auth route handlers still live together in `backend/auth.py`.

Medium:

- Cookie `secure` defaults to false unless `JWT_COOKIE_SECURE=1`.
- `SameSite=Lax` is reasonable for local dev but should be reviewed for deployment topology.
- Public challenge detail and members endpoints are unauthenticated; this may be intended, but it should be explicitly decided.

### API Risks

- Profile avatar URLs reject invalid schemes and protocol-relative URLs.
- Profile bio/name updates trim and validate type/length, but do not apply deeper content moderation rules.
- `debug_service.sqlite_schema()` uses a table allowlist, and route access is development-only.
- No central request schema validation layer exists.

### DB Exposure Risks

- Local `backend/users.db` exists in the tree; ensure real user data is not committed or distributed.
- SQLite database path is anchored through `backend/database.py` when `DB_PATH` is not provided.
- Foreign key enforcement is enabled per database connection.

## C) Performance Issues

### Backend Bottlenecks

- `list_challenges()` performs member count and preview queries per challenge, creating N+1 query behavior.
- `leaderboard_service.enrollment_leaderboard()` performs count and date queries per enrollment.
- `activity_service.get_activity_feed()` recalculates streak/level events from date lists on read.
- Profile aggregation calls stats sync before reading profile fields, so profile reads can write to the database.

### Frontend Rendering Issues

- Dashboard loads multiple endpoint groups and per-enrollment detail calls, which can create request bursts.
- API docs view contains executable API testing logic in a large view component.
- Component-local fetches are duplicated across dashboard/profile rather than cached in a shared store.

### Database Inefficiencies

Missing or recommended indexes:

- `users(lower(username))` cannot be indexed directly in older SQLite forms without an expression index; current public profile lookups use `lower(username) = lower(?)`.

Already present:

- `checkins(user_id, date)`
- `checkins(enrollment_id, date)`
- `checkins(challenge_id)`
- `enrollments(user_id, status)`
- `enrollments(challenge_id, status)`

## D) Scalability Analysis

### What Breaks Under Load

- SQLite write contention will become a bottleneck with frequent check-ins, stats syncs, and achievement unlocks.
- Read-time derived activity/streak calculations will become expensive as check-in history grows.
- Leaderboards will slow down for large challenges due to per-enrollment queries.
- Public profiles can trigger multiple backend calls and derived queries per page load.
- Stateless JWT without revocation makes account compromise/session invalidation difficult.

### What Needs Redesign

- Move from SQLite to PostgreSQL before multi-user production scale.
- Add migrations with Alembic or another explicit migration tool.
- Introduce persisted activity/progression events if timeline becomes a core social surface.
- Use aggregate queries for leaderboard and challenge member counts.
- Define a single profile settings/update API.

## E) Code Quality

### Service Layer Cleanliness

Strengths:

- Most feature logic is in services.
- `stats_service.py` has clear pure calculation helpers.
- Public services enforce visibility checks before returning public data.
- Username validation is centralized.

Weaknesses:

- Some services write during read endpoints (`sync_user_stats` during profile/dashboard reads).
- Auth route handlers and auth helper logic are still grouped in one module.
- Some files use dense one-line formatting, reducing maintainability.
- Error shapes are mostly consistent but not formally centralized.

### Route/Controller Separation

Mostly good:

- Challenge, dashboard, enrollment, history, leaderboard, public profile, and profile settings routes are thin.

Needs improvement:

- Active auth routes live in `backend/auth.py` rather than a normal route module/service split.

### Naming Consistency

Issues:

- Mixed API prefixes: some endpoints are `/me/...`, some are `/api/me/...`, and some are `/api/profile...`.
- Public `members` response uses `telegram_username` for `users.username`, which now appears to be a local/public username field.
- `ANALYS.md` filename matches the user request, but `ANALYSIS.md` would be clearer if renaming is allowed later.

## F) Prioritized Action Plan

### Completed Stabilization

0. Frontend-only seeded content display localization is implemented for known mission/path/challenge copy through helpers such as `missionDisplayCopy.js` and `ringoContentLocalization.js`; Persian onboarding challenge selection and Persian MissionCenter seeded mission display were visually checked, `npm --prefix frontend run build` passed, `npm --prefix frontend run test:router` passed, and `git diff --check` passed. Unknown/custom backend content still falls back by design, and localization key coverage must be maintained as seeded content expands.
1. Production secret requirements are enforced outside development.
2. Active JWT signing/verification uses centralized `Config.JWT_SECRET`.
3. Debug endpoints are blocked outside development.
4. `GET /me/stats` is standardized through `stats_routes.py` and `stats_service.py`.
5. `frontend/src/stores/session.js` is aligned with cookie-based auth.
6. Public/private profile visibility and public profile not-found/privacy behavior have smoke coverage.
7. Private challenge detail/member endpoints and leaderboard ownership have privacy coverage.
8. Progression stats, history, consistency, activity, and achievements respect uncounted check-ins.
9. Backend tests currently pass locally: `153 passed` with `cd backend && ./venv/bin/pytest tests`.

### Important - Next Sprint

1. Add path/mission frontend smoke coverage for `/paths`, MissionCenter loading, mission done/remind/skip, focus-mode dashboard gating, and duplicate mission/check-in behavior.
2. Consolidate active auth code into route + service modules.
3. Add or evaluate an index strategy for public username lookup.
4. Continue expanding shared request/response validation patterns.
5. Normalize profile update endpoints into one clear contract.
7. Add explicit database migrations instead of ad hoc startup migrations.
8. Keep public challenge/member visibility documented as the product policy evolves.
9. Run a QA/microcopy/localization polish pass for seeded Persian content display, especially onboarding challenge copy, MissionCenter seeded mission copy, missing fallback behavior, and localization helper coverage as seed content expands.

### Optional - Future Improvement

1. Persist timeline events instead of deriving all activity on read.
2. Add PostgreSQL migration path.
3. Add OpenGraph/share-card infrastructure for public profiles.
4. Add Telegram auth route if Telegram login remains in scope.
5. Introduce shared frontend API/query composables for dashboard and profile data.
6. Add observability: structured logs, request IDs, error tracking, and slow-query logging.

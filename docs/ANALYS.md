# RingoStrike - Technical Analysis

## A) System Health

### Architecture Quality Score

Overall score: 7/10.

Rationale:

- Strong modular direction with Flask blueprints and service files.
- Progression, achievement, activity, profile, and public profile systems are mostly separated.
- Frontend component grouping is healthy and feature-oriented.
- Some technical debt remains from transitional refactors: duplicate auth logic, duplicate stats route, unused session table, API docs drift, and a broken Pinia session store integration.

### Coupling Issues

- `backend/auth.py` combines decorators, JWT helpers, cookie helpers, and route handlers.
- `services/auth_service.py` duplicates auth behavior but is not active.
- Public profile aggregation calls private `get_profile()`, which syncs stats and queries private profile data before projecting public fields.
- Activity feed is derived from check-ins and achievements on read rather than persisted as an event table; this is simple now but couples feed behavior to current query logic.
- Frontend views call backend endpoints directly; Pinia is not consistently used as a stable state boundary.

### Duplication Hotspots

- Auth logic: `backend/auth.py` and `backend/services/auth_service.py`.
- Stats route: `dashboard_routes.py` and `stats_routes.py` both define `GET /me/stats`.
- Level calculation differs between `stats_service.py` and `dashboard_service.py`; one uses nonlinear thresholds and the other uses 100-point levels.
- Profile update paths overlap: `/api/me/profile/settings`, `/api/profile/visibility`, and `/api/profile` update related user profile fields.

### Complexity Analysis

- Backend complexity is moderate. Services are understandable, but several endpoints trigger multiple per-item queries.
- Frontend complexity is moderate. Component split is good, but state ownership is inconsistent.
- Database complexity is low-to-moderate. Schema is small but lacks migrations and important indexes.

## B) Security Review

### Auth Vulnerabilities

Critical:

- `JWT_SECRET` has a development fallback in `backend/auth.py`; production with fallback would make tokens forgeable.
- `SECRET_KEY` and `JWT_SECRET` also have defaults in `backend/config.py`.

High:

- Debug endpoints are public and expose schema/count metadata.
- No rate limiting on login/register.
- JWT sessions are stateless with no revocation list despite a `sessions` table existing.

Medium:

- Cookie `secure` defaults to false unless `JWT_COOKIE_SECURE=1`.
- `SameSite=Lax` is reasonable for local dev but should be reviewed for deployment topology.
- Public challenge detail and members endpoints are unauthenticated; this may be intended, but it should be explicitly decided.

### API Risks

- `/api/profile` accepts `avatar_url` with only length trimming; URL/path validation is not enforced.
- Profile bio/name updates trim length but do not apply explicit content rules beyond that.
- `debug_service.sqlite_schema()` uses a table allowlist, which reduces SQL injection risk, but the endpoint should still not be public.
- No central request schema validation layer exists.

### DB Exposure Risks

- Local `backend/users.db` exists in the tree; ensure real user data is not committed or distributed.
- SQLite database path depends on process working directory by default.
- Foreign keys are declared but SQLite requires `PRAGMA foreign_keys = ON` per connection to enforce them; current connection helper does not enable it.

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

- `checkins(user_id, date)`
- `checkins(enrollment_id, date)`
- `checkins(challenge_id)`
- `enrollments(user_id, status)`
- `enrollments(challenge_id, status)`
- `users(lower(username))` cannot be indexed directly in older SQLite forms without an expression index; current public profile lookups use `lower(username) = lower(?)`.

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
- Consolidate stats calculation into one service and one API contract.
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
- Auth service duplication creates uncertainty about canonical implementation.
- Some files use dense one-line formatting, reducing maintainability.
- Error shapes are mostly consistent but not formally centralized.

### Route/Controller Separation

Mostly good:

- Challenge, dashboard, enrollment, history, leaderboard, public profile, and profile settings routes are thin.

Needs improvement:

- Active auth routes live in `backend/auth.py` rather than a normal route module/service split.
- Duplicate `/me/stats` route should be resolved.

### Naming Consistency

Issues:

- Mixed API prefixes: some endpoints are `/me/...`, some are `/api/me/...`, and some are `/api/profile...`.
- Public `members` response uses `telegram_username` for `users.username`, which now appears to be a local/public username field.
- `ANALYS.md` filename matches the user request, but `ANALYSIS.md` would be clearer if renaming is allowed later.

## F) Prioritized Action Plan

### Critical - Must Fix Now

1. Set mandatory production secrets and fail startup when `JWT_SECRET`/`SECRET_KEY` are defaults outside development.
2. Protect or remove `/debug/sqlite/schema/:table` and `/debug/sqlite/counts` in non-development environments.
3. Resolve duplicate `GET /me/stats` route and standardize on the `stats_service.py` calculation model.
4. Fix `frontend/src/stores/session.js` or remove it if cookie-only auth is the intended architecture.
5. Add tests for public/private profile visibility to prevent data leaks.

### Important - Next Sprint

1. Consolidate active auth code into route + service modules and remove unused duplication.
2. Add database indexes for check-ins, enrollments, and public username lookup.
3. Add request validation for profile updates and auth payloads.
4. Update `frontend/src/views/ApiDocsView.vue` to match real backend routes.
5. Add rate limiting for auth endpoints.
6. Enable SQLite foreign keys on connection or document why they are not used.
7. Normalize profile update endpoints into one clear contract.

### Optional - Future Improvement

1. Persist timeline events instead of deriving all activity on read.
2. Add PostgreSQL migration path.
3. Add OpenGraph/share-card infrastructure for public profiles.
4. Add Telegram auth route if Telegram login remains in scope.
5. Introduce shared frontend API/query composables for dashboard and profile data.
6. Add observability: structured logs, request IDs, error tracking, and slow-query logging.

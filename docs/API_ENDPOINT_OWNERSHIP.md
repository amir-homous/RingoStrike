# API Endpoint Ownership

This document records the current owner for active backend endpoints.

Purpose:

- Keep route ownership explicit.
- Avoid duplicate route registration.
- Help frontend work find the canonical backend surface.
- Separate public, authenticated, and development-only endpoints.

Current convention:

- Route modules own HTTP method/path registration and request boundary validation.
- Services own database reads/writes and response payload assembly.
- `backend/utils/api_response.py` owns shared success/error response helpers.
- Active frontend route usage is documented in `docs/FRONTEND_CONTRACT.md`.

## Public Endpoints

| Endpoint | Route owner | Service owner | Notes |
| --- | --- | --- | --- |
| `GET /health` | `routes/health_routes.py` | none | Basic liveness check. |
| `GET /health/config` | `routes/health_routes.py` | `config.py` | Safe production-readiness flags only. Must not expose secrets. |
| `POST /auth/register` | `auth.py` | `auth.py`, `services/username_service.py`, `services/rate_limit_service.py` | Public local auth registration. Sets auth cookie and returns bearer fallback token. |
| `POST /auth/login` | `auth.py` | `auth.py`, `services/rate_limit_service.py` | Public local auth login. Sets auth cookie and returns bearer fallback token. |
| `POST /auth/logout` | `auth.py` | `auth.py` | Clears auth cookie. No token blacklist exists currently. |
| `GET /challenges/public` | `routes/challenge_routes.py` | `services/challenge_service.py` | Public challenge discovery subset. |
| `GET /challenges/<challenge_id>` | `routes/challenge_routes.py` | `services/challenge_service.py` | Public for public/invite-only active challenges. Private challenges are blocked. |
| `GET /challenges/<challenge_id>/members` | `routes/challenge_routes.py` | `services/challenge_service.py` | Public member list for public/invite-only active challenges. Private challenges are blocked. |
| `GET /paths` | `routes/path_routes.py` | `services/path_service.py` | Optional auth; returns active paths and user path status when authenticated. |
| `GET /paths/<path_id>/challenges` | `routes/path_routes.py` | `services/path_service.py` | Optional auth; returns path challenge stages, mission previews, and authenticated progress state. |
| `GET /api/public/profile/<username>` | `routes/public_profile_routes.py` | `services/public_profile_service.py` | Respects profile visibility. |
| `GET /api/public/profile/<username>/achievements` | `routes/public_profile_routes.py` | `services/public_achievement_service.py` | Respects profile visibility. |
| `GET /api/public/profile/<username>/consistency` | `routes/public_profile_routes.py` | `services/public_consistency_service.py` | Respects profile visibility. |

## Authenticated Endpoints

| Endpoint | Route owner | Service owner | Notes |
| --- | --- | --- | --- |
| `GET /me` | `routes/dashboard_routes.py` | `services/dashboard_service.py` | Canonical current-user endpoint used by router guard and session bootstrap. |
| `GET /me/challenges` | `routes/dashboard_routes.py` | `services/dashboard_service.py` | Dashboard challenge list. |
| `GET /me/activity` | `routes/dashboard_routes.py` | `services/activity_service.py` | Authenticated activity feed. |
| `GET /me/achievements` | `routes/dashboard_routes.py` | `services/achievement_service.py` | Authenticated achievement list. |
| `GET /me/profile` | `routes/dashboard_routes.py` | `services/profile_service.py` | Private profile aggregate. |
| `GET /me/consistency` | `routes/dashboard_routes.py` | `services/consistency_service.py` | Authenticated consistency heatmap data. |
| `GET /me/stats` | `routes/stats_routes.py` | `services/stats_service.py` | Canonical stats endpoint. Do not reintroduce duplicate stats ownership in dashboard routes. |
| `POST /paths/<path_id>/start` | `routes/path_routes.py` | `services/path_service.py` | Starts/reactivates a user path only. The frontend may separately join the first path challenge. |
| `GET /me/today-missions` | `routes/mission_routes.py` | `services/mission_service.py`, `services/ringo_decision_service.py` | Dashboard MissionCenter source. Returns RingoCoach decision and available daily missions. |
| `POST /me/missions/<mission_id>/done` | `routes/mission_routes.py` | `services/mission_service.py`, `services/enrollment_service.py` | Writes mission log and delegates to existing check-in pipeline. |
| `POST /me/missions/<mission_id>/remind-later` | `routes/mission_routes.py` | `services/mission_service.py` | Route validates JSON object shape; service validates ISO-ish reminder time. |
| `POST /me/missions/<mission_id>/skip` | `routes/mission_routes.py` | `services/mission_service.py` | Writes skipped mission log. Does not check in. |
| `GET /challenges` | `routes/challenge_routes.py` | `services/challenge_service.py` | Authenticated challenge discovery with joined state. |
| `POST /challenges/<challenge_id>/join` | `routes/challenge_routes.py` | `services/challenge_service.py` | Route validates JSON/join-code shape; service owns join policy. |
| `GET /me/enrollments/<enrollment_id>` | `routes/challenge_routes.py` | `services/challenge_service.py` | Enrollment detail used by enrollment view and dashboard metadata hydration. |
| `POST /me/challenges/<enrollment_id>/checkin` | `routes/enrollment_routes.py` | `services/enrollment_service.py` | Check-in submission. |
| `GET /me/challenges/<enrollment_id>/history` | `routes/history_routes.py` | `services/history_service.py` | Enrollment check-in history. |
| `GET /me/enrollments/<enrollment_id>/leaderboard` | `routes/leaderboard_routes.py` | `services/leaderboard_service.py` | Enrollment ownership is enforced before leaderboard data is returned. |
| `GET /api/me/profile/settings` | `routes/profile_settings_routes.py` | `services/profile_settings_service.py` | Profile settings form load. |
| `PATCH /api/me/profile/settings` | `routes/profile_settings_routes.py` | `services/profile_settings_service.py` | Profile settings update. |
| `GET /api/me/telegram/settings` | `routes/telegram_routes.py` | `services/telegram_connection_service.py` | Current Telegram connection state and reminder preferences. |
| `POST /api/me/telegram/connect-code` | `routes/telegram_routes.py` | `services/telegram_connection_service.py` | Generates a short-lived Telegram connect code for the authenticated user. |
| `PATCH /api/me/telegram/settings` | `routes/telegram_routes.py` | `services/telegram_connection_service.py` | Updates reminder preference toggles. |
| `POST /api/me/telegram/disconnect` | `routes/telegram_routes.py` | `services/telegram_connection_service.py` | Disconnects the authenticated user's Telegram chat. |
| `PATCH /api/profile/visibility` | `routes/public_profile_routes.py` | `services/profile_visibility_service.py` | Legacy visibility-specific update surface. Prefer `/api/me/profile/settings` for active settings UI. |
| `PATCH /api/profile` | `routes/public_profile_routes.py` | `services/profile_update_service.py` | Legacy profile update surface. Prefer `/api/me/profile/settings` for active settings UI where possible. |

## Protected Automation Endpoints

| Endpoint | Route owner | Service owner | Notes |
| --- | --- | --- | --- |
| `POST /api/telegram/connect` | `routes/telegram_routes.py` | `services/telegram_connection_service.py` | Bot bridge endpoint protected by `X-Reminder-Token`; redeems a connect code and stores the Telegram chat id. |
| `POST /api/telegram/remind-unchecked-test` | `routes/telegram_routes.py` | `services/reminder_service.py` | Admin-token protected test reminder surface. |

## Development-Only Endpoints

| Endpoint | Route owner | Service owner | Notes |
| --- | --- | --- | --- |
| `GET /debug/sqlite/schema/<table>` | `routes/debug_routes.py` | `services/debug_service.py` | Enabled only when `FLASK_ENV=development`; table allowlist is enforced. |
| `GET /debug/sqlite/counts` | `routes/debug_routes.py` | `services/debug_service.py` | Enabled only when `FLASK_ENV=development`. |

## Canonical Ownership Notes

- Auth route handlers still live in `backend/auth.py`; no separate `routes/auth_routes.py` currently owns active auth paths.
- `GET /me/stats` belongs to `routes/stats_routes.py` and `services/stats_service.py`.
- `GET /me/enrollments/<id>/leaderboard` belongs to `routes/leaderboard_routes.py` and `services/leaderboard_service.py`.
- Public profile read surfaces belong to `routes/public_profile_routes.py`; profile visibility rules belong in public/profile services.
- Path discovery/start belongs to `routes/path_routes.py`; daily mission state belongs to `routes/mission_routes.py`.
- Mission completion must keep using `services/enrollment_service.py` for check-in side effects so stats, streaks, achievements, and activity stay canonical.
- Active profile settings UI should prefer `/api/me/profile/settings`; older `/api/profile` and `/api/profile/visibility` routes remain for compatibility.
- Debug routes must stay gated outside development.

## Duplicate Ownership Risks To Avoid

- Do not register another `GET /me/stats` route in dashboard or profile modules.
- Do not add parallel leaderboard endpoints without preserving enrollment ownership enforcement.
- Do not add public profile endpoints that bypass `profile_visibility`.
- Do not duplicate check-in/progression calculations in route modules; keep them in services.
- Do not add separate XP/streak/achievement logic for missions; route mission completion through the existing check-in/progression services.
- Do not let path start implicitly hide challenge join behavior without documenting the frontend/backend split.
- Do not return production debug data outside development-gated debug routes.

# RingoStrike - Frontend/API Contract

## API Client

Frontend API client: `frontend/src/lib/api.js`.

```js
baseURL = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? "http://localhost:5005" : "")
withCredentials = true
timeout = 15000
```

Production builds default to same-origin relative API requests when `VITE_API_BASE` is unset. Local development can still set `VITE_API_BASE=http://localhost:5005`. If a production build accidentally contains a loopback API base such as `http://localhost:5005` or `http://127.0.0.1:5005`, the client falls back to same-origin because browser loopback would point at the user's machine, not the VPS.

For the current VPS deployment at `http://82.115.24.10`, set:

```env
VITE_API_BASE=/api-proxy
VITE_BASE=/
```

Nginx serves the Vue production build from `frontend/dist` and proxies `/api-proxy/` to the local Flask backend. Do not use an nginx `rewrite` rule for this deployment. Use a trailing slash on `proxy_pass` so nginx strips the `/api-proxy/` location prefix and forwards the remaining backend path:

```nginx
location /api-proxy/ {
    proxy_pass http://127.0.0.1:5005/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Examples:

- `/api-proxy/health` forwards to Flask `/health`
- `/api-proxy/api/telegram/remind-due-missions` forwards to Flask `/api/telegram/remind-due-missions`
- `/api-proxy/me` forwards to Flask `/me`

Vue routes should continue to use the SPA fallback:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

Only omit `VITE_API_BASE` when backend root routes do not conflict with frontend routes. This VPS requires `/api-proxy` because `/challenges` is both a frontend route and a backend API route; proxying `/challenges` directly returns backend JSON instead of the Vue page.

The backend supports HttpOnly cookie auth and Bearer token fallback. The frontend mainly relies on cookies because `withCredentials` is enabled.

`frontend/src/stores/session.js` is aligned with this cookie-based model and uses `/me` plus `/auth/logout`; it does not require `api.setToken()`.

## Auth Endpoints

### `POST /auth/register`

Auth: public.

Request:

```json
{
  "username": "player_name",
  "password": "secret123",
  "name": "Player Name",
  "email": "player@example.com"
}
```

Validation:

- username is normalized lowercase
- username must be 3-24 chars, `a-z`, `0-9`, underscore only
- reserved usernames are rejected
- password must be at least 6 chars
- email must contain `@` if provided

Success `201`:

```json
{
  "ok": true,
  "user_id": 1,
  "username": "player_name",
  "access_token": "jwt"
}
```

Also sets HttpOnly auth cookie.

### `POST /auth/login`

Auth: public.

Request:

```json
{
  "username": "player_name",
  "password": "secret123"
}
```

Success `200`: same shape as register and sets cookie.

### `POST /auth/logout`

Auth: public in route code; clears auth cookie.

Success:

```json
{ "ok": true }
```

### `GET /me`

Auth: required.

Local-auth success:

```json
{
  "ok": true,
  "user_id": 1,
  "username": "player_name",
  "name": "Player Name",
  "email": "player@example.com",
  "auth_method": "local",
  "registered": true
}
```

Telegram-shaped response exists in code for Telegram claims, but no active Telegram login route is registered.

## Health

### `GET /health`

Auth: public.

```json
{ "ok": true }
```

### `GET /health/config`

Auth: public.

Returns a safe production-readiness snapshot with boolean/configuration flags. It must not expose secrets, tokens, full database paths, or integration credentials.

## Challenges

### `GET /challenges/public`

Auth: public.

Returns active public challenges:

```json
{
  "ok": true,
  "items": [
    {
      "challenge_id": 1,
      "name": "Challenge",
      "visibility": "Public",
      "status": "Active",
      "description": "...",
      "duration_days": 30
    }
  ]
}
```

### `GET /challenges`

Auth: required.

Returns active public/invite-only challenges plus joined private challenges visible to the user.

Item shape:

```json
{
  "challenge_id": 1,
  "name": "Challenge",
  "description": "...",
  "visibility": "public",
  "status": "active",
  "duration_days": 30,
  "members_count": 3,
  "members_preview": ["Alice"],
  "is_joined": true,
  "enrollment_id": 10,
  "needs_code": false
}
```

### `GET /challenges/:challenge_id`

Auth: public in route code.

Returns challenge details including visibility, status, duration, max members, proof flag, check-in method, goal type, tags, member count, and whether a join code is required.

### `GET /challenges/:challenge_id/members?limit=20&offset=0`

Auth: public in route code.

Returns active member rows:

```json
{
  "ok": true,
  "challenge_id": 1,
  "items": [
    {
      "enrollment_id": 10,
      "enrollment_status": "Active",
      "role": "Member",
      "user_id": 1,
      "user_name": "Alice",
      "username": "alice",
      "telegram_username": "alice"
    }
  ],
  "has_more": false
}
```

`username` is the canonical local/public username. `telegram_username` is kept as a backward-compatible alias for older frontend/API consumers.

### `POST /challenges/:challenge_id/join`

Auth: required.

Request:

```json
{ "join_code": "optional" }
```

Success:

```json
{
  "ok": true,
  "mode": "created",
  "enrollment_id": 10,
  "challenge_id": 1
}
```

`mode` can be `created`, `reactivated`, or `existing`.

Frontend join UX currently consumes this same response to show JoinSuccessMoment before routing users to the dashboard or enrollment detail. Do not add a separate onboarding/recommendation endpoint for the v1 guided start flow; onboarding and challenge discovery both reuse this join contract.

## First-Run Onboarding

Onboarding is a frontend-guided flow that reuses existing authenticated APIs instead of introducing a separate onboarding backend contract. Authenticated users without a local onboarding completion or skip decision are routed to `/onboarding` before the dashboard. Backend path, joined-challenge, and today-mission data may move the user to the final handoff step, but they must not silently mark onboarding complete.

The onboarding flow stores the selected identity path in `localStorage.ringostrike_identity_path`, resumes at welcome/path selection when no path is stored, resumes at the recommended challenge step when a path is stored, and shows a final handoff when a first challenge or mission already exists. Completion is written only after the final handoff CTA. Skip remains local and intentional through `localStorage.ringostrike_onboarding_skipped`.

## Paths And Missions

Path and mission APIs are the current backend-backed guided progression contract. They sit above the existing challenge/enrollment/check-in system and should not duplicate XP, streak, achievement, or activity calculations.

### `GET /paths`

Auth: optional.

Returns active growth paths. When a user is authenticated, each item includes that user's path state.

```json
{
  "ok": true,
  "items": [
    {
      "path_id": 1,
      "key": "body",
      "title": "Body Momentum",
      "description": "Build energy...",
      "icon": "B",
      "color": "#6ee5ff",
      "sort_order": 1,
      "status": "Active",
      "user_status": "Active",
      "current_stage": 1
    }
  ]
}
```

### `POST /paths/:path_id/start`

Auth: required.

Request body can be an empty JSON object.

Success:

```json
{
  "ok": true,
  "mode": "created",
  "user_path_id": 1,
  "path": {
    "path_id": 1,
    "key": "body",
    "title": "Body Momentum",
    "user_status": "Active",
    "current_stage": 1
  }
}
```

`mode` can be `created`, `existing`, or `reactivated`.

Active frontend behavior in `PathSelection.vue`: after starting a path, the frontend loads the path challenges and joins the first challenge when available through `POST /challenges/:challenge_id/join`. The path API itself does not enroll the user in a challenge.

### `GET /paths/:path_id/challenges`

Auth: optional.

Returns a path summary, path-linked active challenges, mission previews, joined state, and today's mission progress for authenticated users.

```json
{
  "ok": true,
  "date": "2026-06-06",
  "path": {
    "path_id": 1,
    "key": "body",
    "title": "Body Momentum",
    "user_status": "Active"
  },
  "summary": {
    "joined_challenges": 1,
    "today_checked_challenges": 0,
    "today_missions_done": 0,
    "today_missions_total": 1
  },
  "items": [
    {
      "challenge_id": 1,
      "name": "Move Your Body",
      "description": "...",
      "visibility": "Public",
      "status": "Active",
      "duration_days": 7,
      "goal_type": "Daily",
      "tags": ["body"],
      "difficulty": "beginner",
      "stage": 1,
      "estimated_days": 7,
      "ringo_intro": "Start small...",
      "is_joined": true,
      "enrollment_id": 10,
      "enrollment_status": "Active",
      "today_checked": false,
      "total_checkins": 2,
      "today_missions_done": 0,
      "today_missions_total": 1,
      "missions": [
        {
          "mission_id": 1,
          "key": "move_10",
          "title": "Move for 10 minutes",
          "description": "...",
          "mission_type": "daily",
          "difficulty": "easy",
          "is_core": true,
          "xp_reward": 10,
          "order_index": 1,
          "suggested_time": "morning",
          "unlock_after_days": 0,
          "mission_intensity": "main",
          "estimated_minutes": 10,
          "parent_mission_id": null,
          "unlocks_in_days": 0,
          "available_today": true,
          "ringo_message": "...",
          "today_status": "pending",
          "reminder_at": null,
          "xp_earned": 0
        }
      ]
    }
  ]
}
```

`today_status` is `locked` when a mission is not available yet because the user is not joined or the mission's `unlock_after_days` has not elapsed.

### `GET /me/today-missions`

Auth: required.

Returns daily missions available for active enrollments and a RingoCoach decision object.

```json
{
  "ok": true,
  "date": "2026-06-06",
  "ringo": {
    "state": "today_not_started",
    "sprite": "focus",
    "sprite_key": "focus",
    "message": "Today's mission is ready...",
    "primary_action": {
      "label": "Start: Move for 10 minutes",
      "type": "mission",
      "mission_id": 1
    },
    "secondary_action": {
      "label": "View path details",
      "type": "route",
      "to": "/enrollment/10"
    }
  },
  "missions": [
    {
      "mission_id": 1,
      "key": "move_10",
      "title": "Move for 10 minutes",
      "description": "...",
      "mission_type": "daily",
      "difficulty": "easy",
      "is_core": true,
      "xp_reward": 10,
      "order_index": 1,
      "suggested_time": "morning",
      "unlock_after_days": 0,
      "mission_intensity": "main",
      "estimated_minutes": 10,
      "parent_mission_id": null,
      "ringo_message": "...",
      "status": "pending",
      "reminder_at": null,
      "reminder_sent_at": null,
      "done_at": null,
      "skipped_at": null,
      "reminder_set_at": null,
      "status_updated_at": null,
      "xp_earned": 0,
      "challenge_id": 1,
      "challenge_name": "Move Your Body",
      "enrollment_id": 10,
      "path_id": 1,
      "path_title": "Body Momentum"
    }
  ]
}
```

Current `ringo.state` values include `new_user_no_path`, `path_selected_no_challenge`, `no_mission_today`, `today_completed`, `today_reminded`, `today_skipped`, `today_in_progress`, `returning_after_break`, `streak_at_risk`, and `today_not_started`.

Current action types include `route`, `mission`, `mission_reminder`, and `dismiss`.

Mission event timestamp fields are additive and nullable. They are derived from the current Ringo day mission log only:

- `done_at`: UTC timestamp when the current-day log was last written as `done`.
- `skipped_at`: UTC timestamp when the current-day log was last written as `skipped`.
- `reminder_set_at`: UTC timestamp when the current-day log was last written as `remind_later`.
- `status_updated_at`: UTC timestamp for the current-day mission log update, regardless of status.
- `reminder_sent_at`: UTC timestamp set after the backend Telegram delivery job successfully sends the scheduled mission reminder.

For timeline placement, use `reminder_at` for reminder-set missions because it is the scheduled reminder time. Use `done_at` for completed missions and `skipped_at` for skipped missions. If a timestamp is missing, keep the mission in an untimed UI state rather than inventing a time.

MissionCenter may combine `reminder_at`, `reminder_sent_at`, and authenticated Telegram settings to display frontend-only reminder delivery states such as scheduled, due, sent, Telegram not connected, or Telegram reminders off. The frontend must not call protected automation endpoints or receive `X-Reminder-Token`.

### `GET /me/ringo/today`

Auth: required.

Returns Ringo Brain v1 guidance for the Ringo-first dashboard. This endpoint is additive and does not replace `/me/today-missions` or the existing mission mutation APIs.

```json
{
  "ok": true,
  "date": "2026-06-10",
  "ringo": {
    "user_state": "today_not_started",
    "mood": "focused",
    "tone": "warm_no_shame",
    "message": "Today's mission is ready: Move for 10 minutes. One clear step is enough.",
    "sprite_key": "focus"
  },
  "mission": {
    "mission_id": 1,
    "key": "move_10",
    "title": "Move for 10 minutes",
    "description": "...",
    "mission_intensity": "main",
    "estimated_minutes": 10,
    "parent_mission_id": null,
    "xp_reward": 10,
    "status": "pending",
    "reminder_at": null,
    "done_at": null,
    "skipped_at": null,
    "reminder_set_at": null,
    "status_updated_at": null,
    "challenge_id": 1,
    "challenge_name": "Move Your Body",
    "enrollment_id": 10,
    "path_id": 1,
    "path_title": "Body Momentum"
  },
  "actions": [
    {
      "type": "start",
      "label": "Start",
      "mission_id": 1
    },
    {
      "type": "remind_later",
      "label": "Remind me later",
      "mission_id": 1
    }
  ],
  "progress": {
    "today_saved": false,
    "current_streak": 3,
    "total_checkins": 12
  },
  "ringo_day": {
    "date": "2026-06-10",
    "next_reset_at": "2026-06-11T00:00:00Z",
    "reset_basis": "utc",
    "server_now": "2026-06-10T20:52:00Z"
  },
  "agenda": {
    "today_saved": false,
    "next_action_type": "primary_mission",
    "next_mission_id": 1,
    "next_mission_title": "Move for 10 minutes",
    "next_reminder_at": null,
    "pending_count": 1,
    "reminded_count": 0,
    "skipped_count": 0,
    "done_count": 0,
    "has_optional_work": false
  },
  "reward_sequence": {
    "type": "standard",
    "available": true,
    "placeholder": true
  },
  "fallback": {
    "used": false,
    "reason": null
  }
}
```

Supported action `type` values in v1 are `start`, `remind_later`, `make_smaller`, `too_tired`, and `skip_today`.

The `ringo_day` object is additive and describes the backend daily reset boundary used by Ringo Brain. Current reset basis is UTC/server date:

- `date`: current Ringo day as a UTC date.
- `next_reset_at`: next UTC midnight reset timestamp.
- `reset_basis`: currently `utc`.
- `server_now`: backend UTC timestamp when the response was built.

Frontend clients should remain compatible when `ringo_day` is missing. When present, reminder labels can compare reminder times to `next_reset_at`; if a reminder lands after the next reset, copy should clarify that it is after the user's next Ringo daily reset rather than relying only on local calendar-day wording.

Current daily mission reminders should be scheduled before `ringo_day.next_reset_at`. The frontend should block reminder options that cross this boundary when metadata is available, and the backend rejects cross-reset reminder writes with `reminder_after_next_reset`.

The `agenda` object is additive and summarizes the user's daily mission situation. Existing frontend consumers can ignore it safely. `next_action_type` is selected with family-aware priority. Linked `main` and `tiny` missions are one substitute family: a future reminder on either defers the family, a completed tiny satisfies the parent main for today, and a completed main suppresses linked tiny reminder actions. `bonus` missions are not substitute variants; they remain independently visible/actionable optional work after the required family is safe.

When today is not saved, priority is:

1. `due_reminder`
2. `primary_mission`
3. `upcoming_reminder`
4. `skipped_optional`
5. `optional_mission`

When today is saved, priority is:

1. `due_reminder`
2. `upcoming_reminder`
3. `skipped_optional`
4. `optional_mission`
5. `done_for_today`

Pending bonus missions are auto-suggested as `optional_mission` after the parent `main` mission is completed. If the user completed the `tiny` substitute instead, the agenda should prefer a calm `done_for_today` state unless a bonus reminder, skipped optional state, or other higher-priority item already exists.

Agenda fields:

- `today_saved`: mirrors whether today's required step is already safe.
- `next_action_type`: nearest useful next step using the priority order above.
- `next_mission_id`: mission id for the next action, or `null`.
- `next_mission_title`: mission title for the next action, or an empty string.
- `next_reminder_at`: reminder timestamp only for reminder next actions, otherwise `null`.
- `pending_count`, `reminded_count`, `skipped_count`, `done_count`: counts from today's mission list.
- `has_optional_work`: `true` when remaining work exists but should be treated as optional/paused/no-pressure context.

When `today_saved` is `true`, unresolved reminders and skipped missions may still appear in `agenda` as optional context unless they belong to an already satisfied main/tiny family. This does not make them required and does not change mission mutation behavior.

Frontend guidance:

- Use this endpoint to lead the Ringo-first dashboard with Ringo mood, message, suggested mission, action choices, Today Saved state, and reward sequence placeholder.
- Continue using `/me/missions/:mission_id/done`, `/remind-later`, and `/skip` for mission mutations.
- Keep `/me/today-missions` compatibility while the dashboard migrates progressively.

### MissionCenter Frontend Focus Behavior

Mission focus mode is a frontend display contract between `MissionCenter.vue` and `Dashboard.vue`; it is not a backend API contract and does not change mission, XP, streak, achievement, or check-in ownership.

`MissionCenter.vue` emits `focus-state-change` with a local payload shaped like:

```json
{
  "active": true,
  "reason": "primary_mission",
  "todaySafe": false,
  "hasActionableSuggestion": true
}
```

Current local `reason` values include `loading`, `rest_mode`, `first_run`, `due_reminder`, `tiny_flow`, `optional_bonus`, `primary_mission`, `completion_unacknowledged`, `future_reminder_only`, and `done_for_today`. These values are for frontend gating only and should not be treated as stable backend enum values.

While focus mode is active, `Dashboard.vue` hides the large dashboard sections and shows:

- `MissionCenter`
- `CompactProgressStrip`, using existing `/me/stats` data for level, XP progress, and streak
- no duplicate progression calculations

`MissionCenter.vue` keeps mission timeline/status details collapsed by default during focus mode. Users can reveal them explicitly with `Show mission status`. `Finish for today` enters a calm frontend-only Rest Mode card, optionally showing nearest future reminder timing from existing mission `reminder_at` values. `Show dashboard` emits `show-dashboard` so `Dashboard.vue` can reveal the full dashboard with reduced-motion-safe styling.

Mission Context UX Phase 1 is now implemented as a frontend-only clarity layer. The current implementation improves focus, family-aware display, completion tone, and mission-card context clarity, but it does not implement the full future Mission Context UX system, contextual reward sequence, Telegram mission-specific deep-link restoration, or a backend mission context read model.

### MissionContextPanel Display Contract

`frontend/src/components/missions/MissionContextPanel.vue` is a display-only child surface used by `MissionCenter.vue` for mission clarity.

It can display, when available:

- path/challenge breadcrumb from existing mission fields such as `path_title` and `challenge_name`
- mission intensity/time from `mission_intensity` and `estimated_minutes`
- “What counts” instruction copy
- “Why this helps” copy
- tiny mission no-shame framing
- bonus optional framing

Contract rules:

- It must not call mission mutation endpoints.
- It must not calculate XP, streaks, achievements, check-ins, or progression.
- It must not own MissionCenter action hierarchy.
- It must not replace RingoCoach, RewardMoment, CompactProgressStrip, Rest Mode, or dashboard focus gating.
- It must tolerate missing optional context fields by hiding or simplifying display text instead of inventing data.
- English and Persian visible text belongs in the frontend i18n locale files, not backend response shapes.

`MissionCenter.vue` remains the owner of mission actions such as done, remind later, skip, finish for today, and show dashboard. Existing mission mutation APIs remain unchanged.

### `POST /me/missions/:mission_id/done`

Auth: required.

Marks a mission done for today, writes/updates `mission_logs`, and calls the existing enrollment check-in service. This endpoint can therefore return an existing-check-in result if the enrollment was already checked in today.

Success:

```json
{
  "ok": true,
  "mission": {
    "mission_id": 1,
    "title": "Move for 10 minutes",
    "status": "done",
    "date": "2026-06-06",
    "xp_earned": 10,
    "enrollment_id": 10,
    "challenge_id": 1,
    "reminder_at": null
  },
  "checkin": {
    "ok": true,
    "enrollment_id": 10,
    "rewards": {}
  },
  "checkin_status_code": 200,
  "reward_sequence": [
    {
      "type": "ringo_message",
      "title": "Nice work.",
      "text": "You did the small step. That counts.",
      "mood": "proud"
    },
    {
      "type": "mission_completed",
      "title": "Move for 10 minutes",
      "text": "This mission is marked done."
    },
    {
      "type": "xp_earned",
      "title": "XP earned",
      "value": "+10 XP",
      "amount": 10
    },
    {
      "type": "today_saved",
      "title": "Today is safe.",
      "text": "You did enough for today. Anything else is optional.",
      "mood": "celebrating"
    },
    {
      "type": "next_choice",
      "title": "Choose your pace.",
      "text": "You can stop here, or continue only if you have energy."
    }
  ]
}
```

`reward_sequence` is additive. Existing consumers can ignore it and continue reading `ok`, `mission`, `checkin`, and `checkin_status_code`.

The `today_saved` step is included only for the first completion that satisfies today: either a completed `main` mission or a completed linked `tiny` mission whose `parent_mission_id` points to a main mission. If today was already saved before the current completion, the backend does not repeat `today_saved`; it returns bonus/optional progress copy using supported reward step types. Parent main missions are not automatically marked done when a linked tiny mission is completed.

Frontend `MissionCenter.vue` emits the returned payload to `Dashboard.vue`, which reloads dashboard data and shows RewardMoment from the returned check-in reward data.

### `POST /me/missions/:mission_id/remind-later`

Auth: required.

Request:

```json
{ "reminder_at": "2026-06-06T18:00:00Z" }
```

Validation:

- request body must be a JSON object
- `reminder_at` is required
- value must be ISO-parseable after replacing `Z` with `+00:00`
- value must be at most 80 characters
- value must be before the current Ringo day `next_reset_at`; otherwise the endpoint returns `400` with `reminder_after_next_reset`

Success returns the same `mission` shape as mission done with `status: "remind_later"` and no check-in payload.

### `POST /me/missions/plan-reminders`

Auth: required.

Creates gentle reminder times for current-day pending missions that do not already have reminders. Existing `done`, `skipped`, and `remind_later` mission logs are preserved. Planned reminder times are always after server now and before the current Ringo day `next_reset_at`.

Success response:

```json
{
  "ok": true,
  "scheduled": [
    {
      "mission_id": 12,
      "title": "Read five pages",
      "reminder_at": "2026-06-15T10:30:00Z",
      "reason": "gentle_spacing"
    }
  ],
  "unscheduled": [
    {
      "mission_id": 18,
      "title": "Bonus movement",
      "reason": "not_enough_time_before_reset"
    }
  ],
  "summary": {
    "scheduled_count": 1,
    "unscheduled_count": 1
  },
  "ringo_day": {
    "date": "2026-06-15",
    "next_reset_at": "2026-06-16T00:00:00Z",
    "reset_basis": "utc",
    "server_now": "2026-06-15T09:00:00Z"
  }
}
```

### `POST /me/missions/:mission_id/plan-reminder`

Auth: required.

Applies one Ringo-suggested reminder time for a single mission. The mission must be `pending` or already `remind_later`; existing reminders may be replaced. The reminder time is chosen by the same planner rules as the global planner and must be after server now and before `ringo_day.next_reset_at`.

Returns `400` with `no_safe_reminder_time` if no safe reminder slot exists before reset.

Success response includes the applied `mission` and a `scheduled` object:

```json
{
  "ok": true,
  "scheduled": {
    "mission_id": 12,
    "title": "Read five pages",
    "reminder_at": "2026-06-15T10:30:00Z",
    "reason": "gentle_spacing"
  },
  "mission": {
    "mission_id": 12,
    "status": "remind_later",
    "reminder_at": "2026-06-15T10:30:00Z"
  }
}
```

### `POST /me/missions/:mission_id/skip`

Auth: required.

Request may be empty or may include an optional stable reason key:

```json
{ "reason": "too_tired" }
```

Supported reason keys are `too_tired`, `no_time`, `too_hard`, `not_relevant`, `disliked`, and `other`. If provided, `reason` must be a string, is trimmed, and is length-limited.

Marks the mission skipped for today and returns the same `mission` shape with `status: "skipped"` plus `skip_reason` when available. It does not call check-in.

## Enrollment, Check-ins, History, Leaderboard

### `GET /me/challenges`

Auth: required.

Dashboard challenge list response:

```json
{
  "ok": true,
  "date": "2026-05-30",
  "user": {
    "name": "Alice",
    "stats": {
      "total_points": 100,
      "current_streak": 3,
      "longest_streak": 7
    }
  },
  "challenges": [
    {
      "enrollment_id": 10,
      "enrollment_name": "Challenge",
      "status": "Active",
      "challenge_id": 1,
      "today_checked": false
    }
  ]
}
```

### `GET /me/enrollments/:enrollment_id`

Auth: required.

Returns enrollment summary, challenge details, recent logs, `today_checked`, `total_checkins`, and `current_streak`.

### `POST /me/challenges/:enrollment_id/checkin`

Auth: required.

Creates or updates today's check-in for an active enrollment.

Success:

```json
{
  "ok": true,
  "message": "Check-in recorded",
  "rewards": {
    "xp_total": 100,
    "achievements": [],
    "achievement_xp_reward": 0
  }
}
```

Inactive enrollment error `403`:

```json
{ "ok": false, "error": "enrollment_inactive" }
```

### `GET /me/challenges/:enrollment_id/history?days=30`

Auth: required.

Returns up to 120 days of per-day status.

### `GET /me/enrollments/:enrollment_id/leaderboard`

Auth: required.

Returns leaderboard for the challenge connected to the enrollment:

```json
{
  "ok": true,
  "overall": [
    {
      "name": "Alice",
      "username": "alice",
      "enrollment_id": 10,
      "total_checkins": 12,
      "current_streak": 4
    }
  ],
  "today": []
}
```

## Stats, Activity, Achievements, Profile

### `GET /me/stats`

Auth: required.

Owned by `stats_routes.py` and generated through `stats_service.build_user_stats_payload()`.

Response:

```json
{
  "ok": true,
  "stats": {
    "current_streak": 3,
    "level": 2,
    "longest_streak": 7,
    "next_level_xp": 200,
    "progress_percent": 20,
    "total_checkins": 12,
    "total_points": 120,
    "xp": 20
  },
  "user": { "id": 1, "name": "Alice" }
}
```

### `GET /me/activity`

Auth: required.

Returns derived events with types such as `checkin`, `streak`, `level_up`, and `achievement`.

### `GET /me/achievements`

Auth: required.

Returns all achievement definitions with `unlocked` and `unlocked_at` fields.

### `GET /me/profile`

Auth: required.

Returns private profile aggregate:

```json
{
  "ok": true,
  "profile": {
    "id": 1,
    "name": "Alice",
    "username": "alice",
    "avatar_url": "/avatars/avatar-1.png",
    "bio": "...",
    "joined_date": "2026-05-30",
    "profile_visibility": "public",
    "title": { "key": "beginner", "label": "Beginner" },
    "tagline": "Building consistency one strike at a time.",
    "stats": {}
  }
}
```

### `GET /me/consistency`

Auth: required.

Returns `days` as `{ date, count }` rows for the recent heatmap window.

## Profile Settings And Public Profile

### `GET /api/me/profile/settings`

Auth: required.

Returns `avatar_url`, `bio`, and `profile_visibility`.

### `PATCH /api/me/profile/settings`

Auth: required.

Request:

```json
{
  "avatar_url": "/avatars/avatar-1.png",
  "bio": "Short bio",
  "profile_visibility": "public"
}
```

Visibility values: `public`, `private`.

## Telegram Reminder Settings

The frontend does not use Telegram Login and never sends or stores a bot token.

Active frontend reminder settings should only promise delivery paths that exist. `reminders_enabled` controls mission-level Telegram reminder delivery and `daily_checkin_enabled` controls the existing daily unchecked reminder flow. Streak-risk reminders and weekly summaries may remain in the settings response for compatibility, but the current UI treats them as coming soon until a delivery pipeline exists.

### `GET /api/me/telegram/settings`

Auth: required.

Returns:

```json
{
  "ok": true,
  "settings": {
    "connected": true,
    "telegram_username": "alice",
    "reminders_enabled": true,
    "daily_checkin_enabled": true,
    "streak_risk_enabled": true,
    "weekly_summary_enabled": false,
    "bot_username": "ringo_strike_bot",
    "bot_link": "https://t.me/ringo_strike_bot"
  }
}
```

### `POST /api/me/telegram/connect-code`

Auth: required.

Returns a short-lived code and optional bot deep link. A new pending code expires previous pending codes for the same user.

### `PATCH /api/me/telegram/settings`

Auth: required.

Request fields:

```json
{
  "reminders_enabled": true,
  "daily_checkin_enabled": true
}
```

### `POST /api/me/telegram/disconnect`

Auth: required. Disconnects the user's Telegram chat and returns the updated settings.

### `POST /api/telegram/connect`

Auth: protected by `X-Reminder-Token`; intended for a bot-side bridge, n8n, or similar automation. The frontend must not call this endpoint.

Request:

```json
{
  "code": "RS-ABCDEFGH",
  "telegram_chat_id": "123456789",
  "telegram_username": "alice"
}
```

### `POST /api/telegram/remind-due-missions`

Auth: protected by `X-Reminder-Token`; intended for n8n, cron, or similar automation. The frontend must not call this endpoint.

Current VPS public URL:

```http
POST /api-proxy/api/telegram/remind-due-missions
```

The backend finds due mission-level reminders, sends Telegram messages through the configured Telegram bot, and marks each reminder as delivered only after a successful send.

Request:

```json
{
  "dry_run": true,
  "limit": 20
}
```

Response:

```json
{
  "ok": true,
  "server_now": "2026-06-16T12:00:00Z",
  "checked_at": "2026-06-16T12:00:00Z",
  "run_mode": "dry_run",
  "dry_run": true,
  "checked": 3,
  "due": 3,
  "sent": 0,
  "skipped": 0,
  "failed": 0,
  "errors": [],
  "items": [
    {
      "mission_log_id": 1,
      "user_id": 1,
      "mission_id": 12,
      "title": "Send one signal",
      "has_telegram_chat_id": true,
      "status": "dry_run"
    }
  ]
}
```

Rules:

- selects `mission_logs.status = "remind_later"` with `reminder_at <= now`
- ignores already delivered reminders via `mission_logs.reminder_sent_at`
- requires active enrollment, active challenge, and active mission records
- skips users without a connected Telegram chat or with reminders disabled
- dry-run does not send messages and does not set `reminder_sent_at`

### `GET /api/telegram/reminder-diagnostics`

Auth: protected by `X-Reminder-Token`; intended for admin/n8n operational checks. The frontend must not call this endpoint.

Current VPS public URL:

```http
GET /api-proxy/api/telegram/reminder-diagnostics
```

Returns safe reminder observability data without sending Telegram messages. It does not expose Telegram chat IDs, bot tokens, admin tokens, JWT secrets, cookies, or other secret values.

Response:

```json
{
  "ok": true,
  "server_now": "2026-06-16T12:00:00Z",
  "summary": {
    "total_reminders": 4,
    "due_count": 1,
    "scheduled_future_count": 1,
    "already_sent_count": 1,
    "missing_telegram_count": 1,
    "reminders_disabled_count": 0
  },
  "due_reminders": [
    {
      "mission_log_id": 1,
      "user_id": 1,
      "mission_id": 12,
      "mission_title": "Send one signal",
      "status": "remind_later",
      "reminder_at": "2026-06-16T11:55:00Z",
      "reminder_sent_at": null,
      "has_telegram_chat_id": true,
      "reminders_enabled": true,
      "delivery_state": "due"
    }
  ],
  "scheduled_future_reminders": [],
  "already_sent_reminders": [],
  "missing_telegram_reminders": [],
  "reminders_disabled_reminders": [],
  "recent_reminder_logs": []
}
```

Optional query:

- `recent_limit`: number of recent reminder logs to include in `recent_reminder_logs`

### `PATCH /api/profile/visibility`

Auth: required.

Request:

```json
{ "visibility": "private" }
```

### `PATCH /api/profile`

Auth: required.

Request fields: `name`, `bio`, `avatar_url`.

### `GET /api/public/profile/:username`

Auth: public.

Returns public-safe profile aggregate if `profile_visibility = 'public'`; otherwise `403 profile_private`.

### `GET /api/public/profile/:username/consistency`

Auth: public. Returns recent counted check-in dates for public profiles.

### `GET /api/public/profile/:username/achievements`

Auth: public. Returns up to 6 unlocked achievements for public profiles.

## Debug Endpoints

### `GET /debug/sqlite/schema/:table`

Auth: development-only endpoint. Outside development mode, returns `403 debug_disabled`.

Allowed tables: `users`, `challenges`, `enrollments`, `checkins`, `user_stats`.

### `GET /debug/sqlite/counts`

Auth: development-only endpoint. Outside development mode, returns `403 debug_disabled`.

Returns counts for users, challenges, enrollments, checkins, and user_stats.

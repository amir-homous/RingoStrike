# Ringo Brain v1 API Contract

## Purpose

Ringo Brain v1 is the deterministic guidance layer for the Ringo-first daily experience.

Its job is to read the user's current context and return a structured decision for what Ringo should say, how Ringo should feel, which mission should be suggested, which actions are available, and which reward sequence should run after completion.

Ringo Brain v1 is rule-based. It should not depend on AI-generated decisions in the MVP.

Product references:

- [Product Direction Master Notes](PRODUCT_DIRECTION_MASTER_NOTES.md)
- [MVP Relaunch Phases](MVP_RELAUNCH_PHASES.md)
- [GitHub Issue Pack](GITHUB_ISSUE_PACK.md)

Core principle:

```txt
First Ringo. Then system.
```

## Suggested Endpoint

```http
GET /me/ringo/today
```

Auth: required.

This endpoint is additive. It should not replace the existing daily mission endpoints during v1 implementation.

## Response JSON Structure

Successful response:

```json
{
  "ok": true,
  "date": "2026-06-10",
  "ringo": {
    "user_state": "today_not_started",
    "mood": "focused",
    "tone": "warm_no_shame",
    "message": "Today's mission is ready. One small step is enough.",
    "sprite_key": "focus"
  },
  "mission": {
    "mission_id": 1,
    "key": "move_10",
    "title": "Move for 10 minutes",
    "description": "Walk, stretch, or do a light movement session.",
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
    },
    {
      "type": "make_smaller",
      "label": "Make it smaller",
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

If no mission is available, `mission` may be `null`, but `ringo`, `actions`, `progress`, and `fallback` should still be present.

Mission event timestamp fields are additive and nullable. They come from current Ringo day mission logs only:

- `done_at`: current-day completion event time.
- `skipped_at`: current-day skip event time.
- `reminder_set_at`: current-day reminder creation/update event time.
- `status_updated_at`: current-day mission log update time.

Use `reminder_at`, not `reminder_set_at`, when placing reminder-set missions on a daily timeline. If no reliable timestamp is present, the frontend should keep the mission untimed.

## Supported `user_state` Values

Initial v1 values:

- `new_user`
- `no_active_path`
- `path_selected_no_challenge`
- `today_not_started`
- `today_in_progress`
- `today_completed`
- `today_reminded`
- `today_skipped`
- `returning_after_absence`
- `streak_risk`
- `low_energy`
- `high_momentum`
- `no_mission_today`

Notes:

- Values should be stable machine-readable strings.
- Frontend copy should not depend on parsing these strings.
- New values may be added later, but existing values should not be renamed without a compatibility plan.

## Supported `mood` Values

Initial v1 values:

- `welcome`
- `calm`
- `focused`
- `encouraging`
- `celebrating`
- `gentle`
- `concerned`
- `resting`

Mood controls Ringo presentation, sprite selection, animation, and tone. It should not be used as the only source of business logic.

## Supported `mission_intensity` Values

Initial v1 values:

- `tiny`: a smaller low-pressure version for tired, returning, or low-energy users.
- `main`: the recommended mission that is enough for today.
- `bonus`: an optional extra mission for high-momentum users.

The user should always know which action is enough for today. Bonus missions must remain optional.

Selection guidance:

- Normal users should receive `main` missions first.
- Returning or streak-risk users should receive an available `tiny` mission when one exists.
- If no `tiny` mission is available, Ringo Brain should safely fall back to the current `main` mission.
- `parent_mission_id` can link a `tiny` or `bonus` mission back to its main mission, but mission completion must still use the existing mission completion API.

## Supported Action Values

Initial v1 action `type` values:

- `start`
- `remind_later`
- `make_smaller`
- `too_tired`
- `skip_today`

Action object shape:

```json
{
  "type": "start",
  "label": "Start",
  "mission_id": 1
}
```

Rules:

- `type` is the stable machine-readable value.
- `label` is display text and may later be localized or AI-assisted.
- `mission_id` should be present when the action applies to a specific mission.
- `remind_later` should continue to map to the existing reminder flow.
- `skip_today` should not create a check-in.
- `too_tired` should guide Ringo toward a lower-pressure state and may suggest `tiny` intensity.

## Progress Fields

The `progress` object must include:

```json
{
  "today_saved": false,
  "current_streak": 3,
  "total_checkins": 12
}
```

Field meaning:

- `today_saved`: `true` when today's required/main action is complete enough for Ringo to say the day is safe.
- `current_streak`: current counted streak from the existing stats/check-in system.
- `total_checkins`: total counted check-ins from the existing stats/check-in system.

Do not create a separate Ringo-specific streak or XP economy.

## Ringo Day Fields

The `ringo_day` object is additive. It explains the daily mission/check-in boundary used by Ringo Brain so clients can avoid confusing reminder copy around local midnight.

Shape:

```json
{
  "date": "2026-06-14",
  "next_reset_at": "2026-06-15T00:00:00Z",
  "reset_basis": "utc",
  "server_now": "2026-06-14T20:52:00Z"
}
```

Rules:

- `date` is the current Ringo day according to the backend's UTC date.
- `next_reset_at` is the next UTC midnight boundary.
- `reset_basis` is `utc`; this matches the existing mission log/check-in date helpers and does not change completion, reminder, reward, or streak behavior.
- `server_now` is the backend's current UTC timestamp when the guidance payload is built.
- Frontend clients may ignore this object safely. When present, they should use `next_reset_at` to clarify reminder labels that land after the next Ringo daily reset.
- Current daily mission reminders should not be scheduled at or after `next_reset_at`; these reminders point to stale daily work after reset. The frontend should block the option when metadata is available, and the backend may reject the mutation with `reminder_after_next_reset`.

## Agenda Fields

The `agenda` object is additive. It gives Ringo a compact summary of today's mission situation so the frontend can keep Today Saved while still understanding the nearest useful optional/paused action.

Shape:

```json
{
  "today_saved": true,
  "next_action_type": "upcoming_reminder",
  "next_mission_id": 123,
  "next_mission_title": "Get morning light",
  "next_reminder_at": "2026-06-12T19:00:00Z",
  "pending_count": 1,
  "reminded_count": 2,
  "skipped_count": 1,
  "done_count": 1,
  "has_optional_work": true
}
```

Supported `next_action_type` values:

- `due_reminder`
- `upcoming_reminder`
- `primary_mission`
- `optional_mission`
- `skipped_optional`
- `done_for_today`

Priority order:

1. `due_reminder`
2. `upcoming_reminder`
3. `primary_mission`
4. `optional_mission`
5. `skipped_optional`
6. `done_for_today`

Rules:

- Counts are computed from today's mission list: pending, reminded/remind_later, skipped, and done.
- If today is saved and a reminder exists, Today Saved remains true and the reminder appears as optional/paused context.
- If today is saved and skipped missions exist, skipped work appears only as no-shame optional context.
- If today is not saved, pending main/tiny missions remain the meaningful primary mission path.
- If all missions are done or safely paused with no useful next mission, return `done_for_today`.
- Agenda must not change mission mutation APIs, reward sequence behavior, XP, streaks, or check-in writes.

## Reward Sequence Placeholder

The `reward_sequence` object reserves space for the future Ringo Moment flow.

Initial shape:

```json
{
  "type": "standard",
  "available": true,
  "placeholder": true
}
```

Suggested `type` values:

- `standard`
- `comeback`
- `streak_saved`
- `low_energy_win`
- `celebration`
- `none`

Ringo Moment rendering should never block the underlying mission/check-in write. If reward rendering fails, the mission/check-in result should remain valid.

## Fallback Behavior

Ringo Brain v1 must be fallback-safe.

If the decision engine cannot determine a personalized state, return:

```json
{
  "user_state": "today_not_started",
  "mood": "calm",
  "tone": "warm_no_shame",
  "message": "One small step is enough for today."
}
```

Fallback rules:

- Prefer a safe mission from the existing `/me/today-missions` data when available.
- If no mission exists, return `mission: null` and a gentle route/action toward path selection.
- Never shame the user for missed days, skipped missions, or low energy.
- Never fail the whole response only because message personalization, sprite choice, or reward sequence selection is unavailable.
- Include `fallback.used: true` and a short machine-readable `fallback.reason` when fallback behavior is used.

Example fallback object:

```json
{
  "fallback": {
    "used": true,
    "reason": "no_active_mission"
  }
}
```

## Backward Compatibility Notes

Existing mission APIs remain canonical for mission state and completion:

- `GET /me/today-missions`
- `POST /me/missions/:mission_id/done`
- `POST /me/missions/:mission_id/remind-later`
- `POST /me/missions/plan-reminders`
- `POST /me/missions/:mission_id/plan-reminder`
- `POST /me/missions/:mission_id/skip`

Ringo Brain v1 should not duplicate mission logs, check-ins, XP, streaks, achievements, or activity writes.

Reminder planning is additive. `POST /me/missions/plan-reminders` applies gentle reminder times to eligible pending current-day missions that do not already have reminders. `POST /me/missions/:mission_id/plan-reminder` applies one suggested reminder time for a pending or reminder-set mission. Both planner paths must schedule after server now and before `ringo_day.next_reset_at`, preserve done/skipped missions, and avoid changing completion, streak, check-in, or reward behavior.

Mission completion may return an additive `reward_sequence` array for frontend Ringo Moment rendering. Existing completion fields remain valid and should not be removed or renamed. Initial completion step types are:

- `ringo_message`
- `mission_completed`
- `xp_earned`
- `today_saved`
- `next_choice`

The `today_saved` completion step should be included only for the first completion that satisfies today: either a `main` mission or a linked `tiny` mission whose `parent_mission_id` points to a main mission. If today was already saved before the current completion, the backend should not repeat the `today_saved` step and should return warm bonus/optional progress copy using frontend-supported step types. Completing a linked tiny mission must not automatically mark the parent main mission done unless a later compatibility plan explicitly changes that.

Implementation guidance:

- Build `GET /me/ringo/today` as an additive guidance endpoint.
- Reuse existing mission, path, stats, and Ringo decision services where practical.
- Mission completion must continue to flow through `POST /me/missions/:mission_id/done`.
- Reminder and skip actions should continue to use the existing mission mutation endpoints.
- Mission skip may include an optional stable `reason` key: `too_tired`, `no_time`, `too_hard`, `not_relevant`, `disliked`, or `other`. Skip reasons are context for future adaptation only and must not create shame, punishment, XP loss, streak loss, or check-in writes.
- Frontend can adopt this endpoint progressively while keeping `MissionCenter` compatible with `/me/today-missions`.
- Existing `ringo.state` values from `/me/today-missions` should be mapped carefully rather than renamed in place.

## Future AI-Assisted Language Layer

AI may later help with message variation, personalized wording, gentle conversation, creative reward copy, and summaries.

AI must not make uncontrolled product decisions in v1.

Future AI layer rules:

- Ringo Brain decides `user_state`, `mood`, `mission_intensity`, selected mission, actions, and reward sequence type.
- AI may generate or vary `message` and `label` text after deterministic decisions are made.
- AI output must be structured, validated, length-bounded, and fallback-safe.
- AI text must follow Ringo's tone: caring, relaxed, emotionally intelligent, honest, playful, and never shame-based.
- Backend should preserve deterministic fallbacks for every AI-assisted field.

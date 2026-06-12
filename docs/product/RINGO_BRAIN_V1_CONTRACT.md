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
- `POST /me/missions/:mission_id/skip`

Ringo Brain v1 should not duplicate mission logs, check-ins, XP, streaks, achievements, or activity writes.

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

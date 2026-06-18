# Mission Context Component Impact Analysis

## 1. Purpose

This document converts the Mission Context wireframes into a component-level impact analysis.

The previous Mission Context documents answered:

```txt
What should the user see?
What context should be visible?
What action hierarchy should each mission state use?
How should mission -> reward -> rest flow work?
```

This document answers:

```txt
Which existing components are affected?
Which components should be extended?
Which small reusable components may be introduced?
Which current API fields are already enough?
Which backend fields may be needed later as additive read-model support?
What should not be changed?
```

This is planning documentation only. It does not implement code, create Codex implementation prompts, modify frontend/backend source code, redesign the dashboard, or introduce new progression logic.

The product goal remains:

```txt
Make missions clearer without turning RingoStrike into a dense productivity dashboard.
```

## 2. Relationship To Previous UX Docs

This document continues the Mission Context planning sequence:

```txt
docs/product/mission-context-ux-flow-map.md
  -> defined the mission context problem, model, states, and UX flows

docs/product/mission-context-wireframes.md
  -> converted those flows into low-fidelity text wireframes

docs/product/mission-context-component-impact.md
  -> maps the planned UX to existing components, possible reusable components,
     API field usage, backend boundaries, and implementation risk
```

The previous docs established this mental model:

```txt
Path -> Challenge -> Mission -> Completion -> Reward -> Progress
```

They also established this reusable mission context model:

```txt
Mission Context = origin + purpose + action + progress impact + reward impact
```

This component impact analysis should be used before implementation planning. It is not the implementation plan itself.

## 3. Current Implementation Boundary

Mission focus mode is implemented.

Full Mission Context UX is still planned.

These must remain separate.

### Implemented

- Mission focus mode.
- CompactProgressStrip.
- First-run staged reveal.
- Post-first-win completion UX.
- Rest Mode.
- Collapsed mission status details.
- Main/tiny mission-family behavior.
- Bonus missions as optional extra momentum.
- Telegram reminder automation and diagnostics.

### Still Planned

- Full Mission Context UX layer.
- Universal Path -> Challenge -> Mission breadcrumbs.
- Contextual reward sequence showing affected path/challenge progress.
- Complete tiny/bonus/remind-later context clarity across all surfaces.
- Possible additive backend read-model fields.
- Implementation of the wireframes.

### Boundary Rule

The planned Mission Context UX should extend the current guided loop. It should not replace the current architecture.

Safe direction:

```txt
Extend MissionCenter + RingoCoach + RewardMoment display
Use current API fields first
Add small reusable context components only where helpful
Add backend read-model fields only if frontend display cannot stay reliable
```

Unsafe direction:

```txt
Rewrite MissionCenter
Move mission completion outside existing endpoints
Duplicate XP/streak/achievement logic
Turn dashboard into a dense context dashboard
Treat optional bonus missions as required work
```

## 4. Component Impact Overview

| Area | Impact | Reason | Risk |
| --- | --- | --- | --- |
| `MissionCenter.vue` | High | Primary surface for mission card, action hierarchy, focus mode, Rest Mode, tiny/bonus/reminder states | High |
| `RingoCoach.vue` | Medium | Ringo remains first guidance layer and needs state-aware copy compatibility | Medium |
| `RewardMoment.vue` | Medium | Future contextual reward steps may show mission/challenge/path impact | Medium |
| `CompactProgressStrip.vue` | Low | Should stay lightweight and display-only | Low |
| `Dashboard.vue` | Medium | Owns focus-mode gating and dashboard reveal behavior | Medium |
| i18n locale files | Medium | New copy keys needed for mission context labels and state copy | Medium |
| Backend mission/ringo services | Low-to-Medium | Existing fields likely support Phase 1; later additive read-model fields may help | Medium |
| Progression services | No change | Must remain canonical owner of XP, streaks, achievements, check-ins, activity | High if changed |

The highest-impact component is `MissionCenter.vue` because it owns most visible mission states. However, the safest approach is not to make it bigger and messier. The safer approach is to keep MissionCenter as the orchestrating surface and introduce small reusable context pieces if needed.

## 5. Existing Components To Extend

### 5.1 MissionCenter.vue

#### Current Role

`MissionCenter.vue` is the primary dashboard mission surface. It loads today’s missions, renders Ringo guidance, presents mission actions, manages mission action states, emits focus-state changes to Dashboard, handles first-run staged reveal behavior, preserves collapsed mission status details, and owns Rest Mode presentation after `Finish for today`.

It is already the center of the daily loop:

```txt
Ringo guidance -> Today's Mission -> Mission action -> Reward / Today Saved -> Next gentle step
```

#### Why It Is Affected

Mission Context UX is mainly about making the mission card clearer. MissionCenter is where users see:

- the active mission
- tiny substitute options
- optional bonus states
- reminder confirmations
- due reminders
- today-safe completion states
- Rest Mode
- collapsed mission status

Therefore, MissionCenter is the primary component that would need to show:

- path/challenge breadcrumb
- mission intensity chip
- concrete instruction block
- why-this-helps block
- tiny parent relation line
- bonus optional framing
- reminder context notice
- today-safe summary
- action hierarchy based on mission state

#### Recommended Extension

MissionCenter should be extended as the orchestrator of mission context display.

Recommended future extensions:

- Add a compact `Path -> Challenge` breadcrumb near the top of the mission card.
- Add a mission intensity chip for `MAIN`, `TINY`, `BONUS`, `REMINDER`, `COMPLETED`, or `SKIPPED` display states.
- Surface a concrete action instruction before the primary button.
- Add a short “Why this helps” block before actions.
- Show a tiny parent relation line when `mission_intensity = tiny` and `parent_mission_id` exists.
- Keep bonus copy explicitly optional and keep `Finish for today` as the primary action when today is already safe.
- Show reminder context when `status = remind_later`, when `reminder_at` exists, or when a due reminder returns.
- Show `Today is safe` summary after main/tiny completion.
- Preserve collapsed mission status details by default.
- Preserve Rest Mode as the successful ending.

MissionCenter should use existing fields first before requiring backend changes.

#### What Should Not Change

- Do not replace MissionCenter.
- Do not move mission mutation logic into new components.
- Do not change mission completion endpoints.
- Do not duplicate check-in, XP, streak, achievement, or activity logic.
- Do not remove Rest Mode.
- Do not remove collapsed mission status behavior.
- Do not reveal the full dashboard automatically after mission completion.
- Do not turn optional bonus states into the dominant primary action.

#### Risk Level

High

#### Notes For Later Implementation

MissionCenter is high risk because it is central to the daily loop. Future implementation should be phased and small.

Recommended safe approach:

1. Add purely visual context blocks using existing fields.
2. Keep all existing action handlers and mutation endpoints unchanged.
3. Keep focus-state emission unchanged unless a later issue explicitly updates the focus contract.
4. Add tests/smoke checks around main/tiny/bonus/reminder states after implementation.

### 5.2 RingoCoach.vue

#### Current Role

`RingoCoach.vue` displays Ringo’s sprite, message, and one or two action payloads from backend Ringo decisions. It is the emotional guidance layer and should remain the first thing users emotionally notice.

#### Why It Is Affected

Mission Context UX relies on the rule:

```txt
First Ringo. Then system.
```

RingoCoach may need to support more precise state-aware copy placement for:

- main mission explanation
- tiny mission validation
- bonus optional framing
- reminder-return copy
- today-safe confirmation
- multiple-active-challenges explanation

However, RingoCoach should not become the full mission card.

#### Recommended Extension

RingoCoach should remain the emotional explanation layer.

Recommended future extensions:

- Support shorter state-aware copy slots that can sit above MissionCenter context blocks.
- Keep sprite mood aligned with mission state.
- Keep message text deterministic and i18n-safe.
- Allow MissionCenter to provide contextual mission display below RingoCoach.
- Keep action payload display compatible with existing route/mission/reminder/dismiss behavior.

Possible state-to-mood alignment:

| State | Suggested Ringo Mood |
| --- | --- |
| Main mission pending | focus / encouraging |
| Tiny mission offered | encouraging / caring |
| Bonus offered | happy / calm |
| Reminder returned | talking / focus |
| Today safe / Rest Mode | sleeping / proud |
| Reward | victory / celebration / proud |

#### What Should Not Change

- Do not make RingoCoach own mission mutation logic.
- Do not make RingoCoach calculate today-safe status.
- Do not turn RingoCoach into a full mission context card.
- Do not duplicate MissionCenter action hierarchy inside RingoCoach.
- Do not use AI-generated copy as the first implementation layer.

#### Risk Level

Medium

#### Notes For Later Implementation

RingoCoach should stay simple. The main risk is overloading it with mission metadata. It should explain, not contain the whole system.

### 5.3 RewardMoment.vue

#### Current Role

`RewardMoment.vue` displays reward feedback from mission/check-in completion. It consumes existing reward/check-in data and can show XP, streak, achievements, and guided unlock hints.

#### Why It Is Affected

The Mission Context wireframes recommend a contextual reward sequence that explains:

1. Ringo reaction.
2. Completed mission.
3. Affected challenge.
4. Affected path.
5. XP/check-in reward.
6. Today saved / streak protected.
7. Achievements if any.
8. Next gentle step.

This means RewardMoment may later need contextual reward steps, not only generic reward feedback.

#### Recommended Extension

RewardMoment should be extended carefully to show context when the data exists.

Recommended future extensions:

- Accept/display completed mission title.
- Show affected challenge name when available.
- Show affected path title when available.
- Keep XP/check-in reward display based on existing backend data.
- Show today-safe/streak-protected copy only when existing reward/check-in/agenda data supports it.
- Show achievements from existing achievement data.
- End with a gentle next step: `Finish for today`, optional bonus, or dashboard reveal.

#### What Should Not Change

- Do not calculate XP in RewardMoment.
- Do not calculate streaks in RewardMoment.
- Do not evaluate achievements in RewardMoment.
- Do not create a separate reward economy.
- Do not replace existing check-in reward payloads.
- Do not make RewardMoment responsible for mission mutation.

#### Risk Level

Medium

#### Notes For Later Implementation

RewardMoment can be extended in phases. The first safe improvement is display-only context using fields already returned by mission completion payloads or existing mission data. A full tap-by-tap reward sequence should wait until the component impact and Phase 1 implementation plan are validated.

### 5.4 CompactProgressStrip.vue

#### Current Role

`CompactProgressStrip.vue` provides lightweight progress context during mission focus mode. It uses existing `/me/stats` data for level, XP progress, streak, and today-safe context.

#### Why It Is Affected

Mission Context UX may increase context around missions, but CompactProgressStrip should remain minimal. It supports the focused state without becoming a second dashboard.

#### Recommended Extension

CompactProgressStrip should mostly stay unchanged.

Possible future refinements:

- Ensure labels remain compatible with today-safe states.
- Keep compact wording aligned with mission completion/rest states.
- Avoid showing path/challenge detail here; that belongs in the mission card or reward context.

#### What Should Not Change

- Do not calculate stats locally.
- Do not become a second progression engine.
- Do not show dense mission status.
- Do not show full path/challenge progress.
- Do not replace dashboard stats.

#### Risk Level

Low

#### Notes For Later Implementation

CompactProgressStrip is low risk if kept display-only. The main risk is adding too much context to it. Mission context belongs in MissionCenter, not the strip.

### 5.5 Dashboard.vue

#### Current Role

`Dashboard.vue` owns the broader dashboard composition. It listens to MissionCenter focus state and hides secondary dashboard sections while mission focus mode is active. It also owns the explicit full dashboard reveal after the user chooses `Show dashboard`.

#### Why It Is Affected

Mission Context UX should preserve the current focus-mode behavior. If MissionCenter gains richer context blocks, Dashboard must continue to keep secondary sections hidden until the focus loop is resolved or the user explicitly reveals the dashboard.

#### Recommended Extension

Dashboard should remain the focus-mode container.

Recommended future extensions:

- Continue to listen to MissionCenter focus-state changes.
- Continue to show CompactProgressStrip during focus mode.
- Continue to hide secondary sections during active mission, reminder, bonus, unacknowledged completion, and Rest Mode states.
- Continue to reveal the full dashboard only when focus resolves or the user chooses `Show dashboard`.
- Keep reduced-motion-safe reveal behavior.

#### What Should Not Change

- Do not redesign the dashboard.
- Do not move MissionCenter logic into Dashboard.
- Do not make Dashboard calculate mission context.
- Do not show all dashboard sections during mission focus just because more context exists.
- Do not remove explicit `Show dashboard` escape hatch.

#### Risk Level

Medium

#### Notes For Later Implementation

Dashboard should remain stable. Most Mission Context work should happen inside MissionCenter and small display components. Dashboard changes should be limited to preserving focus behavior and passing display data if needed.

### 5.6 i18n Locale Files

#### Current Role

The frontend i18n locale files provide English and Persian UI copy. Backend values remain raw logic inputs, while display labels are translated in the frontend.

Relevant files:

- `frontend/src/i18n/locales/en.js`
- `frontend/src/i18n/locales/fa.js`

#### Why It Is Affected

Mission Context UX introduces new labels and copy patterns:

- mission intensity labels
- today-safe language
- tiny mission relation copy
- bonus optional framing
- reminder returned copy
- reward context steps
- accessibility labels
- collapsed status labels

Persian copy must feel natural and emotionally safe, especially for phrases like:

```txt
Today is safe.
You did enough.
The smaller step counts.
Anything else is optional.
```

#### Recommended Extension

Add or adjust frontend translation keys for mission context display.

Recommended copy-key groups:

- `missionContext.intensity.main`
- `missionContext.intensity.tiny`
- `missionContext.intensity.bonus`
- `missionContext.todaySafe.title`
- `missionContext.todaySafe.body`
- `missionContext.tiny.smallerVersionOf`
- `missionContext.tiny.stillCounts`
- `missionContext.bonus.optionalTitle`
- `missionContext.bonus.optionalBody`
- `missionContext.reminder.youAsked`
- `missionContext.reminder.due`
- `missionContext.reward.missionCompleted`
- `missionContext.reward.challengeAffected`
- `missionContext.reward.pathAffected`
- `missionContext.actions.finishForToday`
- `missionContext.actions.showMissionStatus`

These names are conceptual only and are not implementation instructions.

#### What Should Not Change

- Do not move translations into backend response shapes.
- Do not localize raw backend logic values.
- Do not add component-local font overrides for normal UI text.
- Do not use AI-generated copy as the first deterministic copy layer.

#### Risk Level

Medium

#### Notes For Later Implementation

Persian wording is important. Literal translations may feel mechanical. The implementation plan should include a copy review pass for both English and Persian.

## 6. Possible New Reusable Components

### 6.1 MissionContextBreadcrumb

#### Purpose

Display the mission’s origin:

```txt
Path -> Challenge
```

Example:

```txt
Body Momentum -> Move Your Body
```

#### Where It Would Be Used

- MissionCenter mission card.
- RewardMoment contextual reward steps.
- Reminder-return state.
- Telegram reminder return view.
- Possibly collapsed mission status details.

#### Conceptual Props / Data

- `pathTitle`
- `challengeName`
- `pathId`
- `challengeId`
- optional `compact`
- optional `ariaLabel`

#### Can Be Frontend-Only?

Yes.

#### Needs Backend Support?

No for Phase 1 if `path_title` and `challenge_name` are available.

#### Recommended Timing

Phase 1

#### Risk Level

Low

### 6.2 MissionIntensityChip

#### Purpose

Show mission type/intensity in a consistent way.

Examples:

```txt
MAIN · 10 min
TINY · 2 min
BONUS · optional
DUE REMINDER · MAIN
COMPLETED · TINY
SKIPPED · BONUS
```

#### Where It Would Be Used

- MissionCenter mission card.
- Tiny mission offered/completed states.
- Bonus mission offered/completed states.
- Reminder states.
- Reward sequence steps.

#### Conceptual Props / Data

- `missionIntensity`
- `estimatedMinutes`
- `status`
- `isReminderDue`
- `isCompleted`
- `isSkipped`
- optional `variant`

#### Can Be Frontend-Only?

Yes.

#### Needs Backend Support?

No if `mission_intensity`, `estimated_minutes`, and `status` are available.

#### Recommended Timing

Phase 1

#### Risk Level

Low

### 6.3 MissionInstructionBlock

#### Purpose

Show the concrete “what counts?” instruction before the primary action.

Example:

```txt
Walk, stretch, or do light mobility. Anything intentional counts.
```

#### Where It Would Be Used

- Main mission pending.
- Tiny mission offered.
- Bonus mission offered.
- Reminded mission returns.
- Telegram reminder opens app.

#### Conceptual Props / Data

- `title`
- `description`
- `instruction`
- `estimatedMinutes`
- optional `fallbackByIntensity`

#### Can Be Frontend-Only?

Mostly yes.

#### Needs Backend Support?

Not required if existing mission `description` is clear enough. Future backend support may help if mission descriptions remain too vague.

#### Recommended Timing

Phase 1

#### Risk Level

Medium

### 6.4 MissionWhyBlock

#### Purpose

Explain why the mission matters and what progress it affects.

Example:

```txt
Keeps today safe for this challenge and keeps your Body Momentum path moving.
```

#### Where It Would Be Used

- Main mission pending.
- Tiny mission offered.
- Bonus mission offered.
- Reminder return.
- Multiple active challenges.

#### Conceptual Props / Data

- `pathTitle`
- `challengeName`
- `missionIntensity`
- `todaySaved`
- `ringoMessage`
- `whyNowKey`
- optional `whyText`

#### Can Be Frontend-Only?

Yes for deterministic Phase 1 copy using current fields.

#### Needs Backend Support?

Not required for Phase 1. Future `why_now_key` or `why_now_text` could help if copy needs to reflect more precise decision reasons.

#### Recommended Timing

Phase 1

#### Risk Level

Medium

### 6.5 MissionParentRelation

#### Purpose

Show the relationship between a tiny mission and its parent main mission.

Example:

```txt
Smaller version of: Move for 10 minutes
```

#### Where It Would Be Used

- Tiny mission offered.
- Tiny mission completed.
- Reward sequence after tiny completion.
- Reminder return if the reminded mission is tiny.

#### Conceptual Props / Data

- `parentMissionId`
- `parentMissionTitle`
- `missionIntensity`
- optional `relationshipLabel`

#### Can Be Frontend-Only?

Partially.

If the parent mission exists in the current mission list, the frontend can derive the title. If only `parent_mission_id` is available and the parent mission is not in the loaded set, backend read-model support may be needed.

#### Needs Backend Support?

Maybe later.

Potential additive field:

- `parent_mission_title`

#### Recommended Timing

Phase 2

#### Risk Level

Medium

### 6.6 ReminderContextNotice

#### Purpose

Show reminder context clearly.

Examples:

```txt
Reminder set for today at 18:30.
You asked Ringo to bring this mission back.
Telegram connected · reminders enabled.
```

#### Where It Would Be Used

- Mission reminded later confirmation.
- Reminded mission returns.
- Telegram reminder opens app.
- Collapsed mission status details.

#### Conceptual Props / Data

- `status`
- `reminderAt`
- `reminderSentAt`
- `reminderSetAt`
- `nextResetAt`
- `telegramConnected`
- `telegramRemindersEnabled`
- `todaySaved`

#### Can Be Frontend-Only?

Mostly yes.

#### Needs Backend Support?

No for basic state. Later mission-specific deep-link restoration may require additive support.

#### Recommended Timing

Phase 2

#### Risk Level

Medium

### 6.7 TodaySafeSummary

#### Purpose

Confirm that the required daily step is complete and stopping is allowed.

Example:

```txt
Today is safe. You did enough. Anything else is optional.
```

#### Where It Would Be Used

- Main mission completed.
- Tiny mission completed.
- Bonus mission offered.
- Bonus mission completed.
- Today Already Saved / Rest Mode.
- Reward sequence final step.

#### Conceptual Props / Data

- `todaySaved`
- `completedMissionTitle`
- `missionIntensity`
- `challengeName`
- `pathTitle`
- optional `nextReminderAt`

#### Can Be Frontend-Only?

Yes if `today_saved` or equivalent agenda/check-in response context is available.

#### Needs Backend Support?

Not required for Phase 1/2 if existing agenda and completion payloads are enough. Future read-model fields could make this safer.

#### Recommended Timing

Phase 2

#### Risk Level

Medium

### 6.8 RewardContextStep

#### Purpose

Show one step in a contextual reward sequence.

Examples:

- Mission completed.
- Challenge affected.
- Path affected.
- XP/check-in reward.
- Today saved.
- Achievement unlocked.
- Next gentle step.

#### Where It Would Be Used

- RewardMoment.
- Future contextual reward sequence.
- Possibly post-completion MissionCenter summary.

#### Conceptual Props / Data

- `type`
- `title`
- `text`
- `value`
- `mission`
- `challenge`
- `path`
- `achievement`
- optional `mood`

#### Can Be Frontend-Only?

Partially.

Some steps can be built from current fields and existing `reward_sequence`. More precise context may require backend read-model support later.

#### Needs Backend Support?

Maybe later.

Potential additive field:

- `reward_context_steps`

#### Recommended Timing

Phase 3

#### Risk Level

Medium

## 7. Existing API Fields That Are Enough

Many Mission Context UX improvements can likely be frontend-first using current fields.

| Field | Can Support | Notes |
| --- | --- | --- |
| `path_id` | Internal route/context identity | Useful for linking to path details later. |
| `path_title` | Path part of breadcrumb | Enough for `Body Momentum -> Challenge` display. |
| `challenge_id` | Internal route/context identity | Useful for enrollment/challenge links. |
| `challenge_name` | Challenge part of breadcrumb | Enough for most mission card context. |
| `enrollment_id` | Existing completion/check-in linkage | Should remain the bridge to existing progression pipeline. |
| `mission_id` | Mission action identity | Used for existing done/remind/skip endpoints. |
| `mission_intensity` | MAIN/TINY/BONUS chip | Supports action hierarchy and optional framing. |
| `estimated_minutes` | Time estimate label | Supports `MAIN · 10 min`, `TINY · 2 min`. |
| `parent_mission_id` | Tiny/main relation | Enough if parent mission title can be found in loaded mission list. |
| `ringo_message` | Mission-specific guidance | Can help Ringo explanation or why block. |
| `status` | Pending/done/skipped/remind-later display | Supports mission state visuals. |
| `reminder_at` | Reminder scheduled time | Supports reminder confirmation and future reminder display. |
| `reminder_sent_at` | Reminder delivery state | Supports sent/due/scheduled display without exposing admin data. |
| `done_at` | Completion timestamp | Supports completed state/time if needed. |
| `skipped_at` | Skip timestamp | Supports skipped state if needed. |
| `reminder_set_at` | Reminder creation context | Supports “you asked me earlier” context. |
| `status_updated_at` | Generic state update time | Useful fallback when specific timestamp is missing. |
| `xp_earned` | Mission display reward value | Display-only; canonical XP still comes from stats/check-in. |
| `reward_sequence` | Existing reward steps | Can support early contextual reward display if enriched enough. |
| `agenda` | Daily mission situation summary | Supports next-action and today-safe logic. |
| `today_saved` | Safe-day display | Supports TodaySafeSummary and action hierarchy. |
| `next_action_type` | Ringo/action priority | Supports state selection and explanation. |
| `next_reset_at` | Reminder boundary context | Supports warning/blocking reminder times after reset. |

### Likely Enough For Phase 1

The following should be enough for frontend-only mission clarity:

- breadcrumb from `path_title` and `challenge_name`
- intensity chip from `mission_intensity`
- time label from `estimated_minutes`
- mission action/title from existing mission fields
- status display from `status`
- reminder display from `reminder_at`
- today-safe display from `agenda.today_saved` or equivalent payload context

### Needs Care

`parent_mission_id` is enough only if the parent mission title is available in the current mission list. If the parent title is missing, a future additive `parent_mission_title` read-model field may be needed.

`xp_earned` should be treated as display data only. The canonical XP model remains the existing stats/check-in/achievement pipeline.

## 8. Possible Additive Backend Read-Model Fields

Backend changes should be additive and read-only unless a later issue explicitly requires deeper changes.

Possible future fields:

| Field | Purpose | Required Now? | Notes |
| --- | --- | --- | --- |
| `parent_mission_title` | Show tiny relation line reliably | No | Useful if parent mission is not in loaded list. |
| `why_now_key` | Deterministic reason key for Ringo decision | No | Helps frontend choose safe copy. |
| `why_now_text` | Backend-provided explanation text | No | Use carefully; frontend i18n may prefer keys. |
| `today_safe_after_completion` | Predict whether completing this mission saves today | No | Must not become duplicate progression logic. |
| `family_satisfied_after_completion` | Clarify main/tiny family outcome | No | Useful for tiny completion explanation. |
| `progress_context_label` | Human-readable progress impact | No | Should remain display-only. |
| `reward_context_steps` | Contextual reward sequence steps | No | Phase 3/4 only if current reward_sequence is insufficient. |
| `deep_link_mission_context` | Restore a specific mission after Telegram/open link | No | Useful for future reminder deep-link behavior. |

### Read-Model Rule

These fields, if added later, should be read-model support only.

They should not:

- write XP
- write streaks
- unlock achievements
- create check-ins
- create a new progression economy
- replace mission logs
- replace existing reward/check-in payloads

## 9. Backend Systems That Must Not Be Changed

The following backend systems must remain canonical and should not be duplicated for Mission Context UX.

### `backend/routes/mission_routes.py`

Must remain the route boundary for mission reads and mission mutation endpoints.

Do not add parallel mission completion routes for context UX.

### `backend/services/mission_service.py`

Must remain the mission state owner for today’s missions, done/remind/skip state, and mission logs.

Do not add a second mission log system.

### `backend/services/enrollment_service.py`

Must remain the check-in side-effect owner when mission completion delegates to existing check-in behavior.

Do not bypass it for mission completion.

### `backend/services/stats_service.py`

Must remain the XP, level, streak, and stats calculation owner.

Do not calculate canonical XP/streak in Mission Context code.

### `backend/services/achievement_service.py`

Must remain the achievement unlock owner.

Do not unlock achievements from frontend context components.

### `backend/services/ringo_decision_service.py`

Must remain the deterministic RingoCoach decision source for current Ringo state/action decisions.

Do not duplicate decision logic in route modules.

### `backend/services/ringo_brain_service.py`

Must remain additive guidance/read-model support.

Do not make it own mission completion or progression writes.

### `backend/services/reminder_service.py`

Must remain the server-owned reminder selection/delivery and diagnostics layer.

Do not let frontend call protected automation endpoints.

### `backend/services/telegram_service.py`

Must remain the Telegram delivery abstraction.

Do not expose bot tokens, chat IDs, or admin reminder tokens to frontend Mission Context UI.

## 10. Frontend Systems That Must Not Be Replaced

### MissionCenter

Do not replace it. Extend it.

MissionCenter is already the primary daily surface and should remain the mission loop owner.

### RingoCoach

Do not replace it. Keep it as the emotional guidance layer.

RingoCoach should not become a full mission card.

### RewardMoment

Do not replace it with a separate reward system.

It may later gain contextual steps, but must keep using existing reward/check-in data.

### CompactProgressStrip

Do not replace or expand it into a full stats dashboard.

It should remain lightweight and display-only.

### Dashboard Focus Mode

Do not remove focus-mode gating.

The dashboard should remain calm while the daily loop needs attention.

### Rest Mode

Do not remove Rest Mode.

Rest Mode is a successful ending, not an empty state.

### i18n Architecture

Do not move display translations into backend responses.

Keep frontend translations frontend-only and raw backend values logic-safe.

## 11. i18n Impact

Mission Context UX will require new copy keys and careful wording.

### New Copy Areas

- Mission intensity labels:
  - Main
  - Tiny
  - Bonus
  - Reminder
  - Completed
  - Skipped
- Today-safe copy:
  - Today is safe.
  - You did enough.
  - Anything else is optional.
- Tiny mission relation:
  - Smaller version of...
  - This still counts.
  - No need to force the bigger version.
- Bonus optional framing:
  - Optional extra momentum.
  - Only if you still have energy.
- Reminder context:
  - You asked me to remind you.
  - Reminder set for...
  - Reminder returned.
- Reward context steps:
  - Mission completed.
  - Challenge affected.
  - Path affected.
  - Today saved.
  - Next gentle step.
- Accessibility labels:
  - Path breadcrumb label.
  - Mission intensity label.
  - Show mission status.
  - Finish for today.

### English Copy Direction

Keep English copy short, direct, and calm.

Examples:

```txt
Today is safe.
The smaller step counts.
Only if you still have energy.
You asked me to remind you.
```

### Persian Copy Direction

Persian copy must feel natural, not literal or robotic.

Important phrases need careful review:

```txt
Today is safe.
You did enough.
The smaller step counts.
Anything else is optional.
```

Possible Persian tone should be warm and simple, not formal or judgmental.

### Translation Rule

Backend should continue returning raw values such as:

```txt
main
tiny
bonus
remind_later
done
skipped
```

Frontend should translate labels for display.

## 12. Accessibility Impact

Mission Context UX should improve accessibility by making purpose, action, and progress impact clearer.

### Positive Accessibility Impact

- Clearer mission instructions reduce cognitive load.
- One primary action reduces decision fatigue.
- Tiny missions support low-energy users.
- No-shame skip copy supports emotionally safer use.
- Text labels avoid relying only on color.
- Breadcrumbs help screen-reader users understand origin.

### Required Accessibility Behaviors

- Mission title should be reachable as the main heading inside the mission card.
- Breadcrumb should have a readable text/ARIA form:

```txt
Path: Body Momentum. Challenge: Move Your Body.
```

- Intensity chips should include text, not color only.
- Buttons should use clear labels:

```txt
Complete mission
Complete tiny mission
Finish for today
Remind me later
Show mission status
```

- Collapsed mission status should be keyboard-accessible.
- Reward sequence should be navigable without relying on animation.
- Reduced-motion preferences should be respected.

### Accessibility Risks

- Too many context blocks may increase cognitive load.
- Too many secondary actions may confuse users.
- Reward sequence may become tedious if every step requires interaction.
- Breadcrumbs may wrap poorly on small screens or screen readers if not handled carefully.

## 13. Responsive Layout Impact

### Mobile

Mission context should remain stacked and readable.

Recommended mobile order:

```txt
Ringo explanation
Breadcrumb
Intensity chip
Mission title
Concrete instruction
Why this helps
Primary action
Secondary actions
Collapsed status
Compact progress strip
```

Mobile rules:

- Use one full-width primary action.
- Allow secondary actions to wrap.
- Keep breadcrumb compact.
- Keep mission instruction visible.
- Keep “why this helps” short.
- Keep collapsed details below actions.

### Desktop

Desktop should not automatically reveal more dashboard just because there is more space.

Recommended desktop behavior:

- Keep MissionCenter centered.
- Keep CompactProgressStrip nearby.
- Keep secondary sections hidden during focus mode.
- Keep status/details collapsed unless requested.
- Avoid side-by-side dense context panels.

### Tablet / Medium Width

Tablet can use slightly richer spacing, but the hierarchy should remain the same.

Do not split Ringo explanation and mission card into disconnected columns unless the visual relationship remains obvious.

## 14. Implementation Risk Notes

### Highest Risk

`MissionCenter.vue` has the highest risk because it owns the active daily loop. Adding too much inside it could create a large, difficult-to-maintain component.

Mitigation:

- add small reusable display pieces
- keep action handlers unchanged
- avoid new state machines unless necessary
- implement in phases

### Medium Risk

Reward context has medium risk because it touches user perception of XP, streak, today-safe, and achievements.

Mitigation:

- use existing reward/check-in data
- do not calculate rewards locally
- clearly mark optional reward context as display-only

### Copy Risk

Mission clarity depends heavily on copy quality.

Mitigation:

- deterministic copy first
- i18n-safe keys
- Persian copy review
- avoid AI-generated variation until stable patterns exist

### Backend Risk

Backend read-model support may be useful later, but adding fields too early could create unnecessary coupling.

Mitigation:

- use current fields first
- add read-model fields only when a frontend need is proven
- keep fields display-only

### Product Risk

Bonus missions could accidentally feel required.

Mitigation:

- keep `Finish for today` primary when today is safe
- use explicit optional language
- avoid streak-pressure copy

### Emotional UX Risk

Tiny missions could feel like failure if copy is wrong.

Mitigation:

- always show “smaller version of...”
- always say “still counts” when applicable
- avoid “easy mode” language

## 15. Recommended Implementation Phases

This section is a planning sequence only. It is not a Codex prompt and does not implement code.

### Phase 1 — Frontend-Only Mission Clarity

Goal:

Add the highest-value context with the lowest architecture risk.

Scope:

- Add breadcrumb/intensity/instruction/why blocks using existing fields.
- Preserve current actions and mutations.
- Preserve focus mode and Rest Mode.
- Keep MissionCenter as the orchestrator.
- Keep RingoCoach as the emotional explanation layer.
- Add i18n labels for intensity/context basics.

Likely useful components:

- MissionContextBreadcrumb
- MissionIntensityChip
- MissionInstructionBlock
- MissionWhyBlock

Backend changes:

```txt
None expected.
```

### Phase 2 — Reminder And Tiny/Bonus Context Polish

Goal:

Make the confusing states feel intentional and emotionally safe.

Scope:

- Improve tiny parent relation display.
- Improve bonus optional framing.
- Improve reminder-return context.
- Add/adjust i18n keys.
- Keep collapsed mission status behavior.
- Keep Telegram reminder data display safe.

Likely useful components:

- MissionParentRelation
- ReminderContextNotice
- TodaySafeSummary

Backend changes:

```txt
Only consider additive read-model fields if parent mission title or reminder restoration context cannot be derived safely.
```

### Phase 3 — Contextual Reward Sequence

Goal:

Make reward moments explain what changed across mission, challenge, path, XP, today-safe state, and achievements.

Scope:

- Add affected mission/challenge/path reward framing.
- Use existing reward/check-in data first.
- Preserve RewardMoment ownership.
- Avoid duplicate XP/streak/achievement calculations.
- Keep next gentle step at the end.

Likely useful component:

- RewardContextStep

Backend changes:

```txt
Add backend read-model only if existing reward_sequence and mission context are insufficient.
```

### Phase 4 — Backend Read-Model Support If Needed

Goal:

Add optional display-only context fields if frontend-only derivation becomes fragile.

Scope:

- Add optional read-only context fields.
- Do not alter progression writes.
- Do not alter mission completion behavior.
- Do not create a new reward economy.
- Keep current APIs backward-compatible.

Possible fields:

- `parent_mission_title`
- `why_now_key`
- `why_now_text`
- `today_safe_after_completion`
- `family_satisfied_after_completion`
- `progress_context_label`
- `reward_context_steps`
- `deep_link_mission_context`

## 16. Non-Goals

This document does not:

- implement code
- create Codex implementation prompts
- define final component APIs
- define final visual design
- replace existing architecture
- add backend writes
- add new progression economy
- claim Mission Context UX is already complete
- replace MissionCenter
- replace RingoCoach
- replace RewardMoment
- replace CompactProgressStrip
- redesign the full dashboard
- duplicate XP logic
- duplicate streak logic
- duplicate achievement logic
- create a new mission completion pipeline
- replace the check-in flow
- introduce AI-generated mission copy as the first implementation layer

## 17. Open Questions

- Can Phase 1 ship using only current mission fields, or does `parent_mission_title` become necessary immediately?
- Should MissionContextBreadcrumb be a tiny component or simple markup inside MissionCenter at first?
- Should MissionIntensityChip represent both intensity and status, or should status be a separate display element?
- Should “Why this helps” use `ringo_message`, deterministic frontend copy, or a future `why_now_key`?
- How much of the reward sequence should live in RewardMoment versus MissionCenter post-completion summary?
- Should TodaySafeSummary be shown inside MissionCenter, RewardMoment, or both?
- How should Persian copy phrase “Today is safe” in the most natural, emotionally warm way?
- Should Telegram reminder opening route to the dashboard only, or should future deep-link restoration target a specific mission focus state?
- How should multiple active challenges be explained without creating an algorithm-explanation UI?
- What smoke tests should be added after Phase 1 implementation?
- Should skipped required missions always offer tiny alternatives if available?
- How should bonus reminders behave if today is already safe and the user ignores them?

## 18. Next Step

Next recommended step: Implementation Plan for Mission Context UX Phase 1

After this component impact analysis, the next document should define a safe Phase 1 implementation plan before Codex prompts are created.

That plan should specify:

- exact Phase 1 scope
- components to touch
- components not to touch
- API fields to use
- copy keys to add
- manual QA checks
- regression risks
- what must remain unchanged

The Phase 1 implementation plan should still avoid code changes inside the document itself and should not become a Codex implementation prompt unless a later issue explicitly asks for that.

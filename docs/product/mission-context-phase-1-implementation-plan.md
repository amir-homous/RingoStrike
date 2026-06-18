# Mission Context UX Phase 1 Implementation Plan

## 1. Purpose

This document defines a safe Phase 1 implementation plan for Mission Context UX.

Phase 1 is focused on frontend-only mission clarity using current API fields. It should make the existing mission experience easier to understand without changing the backend progression model, mission mutation endpoints, check-in pipeline, dashboard architecture, XP/streak/achievement logic, or reward ownership.

Phase 1 should help users understand:

```txt
What mission am I doing?
Which path/challenge does it belong to?
Is it main, tiny, or bonus?
What exactly counts as completion?
Why does this help?
What is the next safe action?
```

This plan is documentation only. It does not implement code, create Codex prompts, modify frontend/backend source code, or redesign the dashboard.

## 2. Relationship To Previous Mission Context Docs

This plan continues the Mission Context UX planning sequence:

```txt
docs/product/mission-context-ux-flow-map.md
  -> defined the mission context problem, mental model, states, and product rules

docs/product/mission-context-wireframes.md
  -> defined low-fidelity text wireframes and action hierarchy

docs/product/mission-context-component-impact.md
  -> mapped the wireframes to affected components, reusable component ideas,
     current API fields, backend boundaries, and implementation risk

docs/product/mission-context-phase-1-implementation-plan.md
  -> defines the first safe implementation phase before Codex prompts are created
```

The previous docs established this context model:

```txt
Mission Context = origin + purpose + action + progress impact + reward impact
```

Phase 1 should implement only the safest visible subset of that model:

```txt
origin + action + basic purpose
```

Phase 1 should not attempt full reward context, backend read-model support, mission-specific deep links, or a full dashboard redesign.

## 3. Phase 1 Scope

Phase 1 scope is intentionally narrow.

### Included

- Add clearer mission origin context using existing `path_title` and `challenge_name`.
- Add a mission intensity label using existing `mission_intensity`.
- Add estimated time display using existing `estimated_minutes` when available.
- Add a concrete instruction block using existing mission title/description and deterministic fallback copy.
- Add a short “Why this helps” block using existing fields and frontend deterministic copy.
- Improve tiny mission clarity when `mission_intensity = tiny` and parent context is available.
- Improve bonus mission optional framing when `mission_intensity = bonus`.
- Improve basic reminder context using existing reminder fields.
- Add frontend i18n copy keys for mission context labels and state copy.
- Preserve current MissionCenter actions and mutation flows.
- Preserve focus mode, CompactProgressStrip, collapsed mission status, and Rest Mode.

### Phase 1 UX Target

The mission card should move from:

```txt
Mission title + actions
```

toward:

```txt
Ringo explanation
Path -> Challenge
MAIN/TINY/BONUS · estimated time
Mission title
What counts instruction
Why this helps
Primary action
Secondary actions
Collapsed status
```

### Phase 1 Technical Target

Use current frontend data and current API fields first.

Expected backend impact:

```txt
None.
```

## 4. Phase 1 Non-Goals

Phase 1 does not:

- implement backend read-model fields
- create new mission mutation endpoints
- alter mission completion behavior
- alter check-in behavior
- alter XP logic
- alter streak logic
- alter achievement logic
- alter activity logic
- create a new reward system
- create a new progression economy
- redesign the full dashboard
- replace MissionCenter
- replace RingoCoach
- replace RewardMoment
- replace CompactProgressStrip
- replace Rest Mode
- implement full contextual reward sequence
- implement mission-specific Telegram deep-link restoration
- implement AI-generated mission explanations
- create Codex implementation prompts

Phase 1 should make the existing UI clearer, not architecturally broader.

## 5. Current Fields To Use

Phase 1 should use current API fields before requesting backend changes.

| Field | Phase 1 Usage | Notes |
| --- | --- | --- |
| `path_id` | Optional internal route/context identity | Do not require new navigation in Phase 1. |
| `path_title` | Breadcrumb path label | Primary field for mission origin. |
| `challenge_id` | Optional internal route/context identity | Existing links can remain unchanged. |
| `challenge_name` | Breadcrumb challenge label | Primary field for mission origin. |
| `enrollment_id` | Existing mission/check-in linkage | Do not alter usage. |
| `mission_id` | Existing action identity | Continue using current done/remind/skip endpoints. |
| `mission_intensity` | Main/tiny/bonus chip | Core Phase 1 field. |
| `estimated_minutes` | Time label | Show when available; hide safely when missing. |
| `parent_mission_id` | Tiny relation detection | Use only if parent mission title can be resolved from current data. |
| `ringo_message` | Optional guidance/purpose copy | Use carefully; frontend i18n/deterministic copy should remain primary for labels. |
| `status` | Pending/done/skipped/remind-later display | Do not create new status meanings. |
| `reminder_at` | Reminder scheduled time | Use in basic reminder context. |
| `reminder_sent_at` | Reminder sent state | Display only if already surfaced safely to frontend. |
| `done_at` | Completion context | Optional display; not necessary for Phase 1. |
| `skipped_at` | Skip context | Optional display; not necessary for Phase 1. |
| `reminder_set_at` | Reminder context | Optional display; useful for “you asked me earlier” copy if available. |
| `status_updated_at` | Fallback timestamp | Use only as fallback for display. |
| `xp_earned` | Display-only mission reward value | Do not calculate canonical XP from it. |
| `reward_sequence` | Existing reward response | Do not expand in Phase 1 beyond current behavior. |
| `agenda` | Today-safe / next action context | Use if already available in active frontend path. |
| `today_saved` | Today-safe display | Use when available; otherwise infer only from existing current UI state, not new logic. |
| `next_action_type` | Action hierarchy context | Use if already consumed safely. |
| `next_reset_at` | Reminder boundary context | Use only for basic reminder safety copy if already available. |

### Safe Fallback Rules

- If `path_title` is missing, hide the path part of the breadcrumb instead of inventing it.
- If `challenge_name` is missing, hide the challenge part instead of inventing it.
- If `estimated_minutes` is missing, show only the intensity label.
- If `mission_intensity` is missing, fall back to neutral `Mission` label.
- If parent mission title cannot be resolved, show a generic tiny relation copy rather than inventing the parent title.
- If today-safe state is uncertain, avoid strong `Today is safe` copy.

## 6. Components To Touch

### 6.1 MissionCenter.vue

#### Phase 1 Role

Primary implementation surface.

MissionCenter should receive the most visible Phase 1 improvements because it owns the current mission card, mission action states, focus-mode behavior, collapsed mission status, and Rest Mode.

#### Planned Phase 1 Changes

- Add path/challenge breadcrumb display using current fields.
- Add mission intensity/time display.
- Add concrete instruction block under the mission title.
- Add “Why this helps” block before actions.
- Add tiny relation copy when safe.
- Add bonus optional framing when safe.
- Add reminder context copy when safe.
- Preserve current primary/secondary action behavior.
- Preserve collapsed mission status details.
- Preserve Rest Mode.

#### What Must Stay Unchanged

- Existing mission mutation calls.
- Existing done/remind/skip action handlers.
- Existing focus-state emission behavior unless unavoidable.
- Existing Rest Mode behavior.
- Existing collapsed mission status details.
- Existing main/tiny/bonus family behavior.
- Existing reward trigger path.

#### Risk

High, because MissionCenter is the core daily loop.

#### Phase 1 Safety Notes

Do not turn MissionCenter into a large all-in-one dashboard. If the markup becomes dense, extract small display-only components.

### 6.2 RingoCoach.vue

#### Phase 1 Role

Emotional guidance layer.

RingoCoach should remain the “First Ringo” part of the experience. Phase 1 should not make it responsible for mission card structure.

#### Planned Phase 1 Changes

- Review whether current Ringo copy still reads well once mission context blocks appear below it.
- Keep Ringo’s explanation short and state-aware.
- Preserve sprite mood behavior.
- Preserve existing action payload compatibility.

#### What Must Stay Unchanged

- RingoCoach should not own mission mutation logic.
- RingoCoach should not calculate mission context.
- RingoCoach should not become the full mission card.
- RingoCoach should not duplicate MissionCenter action hierarchy.

#### Risk

Medium.

#### Phase 1 Safety Notes

Most Phase 1 work may not require structural changes to RingoCoach. It may only require copy compatibility and layout coordination with MissionCenter.

### 6.3 RewardMoment.vue

#### Phase 1 Role

Mostly unchanged.

Full contextual reward sequence is not a Phase 1 goal.

#### Planned Phase 1 Changes

- Avoid major RewardMoment changes in Phase 1.
- Only align final safe-day/optional-copy if current completion UX needs consistency with the new mission context copy.
- Keep existing reward/check-in data usage.

#### What Must Stay Unchanged

- Do not calculate XP.
- Do not calculate streak.
- Do not evaluate achievements.
- Do not create new reward sequence logic.
- Do not replace existing reward/check-in payload handling.

#### Risk

Low-to-Medium for Phase 1 if kept mostly unchanged.

#### Phase 1 Safety Notes

Contextual reward sequence should remain Phase 3. Phase 1 can prepare copy consistency but should not expand RewardMoment heavily.

### 6.4 CompactProgressStrip.vue

#### Phase 1 Role

No major change expected.

CompactProgressStrip should continue to provide lightweight progress context during focus mode.

#### Planned Phase 1 Changes

- No functional changes expected.
- Verify it still visually supports MissionCenter after context blocks are added.
- Keep it display-only.

#### What Must Stay Unchanged

- Do not calculate stats locally.
- Do not add mission context into the strip.
- Do not expand into full dashboard progress.
- Do not duplicate XP/streak/progress logic.

#### Risk

Low.

#### Phase 1 Safety Notes

If MissionCenter becomes taller, verify CompactProgressStrip still appears in a calm, non-competing position.

### 6.5 Dashboard.vue

#### Phase 1 Role

Focus-mode container and dashboard reveal owner.

Dashboard should continue to hide secondary dashboard sections while the daily loop is active.

#### Planned Phase 1 Changes

- No redesign.
- Preserve focus-mode gating.
- Preserve `Show dashboard` explicit reveal behavior.
- Verify new MissionCenter context blocks do not accidentally reveal or compete with full dashboard sections.

#### What Must Stay Unchanged

- Do not move MissionCenter logic into Dashboard.
- Do not make Dashboard calculate mission context.
- Do not redesign dashboard sections.
- Do not remove explicit `Show dashboard` escape hatch.

#### Risk

Medium.

#### Phase 1 Safety Notes

Dashboard changes should be minimal. Most Phase 1 work belongs in MissionCenter and optional display-only child components.

### 6.6 i18n Locale Files

#### Phase 1 Role

Copy support for new mission context labels.

Relevant files:

- `frontend/src/i18n/locales/en.js`
- `frontend/src/i18n/locales/fa.js`

#### Planned Phase 1 Changes

Add copy keys for:

- mission intensity labels
- breadcrumb accessibility labels
- concrete instruction labels
- why-this-helps labels
- tiny relation copy
- bonus optional copy
- reminder context copy
- today-safe/finish copy if needed
- action labels if missing

#### What Must Stay Unchanged

- Do not move translations to backend.
- Do not localize raw backend logic values.
- Do not add component-local font overrides.
- Do not use AI-generated variation as the first copy layer.

#### Risk

Medium.

#### Phase 1 Safety Notes

Persian copy should be reviewed carefully. Literal translations may feel unnatural, especially for “Today is safe,” “You did enough,” and “The smaller step counts.”

## 7. Components Not To Touch

Phase 1 should not touch these systems unless a later implementation review finds a direct, unavoidable reason.

### Backend Source Files

Do not modify:

- `backend/routes/mission_routes.py`
- `backend/services/mission_service.py`
- `backend/services/ringo_decision_service.py`
- `backend/services/ringo_brain_service.py`
- `backend/services/enrollment_service.py`
- `backend/services/stats_service.py`
- `backend/services/achievement_service.py`
- `backend/services/reminder_service.py`
- `backend/services/telegram_service.py`

### Progression Systems

Do not touch:

- XP calculation
- streak calculation
- achievement evaluation
- activity feed derivation
- check-in writes
- mission log writes
- reward writes

### Major Frontend Surfaces

Do not redesign:

- full dashboard sections
- profile surfaces
- paths page
- challenge discovery
- enrollment detail
- leaderboard

### Deployment / Automation

Do not touch:

- n8n reminder flow
- Telegram protected automation endpoints
- deployment scripts
- environment config

## 8. Possible Small Components For Phase 1

Phase 1 can be implemented either directly inside MissionCenter or with small display-only components. If MissionCenter becomes too dense, prefer small reusable pieces.

### Recommended Phase 1 Candidates

#### MissionContextBreadcrumb

Purpose:

```txt
Show Path -> Challenge origin.
```

Likely data:

- `pathTitle`
- `challengeName`

Phase 1 value:

High.

Risk:

Low.

#### MissionIntensityChip

Purpose:

```txt
Show MAIN / TINY / BONUS and optional estimated time.
```

Likely data:

- `missionIntensity`
- `estimatedMinutes`
- `status`

Phase 1 value:

High.

Risk:

Low.

#### MissionInstructionBlock

Purpose:

```txt
Show what counts as mission completion.
```

Likely data:

- mission title
- mission description
- deterministic fallback copy

Phase 1 value:

High.

Risk:

Medium.

#### MissionWhyBlock

Purpose:

```txt
Explain why this mission helps.
```

Likely data:

- `path_title`
- `challenge_name`
- `mission_intensity`
- `today_saved`
- `ringo_message`

Phase 1 value:

High.

Risk:

Medium.

### Defer To Later Unless Easy

#### MissionParentRelation

Useful for tiny missions, but may require parent mission title resolution.

Phase 1 can include a simple fallback:

```txt
Smaller version of today’s main mission.
```

Do not block Phase 1 on backend `parent_mission_title`.

#### ReminderContextNotice

Useful for reminders, but full reminder-return polish belongs to Phase 2.

Phase 1 can include basic reminder time copy if fields are already present.

#### TodaySafeSummary

Useful after completion/rest, but Phase 1 should avoid large completion-flow changes.

#### RewardContextStep

Defer to Phase 3.

## 9. Copy And i18n Plan

Phase 1 should use deterministic frontend copy.

### Copy Principles

- short
- warm
- clear
- no shame
- no pressure
- easy to translate
- no casino-style excitement
- no heavy streak anxiety

### Suggested English Copy Keys

Conceptual key names only:

```txt
missionContext.label.pathChallenge
missionContext.intensity.main
missionContext.intensity.tiny
missionContext.intensity.bonus
missionContext.intensity.mission
missionContext.time.minutes
missionContext.instruction.title
missionContext.why.title
missionContext.why.main
missionContext.why.tiny
missionContext.why.bonus
missionContext.tiny.smallerVersionGeneric
missionContext.tiny.stillCounts
missionContext.bonus.optionalTitle
missionContext.bonus.optionalBody
missionContext.reminder.setFor
missionContext.reminder.youAsked
missionContext.actions.completeMission
missionContext.actions.completeTinyMission
missionContext.actions.finishForToday
missionContext.actions.showMissionStatus
```

### Main Mission Copy

```txt
This is today’s main step. Complete it once and today is safe.
```

### Tiny Mission Copy

```txt
This is the smaller version of today’s main mission. It still counts.
```

### Bonus Mission Copy

```txt
Today is already safe. This bonus is optional extra momentum.
```

### Reminder Copy

```txt
Reminder set for {time}. Ringo will bring this mission back later.
```

### Persian Copy Note

Persian copy should be reviewed for natural tone. Avoid literal, stiff translations.

Especially review:

```txt
Today is safe.
You did enough.
The smaller step counts.
Anything else is optional.
```

## 10. State Coverage For Phase 1

Phase 1 does not need full coverage of every planned Mission Context state. It should cover the highest-confusion states with current fields.

### Must Cover

#### Main Mission Pending

Show:

- Ringo explanation
- Path -> Challenge breadcrumb
- MAIN chip
- estimated time if available
- mission title
- concrete instruction
- why this helps
- existing primary/secondary actions

#### Tiny Mission Offered

Show:

- TINY chip
- smaller-version copy
- still-counts copy when safe
- concrete instruction
- existing actions

If parent title is not available, use generic copy instead of inventing the parent title.

#### Bonus Mission Offered

Show:

- BONUS chip
- optional framing
- finish/rest remains primary when today is safe
- start bonus stays secondary

#### Mission Reminded Later

Show:

- reminder time
- mission context if available
- reminder is not completion
- Telegram status only if already available in current UI state

#### Reminded Mission Returns

Basic Phase 1 support:

- show “you asked me to remind you” copy when status/reminder state supports it
- show breadcrumb/intensity/instruction like normal mission card

Full deep-link restoration is not Phase 1.

### Should Preserve

#### Today Already Saved / Rest Mode

Preserve existing Rest Mode.

Phase 1 may align copy but should not redesign it.

#### Main Mission Completed / Tiny Completed

Preserve current post-first-win completion UX.

Phase 1 may align `Today is safe` copy but should not implement the full contextual reward sequence.

### Defer

#### Full Reward Sequence After Completion

Defer to Phase 3.

#### Telegram Reminder Opens Specific Mission Deep Link

Defer to later backend/read-model/deep-link planning.

#### Multiple Active Challenges Explanation

Phase 1 can avoid complex multi-challenge explanations unless existing UI already has the needed `agenda` context safely available.

## 11. Manual QA Checklist

Manual QA should confirm Phase 1 improves clarity without breaking current flows.

### General

- [ ] Dashboard loads normally.
- [ ] MissionCenter still appears before dense dashboard sections.
- [ ] Focus mode still hides secondary dashboard sections while active.
- [ ] CompactProgressStrip still appears during focus mode.
- [ ] `Show dashboard` still reveals the full dashboard.
- [ ] Rest Mode still appears after `Finish for today`.

### Main Mission Pending

- [ ] Path/challenge breadcrumb appears when fields exist.
- [ ] Breadcrumb hides safely if fields are missing.
- [ ] MAIN chip appears for main missions.
- [ ] Estimated time appears only when available.
- [ ] Mission instruction is visible before actions.
- [ ] Why-this-helps block is visible and short.
- [ ] Complete mission still works.
- [ ] Remind me later still works.
- [ ] Make it smaller still works if available.
- [ ] Show mission status still expands details.

### Tiny Mission

- [ ] TINY chip appears.
- [ ] Tiny copy clearly says it is a smaller version.
- [ ] Tiny copy does not shame the user.
- [ ] Complete tiny mission still works.
- [ ] Return to main still works if present.
- [ ] Parent title is not invented if unavailable.

### Bonus Mission

- [ ] BONUS chip appears.
- [ ] Bonus copy clearly says optional.
- [ ] Finish for today remains primary when today is safe.
- [ ] Start bonus remains secondary.
- [ ] Bonus completion flow still works.

### Reminder

- [ ] Reminder time appears when `reminder_at` exists.
- [ ] Reminder copy does not imply completion.
- [ ] Reminder scheduling still works.
- [ ] Due reminder state still works.
- [ ] Telegram status copy does not expose private/admin data.

### Reward / Completion

- [ ] Existing RewardMoment still opens correctly.
- [ ] XP/streak/achievement display remains based on existing backend response.
- [ ] No duplicate reward appears.
- [ ] Today-safe copy remains calm.

### i18n

- [ ] English labels render correctly.
- [ ] Persian labels render correctly.
- [ ] Persian RTL layout does not break mission card hierarchy.
- [ ] Long Persian text wraps cleanly.

### Responsive

- [ ] Mobile mission card remains readable.
- [ ] Primary action remains visible.
- [ ] Secondary actions wrap safely.
- [ ] Breadcrumb does not cause horizontal overflow.
- [ ] Reduced-motion behavior remains respected.

### Regression

- [ ] No new backend requests are required for Phase 1 context.
- [ ] No protected automation endpoint is called from frontend.
- [ ] No console errors on dashboard.
- [ ] No route guard/auth behavior changes.

## 12. Regression Risks

### MissionCenter Complexity

Risk:

Adding too many context blocks directly to MissionCenter can make it harder to maintain.

Mitigation:

Use small display-only components if the template becomes dense.

### Action Hierarchy Drift

Risk:

Bonus mission could accidentally become the primary action when today is already safe.

Mitigation:

Keep `Finish for today` primary in today-safe/bonus states.

### Tiny Mission Shame

Risk:

Tiny copy may make users feel they failed the main mission.

Mitigation:

Use “smaller version” and “still counts” language.

### Missing Field Confusion

Risk:

Some missions may not have `path_title`, `challenge_name`, or `estimated_minutes`.

Mitigation:

Hide missing pieces safely. Do not invent data.

### Reward Logic Confusion

Risk:

Displaying `xp_earned` incorrectly could imply a separate mission XP economy.

Mitigation:

Treat it as display-only and keep RewardMoment using existing reward/check-in data.

### i18n Layout Issues

Risk:

Persian labels may be longer and break compact mission card layouts.

Mitigation:

Test RTL wrapping and avoid overly long labels.

### Reminder Privacy Risk

Risk:

Reminder context could accidentally expose internal diagnostics or Telegram-sensitive data.

Mitigation:

Display only frontend-safe reminder state. Never expose tokens, chat IDs, or protected diagnostics.

## 13. Backend Impact

Expected Phase 1 backend impact:

```txt
None.
```

Phase 1 should use current fields from existing mission/Ringo endpoints.

Do not add:

- backend migrations
- new tables
- new write endpoints
- new mission completion logic
- new reward logic
- new progression logic
- new Telegram automation endpoints

Potential later backend read-model fields are explicitly out of Phase 1:

- `parent_mission_title`
- `why_now_key`
- `why_now_text`
- `today_safe_after_completion`
- `family_satisfied_after_completion`
- `progress_context_label`
- `reward_context_steps`
- `deep_link_mission_context`

If a Phase 1 implementation discovers one of these is required, stop and document the need instead of adding backend logic inside Phase 1.

## 14. Testing Notes

This plan does not implement tests, but Phase 1 implementation should consider tests/smoke checks around the mission card display.

### Suggested Test Focus

- MissionCenter renders with mission context fields present.
- MissionCenter renders safely with missing optional fields.
- Main/tiny/bonus labels map correctly from `mission_intensity`.
- Reminder copy appears when `status = remind_later` or `reminder_at` exists.
- Existing mission actions still call the same handlers.
- Focus mode state remains unchanged.
- Rest Mode remains reachable.
- i18n labels exist in English and Persian.

### Manual First, Automated Later

Because this is a UX clarity phase, manual QA should happen first. Automated smoke coverage can follow once the final component structure is known.

### No Backend Tests Expected

If Phase 1 remains frontend-only, backend tests should not need changes.

## 15. Implementation Order

This is a recommended future implementation order, not an implementation prompt.

### Step 1 — Prepare Copy Keys

- Add English/Persian mission context labels.
- Add intensity labels.
- Add tiny/bonus/reminder copy.
- Keep copy short and deterministic.

### Step 2 — Add Small Display Helpers Or Components

- Add breadcrumb display.
- Add intensity chip display.
- Add instruction block.
- Add why-this-helps block.

If MissionCenter remains readable without new components, keep the implementation simple. If it becomes dense, extract display-only components.

### Step 3 — Integrate Into MissionCenter Pending State

- Add breadcrumb/intensity/instruction/why blocks to main mission pending state.
- Preserve actions.
- Preserve focus mode.

### Step 4 — Extend Tiny And Bonus Display

- Add tiny relation fallback copy.
- Add bonus optional framing.
- Keep bonus secondary when today is safe.

### Step 5 — Add Basic Reminder Context

- Show reminder time where already available.
- Add “Ringo will bring this back later” copy.
- Avoid protected diagnostics or admin data.

### Step 6 — Verify Completion / Rest Flow

- Confirm main completion still triggers current reward flow.
- Confirm tiny completion still protects today where current logic supports it.
- Confirm Rest Mode still appears.
- Confirm Show dashboard still works.

### Step 7 — Manual QA Pass

Run the manual QA checklist from this document.

### Step 8 — Document Any Phase 2 Needs

If any issue cannot be solved cleanly with current fields, document it for Phase 2 or backend read-model support instead of expanding Phase 1.

## 16. Rollback Strategy

Phase 1 should be easy to roll back because it is frontend-only and display-focused.

### Safe Rollback Expectations

- No database changes.
- No backend changes.
- No migration rollback.
- No API contract rollback.
- No mission/progression data impact.

### Rollback Options

1. Revert the Phase 1 frontend commit.
2. Remove or hide new context blocks from MissionCenter.
3. Keep i18n keys if harmless, or revert them with the frontend commit.
4. Keep existing MissionCenter actions and backend behavior unchanged.

### Rollback Validation

After rollback:

- Dashboard loads.
- MissionCenter loads.
- Mission complete works.
- Remind later works.
- Skip works.
- RewardMoment still appears.
- Rest Mode still works.
- Full dashboard reveal still works.

## 17. Acceptance Criteria

Phase 1 is acceptable when:

- MissionCenter shows path/challenge context when available.
- MissionCenter shows mission intensity clearly.
- Main/tiny/bonus missions are visually distinguishable.
- Mission instruction is visible before action.
- “Why this helps” copy appears and stays short.
- Tiny missions are framed as valid smaller steps.
- Bonus missions are framed as optional.
- Reminder state has basic context and time display.
- Existing mission actions still work.
- Existing reward/check-in flow still works.
- Rest Mode still works.
- Focus mode still gates the dashboard.
- CompactProgressStrip remains display-only.
- No backend changes are required.
- No XP/streak/achievement/check-in logic is duplicated.
- English and Persian UI labels exist for new visible text.
- Mobile/RTL layout remains readable.
- Missing optional fields do not break the UI.
- No protected reminder/admin data is exposed.

## 18. Next Step

Next recommended step: Codex Implementation Prompt for Mission Context UX Phase 1.

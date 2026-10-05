# Living Space Home Shell Spec

## Purpose

Living Space should become the user's Home shell, not a card that links away to separate daily workflow pages.

Current implementation status:

- Living Space renders inside the expanded dashboard.
- Zones show rewards, previews, and path action links.
- Clicking path actions can navigate to `/paths`, `/challenges`, or `/enrollment/:id`.

This proves the data wiring, but it is not the final product shape. The next product step is to keep the daily path, challenge, mission, reward, and rest loop inside the Living Space surface.

Core rule:

```txt
Home stays the room.
Ringo guides the room.
Real progress changes the room.
```

Operational shell rule:

```txt
ROOM LAYER
  -> RINGO GUIDE LAYER
  -> ONE ACTIVE WORK SURFACE
```

Only one work surface should be active at a time. Do not stack zone panel, mission panel, reward modal, and large Ringo dialogue simultaneously.

## Product Position

Living Space Home Shell is the navigation and interaction contract for turning the room into the primary daily surface.

It does not replace the existing systems:

- paths
- challenges
- missions
- MissionCenter
- Ringo Brain
- check-ins
- rewards
- stats
- achievements

It wraps those systems into one coherent Home experience.

## UX Principle

Daily use should not feel like moving between product modules.

The user should feel:

```txt
I am in my space.
Ringo is guiding me.
Each path zone can open the right work surface.
When I do real work, the space changes.
```

## Home Shell Layout Contract

The shell has three conceptual layers.

### 1. Room Layer

The persistent visual anchor.

Contains:

- one room
- five fixed zones
- unlocked reward objects
- locked previews
- active selected zone state
- room-level progress summary

The room layer should remain visible during normal daily interactions when space allows.

### 2. Ringo Guide Layer

Ringo remains the guide, not a room zone.

Contains:

- current state message
- recommended next action
- tone/mood
- optional secondary suggestion
- completion/rest guidance

Ringo can point to a zone, mission, or reward, but should not become a sixth clickable room zone.

### 3. Work Panel Layer

The interaction surface that opens inside the room shell.

Contains one active panel at a time:

- zone overview
- path detail
- challenge detail
- mission focus
- reward moment
- rest summary

The work panel can be a side panel on desktop and a bottom sheet/full-width panel on mobile. Final visual treatment requires product/design approval.

Desktop target:

- overlay side panel, roughly 380-480px depending state
- room remains the primary surface
- panel should not cover Ringo-safe positions or primary reward anchors

Mobile target:

- bottom sheet with the room preserved above/behind it
- controlled room crop in overview
- selected-zone crop/zoom after zone selection
- avoid forcing all five zones to be equally visible in portrait after a zone is selected

## State Model

### State 1: Room Overview

Default Home state.

Shows:

- all five zones
- object count
- unseen reward marker if any
- Ringo's recommended next step
- primary CTA based on Ringo Brain / MissionCenter state
- no permanent zone labels
- no dense challenge cards or stats grid

Allowed actions:

- select zone
- start/continue Ringo recommended mission
- finish/rest if today is safe
- open optional choices if today is already safe

Overview should answer:

```txt
"What is my next step today?"
```

not:

```txt
"What is every system in my account?"
```

Ringo guidance should stay short: one or two sentences and one primary CTA.

### State 2: Zone Selected

Triggered by clicking/tapping a zone.

Shows:

- path name
- unlocked objects for this zone
- locked preview objects
- next visible change copy
- today's path state
- active challenge if any
- primary/secondary path actions

Selected zone behavior:

- selected zone receives subtle focus lighting
- other zones remain visible but subdued
- zone label appears on selection, hover, or focus
- related reward anchors/previews can become clearer
- panel stays atmospheric and compact, not tab-heavy

Primary action rules:

| Zone state | Primary action | Secondary action |
| --- | --- | --- |
| Active challenge, mission ready | Continue today's mission | View path details |
| Active challenge, today complete | Review challenge | Optional next step |
| No active challenge | Start this path | Browse challenges |
| No path content available | Keep room overview | None |

### State 3: Path Detail In Room

Triggered from Zone Selected.

Shows the selected path without leaving Home.

Data:

- path title/description
- active challenge count
- ready challenge count
- today missions done/total
- next recommended challenge
- first locked preview reward for that path

Allowed actions:

- open current challenge
- start next challenge
- return to zone overview
- compare other zones

### State 4: Challenge Detail In Room

Triggered from Zone Selected or Path Detail.

Data:

- challenge name
- challenge status
- enrollment id if joined
- current streak
- total check-ins
- today mission count
- available today missions
- locked future missions as preview only

Allowed actions:

- open mission focus for an available mission
- start/join challenge if not joined
- review completed challenge state
- return to path detail

### State 5: Mission Focus In Room

The user should be able to complete the daily action from inside Home.

Data:

- mission title
- mission intensity: main, tiny, or bonus
- instruction
- why this matters
- path/challenge breadcrumb
- XP/reward context
- reminder state if any

Actions:

- Done
- Remind me
- Skip
- Make it smaller, when tiny version exists

Completion should trigger the existing mission/check-in pipeline. Living Space must not create a second completion system.

Use the existing terminology above. Avoid introducing a separate `Finish` action for mission completion, because Living Space should not become a second completion model.

### State 6: Reward Moment In Room

Triggered after mission completion when reward data exists.

Shows:

- Ringo feedback
- XP/streak/achievement summary when available
- room reward if newly unlocked
- object appears in the room
- next gentle action

Rules:

- Only newly unlocked room rewards show an unlock moment.
- Backfilled legacy rewards remain seen and do not replay.
- The room refreshes after the moment closes.
- The reveal is in-room and minimal.
- Reward materialization should be calm and premium, not confetti/loot/explosion feedback.
- The room should remain visually present during the reward moment.

### State 7: Rest / Finish Today

Triggered when today is safe or the user finishes for today.

Shows:

- room still visible
- Ringo rest message
- today saved summary
- completed mission count
- reminder count if any
- newly changed room object if any
- optional next step only if energy remains

The rest state should not become an empty page. It should feel like the user is resting inside the same Living Space.

Keep rest summaries short: two or three lines plus one ending action is enough.

## Routing Contract

The current standalone routes remain valid:

- `/paths`
- `/challenges`
- `/enrollment/:id`

But their role changes:

| Route | Future role |
| --- | --- |
| `/paths` | Full planning/library view, not the daily default |
| `/challenges` | Browse/search/add challenge fallback |
| `/enrollment/:id` | Deep detail fallback and shareable/debuggable view |
| `/dashboard` | Home route that renders Living Space shell |

Daily flow should prefer in-room panels over route changes.

## Data Contract Direction

The shell should initially reuse existing APIs:

- `GET /me/space`
- `GET /me/challenges`
- `GET /me/stats`
- `GET /me/today-missions`
- `GET /me/enrollments/:id`
- mission completion endpoints

Avoid adding a backend endpoint until the frontend state contract proves what shape is missing.

Likely future consolidated shape:

```json
{
  "space": {},
  "ringo": {},
  "zones": [
    {
      "path_key": "creativity",
      "room": {},
      "path_state": {},
      "active_challenge": {},
      "today_missions": [],
      "recommended_action": {}
    }
  ],
  "today": {
    "safe": true,
    "completed_count": 1,
    "optional_count": 2
  }
}
```

Do not implement this consolidated endpoint until the in-room frontend model is validated.

## Ringo Recommendation Contract

Ringo suggestions should be visible from Room Overview and contextual inside selected panels.

Recommendation types:

- continue main mission
- switch to tiny mission
- rest because today is safe
- optional bonus only if energy remains
- start first challenge for selected path
- review reward/object change

Ringo should not present more than one primary action at a time.

## Interaction Flow

```txt
Open Home
-> Room Overview
-> Ringo recommends next action
-> user selects zone or accepts recommendation
-> Zone Selected
-> Challenge Detail
-> Mission Focus
-> Done / Remind / Skip
-> Reward Moment if applicable
-> Room Overview or Rest state
```

## Implementation Sequence

### Step 1: Product Contract

Create this spec and link it from roadmap/context docs.

### Step 2: Frontend Shell State

Introduce a Living Space shell state machine:

- `overview`
- `zone`
- `path`
- `challenge`
- `mission`
- `reward`
- `rest`

No visual redesign required.

### Step 3: In-Room Path Panel

Move current route-link path actions into an in-room panel using existing dashboard/path data.

### Step 4: In-Room Challenge Panel

Show current active challenge details inside the room shell.

### Step 5: In-Room Mission Focus

Let the user complete/remind/skip the selected mission without leaving Home.

### Step 6: Rest State

After Finish for Today, show a compact Living Space rest summary instead of an empty surface.

### Step 7: Route Demotion

Keep `/paths`, `/challenges`, and `/enrollment/:id` as full-detail fallback routes, not the default daily flow.

## Non-Goals

This spec does not approve:

- new room art
- generated background imagery
- object illustrations
- drag/drop room editing
- inventory
- shop/currency
- social visits
- city map
- second progression economy
- AI-generated progression decisions

Any final room background, object art, lighting direction, bitmap imagery, or visual style decision still requires explicit product/design approval.

## Open Product Questions

Before implementation beyond Step 3, answer:

- Should Room Overview replace MissionCenter visually, or should MissionCenter be refactored into the Ringo Guide Layer?
- Which exact mission actions must be supported inside the room first: Done only, or Done/Remind/Skip/Tiny?
- Should optional missions appear inside the same challenge panel or in a separate optional drawer?
- Should selecting a locked preview explain future reward rules, or keep it as a passive preview?
- What is the minimum mobile layout that still feels like a room rather than a list?

## Recommended Next Issue

```txt
[Frontend] Introduce Living Space Home shell state model
```

Scope:

- Add shell states and panel routing inside `LivingSpace`.
- Keep existing visual layout mostly intact.
- Replace direct zone action route jumps with in-room panels where possible.
- Preserve route links as secondary fallback actions.
- Do not add new art or final visual design.

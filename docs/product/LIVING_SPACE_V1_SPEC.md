# RingoStrike Living Space v1 Spec

## Product Goal

RingoStrike Home should become a living space of progress, not only a dashboard of stats.

Core rule:

```txt
Real progress -> visible change
```

When the user completes missions, keeps consistency, grows inside a path, or unlocks achievements, the home should visibly evolve. Rewards should become persistent objects in the user's space, not temporary UI feedback.

This feature must remain Ringo-first. Ringo is not a room zone. Ringo is the guide layer across the whole space.

Final product framing:

```txt
One room. Five path zones. Ringo guides from the room.
```

---

## Why This Matters

The current guided progression foundation already supports paths, missions, check-ins, XP, streaks, achievements, Ringo Brain, MissionCenter, and reward moments.

Living Space v1 turns those systems into visible identity:

- Missions create action.
- Progression records meaning.
- Rewards make progress visible.
- The room becomes a personal history of showing up.

This should reduce early-user confusion by making progress concrete and emotionally memorable.

---

## Core UX Flow

```txt
signup / login
-> Ringo welcome
-> minimal empty living space
-> path preview
-> choose first focus path
-> Ringo suggests first mission
-> user completes mission
-> Ringo Moment confirms progress
-> first reward unlocks
-> reward appears in the space
-> user can click the zone for today's mission, progress, rewards, and next reward
```

The first implementation should prove this loop before building deeper customization.

---

## Space Model

Living Space v1 has one room with five clickable zones:

| Zone | Backend path key | Display path | Zone key | Role |
| --- | --- | --- | --- | --- |
| Work Desk | `career` | Career | `work_desk` | focus, work, projects, professional growth |
| Creative Corner | `creativity` | Creativity | `creative_corner` | ideas, art, making, self-expression |
| Fitness Corner | `fitness` | Fitness | `fitness_corner` | movement, energy, body |
| Learning Corner | `learning` | Learning | `learning_corner` | study, curiosity, skill growth |
| Sleep Corner | `sleep` | Sleep / Recovery | `sleep_corner` | rest, calm, recovery |

The backend path keys must match the current seeded paths in `backend/services/path_seed_service.py`: `fitness`, `learning`, `career`, `creativity`, and `sleep`.

Ringo can sit centrally or move contextually, but Ringo should not be treated as a sixth zone.

Each zone has a distinct progression personality:

| Path | Personality | Room expression |
| --- | --- | --- |
| Career | focused, precise, composed | workbench, planning, future identity |
| Creativity | expressive, warm, generative | sketch, lamp, studio signal |
| Fitness | kinetic, grounded, energetic | floor, body momentum, equipment |
| Learning | quiet, curious, layered | shelves, notes, knowledge accumulation |
| Sleep / Recovery | calm, restorative, protective | moonlight, soft textiles, recovery rhythm |

## Visual Direction

Living Space visual direction is:

```txt
Dark Cinematic Diorama
```

with a controlled amount of:

```txt
Stylized Night Progress
```

The room should feel premium, cinematic, calm, and emotionally intelligent. It should not feel like a noisy productivity app, a chaotic game board, or a casino reward surface.

Camera direction:

```txt
elevated 3/4 soft-perspective
```

Do not treat the room as strict isometric. The camera should make all five zones readable while preserving atmosphere and depth.

Lighting is part of progression. It can communicate selected zone, today's safe state, reward materialization, rest mode, and long-term growth, but it must stay subtle and accessible.

---

## Stage 0 / Day-One State

The first room should be usable, calm, sparse, and pleasant.

It should not feel fully decorated or already successful. The user should see space for growth.

Day-one examples:

- Career: simple desk or laptop.
- Creativity: basic empty easel or pencil cup.
- Fitness: plain mat.
- Learning: one book or small study surface.
- Sleep / Recovery: simple bed or pillow.

The goal is for the user to notice visible change after the first week.

Stage 0 must reserve:

- empty wall areas for future identity/reward expression
- floor anchors for future objects
- surface/shelf anchors for small objects
- ceiling or wall lighting anchors
- central circulation so the room does not become a storage grid
- three Ringo-safe positions

Do not bake future reward assets into Stage 0. The base room should include anchor points and spatial readiness, not pre-rendered future rewards.

---

## Path Preview

Before choosing a first path, the user can hover or tap a path/zone.

The matching zone should highlight and future rewards should appear as locked previews:

- ghost treatment based on the final asset
- lower opacity
- desaturated or cooler material
- reduced detail contrast
- soft glow only when needed for readability
- lock state as secondary information

Example copy:

```txt
Build this corner by showing up for your creative missions.
```

Path preview should be informative, not a heavy shop/inventory screen.

Zone labels should not be permanently visible across the room. Show labels primarily on hover, keyboard focus, tap/selection, or active state so the room still feels like a place rather than a map HUD.

---

## First Path Choice

Ringo asks:

```txt
Which part of your life do you want to grow first?
```

The user's first choice is a first focus, not a permanent lock.

After selection, Ringo immediately recommends a first mission using the existing mission system where possible.

Implementation contract:

- First focus selection uses the existing path start flow: `POST /paths/:id/start`.
- Starting a path does not permanently lock the user to that path.
- If the frontend joins a suggested first challenge after path selection, it should continue using the existing challenge join flow.
- Living Space v1 should not add a separate onboarding backend.
- The selected path should be treated as the first highlighted room zone for preview and mission recommendation, not as the only zone the user can ever grow.

---

## Mission Structure

Living Space v1 should reuse the existing daily mission structure:

- Main Mission: the primary step for today.
- Tiny Mission: a low-pressure substitute for tired days.
- Bonus Mission: optional momentum.

Do not create a separate quest economy for the room. The room should reflect the existing mission/check-in/progression economy.

---

## Reward Moment

When a mission unlocks a room reward, the user should see the normal Ringo Moment plus a persistent room unlock.

Example sequence:

```txt
Mission Complete
+ XP
Today saved
Creativity progress
Unlocked: Sketchbook
Sketchbook appears in Creative Corner
```

The important rule:

```txt
Reward is not only feedback. Reward changes world state.
```

The reveal should feel like calm materialization:

```txt
ghost preview -> quiet unlock -> object/material/light resolves -> persistent room change
```

Avoid:

- confetti
- loot bursts
- full-screen reward explosions
- repeated modal interruptions
- effects that hide the room

---

## Reward Matrix v1

For v1, keep the canonical reward definition set intentionally small: five rewards per path, 25 total.

Important distinction:

```txt
25 reward definitions does not require 25 independent visible objects.
```

Visual manifestation can share art anchors when a reward evolves or changes the room instead of adding a separate object.

Each reward definition should be planned with a manifestation behavior:

| Behavior | Meaning |
| --- | --- |
| `ADD` | A new object appears in a reserved anchor. |
| `REPLACE` | An existing object evolves into a more advanced form. |
| `ENVIRONMENT` | A room-level or zone-level property changes. |
| `ATMOSPHERE` | Light, ambience, texture, or motion changes. |
| `IDENTITY` | The room expresses the user's progression identity more clearly. |

The current backend keeps 25 deterministic reward definitions. Visual behavior and shared art-anchor mapping are product/art contracts and should not be confused with a new progression economy.

The first implementation may still render simple object chips. Final art direction should gradually map reward definitions to fewer, higher-quality anchors where replacement, environment, atmosphere, or identity states make the room feel more premium.

## Reference Vertical Slice

Creativity is the first reference slice for art direction, implementation pacing, and QA.

Target sequence:

```txt
Stage 0 base
  -> Sketchbook ghost preview
  -> unlock / materialize
  -> persistent placed sketchbook object
  -> next Lamp preview
```

This slice should prove:

- base room sparseness is pleasant
- locked preview uses final asset ghost treatment
- reveal is calm and premium
- placed reward persists in the room
- next reward preview is readable without clutter
- Ringo, panels, and reward anchors do not overlap.

### Creativity

| Progress source | Reward |
| --- | --- |
| First Mission | Sketchbook |
| Early consistency | Desk Lamp |
| Progress milestone | Easel Upgrade |
| Achievement | Art Wall |
| Major milestone | Creative Trophy |

### Fitness

| Progress source | Reward |
| --- | --- |
| First Mission | Water Bottle |
| Early consistency | Dumbbells |
| Progress milestone | Better Mat |
| Achievement | Training Bench |
| Major milestone | Fitness Trophy |

### Learning

| Progress source | Reward |
| --- | --- |
| First Mission | First Book |
| Early consistency | Study Lamp |
| Progress milestone | Book Stack |
| Achievement | Bookshelf |
| Major milestone | Globe / Learning Trophy |

### Career

| Progress source | Reward |
| --- | --- |
| First Mission | Planner |
| Early consistency | Desk Lamp |
| Progress milestone | Monitor |
| Achievement | Project Board |
| Major milestone | Career Trophy |

### Sleep / Recovery

| Progress source | Reward |
| --- | --- |
| First Mission | Pillow |
| Early consistency | Bedside Lamp |
| Progress milestone | Blanket |
| Achievement | Moon Decoration |
| Major milestone | Recovery Trophy |

---

## Reward Sources

A reward can be unlocked by several source types:

- mission_reward
- consistency_reward
- path_reward
- achievement_reward
- challenge_reward
- event_reward, later

Do not bind every object directly to raw XP. XP can contribute to progression, but objects should explain the meaningful behavior that unlocked them.

### First Reward Unlock Rule

For v1, the first reward for a path unlocks when the user completes their first non-bonus mission for that path.

Precise backend rule:

- Trigger from successful `POST /me/missions/:id/done`.
- Use the completed mission's `path_id` through `missions -> challenges -> paths`.
- Unlock only the first `reward_definitions` row for that path where `unlock_condition_type = 'first_path_mission_done'`.
- Count `main` and linked `tiny` missions because both can save the day through the existing mission/check-in pipeline.
- Do not count `bonus` missions for the first reward unlock.
- Do not unlock again when the mission was already done for that day.
- Enforce idempotency with a unique `user_rewards(user_id, reward_id)` constraint or equivalent service guard.
- Store `source_type = 'mission_reward'` and `source_id = mission_id` for the first unlock.

This keeps the rule simple, deterministic, and tied to real progress without adding a second economy.

---

## Object Meaning

Every unlocked object should explain why it exists.

Example object detail:

```txt
Sketchbook
Unlocked because you completed your first Creativity mission.
```

Another example:

```txt
Art Wall
Unlocked after completing 10 Creativity missions.
```

This keeps the room emotionally meaningful rather than decorative clutter.

---

## Interactive Home Behavior

After onboarding, Home becomes the primary interface.

Clicking a zone opens a compact panel with:

- Today's Mission
- Path Progress
- Current streak or today-safe state
- Unlocked Rewards
- Next Reward
- Recent Achievement, if relevant
- View Path Details action

The panel should stay compact. Detailed path/challenge views should remain separate routes.

Clicking Ringo is different. Ringo gives cross-zone guidance such as:

```txt
Career does not need much today. Want to save the day with a Tiny Mission?
```

```txt
Learning has been quiet for three days. Five minutes is enough.
```

```txt
Today is safe. Want to stop here or take a bonus step?
```

---

## Conceptual Data Model

V1 can use fixed object slots. Do not build drag-and-drop, free placement, rotation, or a full inventory editor yet.

`slot_key` identifies the logical reward slot used by persistence and deterministic seeding. It is not the same as a final art anchor. Multiple reward slots may later share a visual anchor through `REPLACE`, `ENVIRONMENT`, `ATMOSPHERE`, or `IDENTITY` behavior.

If implementation later needs explicit art mapping, add a separate visual/art contract or an additive field such as `manifestation_behavior` / `visual_anchor_key`. Do not reinterpret existing unlock rows as draggable inventory.

### reward_definitions

- id
- key
- title
- description
- path_id
- zone_key
- object_type
- asset_key
- rarity
- unlock_condition_type
- unlock_condition_value
- stage
- slot_key

Canonical v1 reward definition keys:

| Path key | Zone key | Reward key | Slot key | Unlock condition |
| --- | --- | --- | --- | --- |
| `career` | `work_desk` | `career_planner` | `work_desk_first_reward` | `first_path_mission_done` |
| `career` | `work_desk` | `career_desk_lamp` | `work_desk_consistency` | `early_consistency` |
| `career` | `work_desk` | `career_monitor` | `work_desk_progress` | `path_progress_milestone` |
| `career` | `work_desk` | `career_project_board` | `work_desk_achievement` | `achievement_unlocked` |
| `career` | `work_desk` | `career_trophy` | `work_desk_major` | `major_path_milestone` |
| `creativity` | `creative_corner` | `creativity_sketchbook` | `creative_corner_first_reward` | `first_path_mission_done` |
| `creativity` | `creative_corner` | `creativity_desk_lamp` | `creative_corner_consistency` | `early_consistency` |
| `creativity` | `creative_corner` | `creativity_easel_upgrade` | `creative_corner_progress` | `path_progress_milestone` |
| `creativity` | `creative_corner` | `creativity_art_wall` | `creative_corner_achievement` | `achievement_unlocked` |
| `creativity` | `creative_corner` | `creativity_trophy` | `creative_corner_major` | `major_path_milestone` |
| `fitness` | `fitness_corner` | `fitness_water_bottle` | `fitness_corner_first_reward` | `first_path_mission_done` |
| `fitness` | `fitness_corner` | `fitness_dumbbells` | `fitness_corner_consistency` | `early_consistency` |
| `fitness` | `fitness_corner` | `fitness_better_mat` | `fitness_corner_progress` | `path_progress_milestone` |
| `fitness` | `fitness_corner` | `fitness_training_bench` | `fitness_corner_achievement` | `achievement_unlocked` |
| `fitness` | `fitness_corner` | `fitness_trophy` | `fitness_corner_major` | `major_path_milestone` |
| `learning` | `learning_corner` | `learning_first_book` | `learning_corner_first_reward` | `first_path_mission_done` |
| `learning` | `learning_corner` | `learning_study_lamp` | `learning_corner_consistency` | `early_consistency` |
| `learning` | `learning_corner` | `learning_book_stack` | `learning_corner_progress` | `path_progress_milestone` |
| `learning` | `learning_corner` | `learning_bookshelf` | `learning_corner_achievement` | `achievement_unlocked` |
| `learning` | `learning_corner` | `learning_trophy` | `learning_corner_major` | `major_path_milestone` |
| `sleep` | `sleep_corner` | `sleep_pillow` | `sleep_corner_first_reward` | `first_path_mission_done` |
| `sleep` | `sleep_corner` | `sleep_bedside_lamp` | `sleep_corner_consistency` | `early_consistency` |
| `sleep` | `sleep_corner` | `sleep_blanket` | `sleep_corner_progress` | `path_progress_milestone` |
| `sleep` | `sleep_corner` | `sleep_moon_decoration` | `sleep_corner_achievement` | `achievement_unlocked` |
| `sleep` | `sleep_corner` | `sleep_trophy` | `sleep_corner_major` | `major_path_milestone` |

Only the `first_path_mission_done` rewards must unlock in the first backend implementation. The other definitions can be seeded as locked previews so v1 has a visible growth direction.

### user_rewards

- id
- user_id
- reward_id
- unlocked_at
- source_type
- source_id
- is_seen

### user_space

- user_id
- theme
- current_stage
- updated_at

A later version can add placement/customization fields. V1 should not require them.

---

## Stage System

A user's space can have an overall stage:

1. Beginning
2. Taking Shape
3. Growing
4. Thriving
5. Flourishing

Stage should reflect a combination of:

- rewards earned
- active path coverage
- consistency
- meaningful milestones

Stage should not be only a level number copied from XP.

---

## MVP Scope

Living Space v1 should include exactly this initial loop:

1. Base empty room.
2. Five clickable zones.
3. Path hover/tap preview.
4. First path selection.
5. Mission recommendation.
6. Reward definitions.
7. First reward unlock with persistence.
8. Object visually appears in the room.

---

## Explicit Non-Goals

Do not include these in v1:

- shop
- inventory management
- drag-and-drop room editor
- rotate/place furniture
- multiple rooms
- city map
- friend room visits
- neighborhood/world map
- heavy social feed
- AI-generated reward decisions
- strict isometric redesign
- reward reveal based on confetti, loot boxes, or casino-style feedback

---

## Implementation Plan

### 1. Documentation alignment

Update product docs so Living Space is an official part of the guided progression direction.

Likely docs:

- `docs/ROADMAP.md`
- `docs/product/PRODUCT_DIRECTION_MASTER_NOTES.md`
- `docs/product/MVP_RELAUNCH_PHASES.md`
- `docs/product/GITHUB_ISSUE_PACK.md`
- `docs/AI_CONTEXT.md`
- `docs/DATABASE_SCHEMA.md`, when schema work begins
- API docs, when endpoints are added
- launch QA checklist, before release

### 2. Backend design

Add additive reward persistence without replacing current progression logic.

Likely backend files:

- `backend/database.py`
- `backend/services/mission_service.py`
- `backend/services/path_service.py`
- `backend/services/achievement_service.py`
- new `backend/services/living_space_service.py`
- new or existing route file for authenticated space state

Likely endpoints:

```txt
GET /me/space
GET /me/space/rewards
POST /me/space/rewards/:id/seen
```

Mission completion can later include newly unlocked space rewards as an additive response field.

### 3. Frontend design

Add the room as the new Home surface only after the data contract is defined.

Likely frontend files:

- `frontend/src/views/Dashboard.vue`
- `frontend/src/components/missions/MissionCenter.vue`
- `frontend/src/components/ringo/`
- new `frontend/src/components/space/LivingSpace.vue`
- new `frontend/src/components/space/SpaceZone.vue`
- new `frontend/src/components/space/RewardUnlockMoment.vue`
- `frontend/src/lib/api.js`
- `frontend/src/i18n/`

### 4. Testing and QA

Minimum backend coverage:

- first mission unlocks the correct reward once
- duplicate mission/check-in does not duplicate reward
- `/me/space` returns unlocked and locked preview state
- reward source metadata is persisted
- reward definitions remain deterministic

Minimum frontend coverage:

- room loads with empty/locked state
- selecting/previewing a path highlights the right zone
- mission completion shows first reward unlock when provided
- refreshed dashboard still shows the unlocked object
- RTL/Persian text does not break zone panels

---

## Future Phases

After v1 proves the loop:

- more reward tiers per path
- seasonal/event rewards
- profile `Visit Space`
- friends visiting public spaces
- room themes
- optional customization
- Room -> Neighborhood -> City -> Country -> World progression vision

Future architecture should not make these impossible, but v1 should not build them early.

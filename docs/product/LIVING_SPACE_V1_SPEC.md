# RingoStrike Living Space v1 Spec

## Product Goal

RingoStrike Home should become a living space of progress, not only a dashboard of stats.

Core rule:

```txt
Real progress -> visible change
```

When the user completes missions, keeps consistency, grows inside a path, or unlocks achievements, the home should visibly evolve. Rewards should become persistent objects in the user's space, not temporary UI feedback.

This feature must remain Ringo-first. Ringo is not a room zone. Ringo is the guide layer across the whole space.

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

| Zone | Path | Role |
| --- | --- | --- |
| Work Desk | Career | focus, work, projects, professional growth |
| Creative Corner | Creativity | ideas, art, making, self-expression |
| Fitness Corner | Fitness | movement, energy, body |
| Learning Corner | Learning | study, curiosity, skill growth |
| Sleep Corner | Sleep / Recovery | rest, calm, recovery |

Ringo can sit centrally or move contextually, but Ringo should not be treated as a sixth zone.

---

## Day-One State

The first room should be usable, calm, and sparse.

It should not feel fully decorated or already successful. The user should see space for growth.

Day-one examples:

- Career: simple desk or laptop.
- Creativity: basic empty easel or pencil cup.
- Fitness: plain mat.
- Learning: one book or small study surface.
- Sleep / Recovery: simple bed or pillow.

The goal is for the user to notice visible change after the first week.

---

## Path Preview

Before choosing a first path, the user can hover or tap a path/zone.

The matching zone should highlight and future rewards should appear as locked previews:

- ghost objects
- silhouettes
- translucent objects
- soft glow
- lock state

Example copy:

```txt
Build this corner by showing up for your creative missions.
```

Path preview should be informative, not a heavy shop/inventory screen.

---

## First Path Choice

Ringo asks:

```txt
Which part of your life do you want to grow first?
```

The user's first choice is a first focus, not a permanent lock.

After selection, Ringo immediately recommends a first mission using the existing mission system where possible.

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

---

## Reward Matrix v1

For v1, keep the reward set intentionally small: five rewards per path.

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

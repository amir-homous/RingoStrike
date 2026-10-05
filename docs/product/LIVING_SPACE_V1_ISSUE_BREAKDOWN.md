# Living Space v1 — GitHub Issue Breakdown

Milestone:

```txt
RingoStrike Living Space v1
```

Goal:

Turn RingoStrike Home into a visible progress space where mission/path/achievement progress unlocks persistent room objects.

Reference:

- [Living Space v1 Spec](LIVING_SPACE_V1_SPEC.md)
- [Living Space Visual System Spec](LIVING_SPACE_VISUAL_SYSTEM_SPEC.md)
- [Living Space Home Shell Spec](LIVING_SPACE_HOME_SHELL_SPEC.md)
- [Living Space v1 UX Polish Backlog](LIVING_SPACE_V1_UX_POLISH_BACKLOG.md)

---

# Issue 1 — [Docs] Finalize Living Space v1 product contract

## Goal

Lock the implementation-ready rules for Living Space v1 before changing UI or backend code.

## Scope

- Confirm the five zones.
- Confirm the first five rewards per path.
- Confirm the visual direction: Dark Cinematic Diorama with controlled Stylized Night Progress influence.
- Confirm elevated 3/4 soft-perspective camera, not strict isometric.
- Confirm fixed slots and no drag-and-drop for v1.
- Confirm unlock source types.
- Confirm reward manifestation behaviors: `ADD`, `REPLACE`, `ENVIRONMENT`, `ATMOSPHERE`, and `IDENTITY`.
- Confirm what appears during first path preview.
- Confirm reward object detail copy rules.

## Do Not Change

- No backend code.
- No frontend code.
- No database schema.

## Acceptance Criteria

- `docs/product/LIVING_SPACE_V1_SPEC.md` is present and treated as the source of truth.
- MVP scope and non-goals are explicit.
- Implementation issues link back to this spec.

---

# Issue 2 — [Backend] Add Living Space schema foundations

## Goal

Add additive persistence for room rewards without replacing existing progression systems.

## Suggested Tables

```txt
reward_definitions
user_rewards
user_space
```

## Suggested Files

```txt
backend/database.py
backend/services/living_space_service.py
```

## Requirements

- Reward definitions are deterministic and seedable.
- User reward unlocks are idempotent.
- Reward source metadata is stored.
- Objects use fixed `zone_key` and `slot_key` in v1.

## Do Not Change

- Do not rewrite check-ins, stats, achievements, paths, or missions.
- Do not add a second XP economy.
- Do not add free placement fields unless needed later.

## Acceptance Criteria

- Schema initializes safely for existing SQLite databases.
- Existing app startup still works.
- Re-running initialization does not duplicate reward definitions.
- Basic service functions can list definitions, unlock a reward, and list user space state.

---

# Issue 3 — [Backend] Unlock first path reward after first mission completion

## Goal

When a user completes their first mission for a path, unlock the first Living Space reward for that path.

## Likely Files

```txt
backend/services/mission_service.py
backend/services/living_space_service.py
backend/services/path_service.py
```

## Behavior

Example:

- First Creativity mission completed -> unlock `creativity_sketchbook`.
- First Fitness mission completed -> unlock `fitness_water_bottle`.

## Do Not Change

- Do not break current mission completion response.
- Do not duplicate check-ins.
- Do not duplicate rewards on repeated completion attempts.

## Acceptance Criteria

- First path reward unlocks once.
- Duplicate completion/check-in attempts do not create duplicate `user_rewards` rows.
- Unlock metadata includes source type and source id when available.
- Existing XP/streak/achievement behavior still works.

---

# Issue 4 — [API] Add authenticated Living Space endpoints

## Goal

Expose the user's room state and reward unlock state to the frontend.

## Suggested Endpoints

```txt
GET /me/space
GET /me/space/rewards
POST /me/space/rewards/:id/seen
```

## Response Direction

`GET /me/space` should include:

- current stage
- zones
- unlocked objects
- locked preview objects
- next reward per zone if available
- whether newly unlocked rewards are unseen

## Do Not Change

- Do not expose another user's private room yet.
- Do not build public visit-space endpoints in v1.
- Do not expose sensitive mission details in reward metadata.

## Acceptance Criteria

- Authenticated user can load room state.
- Locked preview data is available for onboarding/path preview.
- Seen state can be marked without changing unlock state.
- Existing APIs remain backward-compatible.

---

# Issue 5 — [Frontend] Build Living Space room components

## Goal

Create the visual room shell and five clickable path zones.

## Suggested Files

```txt
frontend/src/components/space/LivingSpace.vue
frontend/src/components/space/SpaceZone.vue
frontend/src/components/space/SpaceObject.vue
frontend/src/components/space/SpaceZonePanel.vue
```

## Behavior

- Show the sparse base room.
- Render five zones.
- Render locked preview objects during path preview.
- Render unlocked objects from API state.
- Open compact zone panel on zone click/tap.
- Keep zone labels non-permanent: hover, keyboard focus, tap/selection, or active state.
- Preserve room anchors, central circulation, and Ringo-safe positions.

## Do Not Change

- Do not build drag-and-drop.
- Do not build inventory.
- Do not replace existing Path details page.
- Do not hide MissionCenter until the new flow is validated.

## Acceptance Criteria

- Room renders on desktop and mobile.
- Zone click/tap opens compact panel.
- Locked previews are visually distinct from unlocked objects.
- The layout works in English and Persian/RTL.

---

# Issue 5B — [Frontend] Introduce Living Space Home shell state model

## Goal

Turn Living Space from a dashboard card with route links into the primary Home shell where room, Ringo guidance, path state, challenge state, mission focus, rewards, and rest state can happen in one surface.

Reference:

- [Living Space Home Shell Spec](LIVING_SPACE_HOME_SHELL_SPEC.md)

## Suggested Files

```txt
frontend/src/components/space/LivingSpace.vue
frontend/src/components/space/SpaceZonePanel.vue
frontend/src/views/Dashboard.vue
frontend/src/components/missions/MissionCenter.vue
```

## Behavior

- Add shell states such as `overview`, `zone`, `path`, `challenge`, `mission`, `reward`, and `rest`.
- Keep the room visible as the anchor during normal daily interactions.
- Keep Ringo as the guide layer, not as a sixth zone.
- Prefer in-room panels over direct jumps to `/paths`, `/challenges`, or `/enrollment/:id`.
- Preserve those routes as secondary fallback/deep-detail links.

## Do Not Change

- Do not add room art, background imagery, or object illustrations.
- Do not build drag-and-drop, inventory, shop, public visits, or a second economy.
- Do not replace backend progression APIs until the frontend state contract proves a missing shape.

## Acceptance Criteria

- Selecting a zone can move into an in-room state instead of immediately leaving Home.
- The primary next action is visible from the selected zone.
- Existing direct routes still work.
- Mission/check-in completion continues to use existing APIs.
- English and Persian copy remain available.

---

# Issue 5C — [Design/Frontend] Build Creativity visual vertical slice

## Goal

Use Creativity as the first visual reference slice for the Living Space room system.

Reference:

- [Living Space Visual System Spec](LIVING_SPACE_VISUAL_SYSTEM_SPEC.md)

## Behavior

Sequence:

```txt
Stage 0 base
  -> Sketchbook ghost preview
  -> unlock/materialize
  -> persistent placed sketchbook
  -> Lamp ghost preview
```

## Requirements

- Use Dark Cinematic Diorama as the base direction.
- Use elevated 3/4 soft-perspective camera.
- Keep Stage 0 sparse but pleasant.
- Do not bake future reward assets into the base room.
- Locked preview must use final asset ghost treatment.
- Reward reveal should be calm in-room materialization, not confetti or loot feedback.
- Ringo and active panels must not cover the Creativity reward anchors.

## Do Not Change

- Do not add new reward unlock rules.
- Do not add a shop, inventory, drag/drop editor, or second economy.
- Do not require all 25 reward definitions to receive final art in this issue.

## Acceptance Criteria

- Creativity first reward can be previewed as a ghost, unlocked, and shown persistently.
- Next Creativity reward preview is readable without visual clutter.
- Desktop side panel and mobile bottom sheet preserve room context.
- Reduced-motion users can see the resolved state without relying on animation.

---

# Issue 6 — [Frontend] Add first path preview and selection flow

## Goal

Let first-time users preview how each path grows the room before choosing their first focus.

## Likely Files

```txt
frontend/src/views/Onboarding.vue
frontend/src/components/onboarding/
frontend/src/components/space/
```

## Behavior

- Hover on desktop or tap on mobile highlights the matching zone.
- The zone shows future reward silhouettes.
- Ringo copy explains the focus path.
- Selecting a path starts/reactivates it through existing path APIs where possible.

## Do Not Change

- Do not make the first focus permanent.
- Do not require all paths to be joined at once.
- Do not introduce a separate onboarding backend unless necessary.

## Acceptance Criteria

- User can preview all five paths.
- User can choose first focus path.
- Existing path start/join flow still works.
- User lands in the daily mission loop after choosing.

---

# Issue 7 — [Frontend] Add room reward unlock moment

## Goal

After mission completion, show a newly unlocked room object and then persist it in the room.

## Likely Files

```txt
frontend/src/components/ringo/
frontend/src/components/space/RewardUnlockMoment.vue
frontend/src/components/missions/MissionCenter.vue
```

## Behavior

- Mission completion still shows Ringo Moment.
- If the API returns new room rewards, show an unlock step.
- After the unlock step, the object appears in the correct zone.
- Refreshing the dashboard keeps the object visible.

## Do Not Change

- Do not block mission completion if reward animation fails.
- Do not depend on a full animation system for v1.
- Do not show duplicate unlocks for already seen rewards.

## Acceptance Criteria

- New reward can be displayed after mission completion.
- User can dismiss/continue.
- Object remains visible after reload.
- Seen state can be marked when supported by API.

---

# Issue 8 — [Backend Tests] Cover Living Space reward persistence

## Goal

Protect the new progression surface from duplicate unlocks and response drift.

## Coverage

- reward definition seeding
- first reward unlock for each path
- idempotent unlock behavior
- `/me/space` authenticated response
- `seen` update behavior
- mission completion with additive space reward data

## Do Not Change

- Do not remove existing mission/path/check-in tests.
- Do not assume frontend-specific animation behavior in backend tests.

## Acceptance Criteria

- Backend tests pass.
- Existing progression tests still pass.
- Duplicate mission completion does not duplicate room rewards.

---

# Issue 9 — [Frontend Tests/QA] Validate Living Space v1 flow

## Goal

Verify the first-run room experience and reward appearance flow.

## Coverage

- empty room loads
- five zones render
- path preview highlights the correct zone
- selected first path leads to mission recommendation
- mission completion can display new room reward
- unlocked object remains visible after reload
- mobile and RTL smoke pass

## Do Not Change

- Do not require polished final art assets for functional smoke coverage.
- Do not remove existing dashboard smoke tests.

## Acceptance Criteria

- Frontend build passes.
- Core route smoke checks remain valid.
- New Living Space flow has at least one repeatable manual QA checklist.

---

# Issue 10 — [Docs] Sync schema, API, and launch QA after implementation

## Goal

After implementation, update the supporting docs so the feature is not trapped in code only.

## Docs To Update

- `docs/DATABASE_SCHEMA.md`
- frontend API docs surface
- `docs/LAUNCH_QA_CHECKLIST.md`
- `docs/AI_CONTEXT.md`
- `docs/ROADMAP.md`
- README if Home positioning changes materially

## Do Not Change

- Do not mark the feature complete before code and QA are done.
- Do not document endpoints that do not exist yet.

## Acceptance Criteria

- Schema docs match actual database implementation.
- API docs match actual route behavior.
- QA checklist includes Living Space onboarding, mission completion, and reward persistence.
- AI context tells future Codex sessions to preserve Living Space as part of the Ringo-first experience.

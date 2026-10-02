# Living Space v1 UX Polish Backlog

## Purpose

Living Space v1 core rules are validated:

```txt
real mission progress -> first path reward -> persistent room object
```

This backlog captures UX polish follow-ups without starting a visual redesign. The current room UI is an implementation shell. Any richer room art, bitmap background, object illustration, lighting direction, or new visual style requires explicit product/design approval before implementation.

## Current Status

Validated:

- First eligible non-bonus mission unlocks the first reward for that path.
- First rewards persist after refresh.
- Completing another challenge in the same path does not replay the first reward.
- Legacy users receive first-path rewards from historical mission progress.
- Backfilled rewards are marked seen and do not replay old unlock modals.
- Later reward definitions remain locked previews until their rules are specified.

Known boundary:

- The room is not visually final.
- The object chips are placeholders, not final room art.
- Later rewards are preview-only, not active unlock targets.

## Polish Candidates

### 1. Room Clarity Copy

Problem:

The room explains the core idea, but it can be clearer that only real mission progress changes the room.

Potential improvements:

- Add a short empty-state line for new users:
  - "Complete your first mission in a path to place the first object here."
- Add a legacy-safe line when objects already exist:
  - "This room includes progress you made before Living Space existed."

Acceptance:

- Copy does not imply shop, inventory, decoration editing, or manual placement.
- Copy works in EN and FA.

### 2. Zone Panel Next Step

Problem:

The zone panel shows unlocked rewards, locked previews, and next reward, but does not clearly explain how the next visible change happens.

Potential improvements:

- Rename or supplement `Next visible change`.
- For v1, show first reward status only:
  - unlocked: "First reward placed."
  - locked: "Complete one non-bonus mission in this path."
- Keep later rewards as preview-only until rules exist.

Acceptance:

- The panel does not promise `early_consistency`, `path_progress_milestone`, `achievement_unlocked`, or `major_path_milestone` unlocks yet.
- The next-step copy remains compact.

### 3. Locked vs Unlocked Object Readability

Problem:

Current placeholder object chips distinguish locked/unlocked, but the difference is subtle and still feels like a list of labels rather than placed room objects.

Potential improvements:

- Improve text labels/state markers without adding new art.
- Add accessible labels for locked previews.
- Make unlocked state more legible in RTL and narrow widths.

Acceptance:

- No new graphics or object art without approval.
- Locked previews remain visually distinct from unlocked rewards.

### 4. Reward Unlock Moment Context

Problem:

The unlock moment works, but can better connect the reward to the room.

Potential improvements:

- Include a compact "Placed in: Fitness Corner" style line.
- After close, keep room refresh predictable.
- Avoid replaying old/backfilled rewards.

Acceptance:

- New reward modal appears only for newly unlocked rewards.
- Backfilled rewards never trigger old unlock modals.

### 5. Mobile And RTL Polish

Problem:

Manual QA says Persian/RTL is structurally usable, but not visually final.

Potential improvements:

- Check chip wrapping in Persian.
- Ensure zone panel does not crowd the room on mobile.
- Confirm close/action buttons stay reachable.

Acceptance:

- No horizontal overflow.
- Text wraps before clipping.
- Zone controls remain tappable.

## Deferred Product Decisions

These are intentionally not part of the next polish pass:

- Final room background art.
- Object illustrations or generated room assets.
- Drag/drop placement.
- Inventory.
- Shop or currency.
- Friend/public room visits.
- Later reward unlock rules.

## Later Reward Rule Questions

Before implementing later rewards, answer:

- `early_consistency`: how many days or completions?
- `path_progress_milestone`: based on missions, XP, path stage, or challenge count?
- `achievement_unlocked`: any achievement, path-specific achievement, or selected milestone achievements?
- `major_path_milestone`: v1.1 or v2?
- Should legacy users receive later rewards from history, or only first-path backfill?

## Recommended Next Issue

```txt
[Frontend] Living Space v1 copy and state clarity polish
```

Scope:

- Copy-only and state-label improvements.
- No room art changes.
- No layout redesign beyond small responsive fixes.
- No later reward unlock rules.

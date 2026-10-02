# Living Space v1 QA Checklist

## Purpose

This checklist validates the first Living Space v1 loop:

```txt
empty room -> path preview -> first path start -> mission recommendation -> mission completion -> room reward unlock -> persistent room object
```

It is a repeatable QA script for the current v1 implementation. It does not require final art assets, shop/inventory behavior, drag/drop editing, social rooms, or a second progression economy.

## Scope

Covered:

- Empty room loads for a new authenticated user.
- Five fixed path zones render.
- Onboarding path preview highlights the matching room zone.
- Selected first path starts the backend path and leads to a mission recommendation.
- Mission completion can return and display a new Living Space reward.
- Dismissing the reward marks it seen when the API supports it.
- The unlocked object remains visible after reload.
- Mobile and RTL smoke checks.

Not covered:

- Final room art direction.
- Drag/drop room editing.
- Inventory management.
- Shop or currency behavior.
- Friend visits or public rooms.
- Production device-matrix QA.

## Automated Checks

Run these before manual QA:

```bash
cd frontend
npm run build
npm run test:localization
npm run test:router
npm run test:dashboard
```

Backend persistence checks should also pass:

```bash
pytest backend/tests/test_living_space_service.py backend/tests/test_living_space_routes.py backend/tests/test_paths_missions.py -q
pytest backend/tests -q
```

Expected:

- Frontend build completes.
- Existing route/dashboard smoke checks remain valid.
- Backend tests confirm reward seeding, first reward unlock, duplicate prevention, `/me/space`, seen updates, and mission completion payload behavior.

## Manual QA Setup

Use a clean local database or a user that has not completed missions today.

Start backend:

```bash
cd backend
FLASK_ENV=development py app.py
```

Start frontend:

```bash
cd frontend
npm run dev
```

Open the frontend local URL in a browser.

## Fresh User Flow

1. Register a new user.
2. Confirm the onboarding path step appears.
3. Confirm the room preview is visible in the path step.
4. Hover or focus each path option on desktop.
5. Tap each path option on mobile width.
6. Confirm the highlighted room zone matches the selected path:

| Path | Expected Zone |
| --- | --- |
| Career | Work Desk |
| Creativity | Creative Corner |
| Fitness | Fitness Corner |
| Learning | Learning Corner |
| Sleep | Sleep Corner |

Expected:

- The preview renders one room, not separate mini dashboards.
- Ringo appears as guide/context, not as a room zone.
- Locked preview objects are visible enough to explain future room changes.
- The selected path can be started without a frontend error.

## Empty Room Dashboard

1. Complete onboarding or log in as a new user.
2. Open `/dashboard`.
3. Confirm Living Space appears below Mission Center when the full dashboard is visible.
4. Confirm five zones render.
5. Confirm no unlocked objects are shown yet.
6. Confirm each zone has a next locked reward preview.

Expected:

- The room loads from `GET /me/space`.
- Empty state copy tells the user real mission progress creates the first object.
- No shop, inventory, editor, or alternate currency UI appears.

## First Reward Unlock

1. Start a first path if onboarding has not already done it.
2. Complete the recommended main or tiny mission.
3. Confirm the normal mission completion feedback still appears.
4. Confirm a Living Space reward unlock moment appears when the API returns `living_space_reward`.
5. Dismiss the unlock moment.

Expected:

- The unlock moment names the reward and zone.
- Dismissal does not block mission completion.
- The dashboard room refreshes after unlock/dismiss.
- The unlocked object appears in the correct zone.

## Persistence And Duplicate Safety

1. Reload `/dashboard`.
2. Confirm the unlocked object is still visible.
3. Complete or resubmit the same already completed mission if the UI/API path allows it.
4. Start and complete a second challenge in the same path if available.
5. Confirm no duplicate Living Space unlock moment appears.
6. Open the room state again.

Expected:

- `GET /me/space` still shows the unlocked object.
- Already seen rewards do not keep showing as new.
- Duplicate mission completion does not duplicate room rewards.
- Completing another challenge in the same path does not replay that path's first reward.
- Other reward sequence behavior remains unchanged.

## Legacy User Backfill

Use an account that completed non-bonus missions before Living Space rewards existed.

1. Open `/dashboard` or request `GET /me/space`.
2. Confirm the first reward for each previously completed path appears in the room.
3. Confirm those backfilled rewards do not show old unlock modals.
4. Complete a new challenge in a path that already has backfilled progress.

Expected:

- Backfilled rewards use real historical mission progress.
- Backfilled rewards are already marked seen.
- The room is not empty for users with prior path progress.
- New mission completion does not replay a first reward that was backfilled from history.
- Later reward types such as `early_consistency`, `path_progress_milestone`, `achievement_unlocked`, and `major_path_milestone` remain locked previews until their rules are explicitly implemented.

## Mobile Smoke

Check the onboarding path preview and dashboard room at a narrow viewport.

Expected:

- No horizontal overflow.
- Zone controls remain tappable.
- Reward unlock modal fits the viewport.
- Text wraps before clipping.
- Room objects do not overlap the zone labels.

## RTL And Persian Smoke

Switch to Persian and repeat:

- Onboarding path preview.
- Dashboard empty room.
- First reward unlock moment.
- Reload after unlock.

Expected:

- Persian copy renders without missing translation keys.
- RTL layout remains readable.
- Zone names and reward moment copy are understandable.
- Modal actions remain easy to tap.

## Current Development Verification

Last updated: 2026-10-02

Verified commands during Living Space v1 implementation:

- `npm run build`
- `npm run test:localization`
- `npm run test:router`
- `npm run test:dashboard`
- `pytest backend/tests/test_living_space_service.py backend/tests/test_living_space_routes.py backend/tests/test_paths_missions.py -q`
- `pytest backend/tests -q`

Latest frontend verification after Rest Mode summary and Living Space unlock visibility hardening:

- `npm run build`
- `npm run test:localization`
- `npm run test:router`
- `npm run test:dashboard`
- `git diff --check`

Latest backend coverage added:

- Mission completion now has route coverage confirming `/me/space` shows the newly unlocked object before the reward is marked seen.
- The same coverage confirms room-level and zone-level `has_unseen_rewards` are true before dismissal, then existing seen-state checks preserve the unlocked object after dismissal.
- Mission completion coverage now confirms a second challenge in the same path does not replay the first path reward.
- Legacy mission history coverage now confirms historical first-path rewards are backfilled as seen and do not trigger old unlock modals.

Known QA boundary:

- This checklist is development-level functional QA. It does not replace a full production device/browser matrix before launch candidate approval.
- Backend pytest commands require a local backend test environment with pytest installed, such as the project backend virtualenv.

# Ringo Daily Loop QA Report

## Purpose

This report summarizes the QA state of the current Ringo daily loop after the Emotional MVP Relaunch work.

The focus is the companion-first daily experience:

```txt
Ringo guidance -> Today's Mission -> Mission action -> Ringo Moment -> Today Saved -> optional next step
```

The report is intended to help decide whether the loop is ready for broader launch hardening, not to claim product outcomes or user-study validation.

## Evidence boundary

This is a documentation report based on the current repository state, product/contract documentation, and manual development flows that were exercised during implementation.

Evidence included:

- Product and technical contracts in `docs/`.
- Existing frontend/backend daily mission contracts.
- Manual development checks covering the daily-loop interactions listed below.
- Frontend production build checks performed during the daily-loop implementation/polish work.

Evidence not included:

- No screenshots are attached.
- No browser recording is attached.
- No fresh automated end-to-end test log is attached to this report.
- No user research, analytics, retention data, or clinical outcome evidence is claimed.
- No full cross-browser or device-matrix QA was completed as part of this report.

## Test environment

Reported development QA was performed against the local RingoStrike development environment:

- Backend: Flask app using the existing local development setup.
- Frontend: Vue 3 + Vite.
- Daily mission APIs:
  - `GET /me/today-missions`
  - `GET /me/ringo/today`
  - `POST /me/missions/:id/done`
  - `POST /me/missions/:id/remind-later`
  - `POST /me/missions/:id/skip`
- Frontend build command used during implementation/polish checks:

```bash
cd frontend
npm run build
```

The report does not assert that a production deployment was tested end to end.

## Tested flows

The following flows were manually reasoned through and tested during development of the Ringo-first loop:

- Fresh user selecting/starting 3 challenges.
- Seeing one Ringo-led daily card.
- Setting one mission to Remind Later.
- Skipping one mission with a reason.
- Completing one mission.
- Seeing the reward sequence.
- Returning to Today Saved state.
- Using Optional Next Step.
- Expanding Optional Missions.
- Persian mode checks.
- Mission Context UX Phase 1 main/tiny/bonus clarity checks.
- Mission Context UX Phase 1 after-done/detail card check.
- Persian RTL visual check for the new mission context copy.
- Frontend build checks.
- Frontend router smoke check.
- Git diff whitespace check.

These checks were useful for validating the main loop shape, but they should not be treated as a replacement for repeatable automated smoke coverage.

## Mission Context UX Phase 1 addendum

Status: implemented and manually checked after merge into `dev`.

Scope checked:

- Main mission context state.
- Tiny mission context state.
- Bonus mission context state.
- After-done/detail card state.
- Persian RTL visual behavior for the new context layer.

Observed QA notes:

- `MissionContextPanel.vue` appears as a display-only clarity layer inside MissionCenter.
- Path/challenge breadcrumb appears when available.
- Mission intensity/time display appears when available.
- “What counts” instruction copy appears for mission clarity.
- “Why this helps” copy appears for mission purpose clarity.
- Tiny mission framing is no-shame and keeps the smaller step valid.
- Bonus mission framing remains optional.
- Optional bonus action hierarchy keeps `Finish for today` primary when today is already safe.
- Existing MissionCenter actions, focus mode, CompactProgressStrip, RewardMoment behavior, Rest Mode, and `Show dashboard` behavior are preserved.

Validation commands/results:

- `npm --prefix frontend run build` passed.
- `npm --prefix frontend run test:router` passed.
- `git diff --check` passed.
- Existing Vite large chunk warning remains.

Boundaries confirmed:

- No backend changes.
- No database changes.
- No API changes.
- No mission mutation behavior changes.
- No XP, streak, achievement, check-in, reminder delivery, or progression logic changes.
- No dashboard redesign.
- No contextual reward sequence implementation.
- No Telegram mission-specific deep-link restoration.

Not fully verified:

- No fresh automated end-to-end test log is attached for Mission Context UX Phase 1.
- No full mobile viewport matrix was completed for every mission context state.
- No screen-reader/accessibility pass was completed for the new context layer.
- Full contextual reward sequence and Telegram mission-specific deep-link restoration remain future work.


## Frontend-only seeded content display localization addendum

Status: implemented and partially manually checked after merge into `dev`.

Scope checked:

- Persian MissionCenter seeded mission display.
- Persian onboarding challenge selection.
- Known seeded challenge/path/mission display copy where available.
- Fallback behavior by design for unknown/custom backend content.

Observed QA notes:

- Known seeded mission/path/challenge copy can now be localized at the frontend display layer.
- `missionDisplayCopy.js` and `ringoContentLocalization.js` are the display-localization helpers.
- Persian onboarding and Challenge Discovery surfaces now avoid several obvious English seed-content leaks.
- Unknown/custom backend content still falls back to backend-provided title/name/description.
- Raw backend values remain logic inputs.

Validation commands/results:

- `npm --prefix frontend run build` passed.
- `npm --prefix frontend run test:router` passed.
- `git diff --check` passed.
- Existing Vite large chunk warning remains.

Boundaries confirmed:

- No backend changes.
- No database changes.
- No schema changes.
- No API changes.
- No seed data changes.
- No onboarding completion logic changes.
- No path start logic changes.
- No challenge join logic changes.
- No mission mutation behavior changes.
- No XP, streak, achievement, check-in, reminder delivery, or progression logic changes.
- No CMS.
- No AI-generated copy.

Not fully verified:

- No full audit of every seeded mission/path/challenge key.
- No full mobile viewport matrix for onboarding/challenge discovery after localization.
- No automated test currently asserts localization fallback coverage for every known seeded key.
- Unknown/custom content fallback is design-validated but not exhaustively tested.


## Optional explorer progress-map and RTL/root-background addendum

Status: implemented and manually checked during frontend polish.

Scope checked:

- English MissionCenter optional explorer visual behavior.
- Persian MissionCenter optional explorer visual behavior.
- Path/challenge progress-surface cards.
- Circular icon progress rings.
- Reward-ready/building visual slots.
- Earned/total XP summaries.
- Mission icon fallback behavior.
- Status-aware mission row colors.
- Completed path/challenge visibility.
- Persian/RTL root-background and layout stability around Dashboard/MissionCenter.

Observed QA notes:

- Post-safe optional explorer now behaves like a calm growth/progression map.
- Completed paths/challenges can remain visible so completion feels acknowledged.
- Due reminders still own focus.
- Future reminders remain quiet until due.
- Reward-ready/building states are frontend display states only.
- The previous Persian/RTL white/blank root-background issue was addressed by ensuring dark full-viewport coverage for `html`, `body`, `#app`, and the app shell.
- Existing low-opacity white glass highlights remain intentional parts of the dark UI, not light scrims.

Validation commands/results:

- `npm --prefix frontend run build` passed.
- `npm --prefix frontend run test:router` passed.
- `npm --prefix frontend run test:localization` passed.
- `git diff --check` passed.
- Existing Vite large chunk warning remains.

Boundaries confirmed:

- No backend changes.
- No database changes.
- No schema changes.
- No migrations.
- No API response shape changes.
- No mission mutation behavior changes.
- No XP, streak, achievement, check-in, activity, reminder delivery, or progression ownership changes.
- No reward-claim backend logic.

Not fully verified:

- No screenshot artifact is attached.
- No full mobile/desktop viewport matrix is attached.
- No automated visual regression test asserts the optional explorer growth-map state.


## Mission Reward Moment v1 addendum

Status: implemented and manually checked during frontend polish.

Scope checked:

- Main mission completion reward.
- Tiny mission completion reward.
- Bonus mission completion reward.
- Already-done and no-XP completion behavior.
- English and Persian localized reward copy.
- RTL behavior through the existing i18n/root direction system.

Observed QA notes:

- Mission completion can show a lightweight reward moment after successful completion.
- The reward moment reuses `RingoRewardSequence.vue`; no duplicate reward component was created.
- The full reward moment appears only when `mission.xp_awarded > 0` and `mission.already_done !== true`.
- Already-completed missions do not replay the full reward overlay.
- Missing or zero XP falls back to calm completion copy instead of fake rewards.
- Main/tiny missions can show Today Safe / streak-protected language when appropriate.
- Bonus missions show bonus-complete XP language, but do not claim Today Safe and do not create a new bonus chain.
- Optional explorer / next-action flow still appears after the reward moment is dismissed.

Validation commands/results:

- `npm --prefix frontend run build` passed.
- `npm --prefix frontend run test:router` passed.
- `npm --prefix frontend run test:localization` passed.
- `git diff --check` passed.
- Existing Vite large chunk warning remains.

Boundaries confirmed:

- No backend changes.
- No database changes.
- No schema changes.
- No API contract breaking changes.
- No mission mutation behavior changes.
- No XP, stat, streak, achievement, check-in, activity, reminder delivery, reward economy, or progression ownership changes.
- No Ringo Brain decision policy changes.

Not fully verified:

- No screenshot artifact is attached.
- No full mobile/desktop viewport matrix is attached.
- No automated visual regression test asserts the reward overlay state.


## Fresh user 3-challenge flow

Status: partially verified through manual development flow.

Expected behavior:

- A fresh user can enter the guided path/challenge experience.
- Starting/selecting multiple challenges creates more than one available daily mission.
- The dashboard still leads with one Ringo-led daily card instead of a dense mission dashboard.
- Secondary missions remain available through optional/secondary surfaces.

Observed QA notes:

- The daily surface is designed to prioritize a single focused mission.
- Optional Missions remain available but are visually secondary.
- Main/tiny/bonus mission metadata is surfaced through mission intensity labels.

Not fully verified:

- This report does not include a fresh database replay log proving the exact 3-challenge setup from scratch.
- Long-run behavior across multiple days was not verified.

## Remind Later flow

Status: manually checked during development.

Expected behavior:

- `Remind later` opens reminder options instead of immediately competing with other actions.
- Reminder options remain focused.
- The user can back out of the panel.
- Selecting an option persists through the existing reminder endpoint.
- Ringo Coach shifts to a gentle reminder-oriented message/mood.

Observed QA notes:

- The focused daily card hides the normal action row while reminder options are open.
- Optional mission reminder panels also hide that mission's normal action row while open.
- Reminder choices use the existing `/me/missions/:id/remind-later` endpoint.
- Reminder notices are intentionally kept because they provide operational confirmation.

Not fully verified:

- Actual delivery of native or external notifications is out of scope; the product currently records reminder intent, not native notification delivery.

## Skip reason flow

Status: manually checked during development.

Expected behavior:

- `Skip` opens skip reason options.
- Skip reasons remain focused.
- The user can skip with or without a reason.
- Supported reason values are persisted through the existing skip endpoint where backend support is available.
- Ringo Coach uses a non-shaming tone.

Observed QA notes:

- The focused daily card hides the normal action row while skip reasons are open.
- Optional mission skip panels also hide that mission's normal action row while open.
- The frontend sends stable reason keys such as `too_tired`, `no_time`, `too_hard`, `not_relevant`, `disliked`, and `other`.
- The frontend safely retries without a reason if the backend rejects a reason shape it does not support.

Not fully verified:

- This report does not include database inspection proving every reason was persisted in a specific test row.

## Mission completion flow

Status: manually checked during development.

Expected behavior:

- Completing a mission uses `POST /me/missions/:id/done`.
- Existing check-in, XP, streak, achievement, and activity logic remains canonical.
- Completion does not introduce a separate Ringo-specific progression economy.
- The reward sequence opens after completion.

Observed QA notes:

- Mission completion continues to flow through the existing mission completion endpoint.
- The frontend builds reward steps from backend `reward_sequence` when present.
- If backend reward steps are absent, the frontend uses a local fallback sequence.
- Success notices after completion were reduced so they do not repeat the reward/Today Saved message.

Not fully verified:

- This report does not include a backend test run proving all stats/achievement side effects for the current branch.

## Reward sequence flow

Status: manually checked during development and covered by frontend build verification.

Expected behavior:

- The reward sequence appears after mission completion.
- Steps can advance one by one.
- The user can skip/finish the sequence.
- Reward rendering should not block the underlying mission/check-in write.

Observed QA notes:

- `RingoRewardSequence` uses a modal overlay with step progress and a finish/continue action.
- Supported backend reward step types are filtered before rendering.
- Local fallback steps include Ringo message, mission completed, XP earned when available, Today Saved when applicable, and next choice.

Not fully verified:

- No animation timing/accessibility audit was performed.
- No screen-reader pass was performed.

## Today Saved flow

Status: manually checked during development.

Expected behavior:

- After enough required progress is complete, the UI shows Today Saved.
- Required mission actions are hidden.
- Optional actions remain available but secondary.
- Today Saved copy should not be repeated excessively.

Observed QA notes:

- The daily card displays a Today Saved state when Ringo Brain progress reports `today_saved`.
- Required mission actions are hidden in that state.
- Completion notices were kept subtle and suppressed when they would duplicate reward/Today Saved feedback.
- Copy was polished to make "stop here" explicit.

Not fully verified:

- Multi-day reset behavior was not verified in this report.

## Optional Next Step flow

Status: manually checked during development.

Expected behavior:

- Optional Next Step appears only after Today Saved.
- It should feel optional, not required.
- It should give one extra suggested mission without turning the page back into a dashboard.

Observed QA notes:

- Optional Next Step is gated behind `today_saved`.
- Copy explicitly says the user can ignore it and still be done.
- Actions are secondary, including finishing for today.

Not fully verified:

- Ranking of optional candidates was not exhaustively tested across all possible mission combinations.

## Optional Missions flow

Status: manually checked during development.

Expected behavior:

- Optional Missions remains collapsed/secondary by default.
- Expanding it reveals other missions without competing with the main daily card.
- Reminder and skip panels inside optional missions should not compete with their row actions.

Observed QA notes:

- Optional Missions is visually secondary.
- The toggle keeps other missions tucked away until explicitly expanded.
- Optional mission reminder/skip panels hide that mission's normal action row while open.

Not fully verified:

- Large mission counts were not stress-tested for layout/performance.

## Persian/English UI notes

Status: partially checked during development.

Expected behavior:

- Persian mode should use centralized `lang="fa"` and `dir="rtl"` behavior.
- Persian typography should use the Vazirmatn font through global base styles.
- Daily-loop copy should avoid obvious English/Persian mixing where frontend i18n can safely handle it.

Observed QA notes:

- The app has frontend i18n with persisted locale selection.
- Persian typography is centralized through the active base CSS.
- Daily-loop polish removed several obvious mixed-copy issues in the daily loop.
- Ringo Coach no longer forces a component-local English font family.

Not fully verified:

- This report does not claim all Persian copy across the entire app is clean.
- Some older non-daily-loop Persian strings may still contain English terms such as `Streak` or product names.

## Known issues and follow-ups

- Add repeatable frontend smoke coverage for MissionCenter, MissionContextPanel, `/paths`, mission done, remind later, skip reason, reward sequence, and Today Saved.
- Add a documented QA script for a fresh user starting multiple challenges and exercising the full daily loop.
- Verify actual database persistence for skip reasons in a targeted backend or integration test.
- Verify multi-day reset behavior for Today Saved, deferred missions, skipped missions, and optional mission ranking.
- Run a focused mobile viewport pass for the Ringo daily card, reminder options, skip reasons, reward overlay, and optional mission list.
- Run an accessibility pass for the reward overlay and panel focus behavior.
- Continue localized-copy QA as seeded content expands, especially onboarding, Challenge Discovery, MissionCenter, missing-field fallbacks, and unknown/custom backend content.
- Continue cleaning Persian copy outside the daily loop.
- Keep Ringo sprite assets, `frontend/src/constants/ringoSprites.js`, and backend `sprite_key` values aligned before relying on clean launch builds.
- Expand production/deployment smoke checks after any VPS deployment.

## Overall QA verdict

The Ringo daily loop is in a promising MVP-ready shape for continued launch hardening.

The current implementation appears aligned with the product direction:

- Ringo leads the experience.
- The daily card presents one focused mission.
- Mission actions are calmer and less duplicative.
- Reminder and skip flows are conversational and non-shaming.
- Reward sequence and Today Saved support the emotional loop.
- Optional next actions are present but secondary.
- Mission Context UX Phase 1 improves mission clarity without changing backend/API/database/progression behavior.

However, QA confidence is still development-level rather than release-candidate-level. The loop needs repeatable smoke tests, a documented fresh-user test script, mobile/accessibility passes, and targeted persistence checks before it should be treated as fully launch-verified.

## Recommended next step

Create a small automated and manual QA checklist for the Ringo daily loop:

1. Add frontend smoke coverage for MissionCenter daily actions.
2. Add backend/integration coverage for skip reason persistence and reminder state.
3. Run a fresh-user manual script on a clean local database.
4. Capture screenshots for English, Persian, desktop, and mobile daily-loop states.
5. Re-run `cd frontend && npm run build` and the relevant backend smoke tests before release candidate review.

# Living Room Friends Beta — Milestone Plan & Issue Pack

Status: approved by Amir on 2026-10-18 (plan and recommended decisions D1–D6).
Source plan: Claude Docs "Living Space Testable Release — Milestone & Issue Plan".
Baseline: `dev` @ `9a19e48` (2026-10-14). Audit: project doc `context/LIVING_SPACE_AUDIT_2026-10-18.md`.

## Milestone

- **Title:** Living Room Friends Beta
- **Description:** Ship the Living Room as a stable, bilingual, deployed build that 3–5 friends can use daily for one week, including the visual pixel-art Living Space on desktop and mobile (D7, D8).

### Definition of done

- A new user can sign up, choose a path, finish a first mission and see the first room object in about 5 minutes, unaided.
- Icons are readable on every Living Room surface: white on dark, glyph ≥ 20 px, hit target ≥ 44 px.
- Persian and English both work in the room (zone names, object names, Ringo copy, RTL).
- Due reminders open the right room and mission (#337); bonus missions are reachable after the main step (#338).
- `dev` merged to `main`, tagged `v0.9-beta`, deployed on the VPS behind `/api-proxy`, DB backup taken first.
- All backend tests and all frontend smoke tests pass, including a new Living Space smoke test.
- Testers have an invite, a short guide (FA/EN) and one feedback channel.

## Decisions (approved 2026-10-18)

| # | Decision |
| --- | --- |
| D1 | ~~The beta ships the current room shell. Diorama art moves to the next milestone (Living Room Visual v1).~~ Replaced by D7 on 2026-10-19. |
| D2 | The room is the whole Home. MissionCenter becomes Ringo's guide layer inside the room; no separate dashboard surface. |
| D3 | Room panel = one Ringo message + one primary action; details on demand (no tab-heavy panel). Mock-up approval required before build (B9). |
| D4 | Later rewards (Lamp etc.) stay ghost previews with no unlock rule shown until v1.1. |
| D5 | Challenge icons resolve by a stable key, not the DB auto-increment id. |
| D6 | Testers use the website on phone and desktop. PWA install is a later issue; no app-store build. |
| D7 | (2026-10-19, replaces D1) This milestone reaches the first presentable **visual** Living Space on desktop and mobile: a real room scene with zones and objects. The friends beta ships with this visual room. |
| D8 | (2026-10-19) Visual v1 is **layered pixel art**: 480×270 base, integer scaling only, one transparent PNG layer per zone/object keyed by `asset_key`. See [Living Space Visual v1 Spec](LIVING_SPACE_VISUAL_V1_SPEC.md). |
| D9 | (2026-10-19) v1 art per zone: one Stage 0 base prop, the first-reward object (placed when unlocked), and the second reward as a ghost preview — 5 zones × 3 = 15 elements. Other rewards appear only in the panel's object list. |
| D10 | (2026-10-19) RTL never mirrors the room; only the panel and text are mirrored. |

Scope update 2026-10-19: see [Living Room Beta Scope Update](LIVING_ROOM_BETA_SCOPE_UPDATE.md) for D7–D10 and issues B17–B25. The art format is settled by D8 (pixel art).

## Phases and gates

| Phase | Issues | Gate to next phase |
| --- | --- | --- |
| 0 Foundations | B1, B2 | Decisions recorded, milestone and issues exist on GitHub |
| 1 Stabilize | B3–B7 | All tests green, icon sizes measured in a render |
| 2 Beta UX | B8–B9 | Room panel v2 and bonus/recommendation priority merged |
| 2b Room behavior | B23, B24, then B10, B11 | A new account reaches the first reward unaided; Close/"Enough for today" return to the room; reminders are visible |
| 2c Visual v1 | B17 → B18 (approval gate) → B19 → B20 → B21 → B22 | Visual pixel-art room matches the approved mock-ups on desktop and mobile, EN and FA |
| 3 Release | B12–B14 | Smoke script passes on the live URL; QA covers the visual room |
| 4 Beta week | B15–B16 | Feedback synthesized into next-milestone issues |

B10 (copy) and B15 (tester kit) may start during Phase 1. Phase 2b runs while the visual design (B17, B18) happens on the canvas. B25 (final pixel Ringo sprite) is in the next milestone, "Living Room Visual polish", and is not a beta blocker.

## Labels

`living-space`, `beta`, `frontend`, `backend`, `docs`, `ops`, `qa`, `i18n`, `ux`, `bug`, `test`

## Shared rules for every code issue

- One feature branch per issue, PR into `dev`, before/after screenshots for UI changes.
- Run and report from the repo root: `pytest backend/tests -q`, then `cd frontend && npm run build` and every `npm run test:*` script inside `frontend/`.
- No changes to XP, check-in, streak, achievement or reward logic. No schema change unless the issue says so.
- Persian and English verified for any UI change; `prefers-reduced-motion` respected.

---

## B1 — [Docs] Record Living Space foundation decisions

Labels: docs, living-space, beta

**Goal:** Make D1–D6 the source of truth in repo docs.

**Scope**
- Add this file as `docs/product/LIVING_ROOM_FRIENDS_BETA_PLAN.md`.
- Update `docs/product/LIVING_SPACE_HOME_SHELL_SPEC.md`: answer its "Open Product Questions" with D2, D3, D4.
- Link the plan from `docs/ROADMAP.md` and `docs/AI_CONTEXT.md`; add a CHANGELOG entry.

**Acceptance**
- No code changes. Decisions D1–D6 appear in the docs with date 2026-10-18.

## B2 — [Ops] Repo hygiene: milestone, labels, issues, branch sync

Labels: ops, beta

**Scope**
- Create the milestone and labels; create issues B1–B16 (B6 = existing #337, B8 = existing #338; do not duplicate them).
- Add #337 and #338 to the milestone. Comment on #336: moved to the next milestone (Living Room Visual v1).
- Fast-forward local `main` to `origin/main` (no reset, no force).

**Acceptance**
- Milestone lists 16 items; #336 not in it; local `main` == `origin/main`.

## B3 — [Frontend] Icon legibility normalization

Labels: frontend, living-space, ux, beta

**Problem (verified):** All icon PNGs are black glyphs; every component adds its own CSS filter (4 different recipes). PR #307 shrank glyphs (zone 25→18 px, panel 29→21, inline 24→17, mission 31→22; action icons 17 px in 34 px buttons). `RemainingMissionExplorer .missionChoiceIcon img` and `MissionCenter .restModeSummaryIcon img` have no filter (black on dark).

**Scope**
- One shared class or small component for "icon on dark" (white rendering), used by Living Space and the two unfiltered rules.
- Restore glyph sizes to 20–24 px inside existing frames; compact action buttons ≥ 44 px hit target.
- Add a short label under compact action icons (Smaller / Later / Skip), or keep tooltip + visible label on focus — per approved mock-up.

**Out of scope:** new icon art, replacing PNGs with the SVG set.

**Acceptance**
- No `<img>` icon renders black on a dark surface (checked in a Playwright render, EN and FA).
- Measured glyph ≥ 20 px, hit target ≥ 44 px for action buttons.

## B4 — [Frontend] Neutral icon fallback and stable challenge icon keys

Labels: frontend, living-space, beta

**Problem (verified):** `default_path_icon.png` and `default_challenge_icon.png` are copies of `ringo/sleeping.png` (1024×1536) and render as a white blob. Challenge icons resolve by DB id (`30.png`–`44.png`); a fresh DB seeds ids 1–15, so every challenge falls back.

**Scope**
- Replace both fallbacks with a neutral glyph.
- Resolve challenge icons by a stable key (seed key or slug) with id as a temporary alias. Update `FRONTEND_CONTRACT.md`.

**Acceptance**
- Fresh DB and existing DB both show correct or neutral icons; no Ringo sprite used as an icon.

## B5 — [i18n] Persian names in the room

Labels: i18n, frontend, living-space, beta

**Problem (verified):** Zone titles and reward titles come from backend English strings (`SpaceZone`, `SpaceZonePanel`, `SpaceObject`, `RewardUnlockMoment`); zone kicker shows raw `path_key`.

**Scope**
- Map `zone_key` and reward `key` to i18n strings in `en.js` and `fa.js`; keep backend response shape unchanged.

**Acceptance**
- No English string in the room in FA mode; existing localization smoke test extended.

## B6 — [Bug] Due reminder opens wrong room (existing #337)

Labels: bug, living-space, beta

**Scope**
- Reproduce #337 on `dev` @ `9a19e48` (PR #339 claims a fix). Fix what remains; close #337 with evidence.

**Acceptance:** #337's acceptance criteria pass by hand in EN and FA.

## B7 — [Test] Green smoke tests + Living Space smoke test

Labels: test, frontend, beta

**Problem (verified):** `npm run test:challenge` fails: `submitJoinFlow` now returns `challengeId`, `challengeName`, `challengeDescription`, `mode`, `navigated:false`; the test still expects `{enrollmentId, navigated:true}` (stale since 2026-06-05).

**Scope**
- Update the test to the current contract (confirm intended `navigated` behavior first).
- Add a dependency-free smoke test for Living Space state helpers (zone selection, reminder focus, first-reward visibility).

**Acceptance:** all `npm run test:*` scripts pass.

## B8 — [UX] Bonus surfacing and layered Ringo recommendation (existing #338)

Labels: ux, frontend, living-space, beta

**Scope**
- Design first (mock-up in Cowork), then build.
- Frontend: after main is done, Ringo offers bonus as optional ("Main step done. Want a bonus?"); user can change the suggestion; due reminders outrank bonus.
- If recommendation logic needs backend Ringo Brain changes, split into a separate backend issue.

**Acceptance:** #338 acceptance criteria.

## B9 — [UX] Simplify the room panel (D3)

Labels: ux, frontend, living-space, beta

**Scope**
- Approved mock-up first. Panel shows one Ringo message + one primary action; zone/path/challenge details open on demand.
- Reuse existing `SpaceZonePanel` state machine; no new progression logic.

**Acceptance:** build matches the approved mock-up on desktop and 390 px mobile, EN and FA.

## B10 — [Copy] Ringo and room copy pass, EN and FA

Labels: ux, i18n, living-space, beta

**Scope:** empty room, first reward, ghost previews (no promised rule, D4), rest, due reminder, bonus offer. Tone: caring, no shame, "enough for today" clear.

**Acceptance:** copy table reviewed by Amir and merged into `en.js`/`fa.js`.

## B11 — [UX] First run to first reward in about 5 minutes

Labels: ux, qa, living-space, beta

**Scope:** timed run with a fresh account (signup → path → first mission → first object); remove any blocker found.

**Acceptance:** two unaided runs under ~5 minutes, one in FA, one in EN.

## B12 — [QA] Living Space QA on real devices

Labels: qa, living-space, beta

**Scope:** run `docs/qa/LIVING_SPACE_V1_QA_CHECKLIST.md` on a real phone and desktop, EN and FA; record in `docs/MANUAL_QA_REPORT.md`.

**Acceptance:** checklist signed off; blockers filed and fixed.

## B13 — [Release] Merge dev into main and tag v0.9-beta

Labels: ops, beta

**Scope:** PR `dev` → `main`; resolve the one-line `frontend/src/styles/base.css` difference (keep dev's version unless a regression is found); tag `v0.9-beta`.

**Acceptance:** `main` builds and all tests pass at the tag.

## B14 — [Ops] Deploy v0.9-beta to the VPS

Labels: ops, beta

**Scope**
- Back up the production SQLite DB first.
- Build with `VITE_API_BASE=/api-proxy`, `VITE_BASE=/`; restart `ringostrike-backend`; run `scripts/vps_smoke_test.sh`.
- Write rollback steps (previous `dist` + DB copy).
- Check the live URL from an Iranian connection.

**Acceptance:** smoke script passes on the live URL; rollback documented in `DEPLOYMENT_CHECKLIST.md`.

## B15 — [Beta] Tester kit

Labels: beta

**Scope:** 3–5 tester accounts or invite flow; one-page guide (FA/EN): what RingoStrike is, what to try daily for a week; one feedback form or channel; questions about confusion and skipped steps, not "did you like it".

**Acceptance:** all testers logged in on day 1.

## B16 — [Beta] Feedback synthesis

Labels: beta, ux

**Scope:** after one week, synthesize feedback into themes; turn findings into issues for Living Room Visual v1 and backlog.

**Acceptance:** findings doc + new issues created.

---

## Next milestone (not in this one)

**Living Room Visual polish:** B25 final pixel Ringo sprite (Amir retouch), art for the remaining reward definitions beyond the 15 v1 elements, #336 ambient music idea. (The asset contract, room scene, v1 objects, materialization and mobile room moved into this milestone as B17–B22 under D7.)

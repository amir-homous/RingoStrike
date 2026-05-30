# RingoStrike - Changelog

This changelog is reconstructed from recent git history and current code inspection.

## Current `main`

### Merge: Public Identity, Profile System, UX Improvements

Recent head commit:

- `8132155` - Merge dev branch: integrate public identity, profile system, and UX improvements

This merged the public identity/profile work from `dev` into `main`.

## Public Profile And Identity Layer

Relevant commits:

- `165b231` - commit before Goal Milestone
- `84cf941` - feat(profile): complete public identity and profile customization foundation fixes #42
- `5aca253` - add avatar 16x
- `8e9e778` - feat(profile): enhance public & private profile UX + avatar system improvements
- `d4639fd` - feat(profile): implement public profile page, visibility settings and and profile setting flow
- `34b1c8a` - Fix Edite Profile in Profile.vue v.1
- `2ec916a` - add profile visibility enforcement system
- `f9e01d9` - feat(public-profile): improve identity timeline and add profile sharing
- `e164e8b` - refine public profile identity hierarchi
- `c9d8236` - Fix and Remove Edite Profile From Profile Hero file in Public
- `4f59008` - refactor public profile into shared design system
- `1cd8f07` - add public profile frontend foundation
- `803e1a5` - add public profile api foundation
- `ec5e650` - add public profile backend foundation
- `7fc6110` - add public-safe username normalization system
- `dfb5358` - prepare public identity layer database foundation

Current implemented result:

- Public profile page route `/u/:username`.
- Public profile APIs under `/api/public/profile/<username>`.
- Public consistency and public achievements APIs.
- Profile visibility enforcement.
- Avatar URL and bio profile fields.
- Profile settings endpoint under `/api/me/profile/settings`.
- Username normalization and reserved username list.
- Public-safe activity filtering for public profiles.

## Documentation Foundation

Relevant commit:

- `fdfe058` - docs: add complete project architecture and AI context documentation

Current docs have now been resynchronized against actual code, including API routes, schema, architecture, roadmap, and analysis.

## Profile, Achievements, Dashboard Progression

Relevant commits:

- `c841fed` - commit before merge from Future Profile Commit to dev
- `a4c0103` - Add profile identity hub with dynamic title and consistency heatmap
- `1c88292` - Improve Recent Achievements UI with rarity, image slots, and lock states
- `567218e` - Add event-driven achievement engine with dashboard integration
- `6118f32` - Add scalable dashboard activity timeline and /me/activity feed
- `1012149` - Enhance dashboard progression UX with rewarding check-ins
- `87f863c` - Merge branch 'codex-progress-exp' into dev
- `23eea6c` - Add dashboard progress experience with reusable components
- `77bcaf9` - Add authenticated /me/stats endpoint with XP and level engine

Current implemented result:

- XP and level calculations.
- Dashboard progression cards and reward feedback components.
- Activity feed derived from check-ins, streaks, level-ups, and achievements.
- Achievement definitions and user unlock tracking.
- Profile identity hub with dynamic title and consistency data.

## Backend Modularization And Stats Fixes

Relevant commits:

- `b94d61c` - Merge pull request #36 from amir-homous/dev
- `eae8372` - Refactor backend into modular Flask architecture fixes #35
- `b10a22e` - Refactor backend architecture and separate auth services
- `46555bb` - Resolve #27 strike calculation and stats persistence
- `70d00fb` - Merge pull request #34 from amir-homous/dev
- `6f065c0` - commit before auth refactor , fixes #31
- `9c7a3d0` - update requirements.txt and add flask
- `a790883` - add new challenge to database from code
- `7145b40` - update db structure and insert some data in users

Current implemented result:

- Route/service structure under `backend/routes` and `backend/services`.
- Centralized streak and stat calculations.
- SQLite table initialization for users, challenges, enrollments, checkins, stats, achievements, and sessions.
- Auth refactor partially present, though active routes still use `backend/auth.py`.

## Frontend API Docs, UI Polish, Leaderboard, Auth Fixes

Relevant commits:

- `e6d43d7` - Front-End Add App Footer and API DOC link to Website
- `4f2a441` - chore: remove database from tracking and ignore it
- `c0b2694` - Backend Fix New Database Structure base on Old Notion Structur
- `ea30071` - Front-end Fix Router Address for Api Doc
- `6c22b81` - Front-end Create APIT DOC page
- `ea81f7b` - fix register/login/logout with user and password
- `2ebe113` - Merge pull request #20 from amir-homous/dev
- `1bd1778` - docs: update frontend contract to match current architecture
- `8c83d22` - fix: leaderboard page/embed consistency and error handling
- `d99d5d6` - ui: milestone 0.1 polish (dashboard, challenges, enrollment, leaderboard, login)
- `c60a737` - ui(login): apply base UI kit and fix button click crash
- `e422805` - docs: add frontend contract for project architecture
- `4841595` - Fix: leaderboard computed from daily logs (streak + totals)

Current implemented result:

- API docs view exists in frontend.
- Login/register components exist.
- Leaderboard uses check-ins for totals and streak.
- Dashboard, challenge, enrollment, leaderboard, and login UX received reusable UI polish.

## Current Known Issues Discovered During Documentation Sync

- `gapgpt` command in `cmd.txt` is not available in this environment.
- `GET /me/stats` is registered twice.
- `frontend/src/stores/session.js` calls missing `api.setToken()`.
- `services/auth_service.py` duplicates active auth logic but is not wired into route registration.
- Debug endpoints are unauthenticated.
- `sessions` table is unused by active auth.

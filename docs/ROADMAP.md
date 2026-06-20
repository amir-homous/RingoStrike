# RingoStrike - Roadmap

## Current Product Stage

RingoStrike is currently in:

> Post-MVP Stabilization / Emotional MVP Relaunch Planning

The product has moved beyond raw MVP. The core progression identity system is implemented, and the current priority is to preserve that foundation while reshaping the experience around Ringo as the caring daily companion.

The detailed product direction lives in:

- [Product Direction Master Notes](product/PRODUCT_DIRECTION_MASTER_NOTES.md)
- [MVP Relaunch Phases](product/MVP_RELAUNCH_PHASES.md)
- [GitHub Issue Pack](product/GITHUB_ISSUE_PACK.md)

---

## Completed Foundations

### Core App

- Flask backend app factory and blueprint registration.
- Vue 3 + Vite frontend.
- Local auth with JWT cookie/Bearer support.
- SQLite schema initialization.
- Challenge listing, detail, join, enrollment, check-in, history, and leaderboard flows.
- Public and authenticated API surfaces.
- Frontend API docs surface.

### Progression

- XP per check-in.
- Current and longest streak calculations.
- Level and progress percent calculations.
- Dashboard stats.
- Activity feed.
- Achievement definitions and unlock tracking.
- First-check-in achievement rewards.
- Stats sync after check-in.
- Duplicate check-in handling.

### Profile And Public Identity

- Private profile aggregate.
- Dynamic profile title.
- Consistency heatmap data.
- Avatar URL and bio fields.
- Public profile endpoints.
- Public achievements and consistency endpoints.
- Public/private profile visibility.
- Public route `/u/:username`.
- Username normalization and reserved username list.
- Profile settings endpoint.
- Profile update validation for name, bio, avatar URL, and visibility.

### Challenge And Social Momentum

- Default launch challenge seeding.
- Challenge discovery UI polish.
- Challenge card compact mode for dashboard.
- Member count and member preview on challenge discovery.
- Leaderboard rank metadata.
- Deterministic leaderboard tie-breakers.
- Today leaderboard data.
- Leaderboard UI showing rank and today check-in status.
- Enrollment UI with challenge remaining time.
- Enrollment UI with daily reset rhythm and urgency states.

### Guided Paths And Missions

- Backend-backed growth paths with `paths` and `user_paths`.
- Path-linked challenge metadata: `path_id`, `difficulty`, `stage`, `estimated_days`, and `ringo_intro`.
- Mission definitions through `missions`.
- Per-user daily mission state through `mission_logs`.
- Path APIs for listing paths, loading path challenges, and starting/reactivating a path.
- Mission APIs for today's missions, mark done, remind later, and skip.
- Mission completion delegates to the existing check-in pipeline for XP, streak, achievement, activity, and stats consistency.
- Ringo decision service for coach state, sprite key, message, and primary/secondary action selection.
- Dashboard MissionCenter as the first daily action surface.
- Main/tiny mission-family handling where tiny missions are lower-pressure substitutes, while bonus missions remain optional extra momentum.
- Mission focus mode that hides secondary dashboard sections while there is an active Ringo focus, due reminder, primary mission, tiny flow, optional bonus focus, or unacknowledged completion state.
- Compact progress strip for focus mode using existing level, XP progress, streak, and today-safe context.
- First-run staged reveal for Ringo guidance, mission intro, mission card, and action education.
- Post-first-win completion UX, including optional bonus framing, calm reminder copy, and Rest Mode after `Finish for today`.
- Mission Status detail lists are collapsed by default during focus mode and can be revealed manually.
- Post-safe optional explorer growth-map polish with progress-surface path/challenge cards, circular icon progress rings, frontend-only reward-ready/building slots, earned/total XP summaries, mission-key icons, and status-aware mission rows.
- Completed optional paths/challenges can remain visible so users can feel completion while MissionCenter's single-focus loop remains intact.
- `/paths` planning view with path picker, stage panels, mission previews, and today progress summary.
- Ringo helper sprites and RingoCoach component.
- Premium navigation with Paths in desktop/mobile navigation and Settings removed from visible navigation.

### Stabilization Progress Completed

- Removed duplicate `GET /me/stats` route ownership.
- Standardized `/me/stats` through `stats_routes.py` and `stats_service.py`.
- Aligned `frontend/src/stores/session.js` with cookie-based auth.
- Removed frontend `api.setToken()` assumption.
- Gated SQLite debug endpoints behind development environment config.
- Required production `SECRET_KEY` and `JWT_SECRET`.
- Centralized active JWT signing/verification on `Config.JWT_SECRET`.
- Removed unsafe JWT secret fallback from active auth code.
- Added frequent-query indexes for `checkins` and `enrollments`.
- Made SQLite `DB_PATH` launch-location safe.
- Enabled SQLite foreign key enforcement per database connection.
- Removed unused legacy `auth_service.py`.
- Removed unused legacy database helper functions.
- Removed unused `sessions` table initialization.
- Added `.gitignore` coverage for local runtime files.
- Synced `DATABASE_SCHEMA.md` with current database implementation.
- Synced `ApiDocsView.vue` with current backend endpoints.
- Added challenge join payload validation.
- Added profile update/profile settings validation.
- Added launch QA checklist.
- Added backend `.env.example` launch-ready environment documentation.
- Added deployment readiness checklist.
- Added safe `/health/config` production-readiness endpoint.
- Added environment-driven production CORS origin support.
- Added production auth cookie configuration coverage.
- Added production secret requirement tests.
- Cleaned duplicated legacy auth logic from `config.py`.
- Added backend deployment smoke script.
- Added basic in-memory auth rate limiting for login/register endpoints.
- Added shared API response helper foundation.
- Added malformed JSON handling coverage for key endpoints.
- Added public profile not-found coverage.
- Enforced local auth disable behavior through `LOCAL_LOGIN_ENABLED`.
- Preserved omitted profile fields on partial profile updates.
- Hardened profile visibility payload validation.
- Rejected protocol-relative avatar URLs.
- Blocked private challenge detail/member reads.
- Enforced enrollment ownership on leaderboard routes.
- Ignored left enrollments during challenge discovery joined-state checks.
- Included achievement XP rewards in persisted stats.
- Made progression surfaces consistently ignore uncounted check-ins.
- Preserved uncounted check-in state in enrollment history.
- Normalized public profile username lookups.
- Centralized public identity privacy enforcement for public profile, consistency, and achievements endpoints.
- Hardened the active local auth form to use the shared API client, remove auth payload console logging, honor post-login redirects, and match backend password validation.
- Removed stale frontend route/file clutter around the legacy login import and stray `Untitled` view snippet.
- Aligned auth callback token storage with the shared API client Bearer fallback, constrained callback redirects to internal paths, and cleared stored callback tokens on logout.
- Added frontend-only Persian/English i18n with `vue-i18n`, persisted locale selection, automatic `lang`/`dir` updates, and a header language switcher.
- Added frontend-only seeded content display localization for known mission/path/challenge copy through helpers such as `missionDisplayCopy.js` and `ringoContentLocalization.js`, improving Persian MissionCenter, onboarding, path/challenge previews, and Challenge Discovery surfaces while preserving backend seed data.
- Added Persian-only Vazirmatn typography through the active global CSS layer while preserving the existing English system font stack.
- Added guided Today Mission dashboard focus and a reusable first-path empty state for users without active enrollments.
- Added lightweight frontend-only onboarding with identity path selection and suggested first challenge mapping.
- Added JoinSuccessMoment after successful challenge joins so onboarding and discovery lead users toward Today's Mission before dense enrollment details.
- Added premium check-in RewardMoment and frontend-only unlock hints for Activity, Achievements, and Public Profile using existing check-in/stat data.
- Added frontend-only progressive disclosure on the dashboard using existing check-in counts instead of new backend fields.
- Added backend-backed path/mission system, MissionCenter, `/paths`, and RingoCoach on top of the existing challenge/check-in progression model.
- Added mission-level Telegram reminder delivery for due `remind_later` mission logs.
- Added duplicate-prevention for delivered mission reminders through `mission_logs.reminder_sent_at`.
- Added protected due reminder endpoint for n8n/cron automation: `POST /api/telegram/remind-due-missions`.
- Added protected reminder diagnostics endpoint: `GET /api/telegram/reminder-diagnostics`.
- Hardened VPS runtime around `systemd`, env-driven Flask binding, `FLASK_DEBUG=0`, and nginx `/api-proxy` routing to a localhost-only backend.
- Hardened Persian/RTL dashboard and optional explorer rendering by ensuring full-viewport dark root/app background coverage and clipped direction-aware progress surfaces.


### Backend Test Coverage Added

- Health endpoint smoke test.
- Local register/login `/me` auth smoke test.
- Username validation and reserved username smoke test.
- Duplicate username smoke test.
- Logout cookie-session smoke test.
- Challenge list/join/check-in core loop smoke test.
- Invite-only challenge join smoke test.
- Duplicate check-in behavior smoke test.
- Stats update after check-in smoke test.
- Public/private profile visibility smoke test.
- Public consistency privacy smoke test.
- Public achievements privacy smoke test.
- Achievement unlock after first check-in smoke test.
- Profile validation smoke test.
- Enrollment reset metadata smoke test.
- Leaderboard rank/tie-breaker smoke test.
- Temporary SQLite test database setup.
- Safe `/health/config` smoke test.
- Production CORS origin smoke test.
- Production auth cookie configuration smoke tests.
- Production secret requirement tests.
- Auth register/login rate limiting smoke tests.
- Shared API response helper tests.
- Auth malformed JSON payload tests.
- Profile settings malformed JSON payload test.
- Challenge join malformed JSON payload test.
- Public profile not-found smoke tests.
- Protected endpoint missing-auth smoke tests.
- Protected endpoint invalid bearer-token smoke tests.
- Profile settings unauthorized PATCH smoke tests.
- Local auth disabled smoke test.
- Profile partial-update preservation smoke test.
- Profile visibility invalid payload smoke test.
- Private challenge detail/member privacy smoke tests.
- Leaderboard enrollment ownership smoke test.
- Left-enrollment challenge discovery smoke test.
- Achievement XP persistence smoke test.
- Uncounted check-in progression/history smoke tests.
- Public profile username normalization smoke test.
- Path and mission backend behavior tests.
- Ringo decision service tests.
- Service-level leaderboard ordering coverage for overall and today tie-breaker rules.
- Frontend router guard smoke test.
- Frontend login flow smoke test.
- Frontend dashboard loading smoke test.
- Frontend challenge join/check-in flow smoke test.
- Frontend profile loading smoke test.
- Frontend public profile rendering smoke test.
- Expand protected-endpoint auth failure coverage as new authenticated routes are added.



---

## Now: Stabilization Milestone

These items should happen before expanding product scope:

- Keep invalid challenge join payload coverage as route behavior evolves.
- Add frontend smoke coverage for `/paths`, MissionCenter, mission done/remind/skip, and duplicate mission/check-in behavior.
- Continue validating mission context clarity after the focus-mode work. A full Mission Context UX layer, universal path -> challenge -> mission breadcrumbs, and contextual reward sequence are still planned work.
- Frontend-only seeded content display localization is implemented for known mission/path/challenge copy; continue maintaining localization key coverage as seeded content expands. Future content work can include fuller localization for custom content, a CMS/content-management approach if the product scales, and AI-generated copy only later after deterministic copy is stable.
- Add tests for `/auth/logout` edge cases if token blacklist/session invalidation is introduced later.
- Resolve or document remaining GitHub Actions frontend build instability if it reappears.
- Run deployment smoke script after every production/pre-launch deployment.
- Finalize production `.env` values for backend and frontend.
- Normalize API naming conventions where practical (`/api/...` vs non-`/api/...`).
- Add a real migration strategy instead of relying on startup-time additive schema changes for future production database evolution.
- Review profile update endpoints and reduce overlap where possible.
- Public challenge/member endpoint visibility has been hardened for private challenges; keep intended policy documented as product scope evolves.
- Run full `docs/LAUNCH_QA_CHECKLIST.md` before release candidate.
- Expand shared API response helper usage across existing routes.
- Keep service-level leaderboard ordering coverage aligned if tie-breaker behavior changes.
- Keep reminder automation monitored through diagnostics and n8n admin summaries.
- Keep optional explorer progress-map polish display-only unless a future product issue explicitly designs backend reward claiming.


---

## Next Product Milestone: Guided Progression Experience

Goal:

Reduce first-time user confusion by shifting the primary experience from dashboard browsing to a Ringo-first daily companion loop.

Core loop:

```txt
Ringo understands state -> Main/Tiny/Bonus mission -> Small action -> Ringo Moment -> Next gentle step
```

Why:

Early tester feedback shows that the product is valuable but feels too complex. Before wider launch, the app should make the next action obvious, emotionally safe, and guided by Ringo rather than by a dense system surface.

Planned work:

- Continue validating the Today Mission Card and guided empty state with first-time users.
- Reframe the dashboard as Ringo's home and make Ringo the first visual/emotional focus.
- Introduce the daily Main Mission, Tiny Mission, and optional Bonus Mission structure.
- Keep existing path, challenge, mission, check-in, stats, achievement, and activity systems as the supporting infrastructure.
- Refine simplified early navigation/progressive disclosure without blocking direct routes.
- Expand the reward moment and join success moment only when existing backend responses provide enough data.
- Improve first-run onboarding after the identity path flow is validated.
- Consider reminder connection prompts after the first reward/check-in moment, not before.

Non-goals:

- No backend rewrite.
- No duplicate progression logic.
- No complex skill tree yet.
- No native mobile app yet.
- No heavy social systems yet.

---

## Emotional MVP Relaunch Direction

Goal:

Make RingoStrike feel like a caring daily self-improvement companion, not only a habit/challenge tracker.

Near-term product sequence:

1. Ringo-first dashboard: simplify the first screen around Ringo's mood, message, and one clear next action.
2. Ringo Brain v1: add a deterministic decision layer for user state, Ringo mood, suggested mission, mission intensity, tone, actions, and reward sequence type.
3. Main/Tiny/Bonus missions: show a focused daily set so the user always knows what is enough today.
4. Ringo Moment reward sequence: turn mission completion into a step-by-step emotional reward ritual instead of one static result card.
5. Ringo Pulse feed: add a warm lightweight activity/community pulse, with privacy-aware defaults.
6. AI-assisted language layer: later, after the rule-based Ringo Brain exists, use AI for safe wording variation and personalized language only.

Implementation principles:

- First Ringo, then system.
- Preserve existing functionality and avoid rewrites.
- Extend or wrap existing services before replacing them.
- Keep AI out of product decisions until deterministic Ringo Brain behavior is stable.

Reference: [MVP Relaunch Phases](product/MVP_RELAUNCH_PHASES.md).

---

## Next Sprint: Quality And Reliability

### Backend Reliability

- Add tests for reset edge cases when user timezone support is introduced.
- Expand leaderboard ordering tests if tie-breaker behavior changes.
- Expand archived/private challenge tests if challenge lifecycle behavior changes.
- Expand profile visibility tests if new visibility states are added.
- Add tests for auth failure behavior on protected endpoints.
- Expand malformed JSON coverage to any remaining mutation endpoints.
- Keep reliable service-level tests for leaderboard exact tie scenarios aligned with product policy.



### Frontend Reliability

- Keep router guard smoke coverage aligned as route auth policy changes.
- Keep login flow smoke coverage aligned as auth UI behavior changes.
- Keep dashboard loading smoke coverage aligned as dashboard API usage changes.
- Keep challenge join/check-in smoke coverage aligned as challenge flow behavior changes.
- Keep profile loading smoke coverage aligned as profile behavior changes.
- Keep public profile smoke coverage aligned as public profile behavior changes.
- Keep responsive UI pass findings aligned as core route layouts change.
- Keep browser console pass coverage aligned as major route behavior changes.

### API Reliability

- Keep shared API error response convention aligned as routes migrate.
- Keep backward-compatible response shapes for active frontend usage.
- Keep endpoint ownership documentation aligned as routes change.
- Keep duplicate route ownership guard aligned as routes change.
- Keep progression calculations centralized in `stats_service.py`.
- Keep validation boundary ownership aligned as mutation routes change.
- Keep public identity privacy enforcement centralized as public surfaces change.

---

## Product Expansion: Social Momentum

After stabilization:

- Public share cards for profiles and achievements.
- Public profile OpenGraph metadata if server-side rendering or a share proxy is added.
- Challenge discovery improvements with categories/tags.
- Safer public activity controls.
- Social follow or inspiration mechanics that avoid toxic competition.
- Public achievement sharing.
- Profile identity polish for shareable progression.
- Better leaderboard identity states and optional public rank surfaces.

---

## Product Expansion: Automation And Insights

After launch-readiness foundations:

- Telegram login route if Telegram auth is still desired.
- Telegram reminder delivery hardening and production bot bridge.
- Per-challenge reminder time.
- Preferred daily check-in window.
- Late check-in status.
- Normal vs late check-in distinction.
- User timezone preferences.
- Weekly summaries.
- Streak-risk warnings.
- AI-generated progress insights.
- n8n workflow integration hardening.
- Notification-ready check-in reminders.
- Progress recap automation.

---

## Launch Readiness

Before first public launch:

- Production deployment plan.
- Environment/config checklist.
- Database backup process.
- Database migration process.
- Monitoring and error logging.
- Privacy policy.
- Public profile visibility controls review.
- Demo data and onboarding.
- Performance pass for dashboard/profile query load.
- Security pass for auth, debug routes, validation, and public endpoints.
- Manual QA checklist pass for core user flow.
- Frontend production build verification.
- Backend smoke test verification.
- Safe config health verification.
- Production CORS origin verification.
- Auth cookie production settings verification.
- Deployment smoke script execution.

Required commands:

```bash
cd backend
py -m pytest -q
```

```bash
cd frontend
npm run build
```

```bash
python scripts/smoke_backend.py --base-url http://localhost:5005
```

## Launch Readiness Status

Actionable launch-hardening fixes targeted before lunch are complete.

Recommended next work should move from "fix before lunch" to final review:

- Review the latest commits and commit titles.
- Run any manual smoke checks you want before lunch.
- Keep the ongoing maintenance notes above aligned as future features change.

---

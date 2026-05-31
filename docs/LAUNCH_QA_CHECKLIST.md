# RingoStrike - Launch QA Checklist

This checklist is used before every pre-launch deploy or release candidate.

Current product stage:

> Post-MVP Stabilization / Pre-Launch Hardening

Goal:

Make sure the core progression identity loop works reliably before expanding into Telegram reminders, Android, widgets, AI insights, or deeper social systems.

---

## 1. Environment And Startup

### Backend

- [ ] `.env` exists in `backend/`.
- [ ] `SECRET_KEY` is set.
- [ ] `JWT_SECRET` is set.
- [ ] `DB_PATH` is set or expected local fallback is confirmed.
- [ ] `FLASK_ENV=development` is used only locally.
- [ ] Production unsafe fallback secrets are not used.
- [ ] Backend starts without errors.

Command:

```bash
cd backend
FLASK_ENV=development py app.py

Health check:

curl http://localhost:5005/health

Expected:

{"ok": true}
Frontend
 VITE_API_BASE points to the correct backend.
 Frontend starts without errors.

Command:

cd frontend
npm run dev

Build check:

npm run build
2. Automated Tests

Run backend tests before manual QA.

Command:

cd backend
py -m pytest -q

Expected:

 All tests pass.
 Tests use temporary SQLite DB.
 Tests do not mutate backend/users.db.

Current smoke coverage:

 Health endpoint.
 Register/login/auth /me.
 Challenge list/join/check-in/core stats.
 Duplicate check-in behavior.
 Achievement unlock after first check-in.
 Public/private profile visibility.
 Profile input validation.
3. Auth Flow
Register
 Open register/login UI.
 Register a new user.
 User is redirected into authenticated app.
 Auth cookie is set.
 /me returns the correct user.
Login
 Logout.
 Login with the same user.
 Dashboard loads.
 Invalid login shows a clear error.
 Empty username/password shows a clear error.
Logout
 Logout clears session.
 Protected pages redirect or block access.
 Refresh after logout does not restore user.
4. Dashboard

URL:

/dashboard

Check:

 Dashboard loads without console errors.
 User stats are visible.
 Enrolled challenge cards are visible.
 Challenge cards use compact dashboard mode.
 Cards show duration/streak/check-in status where available.
 Cards do not show misleading member counts if dashboard data does not provide member metadata.
 Open button goes to enrollment detail.
 Check in button works.
 Done Today disables repeated check-in when today is already completed.
 Empty state works for a user with no enrollments.
5. Challenge Discovery

URL:

/challenges

Check:

 Page loads available challenges.
 Default launch challenges appear on a fresh database.
 Challenge cards show name and description.
 Challenge cards show duration.
 Challenge cards show members count and preview when available.
 Challenge cards show access type.
 Challenge cards show reward.
 Public challenge can be joined without code.
 Invite-only challenge asks for code.
 Invalid invite code shows a clear error.
 Joined challenge opens enrollment page.
 Visual spacing is clean on desktop and mobile.
6. Enrollment Detail

URL pattern:

/enrollment/:id

Check:

 Challenge title and description are visible.
 Today check-in status is visible.
 Check-in button works.
 Completed check-in changes status to done.
 Duplicate check-in does not create duplicate counted progress.
 Remaining days are visible.
 Start and end dates are visible.
 Timeline progress is visible.
 Consistency score is visible.
 Recent logs are visible.
 Embedded leaderboard preview loads.
 Full leaderboard link works.
7. Daily Reset UI

Check:

 today_date appears in API response.
 next_reset_at appears in API response.
 reset_timezone appears in API response.
 Enrollment UI shows reset timezone.
 Enrollment UI shows next reset time.
 Enrollment UI shows countdown until reset.
 Checked-in state shows Today secured.
 Not checked-in state shows Open window when enough time remains.
 Less than 6 hours remaining shows warning state.
 Less than 2 hours remaining shows final-window state.
 Missing reset metadata does not break the page.

Future reminder system notes:

Per-challenge reminder time.
Preferred daily check-in window.
Late check-in state.
Normal vs late check-in distinction.
User timezone preferences.
8. Leaderboard

URL pattern:

/enrollment/:id/leaderboard

Check:

 Overall leaderboard loads.
 Each row has rank.
 Sorting is deterministic.
 Today leaderboard loads when users checked in today.
 Today checked status is visible.
 Empty today leaderboard state works.
 Full page layout is readable.
 Embedded leaderboard preview still works inside enrollment page.

Expected backend metadata:

 rank
 today_checked
 tie_breakers
 overall
 today
9. Achievements

URL/API:

/me/achievements

Check:

 Achievements list loads.
 Locked achievements show as locked.
 First check-in unlocks first_checkin.
 First check-in unlocks first_challenge_completed.
 Check-in response includes newly unlocked achievements.
 Achievement XP reward is included.
 Duplicate check-in does not re-award same achievements.
 Public achievements endpoint respects profile visibility.

Public endpoint:

/api/public/profile/:username/achievements
10. Profile And Public Identity
Private Profile

URL/API:

/me/profile
/api/me/profile/settings

Check:

 Profile loads.
 Name displays correctly.
 Bio displays correctly.
 Avatar URL displays correctly if set.
 Profile visibility is visible.
 Profile settings can be saved.
 Invalid name type is rejected.
 Too-long bio is rejected.
 Invalid avatar URL is rejected.
 Local avatar path is accepted.
Public Profile

URL pattern:

/u/:username
/api/public/profile/:username

Check:

 Public profile loads when visibility is public.
 Public profile does not expose private-only data.
 Public profile blocks access when visibility is private.
 Private profile returns profile_private.
 Authenticated owner can still access /me/profile.
 Public consistency endpoint respects visibility.
 Public achievements endpoint respects visibility.
11. Activity And Consistency

Check:

 Activity feed loads.
 Check-in creates activity event.
 Achievement unlock creates activity event if supported.
 Consistency heatmap loads.
 Public consistency respects visibility.
 Empty activity state works.
 Empty consistency state works.
12. API Explorer / Docs

Check:

 ApiDocsView.vue lists current active endpoints.
 Removed/legacy endpoints are not documented as active.
 /me/stats appears once.
 Public profile endpoints are documented.
 Debug endpoints are marked development-only.
 Request/response examples match current API behavior.
13. Security Checks
 Debug endpoints are blocked outside development.
 Production requires safe SECRET_KEY.
 Production requires safe JWT_SECRET.
 Auth endpoints do not expose sensitive errors.
 Protected endpoints reject missing token.
 Protected endpoints reject invalid token.
 Public endpoints respect visibility.
 Join payload rejects invalid JSON body.
 Join payload rejects non-string join_code.
 Join payload rejects overly long join_code.
 Profile update rejects invalid payloads.
14. Database Checks
 SQLite DB path is launch-location safe.
 Foreign keys are enabled per connection.
 Default challenges are seeded only once.
 Re-running backend does not duplicate default challenges.
 Checkins indexes exist.
 Enrollments indexes exist.
 Old local-only runtime files are ignored by git.
 Local backend/users.db is not committed.

Useful checks:

git check-ignore -v backend/users.db
cd backend
py - <<'PY'
from database import get_db_connection

conn = get_db_connection()
row = conn.execute("PRAGMA foreign_keys").fetchone()
print(row[0])
conn.close()
PY

Expected:

1
15. Responsive UI Pass

Check these pages on desktop and mobile width:

 Login/register.
 Dashboard.
 Challenges.
 Enrollment detail.
 Leaderboard.
 Profile.
 Public profile.
 API docs.

Mobile checks:

 No horizontal overflow.
 Buttons are tappable.
 Tables scroll or collapse safely.
 Cards have enough spacing.
 Typography remains readable.
 Hero sections do not dominate the whole screen.
16. Browser Console

For every major route:

 No Vue warnings.
 No failed API requests.
 No uncaught exceptions.
 No broken asset paths.
 No CORS errors.
17. Pre-Launch Decision

Before launch, confirm:

 Backend tests pass.
 Frontend build passes.
 Manual QA checklist is completed.
 Known critical bugs are fixed.
 Public/private profile behavior is safe.
 Check-in, leaderboard, achievements, and stats are reliable.
 Production env variables are ready.
 DB backup plan exists.
 Rollback plan exists.

Launch candidate status:

READY / NOT READY

Notes:

Add release-specific notes here.

## 2. بعدش این تست‌ها رو بزن

```bash
cd backend
py -m pytest -q
cd ../frontend
npm run build
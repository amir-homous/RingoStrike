# RingoStrike - Manual QA Report

Manual QA report for the current pre-launch hardening pass.

## QA Context

Product stage:

> Post-MVP Stabilization / Pre-Launch Hardening

Branch:

```txt
dev

Purpose:

Verify the core RingoStrike user journey manually after backend stabilization, frontend polish, backend test coverage, and CI setup.
```

Automated Checks
Backend Tests

Command:
``` bash    
cd backend
py -m pytest -q
```

Result:
PASS / FAIL


Notes:

Add notes here.
Frontend Build

Command:

cd frontend
npm run build

Result:

PASS / FAIL

Notes:

Add notes here.
GitHub Actions

Expected workflows:

Backend Tests
Frontend Build

Backend Tests:

PASS / FAIL / PENDING

Frontend Build:

PASS / FAIL / PENDING

Notes:

Add CI notes here.
Manual Route Checks
Auth

Routes / flows:

Login
Register
Logout
Refresh after logout
Invalid login

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Dashboard

Route:

/dashboard

Check:

Stats visible.
Enrolled challenge cards visible.
Check-in status visible.
Open button works.
Done Today state works.
Empty state is acceptable.

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Challenge Discovery

Route:

/challenges

Check:

Default challenges visible.
Public challenge join works.
Invite-only challenge asks for code.
Challenge metadata is readable.
Member count/preview spacing is clean.
Join/Open buttons are readable and usable.

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Enrollment Detail

Route pattern:

/enrollment/:id

Check:

Challenge title and description visible.
Today status visible.
Check-in works.
Duplicate check-in does not duplicate progress.
Remaining days visible.
Reset countdown visible.
Recent logs visible.
Embedded leaderboard preview visible.

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Leaderboard

Route pattern:

/enrollment/:id/leaderboard

Check:

Overall leaderboard loads.
Today leaderboard loads.
Rank visible.
Today checked status visible.
Empty state acceptable.

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Profile

Routes / APIs:

/me/profile
/api/me/profile/settings

Check:

Profile loads.
Profile edit works.
Bio saves.
Avatar URL saves.
Invalid input errors are acceptable.
Visibility can be changed.

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Public Profile

Route pattern:

/u/:username

Check:

Public profile loads when visibility is public.
Public profile blocks when visibility is private.
Public achievements respect visibility.
Public consistency respects visibility.

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Responsive UI Pass

Viewports:

Desktop
Tablet width
Mobile width

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Browser Console Pass

Check major routes for:

Vue warnings.
Failed API requests.
CORS errors.
Broken assets.
Uncaught exceptions.

Status:

PASS / FAIL / NOT TESTED

Notes:

Add notes here.
Launch Blocking Issues

List any issue that must be fixed before public launch.

- None yet.
QA Decision

Current status:

READY / NOT READY / PARTIAL

Decision notes:

Add final QA notes here.

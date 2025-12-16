# RingoStrike – Frontend Contract

> Living contract for frontend structure, data flow, and UI conventions.
> Keep this updated when you change architecture or data shapes.

## 1) Project Summary

RingoStrike is a challenge-based app to help users build habits via daily check-ins.
Users join challenges, then log daily progress (check-ins). UI shows enrollments, challenge progress, and history.

## 2) Stack & Conventions

- Framework: Vue 3 + Vite
- Style: Composition API (preferred)
- Routing: Vue Router
- State: (Pinia / local state) — **document which one you use**
- API: Axios / Fetch — **document which one you use**
- Dates: ISO strings `YYYY-MM-DD`

**General rules**

- Keep views thin: views orchestrate, components render, composables/utils handle logic.
- Prefer small commits + issue-based work.

## 3) Key Pages (Views)

> Replace names with your actual files if different.

- `src/views/Login.vue`

  - Shows Telegram login instructions/link
  - Handles redirect back and refresh/reload flow

- `src/views/Dashboard.vue` (or `ChallengeDashboard.vue`)

  - Main user dashboard
  - Shows user’s enrollments + progress summaries

- `src/views/ChallengeDetail.vue` (optional)
  - Single challenge page (details + participants + logs)

## 4) Core UI Components

> Add/remove based on what you actually have.

- `src/components/ChallengeCard.vue`

  - Challenge summary (title, status, progress)

- `src/components/EnrollmentList.vue`

  - List of challenges user joined

- `src/components/ChallengeDailyGrid.vue` (planned)
  - Visual grid of days (checked/missed/future)

## 5) Data Models (Frontend View)

> This is the **shape the UI expects**, not necessarily backend DB schema.

### Challenge

```python
type Challenge = {
  id: string
  title: string
  start_date: string // YYYY-MM-DD
  end_date?: string  // YYYY-MM-DD (optional if total_days exists)
  total_days?: number
}
type Enrollment = {
  id: string
  user_id: string
  challenge_id: string
  challenge?: Challenge
}
type DailyLog = {
  date: string // YYYY-MM-DD
  status?: 'checked' | 'missed' // if status exists
  is_counted?: boolean          // if backend uses boolean
}
type DayCell = {
  date: string // YYYY-MM-DD
  state: 'checked' | 'missed' | 'future'
  label?: string // optional: day number, tooltip, etc.
}

```

6) Data Flow (Where data comes from)

Describe the real flow you use right now.

Auth (Telegram)

Frontend triggers backend login URL (Telegram OAuth-like flow)

After user approves in Telegram, backend sets session/cookie or returns token

Frontend redirects back to /login?next=... then navigates to dashboard

Assumptions

Frontend treats auth as “session is valid if backend says so”

Token/session storage strategy:

 Cookie session

 LocalStorage token

 Other: ___________

Challenge / Enrollment / Daily Logs

Views request data via store/service

Store/service calls backend endpoints

UI receives normalized shapes

Backend endpoints used by UI (fill with your real ones)

GET /challenges

GET /challenges/:id

POST /enrollments (join)

GET /enrollments (my enrollments)

GET /enrollments/:id/history (daily logs) OR GET /daily_logs?...

POST /checkin (create daily log)

7) State Management

Pick what you actually use and keep it consistent.

Stores (if using Pinia)

challengeStore

currentChallenge

enrollments

dailyLogsByEnrollmentId (recommended)

actions:

fetchChallenges()

fetchEnrollments()

fetchHistory(enrollmentId)

joinChallenge(challengeId)

checkIn(enrollmentId, date?)

If NOT using a store

Document where shared state lives (composables, provide/inject, etc.)

8) Date & Time Rules (must be consistent)

UI works with ISO date strings YYYY-MM-DD

Date comparisons should be done with a single utility (avoid scattered logic)

Timezone policy:

 backend normalizes dates

 frontend normalizes dates

Current assumption (recommended): backend normalizes

daily_logs ordering:

 guaranteed sorted from backend

 frontend sorts before mapping

9) UI Status & Color Conventions

These are semantic states. Actual colors come from theme/tokens.

checked → success (green)

missed → warning/neutral (gray or red — decide once)

future → disabled (muted)

Optional extra states (add only if needed):

today highlight

streak special glow

late for out-of-window check-ins

10) File Organization Rules

Preferred structure:

src/views/ pages only

src/components/ reusable UI

src/composables/ reusable logic/hooks (data mapping, fetch helpers)

src/utils/ pure functions (dates, formatting)

src/services/ API calls (axios/fetch wrappers)

src/router/ route definitions

11) Feature Development Loop (how we work)

Each feature starts with a GitHub Issue using the team template

Create a branch per issue: feature/issue-XX-...

Implement with small commits

Ask ChatGPT for:

architecture proposal before coding

edge-cases review after first implementation

refactor suggestions before merge

Merge via PR (even if solo)

12) ChatGPT Role

ChatGPT acts as:

Senior frontend engineer

UI/UX + architecture partner

Code reviewer & edge-case checker

ChatGPT should NOT:

rewrite whole project without request

introduce new libraries unless necessary

ignore existing conventions in this contract



### چطور ازش استفاده کنی تو هر چت جدید؟
فقط اینو اول چت بنویس:


```text
Project: RingoStrike
Frontend Contract: docs/FRONTEND_CONTRACT.md (up to date)
Feature: ...
Issue: #...
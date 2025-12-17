Living contract for frontend structure, data flow, and UI conventions.
Update this file whenever routing, UI-kit, API endpoints, or data shapes change.

1) Project Summary

RingoStrike is a challenge-based habit app: users join challenges and perform daily check-ins.
Frontend displays:

User dashboard (active enrollments)

Challenges list + join flow

Enrollment detail (today check + progress + recent logs + embedded leaderboard)

Leaderboard page (total + streak)

2) Stack & Conventions

Framework: Vue 3 + Vite

Language: JavaScript (no TS)

Routing: Vue Router (history mode)

State: Pinia (minimal usage; currently stores/session.js)

API: Axios via src/lib/api.js

Styling: CSS tokens + base styles

src/styles/tokens.css

src/styles/base.css

Environment / Base URLs

Frontend base path: import.meta.env.BASE_URL
(e.g. deployed under /ringostrike/)

Backend API base: import.meta.env.VITE_API_BASE

General Rules

Views orchestrate: fetch data + handle state.

UI components render (no API calls inside presentational components unless explicitly “smart” like Leaderboard embedded/page).

Avoid inline styles; prefer shared UI components + tokens.

Prefer small PRs/commits per issue.

3) Current File Structure (Source of Truth)
Views (Pages) – src/views/

Login.vue

AuthCallback.vue

Dashboard.vue

Challenges.vue

Enrollment.vue

Leaderboard.vue (supports page mode + embedded mode)

Router – src/router/index.js

Routes:

/login

/auth/callback

/dashboard

/challenges

/enrollment/:id

/enrollment/:id/leaderboard

/ → redirect /dashboard

/:pathMatch(.*)* → redirect /dashboard (temporary; 404 page planned)

Auth guard:

Only /login and /auth/callback are public

All other routes call GET /me; if not authenticated → redirect to /login?next=...

UI Kit – src/components/ui/

Base components used across the app:

AppContainer.vue (layout + page width/padding)

AppHeader.vue (top navigation; single source of truth for nav)

BaseCard.vue (standard surface)

BaseButton.vue (primary/secondary/disabled/loading patterns)

BaseInput.vue (focus/error/disabled)

UiState.vue (loading/empty/error + retry)

Spinner.vue, SkeletonBlock.vue

API wrapper – src/lib/api.js

Axios instance (base URL + cookies/session expected)

Frontend treats auth as session cookie-based (server is source of truth)

4) UI Conventions (Milestone 0.1 Baseline)
Layout & Spacing

Use AppContainer for all pages (consistent width/padding).

Use spacing scale via tokens (e.g. 8/12/16/24) and utility classes if available.

Headings hierarchy:

Page title: .h1

Section title: .h2 / .h3 (depending on design)

Caption: .caption

Components (Design Contract)

Buttons:

Variants: primary, secondary (danger optional)

States: disabled, loading

Cards:

BaseCard for all main blocks

Inputs:

BaseInput for consistent focus/error/disabled behavior

UX states:

Use UiState for loading / empty / error

Add retry handler where meaningful

Embedded vs Page Components

Leaderboard.vue supports:

Page mode (default): includes AppHeader + page title

Embedded mode (embedded: true): renders only the table block (no header)

This prevents duplicated nav when Leaderboard is used inside Enrollment.vue.

5) Data Models (Frontend Contract)

These shapes represent what UI expects from backend responses.

User
type User = {
  id?: string | number
  name: string
  username?: string
}

Challenge (from /challenges and enrollment detail payload)
type Challenge = {
  challenge_id: string
  name: string
  description?: string
  visibility?: string
  status?: string
  duration_days?: number
  members_count?: number
  members_preview?: string[]
  needs_code?: boolean
}

Enrollment (from /me/dashboard and /me/enrollments/:id)
type Enrollment = {
  enrollment_id: string
  name?: string
  enrollment_name?: string
  status: string
  today_checked: boolean

  total_checkins?: number
  current_streak?: number
}

Dashboard payload (from /me/dashboard)
type DashboardResponse = {
  user: User
  date: string // display string
  challenges: Array<{
    enrollment_id: string
    enrollment_name: string
    status: string
    today_checked: boolean
  }>
}

Enrollment detail payload (from /me/enrollments/:id)
type EnrollmentDetailResponse = {
  enrollment: Enrollment
  challenge: Challenge
  recent_logs: Array<{
    daily_log_id: string
    date: string // YYYY-MM-DD
  }>
}

History summary (from /me/challenges/:id/history?days=)
type HistoryResponse = {
  summary: {
    checked_days: number
    total_days: number
  }
  // optionally may include daily list later
}

Leaderboard payload (from /me/enrollments/:id/leaderboard)
type LeaderboardResponse = {
  overall: Array<{
    enrollment_id?: string
    name?: string
    username?: string
    total_checkins?: number
    current_streak?: number
  }>
  today?: any[] // reserved for future
}

6) Data Flow
Auth (Telegram session)

Frontend page: Login.vue

Builds login URL: ${VITE_API_BASE}/login?next=...

Backend handles Telegram widget flow + sets session cookie

Router guard checks auth by calling:

GET /me

If unauthenticated:

Redirect to /login?next=<original path>

Challenges / Join

Challenges.vue

GET /challenges → list

POST /challenges/:challenge_id/join

with { join_code } if invite-only

If joined, backend returns enrollment_id in list refresh (assumption)

Dashboard

Dashboard.vue

GET /me/dashboard

POST /me/challenges/:enrollmentId/checkin

POST /logout → then redirect to ${BASE_URL}login

Enrollment detail

Enrollment.vue

GET /me/enrollments/:id → enrollment + challenge + recent_logs

GET /me/challenges/:id/history?days=<duration_days> → summary for progress bar

POST /me/challenges/:id/checkin → then reload

Leaderboard

Leaderboard.vue

GET /me/enrollments/:id/leaderboard

Supports embedded render inside enrollment page:

<Leaderboard :enrollment-id="enrollment.enrollment_id" embedded />

7) State Management

Default: Local state in views (ref/computed)

Pinia exists: src/stores/session.js
Use it only for truly shared session/user state (optional; keep minimal).

Router guard is the primary “auth gate”.

8) Date & Time Rules

UI works with ISO YYYY-MM-DD for logs.

Backend should be source of truth for:

today_checked

current_streak

total_checkins

Timezone policy (v0.2 target):

backend standardizes “today” consistently across endpoints.

9) UX States Contract

Every API-driven view/section must have:

Loading (spinner/skeleton)

Empty state (friendly message)

Error state (friendly + Retry)

Disable actions while request in progress (prevent double submit)

Preferred pattern: UiState component.

10) Development Loop

Each feature starts with a GitHub issue.

Branch per issue: feature/issue-XX-short-name or fix/issue-XX-...

Small commits, PR merge (even solo).

Definition of Done:

No console errors in normal flow

Desktop + Mobile screenshots in PR for touched pages

11) ChatGPT Role

ChatGPT acts as:

Senior frontend engineer + UI consistency partner

Architecture and edge-case reviewer

ChatGPT should NOT:

introduce new libs unless needed

rewrite whole structure without request

ignore the conventions here

How to use in new chats
Project: RingoStrike
Frontend Contract: docs/FRONTEND_CONTRACT.md (up to date)
Feature: ...
Issue: #...

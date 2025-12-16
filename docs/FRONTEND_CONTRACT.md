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

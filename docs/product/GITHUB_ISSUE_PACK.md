# GitHub Issue Pack — RingoStrike Emotional MVP Relaunch

## Milestone

RingoStrike Emotional MVP Relaunch

---

# Issue 1 — [Docs] Add RingoStrike product direction documents

## Goal

Add the core product direction documents for RingoStrike before implementing new UX or AI changes.

## Background

Recent product strategy decisions changed the direction of RingoStrike from a normal habit/challenge tracker into a caring character-driven self-improvement companion.

These decisions need to be documented inside the repository so future development and Codex prompts can follow the same direction.

## Scope

Create the following folder and files:

```text
docs/product/
  PRODUCT_SOUL.md
  RINGO_CHARACTER_BIBLE.md
  EMOTIONAL_CORE_LOOP.md
  RINGO_BRAIN_STRATEGY.md
  MISSION_DESIGN_SYSTEM.md
  RINGO_REWARD_SEQUENCE.md
  RINGO_PULSE_FEED.md
  MVP_RELAUNCH_ROADMAP.md
```

## Important Product Direction

RingoStrike should be treated as:

A caring daily companion that helps users improve their lives through small guided actions, emotional encouragement, playful progress, and a character named Ringo.

Core principle:

First Ringo. Then system.

## Do Not Change

- Do not modify backend code.
- Do not modify frontend code.
- Do not change database schema.
- Do not change existing routes.
- Do not remove any current feature.

## Acceptance Criteria

- `docs/product/` exists.
- All 8 markdown files exist.
- Each file contains clear product direction notes.
- Existing app behavior remains unchanged.

---

# Issue 2 — [Docs] Create Ringo Character Bible v1

## Goal

Create a dedicated character bible for Ringo’s personality, tone, emotional rules, and speaking style.

## Scope

Document:

- who Ringo is
- story inspiration from Amir’s real cat
- personality traits
- tone modes
- phrases Ringo can use
- phrases Ringo must never use
- rules around “مشتی”, “مشتی پسر”, and “مشتی دختر”
- how Ringo should react to failure, comeback, success, tiredness, and streak risk

## Key Direction

Ringo is not a strict coach, boss, or shame-based productivity system.

Ringo is:

- caring
- cool
- relaxed
- emotionally intelligent
- playful
- gentle
- honest
- supportive

## Acceptance Criteria

- `docs/product/RINGO_CHARACTER_BIBLE.md` exists.
- Includes “Ringo should never shame the user.”
- Includes tone examples in Persian and/or English.
- Includes optional nickname/catchphrase guidance.

---

# Issue 3 — [UX] Redesign dashboard direction around Ringo-first experience

## Goal

Plan and then implement a dashboard structure where Ringo becomes the emotional center of the app.

## Background

The dashboard should not feel like a complex habit tracker. It should feel like Ringo’s home.

## Desired Dashboard Structure

- Ringo character image/mood
- Ringo contextual message
- Today’s Main Mission
- Tiny Mission fallback
- Optional Bonus Mission
- Simple path progress preview
- Today Saved / streak preview
- Small Ringo Pulse preview later

## Do Not Change

- Do not delete existing challenge/path/mission data.
- Do not remove current routes.
- Do not break existing check-in flow.
- Do not remove leaderboard/profile pages; just avoid making them the primary early-user focus.

## Acceptance Criteria

- Dashboard has a clear Ringo-first layout.
- User sees one primary next action.
- Existing mission/check-in functionality still works.
- UI is less overwhelming than the previous feature-heavy dashboard.

---

# Issue 4 — [Backend] Add Ringo Brain v1 rule-based service

## Goal

Create a backend service that determines Ringo’s current message, mood, suggested mission, and available actions using deterministic rules.

## Suggested File

```text
backend/services/ringo_brain_service.py
```

## Inputs

Use available existing data where possible:

- user
- today_checked
- current_streak
- total_checkins
- missed_days if available
- active paths/challenges/missions
- current server time
- recent logs if available

## Outputs

Return a structured object like:

```json
{
  "user_state": "returning_after_absence",
  "mood": "concerned",
  "tone": "warm_no_shame",
  "message": "خوشحالم برگشتی. لازم نیست جبران کنی. فقط امروز رو دوباره شروع کنیم.",
  "recommended_mission_id": null,
  "mission_intensity": "tiny",
  "actions": ["start", "make_smaller", "remind_later"],
  "reward_sequence_type": "comeback"
}
```

## Important

This is not AI yet.

This should be rule-based and easy to test.

## Do Not Change

- Do not replace existing `ringo_decision_service.py` unless necessary.
- Prefer extending or wrapping current logic.
- Do not break existing mission APIs.
- Do not add external AI dependencies.

## Acceptance Criteria

- A Ringo Brain service exists.
- It returns structured data.
- It handles at least these states:
  - new_user
  - active_user
  - today_completed
  - returning_after_absence
  - streak_risk
  - low_progress

- Existing backend tests/manual flows still work.

---

# Issue 5 — [API] Add endpoint for today’s Ringo guidance

## Goal

Expose Ringo Brain v1 output to the frontend.

## Suggested Endpoint

```text
GET /me/ringo/today
```

## Response Example

```json
{
  "ringo": {
    "mood": "welcome",
    "message": "صبح بخیر مشتی. امروز فقط یه قدم کوچیک باهم برمی‌داریم.",
    "user_state": "morning_start"
  },
  "mission": {
    "id": "mission_id",
    "title": "Morning Recovery",
    "intensity": "main",
    "estimated_minutes": 2
  },
  "actions": ["start", "remind_later", "make_smaller"],
  "progress": {
    "today_saved": false,
    "current_streak": 2
  }
}
```

## Do Not Change

- Do not remove `/me/today-missions`.
- Do not break current dashboard API.
- This endpoint should be additive.

## Acceptance Criteria

- Authenticated users can request today’s Ringo guidance.
- Endpoint returns Ringo message, mood, suggested mission/action data.
- Existing APIs remain functional.

---

# Issue 6 — [Mission System] Add mission intensity concept: main, tiny, bonus

## Goal

Support different mission intensities so Ringo can adapt to tired and active users.

## Concept

Each daily recommendation can be:

- main
- tiny
- bonus

Tiny missions are for low-energy users.

Bonus missions are optional extra steps for active users.

## Implementation Notes

Use existing mission data if possible.

If database migration is needed, make it safe and backward-compatible.

Possible fields:

- intensity
- difficulty
- estimated_minutes
- time_window
- energy_level
- parent_mission_id

## Do Not Change

- Do not delete existing missions.
- Do not force all old missions to be rewritten.
- Do not break current mission completion.

## Acceptance Criteria

- Mission recommendations can distinguish main/tiny/bonus.
- Existing missions continue to work.
- UI can display the recommended intensity.

---

# Issue 7 — [UX] Add mission action choices: Start, Later, Make Smaller, Too Tired

## Goal

Make mission interaction feel conversational and adaptive.

## User Actions

Each recommended mission should support:

- Start
- Remind me later
- Make it smaller
- I’m too tired
- Skip today

## Ringo Behavior

If user chooses “Make it smaller”:

Ringo should suggest a tiny mission if available.

If user chooses “I’m too tired”:

Ringo should reduce pressure and suggest a very small action.

If user chooses “Later”:

Ringo should allow reminder options.

## Do Not Change

- Do not remove existing Done/Check-in behavior.
- Do not require notification integration in this issue unless already available.
- This can start as frontend state before full backend integration.

## Acceptance Criteria

- Mission card shows adaptive action choices.
- User can choose a lighter interaction path.
- Ringo message changes based on selected action.

---

# Issue 8 — [Gamification] Create Ringo Moment reward sequence component

## Goal

Create a reusable frontend component that displays mission completion rewards step by step.

## Suggested Component

```text
frontend/src/components/ringo/RingoRewardSequence.vue
```

## Sequence Steps

Support step types:

- ringo_message
- mission_completed
- time_spent
- xp_earned
- path_progress
- streak_update
- today_saved
- achievement_unlocked
- ringo_pulse
- next_choice

## UX Behavior

- One step appears at a time.
- User taps/clicks to continue.
- Simple smooth animation between steps.
- Include skip/fast-forward option.
- Should work on mobile.

## Do Not Change

- Do not break check-in API.
- Do not require backend reward data immediately; mock/local sequence is acceptable for first version.
- Do not show all reward information in one static card.

## Acceptance Criteria

- Component can render a sequence of reward steps.
- User can move through steps one by one.
- Skip option exists.
- Component can be triggered after mission completion.

---

# Issue 9 — [API] Return reward sequence data after mission completion

## Goal

After a mission is completed, backend should return structured reward sequence data that frontend can display in RingoRewardSequence.

## Example Response

```json
{
  "status": "completed",
  "reward_sequence": [
    {
      "type": "ringo_message",
      "mood": "proud",
      "text": "دیدی؟ همین قدم کوچیک هم حسابه."
    },
    {
      "type": "mission_completed",
      "title": "Morning Recovery"
    },
    {
      "type": "xp_earned",
      "amount": 10
    },
    {
      "type": "today_saved"
    }
  ]
}
```

## Do Not Change

- Do not break existing completion response.
- Keep backward compatibility if frontend still expects previous fields.
- Add reward_sequence as an additive field.

## Acceptance Criteria

- Mission completion API returns reward_sequence.
- Existing completion/check-in flow remains valid.
- Frontend can consume reward_sequence if available.

---

# Issue 10 — [Gamification] Add Today Saved state

## Goal

Introduce a simple daily completion state that tells the user their core mission for the day is done.

## Concept

When the user completes the main mission of the day, the app can show:

English:

Today is safe.

Persian:

امروزت نجات پیدا کرد.

## Why

Users should know when they have done “enough” for today.

This reduces pressure and supports tired users.

## Do Not Change

- Do not remove streak.
- Do not replace existing stats.
- Today Saved is an additional emotional UX layer.

## Acceptance Criteria

- System can determine whether today’s main mission is complete.
- UI can show Today Saved.
- Reward sequence can include Today Saved step.

---

# Issue 11 — [Backend] Add activity event model for future Ringo Pulse

## Goal

Create a simple activity event system to support Ringo Pulse / feed later.

## Possible Table

```text
activity_events
```

Fields:

- id
- user_id
- event_type
- target_type
- target_id
- message
- visibility
- metadata_json
- created_at

## Event Types

- mission_completed
- streak_milestone
- achievement_unlocked
- user_returned
- path_progress
- bonus_completed

## Privacy

Support visibility:

- private
- public
- friends
- anonymous

## Do Not Change

- Do not build full feed UI in this issue.
- Do not expose sensitive mission details publicly by default.
- Do not break mission completion.

## Acceptance Criteria

- Activity events can be created.
- Mission completion can optionally create an event.
- Events include visibility.
- Existing app works if activity event creation fails gracefully.

---

# Issue 12 — [Frontend] Add Ringo Pulse preview to dashboard

## Goal

Add a small dashboard section showing recent positive community/activity events.

## Name

Ringo Pulse

## UI Direction

Show only 2–3 events.

Examples:

- 🔥 سینا امروز سومین استریکش رو گرفت.
- 🌱 یکی از بچه‌ها بعد از چند روز برگشت.
- 🏆 سارا یک اچیومنت جدید باز کرد.

## Do Not Change

- Do not build a full social feed yet.
- Do not make the dashboard crowded.
- Do not show sensitive/private events.

## Acceptance Criteria

- Dashboard includes a small Ringo Pulse preview.
- Empty state is warm and simple.
- Section can be hidden if no events exist.

---

# Issue 13 — [UX] Add postpone/remind-later interaction for missions

## Goal

Allow users to tell Ringo they want to do a mission later.

## User Options

- 15 minutes later
- 1 hour later
- evening
- tonight
- custom later

## MVP Scope

This issue can initially save postpone state without full push notification support.

If Telegram reminder system exists, integrate only if safe and simple.

## Ringo Copy Direction

Ringo should say something like:

“اوکی. کی صدات کنم؟”

or

“مشتی، همون قدم کوچیکه رو بعداً باهم می‌زنیم.”

## Do Not Change

- Do not break existing reminder jobs.
- Do not require PWA push notifications yet.

## Acceptance Criteria

- User can choose remind later from mission card.
- Postpone choice is saved or reflected in UI.
- Ringo responds with appropriate message.

---

# Issue 14 — [UX] Add skip reason capture

## Goal

When a user skips a mission, capture why in a low-pressure way.

## Skip Reasons

- too tired
- no time
- too hard
- not relevant now
- don’t like this mission
- other

## Why

Skip reasons help future Ringo Brain recommendations.

## Tone

No shame.

Example:

“باشه. فقط کمکم کن بفهمم چرا، تا دفعه بعد بهتر پیشنهاد بدم.”

## Do Not Change

- Do not punish skipping.
- Do not reduce streak aggressively in this issue.
- Do not make reason required if user wants to close.

## Acceptance Criteria

- User can skip with optional reason.
- Reason can be stored.
- Ringo message remains supportive.

---

# Issue 15 — [Docs] Add Ringo Brain AI strategy document

## Goal

Document how AI should be introduced into RingoStrike safely and gradually.

## Key Decision

Do not build a custom AI model in MVP.

Use a hybrid strategy:

1. Rule-based Ringo Brain
2. AI-assisted language layer
3. Structured AI decision support
4. Fine-tuned/custom model only after enough data exists

## Core Principle

AI writes the words. Ringo Brain makes the decisions.

## Acceptance Criteria

- `docs/product/RINGO_BRAIN_STRATEGY.md` explains the phased AI strategy.
- Includes risks of using ChatGPT as uncontrolled decision-maker.
- Includes future data collection notes for fine-tuning.

---

# Issue 16 — [Frontend] Add Ringo mood mapping system

## Goal

Ensure Ringo’s visual sprite/mood matches the emotional state returned by Ringo Brain.

## Mood Examples

- idle
- welcome
- talking
- explaining
- thinking
- encouraging
- warning
- concerned
- happy
- celebration
- achievement
- proud
- sad
- sleeping
- focus
- victory

## Scope

Connect Ringo Brain mood output to existing Ringo sprite system if available.

## Do Not Change

- Do not redesign all Ringo assets.
- Do not break current image imports.
- Use fallback if sprite is missing.

## Acceptance Criteria

- Ringo component can receive mood key.
- Correct sprite is shown when available.
- Fallback works when sprite is missing.
- Mood is used in dashboard and reward sequence.

---

# Issue 17 — [UX] Progressive disclosure for early users based on activity

## Goal

Reduce cognitive load for new users by gradually revealing deeper features.

## Suggested Unlock Rules

0 check-ins:

- Ringo welcome
- Today mission
- Start path CTA

1+ check-ins:

- basic stats
- Today Saved
- simple progress

3+ check-ins:

- Ringo Pulse preview
- recent progress

5+ check-ins:

- achievements preview
- path details

Later:

- leaderboard
- full feed
- advanced profile

## Do Not Change

- Do not remove existing pages.
- Do not add days_active field.
- Use existing stats/check-in data.

## Acceptance Criteria

- Early users see a simplified experience.
- More advanced sections appear after meaningful activity.
- No existing page is deleted.

---

# Issue 18 — [Portfolio] Add project case study notes for future university application

## Goal

Create documentation that can later become a portfolio/university case study.

## Suggested File

```text
docs/portfolio/RINGOSTRIKE_CASE_STUDY_NOTES.md
```

## Include

- project summary
- problem statement
- why normal habit trackers fail
- Ringo as emotional interface
- character-driven UX
- Ringo Brain architecture
- adaptive missions
- reward sequence
- Ringo Pulse
- technical stack
- future roadmap

## Do Not Change

- Documentation only.
- No code changes.

## Acceptance Criteria

- Case study notes file exists.
- It explains the project as an emotionally intelligent self-improvement companion.
- It can later be converted into a portfolio page or PDF.

---

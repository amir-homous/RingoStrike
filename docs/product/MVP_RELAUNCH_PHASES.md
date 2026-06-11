# RingoStrike — MVP Relaunch Phases v1

## Phase 0 — Documentation & Product Alignment

Goal:

Capture all strategic decisions before changing code.

No existing code should be modified in this phase.

Deliverables:

- Product Soul document
- Ringo Character Bible
- Emotional Core Loop document
- Ringo Brain Strategy document
- Mission Design System document
- Reward Sequence document
- Ringo Pulse / Feed concept document
- MVP Relaunch Roadmap document

Why this phase matters:

The project needs a clear product direction before implementing more features.

---

## Phase 1 — Dashboard Simplification & Companion-First UX

Goal:

Make the dashboard feel like Ringo’s home, not a feature-heavy control panel.

Main changes:

- Put Ringo message at the center of the experience
- Show one clear next mission
- Add Tiny Mission and Bonus Mission concept in UI
- Reduce visible complexity for early users
- Keep existing pages/systems available, but avoid overwhelming the dashboard

Important:

Do not remove existing backend functionality.

Do not delete existing challenge/path/mission logic.

Only restructure the user-facing experience carefully.

---

## Phase 2 — Ringo Brain v1: Rule-Based Decision Engine

Goal:

Create a backend/frontend decision layer that determines what Ringo should say and suggest based on user context.

Ringo Brain v1 should be rule-based, not AI-based.

Inputs:

- user profile
- current time
- today_checked
- total_checkins
- current_streak
- missed_days
- active path/challenge
- available missions
- recent mission activity
- postpone/skip state if available

Outputs:

- user_state
- Ringo mood
- Ringo message
- suggested mission
- mission intensity
- available actions
- reward sequence type

Important:

This should be built as a separate service/module so it can later be upgraded with AI.

---

## Phase 3 — Mission Design System & Adaptive Mission Intensity

Goal:

Make missions more flexible and less overwhelming.

Main concepts:

- Main Mission
- Tiny Mission
- Bonus Mission
- time window
- difficulty
- energy level
- path relevance
- user state relevance

Mission system should support:

- low-energy version
- normal version
- bonus/advanced version
- postpone
- skip reason
- remind later

Important:

Do not show 30 random missions to the user.

The system can store many missions, but UI should recommend only a focused daily set.

---

## Phase 4 — Ringo Moment: Step-by-Step Reward Sequence

Goal:

Replace simple completion feedback with a sequential reward ritual.

After completing a mission, the user should see rewards one by one:

1. emotional confirmation
2. mission completed
3. XP earned
4. time/effort
5. path progress
6. streak / today saved
7. achievement unlock if any
8. Ringo Pulse / community update if available
9. next action choice

Important:

This should be a reusable frontend component.

It should support skip/fast-forward.

It should not block core check-in logic if reward rendering fails.

---

## Phase 5 — Ringo Pulse: Lightweight Activity Feed

Goal:

Create a warm community pulse, not a noisy social network.

Main feature:

A small feed preview on dashboard showing recent positive events.

Possible events:

- mission completed
- streak milestone
- achievement unlocked
- user returned
- path progress
- group progress

Privacy:

Feed events need visibility settings.

Sensitive events should be private or anonymous by default.

MVP version can start with simple public/anonymous events.

---

## Phase 6 — Reminder & Postpone UX

Goal:

Make reminder behavior feel conversational and caring.

User should be able to respond to a mission with:

- Start now
- Remind me later
- Make it smaller
- Skip today
- I’m too tired

Ringo should adapt based on this response.

Reminder messages should not feel robotic.

---

## Phase 7 — AI-Assisted Ringo Language Layer

Goal:

Add AI only after the deterministic Ringo Brain exists.

AI should generate natural language variations, not make uncontrolled product decisions.

Principle:

AI writes the words. Ringo Brain makes the decisions.

AI outputs should be structured, validated, and fallback-safe.

---

## Phase 8 — Portfolio / University Case Study

Goal:

Turn RingoStrike into a strong portfolio case study.

Deliverables:

- project story
- product challenge
- UX research insight
- character design
- Ringo Brain architecture
- reward sequence UX
- mission system
- screenshots
- motion/interaction mockups
- technical architecture
- roadmap

This phase can run in parallel after Phase 2 or 3.

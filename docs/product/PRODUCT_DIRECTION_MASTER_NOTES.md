# RingoStrike — Product Direction Master Notes v1

## Purpose

This document captures the main product decisions made during the RingoStrike strategic brainstorming phase.

These decisions should guide future development, GitHub issues, Codex prompts, UI/UX redesign, and product documentation.

The current codebase should not be rewritten unnecessarily. Existing backend/frontend systems should be preserved and extended carefully.

---

# 1. Core Product Decision

RingoStrike should not be positioned as a normal habit tracker.

The stronger direction is:

**RingoStrike is a caring daily companion that helps people improve their lives through small guided actions, emotional encouragement, playful progress, and a living character named Ringo.**

RingoStrike should feel like:

- a daily companion
- a guided self-improvement game
- a cozy emotional growth system
- a character-driven experience
- a small daily journey

It should not feel like:

- a cold checklist
- a complex productivity app
- a generic habit tracker
- a task manager
- a shame-based streak system

---

# 2. Main Product Rule

**First Ringo. Then system.**

The technical systems exist to make Ringo feel alive, useful, caring, and emotionally meaningful.

Paths, challenges, missions, stats, reminders, achievements, feed events, and AI features should all support the feeling that Ringo understands the user and guides them toward the next small step.

---

# 3. Ringo’s Role

Ringo is not only a mascot.

Ringo is the emotional interface of the product.

Ringo should:

- welcome the user
- understand the user’s current state
- suggest the next small mission
- reduce pressure when the user is tired
- celebrate small wins
- respond gently to missed days
- guide the user through reward moments
- narrate community progress
- create emotional continuity

The user should feel:

**“Ringo belongs to everyone, but this Ringo knows me.”**

---

# 4. Ringo’s Personality

Ringo is inspired by Amir’s real cat, Ringo, who was loved deeply and allowed to live freely.

Core personality:

- caring
- cool
- relaxed
- emotionally intelligent
- slightly playful
- honest
- gentle but not weak
- supportive but not fake
- wise but not preachy
- stylish but not arrogant

Ringo should never shame the user.

Ringo should never say things like:

- “You failed.”
- “You ruined your streak.”
- “Why didn’t you do it?”
- “Don’t be lazy.”

Ringo should say things like:

- “خوشحالم برگشتی.”
- “فقط یه قدم کوچیک.”
- “لازم نیست کامل باشی.”
- “همین هم حسابه.”
- “برگشتن خودش یه برده.”
- “امروز رو نجات دادیم.”

Catchphrases like **مشتی**, **مشتی پسر**, and **مشتی دختر** can be used, but they should be optional/personalized and not overused.

---

# 5. Core UX Direction

The current functional loop is:

User opens app → sees missions → completes mission → checks in → stats update

The desired emotional loop is:

User opens app → Ringo understands the user’s state → Ringo gives one clear next step → user completes it → Ringo reacts emotionally → rewards appear step by step → user feels progress → user wants to return tomorrow

---

# 6. Mission Visibility Decision

The system can contain many missions, but the user should not see too many at once.

Recommended daily mission structure:

- Main Mission: the main recommended step for today
- Tiny Mission: a smaller version for tired/low-energy users
- Bonus Mission: optional extra step for active/high-energy users

The user should always know what is “enough” for today.

After the Main Mission is completed, the app can say:

**Today is safe.**
فارسی: **امروزت نجات پیدا کرد.**

Bonus missions should be optional, not required.

---

# 7. Adaptive Experience Decision

Ringo should adapt based on user state.

Important states:

- new user
- first mission completed
- active user
- tired user
- low-energy day
- high-momentum day
- missed days
- returning after absence
- streak risk
- all done today
- morning
- afternoon
- night
- before sleep

Ringo should not recommend the same type of mission at every time of day.

Mission recommendations should consider:

- time of day
- user energy
- active path
- recent activity
- missed days
- previous skip/postpone reasons
- streak status
- mission difficulty
- user preference

---

# 8. Ringo Brain Decision

Do not build a custom AI model from scratch in the MVP.

Instead, build a **Hybrid Ringo Brain**:

Phase 1:

Rule-based decision engine.

Phase 2:

AI-assisted language generation.

Phase 3:

Structured AI decision support.

Phase 4:

Fine-tuned/custom personality model only if enough data exists.

Core principle:

**AI writes the words. Ringo Brain makes the decisions.**

Ringo Brain should decide:

- user state
- Ringo mood
- mission intensity
- recommended mission
- tone
- available actions
- reward sequence type
- reminder style

AI can later help with:

- natural message variation
- personalized wording
- gentle conversation
- creative reward text
- summary generation

---

# 9. Ringo Reward Sequence Decision

Mission completion should not show all results in one static card.

After completing a mission, the user should go through a step-by-step animated reward sequence, inspired by Duolingo.

This can be called:

**Ringo Moment**

Possible sequence:

1. Ringo emotional confirmation
2. Mission completed
3. Time/effort recognition
4. XP earned
5. Path progress
6. Streak / Today Saved
7. Achievement / reward unlock
8. Ringo Pulse / friend/community update
9. Next choice: finish today or continue with bonus mission

Each step should appear one by one with simple smooth animation and user tap/click to continue.

There should be a skip/fast-forward option.

---

# 10. Ringo Pulse / Feed Decision

RingoStrike should eventually include a lightweight social/community feed.

The feed should not feel like a noisy social network.

It should feel like a warm pulse of small wins.

Possible event types:

- mission completed
- streak milestone
- achievement unlocked
- user returned after absence
- path progress
- group progress
- bonus mission completed

Examples:

- “🔥 سینا امروز سومین استریکش رو گرفت.”
- “🌱 یکی از بچه‌ها بعد از چند روز برگشت.”
- “🏆 سارا یک اچیومنت جدید باز کرد.”

Privacy is important.

Visibility levels:

- private
- public
- friends only
- anonymous

Sensitive missions should not be exposed publicly by default.

---

# 11. UI/UX Direction

The dashboard should become Ringo’s home.

Main dashboard structure:

1. Ringo character + contextual message
2. Today’s Step / Main Mission
3. Tiny Mission fallback
4. Optional Bonus Mission
5. Path progress preview
6. Streak / Today Saved status
7. Small Ringo Pulse preview

The app should not overwhelm new users with:

- too many paths
- too many challenges
- too many missions
- too many stats
- full leaderboard
- full feed
- complex profile systems

Deeper systems should unlock gradually.

---

# 12. Portfolio / University Value

RingoStrike can become a strong university portfolio project if presented as:

**An emotionally intelligent, character-driven, gamified self-improvement companion.**

The case study should highlight:

- product strategy
- character design
- emotional UX
- gamification
- adaptive missions
- reward sequence design
- AI strategy
- community feed design
- frontend/backend implementation
- notification systems
- visual design and motion design potential

---

# 13. Development Principle

Do not rewrite existing code unnecessarily.

Preserve current working systems.

Extend the project with small, isolated, testable changes.

Every GitHub issue should clearly state:

- goal
- what to add
- what not to change
- files likely involved
- acceptance criteria
- testing notes

---

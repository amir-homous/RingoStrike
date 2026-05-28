# FRONTEND_CONTRACT.md

# RingoStrike Frontend Contract

Version: v0.4+
Architecture Status: Modular Progression Platform
Frontend Stack: Vue 3 + Vite
Backend Stack: Flask + SQLite

---

# Product Vision

RingoStrike is a premium progression platform focused on:

* consistency
* streak psychology
* momentum building
* progression identity
* emotional reinforcement
* gamified self-improvement
* future social accountability systems

The product should feel:

* cinematic
* premium
* emotionally intelligent
* rewarding
* calm
* modern
* internationally polished

This is NOT:

* a generic todo app
* a noisy productivity tracker
* a dopamine casino
* a social media clone

This IS:

* a progression identity ecosystem

---

# Current Frontend Stack

## Core Technologies

* Vue 3
* Vite
* Vue Router
* Composition API
* TailwindCSS
* Modular component architecture

---

# Current Frontend Structure

```txt
src/
├── App.vue
├── assets/
├── components/
│   ├── achievements/
│   ├── activity/
│   ├── challenges/
│   ├── feedback/
│   ├── profile/
│   ├── progress/
│   └── ui/
├── lib/
├── router/
├── stores/
├── styles/
└── views/
```

---

# Frontend Architectural Philosophy

## Core Rules

### DO

* Keep systems modular
* Reuse progression logic
* Reuse timeline architecture
* Reuse achievement architecture
* Reuse profile identity systems
* Preserve visual consistency
* Preserve emotional UX direction
* Use optimistic UI carefully
* Keep animations restrained
* Keep components composable

### DO NOT

* Duplicate progression systems
* Duplicate timeline systems
* Create disconnected UX patterns
* Add noisy social media behavior
* Add aggressive game UI
* Hardcode backend calculations
* Break current hierarchy

---

# Current Route Architecture

## Existing Views

| Route              | View             |
| ------------------ | ---------------- |
| `/login`           | Login.vue        |
| `/dashboard`       | Dashboard.vue    |
| `/profile`         | Profile.vue      |
| `/challenges`      | Challenges.vue   |
| `/enrollment/:id/leaderboard` | Leaderboard.vue  |
| `/enrollment/:id`      | Enrollment.vue   |
| `/docs`        | ApiDocsView.vue  |
| `/auth/callback`   | AuthCallback.vue |

---

# Dashboard Architecture

## Dashboard.vue

Dashboard is the central progression hub.

Current hierarchy:

1. Hero Progress
2. Stats & Goal Cards
3. Recent Progress Feed
4. Activity Timeline
5. Achievement Preview
6. Active Challenges

The dashboard must preserve:

* progression psychology
* emotional reinforcement
* motivational hierarchy
* rewarding feedback loops

---

# Existing Frontend Systems

# 1. Progression System

Directory:

```txt
components/progress/
```

Current Components:

```txt
HeroProgressCard.vue
NextGoalCard.vue
RecentProgressFeed.vue
StatsGrid.vue
XPProgressBar.vue
```

Responsibilities:

* XP display
* Level display
* Progress visualization
* Next goal motivation
* Progress summaries
* Reward feedback loops

Important:
Frontend must NOT calculate authoritative XP/streak values itself.

Backend is source-of-truth.

Frontend only renders progression state.

---

# 2. Activity Timeline System

Directory:

```txt
components/activity/
```

Current Components:

```txt
ActivityTimeline.vue
ActivityTimelineItem.vue
TimelineDayGroup.vue
EmptyTimelineState.vue
```

Purpose:

* progression memory
* emotional continuity
* historical reinforcement
* activity storytelling

Current Event Types:

* checkin
* achievement
* streak
* level_up

IMPORTANT:
All future activity/social feeds must extend this system.

DO NOT build duplicate timeline architectures.

---

# 3. Achievement System

Directory:

```txt
components/achievements/
```

Current Components:

```txt
AchievementCard.vue
AchievementGrid.vue
AchievementPreview.vue
AchievementToast.vue
```

Current Features:

* rarity display
* unlock states
* reward toasts
* hidden achievements
* XP rewards

Future-Safe Goals:

* seasonal achievements
* social achievements
* collectible systems
* progression badges

---

# 4. Profile Identity System

Directory:

```txt
components/profile/
```

Current Components:

```txt
ConsistencyHeatmap.vue
ProfileHeroCard.vue
ProfileStatsGrid.vue
UserAvatar.vue
```

Purpose:

* identity visualization
* progression ownership
* consistency visualization
* emotional attachment

Future Expansion:

* customizable identity
* public profiles
* social profile sharing
* avatar systems
* title systems

---

# 5. Challenge System

Directory:

```txt
components/challenges/
```

Current Components:

```txt
ChallengeCard.vue
```

Responsibilities:

* challenge display
* challenge metadata
* participation state
* check-in actions
* progression feedback

Future Expansion:

* public discovery
* participant momentum
* challenge communities
* challenge categories

---

# 6. Reward Feedback System

Directory:

```txt
components/feedback/
```

Current Components:

```txt
RewardFeedback.vue
```

Purpose:

* XP reward feedback
* streak reinforcement
* achievement celebration
* level-up reinforcement

UX Direction:

* subtle
* premium
* emotionally rewarding
* restrained

DO NOT:

* overanimate
* create casino UX
* create flashy effects

---

# 7. UI Foundation System

Directory:

```txt
components/ui/
```

Current Components:

```txt
AppContainer.vue
AppFooter.vue
AppHeader.vue
BaseButton.vue
BaseCard.vue
BaseInput.vue
SkeletonBlock.vue
Spinner.vue
UiState.vue
```

Purpose:

* shared design system
* consistency
* reusable layout primitives
* visual stability

IMPORTANT:
All future UI should build on these primitives.

Avoid introducing isolated styling systems.

---

# Current Styling Architecture

## styles/

```txt
styles/
├── base.css
└── tokens.css
```

## Purpose

### tokens.css

Contains:

* colors
* spacing
* shadows
* gradients
* typography tokens
* visual constants

### base.css

Contains:

* base resets
* shared styles
* typography defaults
* global layout rules

---

# Design Language Contract

The visual language must remain:

* dark premium aesthetic
* soft glassmorphism
* restrained gradients
* cinematic spacing
* soft shadows
* elegant hierarchy
* emotionally intelligent UI

Motion should feel:

* smooth
* calm
* rewarding
* subtle

Avoid:

* visual chaos
* excessive glow
* hyper-saturated gaming effects
* loud interactions

---

# Current State Management

## Store

```txt
stores/session.js
```

Current Responsibility:

* authenticated user session
* login state
* auth persistence

Guideline:
Use local component state first.

Only globalize truly shared app state.

---

# API Layer

Directory:

```txt
lib/api.js
```

Purpose:

* centralized API communication
* backend abstraction layer
* auth-aware requests

IMPORTANT:
All backend communication should flow through this layer.

Avoid scattered fetch logic.

---

# Existing Backend API Contracts

# Authentication

## POST `/login`

Authenticate user.

## POST `/register`

Register user.

## POST `/logout`

Destroy session.

## GET `/me`

Return authenticated user.

---

# Progression APIs

## GET `/me/stats`

Returns:

* XP
* Level
* Streaks
* Progress %
* Total check-ins

Used by:

* HeroProgressCard
* StatsGrid
* XPProgressBar

---

## GET `/me/activity`

Returns progression timeline events.

Used by:

* ActivityTimeline

---

## GET `/me/achievements`

Returns:

* unlocked achievements
* achievement metadata

Used by:

* AchievementGrid
* AchievementPreview

---

## GET `/me/profile`

Returns:

* identity information
* title
* XP
* avatar
* progression summary

Used by:

* ProfileHeroCard

---

## GET `/me/consistency`

Returns:

* consistency heatmap data

Used by:

* ConsistencyHeatmap

---

## GET `/me/challenges`

Returns:

* enrolled challenges
* challenge states
* check-in status

Used by:

* Dashboard
* ChallengeCard

---

## POST `/checkin`

Performs challenge check-in.

Frontend Expectations:

* optimistic updates
* reward feedback
* timeline insertion
* rollback on failure
* reconciliation with backend

---

# Optimistic UI Contract

Current systems already support:

* optimistic check-ins
* optimistic XP gain
* optimistic streak continuation
* optimistic timeline insertion

Requirements:

* safe rollback
* backend reconciliation
* state consistency

---

# Mobile Experience Rules

The app must remain:

* responsive
* readable
* touch-friendly
* visually balanced
* lightweight

Mobile UX is critical.

Avoid:

* oversized dashboards
* cluttered cards
* overly dense layouts

---

# Future Architecture Direction

The current frontend is being prepared for:

## Social Systems

* public profiles
* social feed
* challenge discovery
* participant momentum
* reactions
* follow systems

## AI Systems

* AI progression insights
* momentum forecasting
* burnout detection
* habit intelligence
* recommendation systems

## Identity Systems

* profile customization
* profile themes
* avatars
* social cards
* progression showcases

## Advanced Gamification

* seasons
* guilds
* events
* social achievements
* progression paths

---

# Important Engineering Rules

When extending frontend systems:

## ALWAYS

* inspect existing architecture first
* extend existing systems
* reuse event architecture
* reuse progression logic
* preserve UX hierarchy
* preserve emotional design language

## NEVER

* duplicate progression systems
* rebuild timeline systems
* create disconnected UI flows
* break dashboard architecture
* tightly couple UI to DB schema

---

# Final UX Goal

The final product should feel like:

> “A living progression identity ecosystem.”

The user should feel:

* motivated
* emotionally connected
* proud of progression
* rewarded for consistency
* visually immersed
* socially inspired

WITHOUT:

* toxic competition
* social media chaos
* productivity guilt
* noisy gamification

# RingoStrike

> A cinematic progression platform focused on consistency, momentum, identity, and emotionally intelligent gamification.

RingoStrike is not a traditional habit tracker.

It is a progression-driven ecosystem designed to make consistency feel:

* meaningful
* rewarding
* visible
* emotionally engaging

The product combines:

* streak systems
* XP progression
* achievement engines
* activity timelines
* progression identity
* Ringo-led daily missions
* mission focus mode
* staged mission reward sequences
* Daily Momentum Bar
* post-safe optional explorer growth map
* frontend display localization for known seeded mission/path/challenge content
* Telegram reminder automation
* social momentum architecture

into a premium and future-scalable experience.

---

# Vision

Most productivity apps feel:

* mechanical
* emotionally empty
* visually generic

RingoStrike aims to become:

> “A living progression operating system.”

The long-term goal is to create a platform where:

* consistency becomes identity
* progress becomes shareable
* momentum becomes social
* growth feels cinematic

---

# Current Features

## Authentication

* Local authentication
* Telegram-ready authentication architecture
* Session/token system

---

## Progression Engine

* XP system
* Leveling engine
* Current streak tracking
* Longest streak tracking
* Progress percentage calculation
* Reward feedback loops
* Ringo-led paths and daily missions
* Mission reminders, skips, and completion state
* Mission-family behavior for main/tiny substitutes and optional bonus momentum
* Frontend-only staged mission reward sequence that displays mission completion, earned XP, strike/check-in/path/challenge impact where available, and next choice without changing backend progression ownership
* Frontend-only Daily Momentum Bar that shows today safety, streak count, today-only path rings, and contextual actions without changing backend progression ownership

---

## Challenges

* Joinable challenges
* Daily check-ins
* Enrollment system
* Challenge progression
* Active challenge dashboard

---

## Activity Timeline

* Event-driven progression feed
* Timeline grouping
* Momentum history
* Optimistic UI updates
* Future-ready social event architecture

---

## Achievement System

* Centralized achievement engine
* XP reward achievements
* Unlock tracking
* Achievement rarity system
* Dashboard integration
* Timeline integration

---

## Profile Identity Hub

* Dynamic progression titles
* Consistency heatmap
* Profile progression overview
* Avatar architecture
* Identity-focused UX

---

## Frontend Experience

* Premium dark UI
* Glassmorphism-inspired design
* Modular Vue component system
* Ringo-led MissionCenter with focus-mode dashboard gating
* Compact progress strip during focused daily loops
* Daily Momentum Bar as the compact daily strike/path/action dock, with `compactProgressStrip` remaining the top/global XP-level/status strip
* First-run staged reveal and calm Rest Mode after finishing for today
* Optional explorer progress-map polish with path/challenge progress surfaces, icon rings, XP summaries, mission icons, and status-aware mission rows
* Staged Mission Reward Sequence v2 after eligible mission completions, normalizing backend reward steps, using before/after reward snapshots where available, resolving mission icons by `mission.key`, and preserving calm no-XP/already-done fallbacks
* DB-backed path icons, today-only path progress rings, action icons from `frontend/src/assets/action-icons/`, and lightweight Explore Paths navigation to the existing Paths page
* Reminder chip in the compact progress strip only when there are active reminder counts to show
* Reward-driven interactions
* Responsive layouts
* Emotionally intelligent UX
* English/Persian i18n with RTL support
* Full-root dark background coverage for stable LTR/RTL rendering
* seeded mission/path/challenge display localization without backend seed-data changes

---

## Operations

* Flask backend runs from `backend/app.py`
* Production-like VPS runtime uses `systemd` service `ringostrike-backend`
* Current VPS backend bind: `127.0.0.1:5005`
* Current VPS frontend is served by nginx from `frontend/dist`
* Public backend access uses nginx `/api-proxy`
* n8n can trigger due mission Telegram reminders through the protected backend endpoint

---

# Tech Stack

## Frontend

* Vue 3
* Vite
* Vue Router
* Pinia
* CSS tokens/base styles with a Tailwind dependency present but not used as the active global styling layer

## Backend

* Flask
* SQLite
* Modular service architecture

---

# Project Architecture

The backend follows a modular architecture:

```txt
backend/
├── routes/
├── services/
├── database.py
├── config.py
└── app.py
```

Core philosophy:

* thin routes
* centralized business logic
* reusable services
* future-safe progression systems

---

# Frontend Structure

```txt
src/
├── components/
│   ├── achievements/
│   ├── activity/
│   ├── challenges/
│   ├── feedback/
│   ├── guided/
│   ├── missions/
│   ├── profile/
│   ├── progress/
│   ├── ringo/
│   └── ui/
├── i18n/
├── views/
├── router/
├── stores/
└── lib/
```

The frontend is built around:

* reusable progression components
* emotional feedback systems
* Ringo/MissionCenter guided daily focus
* English/Persian localization with RTL support
* scalable identity/social architecture

---

# Documentation

Full project documentation lives inside:

```txt
/docs
```

Important files:

| File                 | Purpose                       |
| -------------------- | ----------------------------- |
| AI_CONTEXT.md        | AI project memory/context     |
| PROJECT_OVERVIEW.md  | High-level product overview   |
| ARCHITECTURE.md      | Backend/frontend architecture |
| DATABASE_SCHEMA.md   | Database documentation        |
| FRONTEND_CONTRACT.md | Frontend/API contracts        |
| DESIGN_SYSTEM.md     | UI/UX philosophy              |
| ROADMAP.md           | Product roadmap               |
| CHANGELOG.md         | Feature evolution             |
| BACKEND_SYSTEMD_RUNBOOK.md | VPS backend service operations |
| REMINDER_AUTOMATION_RUNBOOK.md | Telegram reminder/n8n operations |

---

# Product Direction

Current stage:

* companion-first guided progression
* identity-focused UX
* mission focus and completion-flow hardening
* pre-launch operational polish

Future direction:

* social momentum layer
* fuller Mission Context UX
* contextual path/challenge/mission reward framing
* fuller localization coverage for future custom content and CMS/content-management if the product scales
* AI insights
* seasonal progression systems

---

# Design Philosophy

RingoStrike is intentionally designed to feel:

* cinematic
* premium
* calm
* emotionally rewarding
* socially motivating

NOT:

* noisy
* addictive
* chaotic
* casino-style gamification

---

# Running The Project

## Backend

```bash
cd backend
python app.py
```

Default server:

```txt
http://localhost:5005
```

`backend/app.py` reads:

```env
FLASK_HOST=127.0.0.1
PORT=5005
FLASK_DEBUG=0
```

For the current VPS production-like runtime, use `FLASK_HOST=127.0.0.1`, `PORT=5005`, and `FLASK_DEBUG=0`; public access should go through nginx `/api-proxy`.

---

## Frontend

```bash
npm install
npm run dev
```

Frontend runs on:

```txt
http://localhost:5173
```

---

# Environment Variables

Backend examples:

```env
FLASK_ENV=development
FLASK_HOST=0.0.0.0
PORT=5005
FLASK_DEBUG=1
SECRET_KEY=change-this
JWT_SECRET=change-this-too
DB_PATH=users.db
AUTH_MODE=both
LOCAL_LOGIN_ENABLED=true
```

Frontend VPS example:

```env
VITE_API_BASE=/api-proxy
VITE_BASE=/
```

Do not use `VITE_API_BASE=http://localhost:5005` in production browser builds. Browser `localhost` points at the user's device, not the VPS.

Reminder automation uses:

```env
TELEGRAM_BOT_TOKEN=<server-only-secret>
REMINDER_ADMIN_TOKEN=<server-only-secret>
```

Never commit real `.env` secrets.

---

# Development Philosophy

When contributing:

DO:

* preserve architecture consistency
* reuse progression systems
* extend existing services
* avoid duplicate logic
* preserve design language
* think future-safe

DO NOT:

* tightly couple systems
* duplicate XP/streak logic
* redesign working UX unnecessarily
* create disconnected features

---

# Long-Term Goal

RingoStrike is evolving toward:

> “A social progression ecosystem powered by emotionally intelligent gamification.”

Future systems may include:

* public progression identity
* social feeds
* shared momentum systems
* AI-powered consistency insights
* guilds/teams
* seasonal progression
* progression analytics

---

# Author

Created by Amir Hossein Mousavi
Motion Designer • Product Builder • Creative Technologist

---

# License

This project is currently private/proprietary.
License structure may change in future public releases.

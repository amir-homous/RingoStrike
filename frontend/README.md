# RingoStrike

> A premium progression identity platform focused on consistency, momentum, challenges, XP, streaks, achievements, and emotionally intelligent gamification.

RingoStrike is not a traditional habit tracker.

It is a progression-driven ecosystem designed to make consistency feel:

- meaningful
- rewarding
- visible
- emotionally engaging
- identity-forming

The product combines:

- challenge systems
- daily check-ins
- XP progression
- level growth
- streak systems
- achievement engines
- activity timelines
- public/private profile identity
- social momentum foundations

into a premium and future-scalable experience.

---

## Current Product Stage

RingoStrike is currently in:

> Post-MVP Stabilization / Pre-Launch Hardening

The project has moved beyond raw MVP.

Core product flows are implemented and manually QA-checked. The current focus is:

- reliability
- security
- production configuration
- documentation
- deployment readiness
- final launch hardening

Current local backend test result:

```txt
19 passed
```

---

## Vision

Most productivity apps feel:

- mechanical
- emotionally empty
- visually generic
- disconnected from identity

RingoStrike aims to become:

> A premium progression ecosystem.

The long-term goal is to create a platform where:

- consistency becomes identity
- progress becomes shareable
- momentum becomes social
- growth feels cinematic
- challenges create belonging without toxic competition

---

## Core Features

### Authentication

- Local authentication.
- JWT cookie auth.
- Bearer token fallback support.
- Logout cookie-session clearing.
- Production cookie configuration coverage.
- Telegram-ready integration placeholders.

### Challenges

- Public challenges.
- Invite-only challenges.
- Private challenge foundations.
- Daily check-ins.
- Enrollment system.
- Challenge discovery.
- Join-code flow.
- Challenge progress surfaces.
- Default launch challenge seeding.

### Progression Engine

- XP per check-in.
- Leveling.
- Current streak calculation.
- Longest streak calculation.
- Progress percentage calculation.
- Stats sync after check-in.
- Duplicate check-in handling.
- Reward feedback loops.

### Achievement System

- Achievement definitions.
- Unlock tracking.
- Achievement rarity.
- XP reward achievements.
- First-check-in achievement unlock.
- Streak/check-in/XP milestone foundations.
- Dashboard and profile integration.

### Activity Timeline

- Event-driven progression feed.
- Check-in events.
- Achievement events.
- Level-up-ready event architecture.
- Public-safe activity foundations.
- Timeline UI integration.

### Profile Identity Hub

- Private profile aggregate.
- Public profile route: `/u/:username`.
- Dynamic profile title.
- Avatar URL.
- Bio.
- Public/private visibility.
- Consistency heatmap.
- Public achievements.
- Public consistency.
- Profile settings.
- Profile update validation.

### Social Momentum Foundations

- Leaderboards.
- Today leaderboard.
- Rank metadata.
- Deterministic tie-breaker metadata.
- Member count / member preview foundations.
- Public profile identity layer.

---

## Tech Stack

### Backend

- Flask
- SQLite
- Blueprint-based routing
- Service-layer architecture
- JWT cookie/Bearer auth
- Pytest

### Frontend

- Vue 3
- Vite
- Vue Router
- Pinia
- Modular component architecture
- Premium dark/glass UI system

---

## Project Structure

```txt
RingoStrike/
├── backend/
│   ├── routes/
│   ├── services/
│   ├── tests/
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   └── database.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   ├── stores/
│   │   └── lib/
│   ├── package.json
│   └── vite.config.js
├── docs/
├── scripts/
└── README.md
```

---

## Architecture Principles

The backend should keep:

- thin routes
- reusable services
- centralized progression logic
- centralized stats calculation
- privacy enforcement near public identity services
- future-safe database changes

The frontend should keep:

- modular reusable components
- centralized API usage
- premium visual consistency
- restrained animation
- clear progression hierarchy
- emotional but non-chaotic UX

RingoStrike should feel:

- premium
- cinematic
- calm
- motivational
- elegant
- rewarding

Not:

- noisy
- casino-like
- chaotic
- generic
- addictive by design

---

## Local Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a local env file:

```bash
cp .env.example .env
```

Run backend:

```bash
py app.py
```

Backend default URL:

```txt
http://localhost:5005
```

Health checks:

```bash
curl http://localhost:5005/health
curl http://localhost:5005/health/config
```

---

### Frontend Setup

```bash
cd frontend
npm install
```

Create a local env file:

```bash
cp .env.example .env
```

Run frontend:

```bash
npm run dev
```

Frontend default URL:

```txt
http://localhost:5173
```

---

## Environment Files

### Backend

Example file:

```txt
backend/.env.example
```

Local file:

```txt
backend/.env
```

Important backend variables:

- `FLASK_ENV`
- `SECRET_KEY`
- `JWT_SECRET`
- `JWT_COOKIE_NAME`
- `JWT_COOKIE_SECURE`
- `JWT_COOKIE_SAMESITE`
- `LOCAL_LOGIN_ENABLED`
- `DB_PATH`
- `PUBLIC_BASE_URL`
- `FRONTEND_BASE_URL`
- `FRONTEND_ORIGIN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `NOTION_TOKEN`

Real secrets must never be committed.

### Frontend

Example file:

```txt
frontend/.env.example
```

Local file:

```txt
frontend/.env
```

Important frontend variables:

- `VITE_API_BASE`
- `VITE_BASE`

Local example:

```env
VITE_API_BASE=http://localhost:5005
VITE_BASE=/
```

Production examples:

```env
VITE_API_BASE=https://api.ringostrike.com
VITE_BASE=/
```

or:

```env
VITE_API_BASE=https://www.ringostrike.com
VITE_BASE=/
```

---

## Testing

### Backend Tests

```bash
cd backend
py -m pytest -q
```

Current local result:

```txt
19 passed
```

Backend coverage includes:

- health endpoint
- safe config health endpoint
- auth register/login/me
- logout cookie clearing
- username validation
- challenge join/check-in core loop
- invite-only challenge join
- duplicate check-in behavior
- stats update after check-in
- achievement unlock after first check-in
- public/private profile privacy
- public consistency privacy
- public achievements privacy
- profile validation
- leaderboard rank metadata
- CORS production origin support
- auth cookie production settings
- production secret requirements

### Frontend Build

```bash
cd frontend
npm run build
```

This verifies the production frontend bundle.

---

## Deployment Smoke Check

A backend smoke script is available:

```bash
python scripts/smoke_backend.py --base-url http://localhost:5005
```

Production example:

```bash
python scripts/smoke_backend.py --base-url https://api.ringostrike.com
```

It checks:

- `/health`
- `/health/config`
- valid JSON response
- `ok: true`
- non-zero exit on failure

---

## GitHub Actions

Current workflows:

- Backend Tests
- Frontend Build

Backend CI runs pytest.

Frontend CI runs the production build. If GitHub Actions npm install/build instability reappears, document the failure and compare with local `npm run build`.

---

## Manual QA

Manual QA report:

```txt
docs/MANUAL_QA_REPORT.md
```

Launch QA checklist:

```txt
docs/LAUNCH_QA_CHECKLIST.md
```

Core routes checked during the latest UI polish pass:

- `/login`
- `/dashboard`
- `/challenges`
- `/enrollment/:id`
- `/enrollment/:id/leaderboard`
- `/me/profile`
- `/u/:username`

Current manual QA decision:

```txt
PARTIAL / PRE-LAUNCH READY
```

Meaning: core flows are stable and visually polished, but production deployment, production environment configuration, CI confirmation, and deployment QA are still required before public launch.

---

## Production Readiness

Deployment checklist:

```txt
docs/DEPLOYMENT_CHECKLIST.md
```

Before first public launch:

- Backend tests pass.
- Frontend build passes.
- GitHub Actions pass or known issue is documented.
- Backend `.env` is configured with real secrets.
- Frontend `.env` points to production API.
- Production CORS origin is configured.
- JWT cookie settings are correct for HTTPS.
- Database backup process exists.
- Deployment smoke script passes.
- Manual QA is repeated after deploy.
- Privacy policy and public profile behavior are reviewed.

---

## Important Documentation

Full project documentation lives inside:

```txt
docs/
```

Key files:

| File | Purpose |
| --- | --- |
| `AI_CONTEXT.md` | AI/project memory and current context |
| `PROJECT_OVERVIEW.md` | High-level product overview |
| `ARCHITECTURE.md` | Backend/frontend architecture |
| `DATABASE_SCHEMA.md` | Database documentation |
| `FRONTEND_CONTRACT.md` | Frontend/API contracts |
| `DESIGN_SYSTEM.md` | UI/UX philosophy |
| `ROADMAP.md` | Product roadmap |
| `CHANGELOG.md` | Feature evolution |
| `LAUNCH_QA_CHECKLIST.md` | Launch QA checklist |
| `MANUAL_QA_REPORT.md` | Manual QA result report |
| `DEPLOYMENT_CHECKLIST.md` | Deployment readiness checklist |

---

## Development Workflow

Preferred branch flow:

```txt
dev -> main -> production
```

Recommended local check before commit:

```bash
cd backend
py -m pytest -q
```

```bash
cd frontend
npm run build
```

Optional backend smoke check:

```bash
python scripts/smoke_backend.py --base-url http://localhost:5005
```

---

## Contribution Rules

Do:

- preserve architecture consistency
- reuse existing services
- keep progression logic centralized
- preserve API contracts
- add tests for stabilization work
- update docs after meaningful architecture changes
- keep UI premium, minimal, and emotionally intelligent

Do not:

- duplicate XP/streak/progression logic
- create fat routes
- rewrite working systems unnecessarily
- introduce disconnected UI styles
- add noisy gamification
- commit real secrets
- bypass privacy rules on public identity endpoints

---

## Roadmap Direction

Near-term:

- production deployment readiness
- CI reliability
- database backup/restore planning
- deployment smoke testing
- API error-shape consistency
- auth rate limiting
- migration strategy

Future product expansion:

- Telegram reminders
- Telegram login if still desired
- Android app/widget access
- user timezone preferences
- preferred check-in windows
- late check-in states
- weekly summaries
- AI-generated progress insights
- public share cards
- OpenGraph profile previews
- social inspiration mechanics
- seasonal progression systems

---

## Author

Created by Amir Hossein Mousavi  
Motion Designer • Product Builder • Creative Technologist

---

## License

This project is currently private/proprietary.

License structure may change in future public releases.
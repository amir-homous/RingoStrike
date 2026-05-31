# RingoStrike - Deployment Checklist

Deployment readiness checklist for the first production/pre-launch deployment.

## Deployment Stage

Current target:

```txt
Pre-launch production deployment
```

Primary branch flow:

```txt
dev -> main -> production
```

---

## Pre-Deployment Requirements

- [ ] Backend tests pass locally.
- [ ] Frontend production build passes locally.
- [ ] Backend Tests GitHub Action passes.
- [ ] Frontend Build GitHub Action passes or has a documented CI workaround.
- [ ] Manual QA report is updated.
- [ ] `.env` files are prepared locally on the server.
- [ ] Real secrets are not committed.
- [ ] Database backup strategy is defined.
- [ ] Rollback process is understood.

---

## Backend Environment

Required backend environment file:

```txt
backend/.env
```

Required values:

- [ ] `FLASK_ENV`
- [ ] `SECRET_KEY`
- [ ] `JWT_SECRET`
- [ ] `JWT_COOKIE_NAME`
- [ ] `JWT_COOKIE_SECURE`
- [ ] `JWT_COOKIE_SAMESITE`
- [ ] `LOCAL_LOGIN_ENABLED`
- [ ] `DB_PATH`
- [ ] `PUBLIC_BASE_URL`
- [ ] `FRONTEND_BASE_URL`
- [ ] `FRONTEND_ORIGIN`

Optional / integration values:

- [ ] `TELEGRAM_BOT_TOKEN`
- [ ] `TELEGRAM_BOT_USERNAME`
- [ ] `NOTION_TOKEN`
- [ ] `NOTION_USERS_DB_ID`
- [ ] `NOTION_ENROLLMENTS_DB_ID`
- [ ] `NOTION_CHALLENGES_DB_ID`
- [ ] `NOTION_DAILY_LOGS_DB_ID`
- [ ] `NOTION_TELEGRAM_PROP`

---

## Frontend Environment

Required frontend environment file:

```txt
frontend/.env
```

Required values:

- [ ] `VITE_API_BASE`
- [ ] `VITE_BASE`

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

## Database

- [ ] Confirm production DB path.
- [ ] Confirm database file permissions.
- [ ] Run database initialization safely.
- [ ] Confirm indexes exist.
- [ ] Confirm seed data strategy.
- [ ] Create backup before deployment update.
- [ ] Confirm restore process.

---

## Backend Deployment

- [ ] Install Python version compatible with project.
- [ ] Create virtual environment.
- [ ] Install `backend/requirements.txt`.
- [ ] Configure `.env`.
- [ ] Run backend health check.
- [ ] Confirm auth endpoints.
- [ ] Confirm protected endpoints reject unauthenticated requests.
- [ ] Confirm cookie settings for production HTTPS.
- [ ] Confirm CORS/frontend origin behavior.

Health check:

```bash
curl https://api.ringostrike.com/health
```

Local fallback:

```bash
curl http://localhost:5005/health
```

---

## Frontend Deployment

- [ ] Install Node.js compatible with project.
- [ ] Install dependencies.
- [ ] Build frontend.
- [ ] Confirm generated `dist/`.
- [ ] Serve frontend from correct root/subpath.
- [ ] Confirm `VITE_API_BASE` points to production backend.
- [ ] Confirm routes work after refresh.

Build command:

```bash
cd frontend
npm run build
```

---

## Reverse Proxy / Server

- [ ] Configure HTTPS.
- [ ] Configure frontend route fallback to `index.html`.
- [ ] Configure backend reverse proxy.
- [ ] Confirm API path routing.
- [ ] Confirm cookie domain/security behavior.
- [ ] Confirm static asset caching.
- [ ] Confirm upload/body size limits if needed later.

---

## Post-Deployment Smoke Test

Check these routes manually:

- [ ] `/login`
- [ ] `/dashboard`
- [ ] `/challenges`
- [ ] `/enrollment/:id`
- [ ] `/enrollment/:id/leaderboard`
- [ ] `/me/profile`
- [ ] `/u/:username`

Check these API flows:

- [ ] Health check.
- [ ] Register/login.
- [ ] Load dashboard.
- [ ] Join public challenge.
- [ ] Join invite-only challenge.
- [ ] Check-in.
- [ ] Load leaderboard.
- [ ] Update profile.
- [ ] Toggle profile visibility.
- [ ] Public profile respects visibility.

---

## Monitoring / Recovery

- [ ] Backend logs are accessible.
- [ ] Frontend errors can be inspected.
- [ ] Server restart process is documented.
- [ ] Database backup is available.
- [ ] Rollback commit/tag is known.
- [ ] Known CI issue is documented if unresolved.

---

## Launch Decision

Status:

```txt
READY / NOT READY / PARTIAL
```

Decision notes:

```txt
Add deployment decision notes here.
```
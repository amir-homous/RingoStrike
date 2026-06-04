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
- [ ] `CORS_ORIGINS` if more than one browser origin must be allowed.

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

- [ ] `VITE_BASE`

Production examples:

```env
# Same-origin Nginx deployment with a dedicated API proxy prefix:
VITE_API_BASE=/api-proxy
VITE_BASE=/
```

or:

```env
VITE_API_BASE=https://api.ringostrike.com
VITE_BASE=/
```

Only omit `VITE_API_BASE` when backend API routes can safely live at the same root as frontend routes. The VPS deployment uses `/api-proxy` because `/challenges` is both a Vue route and a backend API route.

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
- [ ] Confirm `VITE_API_BASE` is omitted for same-origin production or points to the separate production API origin.
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

### VPS Same-Origin Nginx Pattern

The current VPS test deployment is served at:

```txt
http://82.115.24.10
```

Nginx serves the frontend from:

```txt
/home/ringo/RingoStrike/frontend/dist
```

Flask runs locally on the VPS at:

```txt
http://127.0.0.1:5005
```

Use a dedicated API proxy prefix and rewrite it to Flask:

```nginx
location /api-proxy/ {
    rewrite ^/api-proxy/(.*)$ /$1 break;
    proxy_pass http://127.0.0.1:5005;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Keep Vue routes on the SPA fallback:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

Do not proxy backend API routes directly through root paths such as `/challenges`, `/me`, or `/auth` on this deployment. `/challenges` is also a Vue frontend route; proxying it directly caused `http://82.115.24.10/challenges` to return backend JSON instead of the Vue page.

Frontend VPS env:

```env
VITE_API_BASE=/api-proxy
VITE_BASE=/
```

Do not use:

```env
VITE_API_BASE=http://localhost:5005
```

In the browser, `localhost` means the user's own device, not the VPS.

Backend VPS env for the current HTTP/IP test deployment:

```env
FLASK_ENV=production
SECRET_KEY=<real_secret>
JWT_SECRET=<real_jwt_secret>
JWT_COOKIE_NAME=ringo_token
JWT_COOKIE_SECURE=0
JWT_COOKIE_SAMESITE=Lax
LOCAL_LOGIN_ENABLED=True
DB_PATH=/home/ringo/RingoStrike/backend/users.db
PUBLIC_BASE_URL=http://82.115.24.10
FRONTEND_BASE_URL=http://82.115.24.10
FRONTEND_ORIGIN=http://82.115.24.10
CORS_ORIGINS=http://82.115.24.10
```

Switch `JWT_COOKIE_SECURE=1` when the deployment moves to HTTPS.

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

VPS proxy smoke checks:

```bash
curl http://127.0.0.1/api-proxy/health
```

Expected:

```json
{"ok": true}
```

Login through the Nginx proxy:

```bash
curl -i -c cookies.txt -X POST http://127.0.0.1/api-proxy/auth/login \
  -H "Origin: http://82.115.24.10" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2","password":"test123456"}'
```

Then verify the authenticated cookie:

```bash
curl -i -b cookies.txt http://127.0.0.1/api-proxy/me \
  -H "Origin: http://82.115.24.10"
```

Expected: `200 OK` with authenticated user data.

Manual browser checks that passed after the `/api-proxy` fix:

- [ ] `/login` loads.
- [ ] Register works.
- [ ] Login works.
- [ ] Dashboard loads authenticated data.
- [ ] `/challenges` opens the Vue page, not backend JSON.
- [ ] Challenge list loads.
- [ ] Join challenge works.
- [ ] Check-in works.
- [ ] Logout works.
- [ ] API docs no longer hit localhost.
- [ ] Site works through the public IP when network access allows it.

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

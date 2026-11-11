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

## Release Order

1. Deploy the current **dev** commit to the VPS with the release bundle below.
2. QA on the live site (https://ringostrike.ir): the routes and API flows in "Post-Deployment Smoke Test", in EN and FA, desktop and phone.
3. Only after QA passes: merge dev -> main and tag `v0.9-beta` (#351).

---

## Release Bundle Deploy (the VPS has no GitHub access)

The VPS cannot reach GitHub and its worktree has manual, uncommitted changes, so **never `git pull` on the VPS**.
A release is a bundle built locally from the tracked files of one commit, uploaded by hand, and installed by
`deploy.sh`. Scripts: `scripts/release/build_bundle.sh`, `scripts/release/deploy.sh`, `scripts/release/rollback.sh`.

### 1. Build (local machine, Node 20+)

```bash
scripts/release/build_bundle.sh --commit origin/dev --out ~/ringo-release --musics ~/RingoStrike-main/frontend/public/Musics
```

- Builds in a temporary clean copy (`git archive`), never in the working directory, with `VITE_API_BASE=/api-proxy` and `VITE_BASE=/`.
- Fails if dist points at `localhost`, `127.0.0.1`, `:5005`, an IP inside a URL, or the old server IP. Two harmless
  `localhost` strings are allowed by exact text: the axios URL-parse fallback, and the guard in `frontend/src/lib/api.js`
  that rejects a loopback API base in production.
- Fails if the bundle contains `.env*`, a venv, `*.db`, `*.db.*`, `*.sqlite*`, `*backup*`, `cookies.txt`, `__pycache__`,
  `.git`, `backend/backups`, audio, or a value for `TELEGRAM_BOT_TOKEN=` / `JWT_SECRET=`.
- Output: `ringostrike-<sha>.tar.gz` + `.sha256` with `backend/` (no tests), `frontend/dist/`, `scripts/` (smoke test,
  reminder sender, release scripts), `VERSION`, and `MANIFEST.sha256` (a checksum per file).
- Music is optional and goes into its own `ringostrike-<sha>-musics.tar.gz`. The track list is fixed at build time, so
  pass `--musics` at build time and upload the music archive too. Without the music archive the focus view simply plays
  no music: a missing track fails quietly and the mute button is hidden; nothing else changes.

### 2. Upload and check (from the local machine)

Once, on the VPS: `mkdir -p /home/ringo/releases`. Then from the local machine:

```bash
scp ~/ringo-release/ringostrike-<sha>.tar.gz ~/ringo-release/ringostrike-<sha>.tar.gz.sha256 \
    ~/ringo-release/ringostrike-<sha>-musics.tar.gz ~/ringo-release/ringostrike-<sha>-musics.tar.gz.sha256 \
    ringo@<server>:/home/ringo/releases/
```

On the VPS, as `ringo`:

```bash
cd /home/ringo/releases && sha256sum -c ringostrike-<sha>.tar.gz.sha256 ringostrike-<sha>-musics.tar.gz.sha256
tar -xzOf ringostrike-<sha>.tar.gz ringostrike-<sha>/scripts/release/deploy.sh > deploy-<sha>.sh
```

### 3. Deploy (on the VPS, as ringo)

```bash
bash deploy-<sha>.sh --dry-run --musics ringostrike-<sha>-musics.tar.gz ringostrike-<sha>.tar.gz
bash deploy-<sha>.sh --musics ringostrike-<sha>-musics.tar.gz ringostrike-<sha>.tar.gz
```

What it does:

- Preflight: user is `ringo`, `backend/venv` and `backend/.env` exist, checksums match (archive and every file), free
  disk, and the DB path resolves the way the app resolves it. That is `DB_PATH` from `.env`, relative to the unit's
  `WorkingDirectory`, else `backend/users.db`.
- Preflight also checks that sudo allows exactly `systemctl restart ringostrike-backend`. If a password is needed, it
  asks once, before anything is created, moved or modified; if sudo fails, it stops and nothing has changed. The check
  runs again right before the code is moved.
- Online DB backup with the sqlite backup API plus `integrity_check`, into
  `/home/ringo/RingoDeployBackups/<time>-<sha>/` (mode 700). It stops if the backup fails.
- Moves the old backend code, `frontend/dist` and the release scripts into that folder. `.env`, `.env.*`, the venv,
  every `*.db*` / `*.sqlite*` file, `backups/` and `cookies.txt` stay in place.
- Installs the bundle and writes `/home/ringo/RingoStrike/RELEASE_VERSION`, which records the deployed commit because
  the server's git HEAD no longer tells.
- Runs `pip install -r requirements.txt` only if a requirement is missing (it is unchanged since 356785d), before any
  code is moved.
- `sudo systemctl restart ringostrike-backend`, then waits for a healthy **new** process: MainPID changed, the port is
  held by that PID, and this stays stable for 5 s.
- Runs `scripts/vps_smoke_test.sh` with `PUBLIC_BASE_URL=https://ringostrike.ir` and prints the exact rollback commands.
- It never edits `.env` or the DB file, and never runs git. No nginx reload is needed, because dist is static and the
  folder keeps its path.

### 4. Rollback

```bash
bash /home/ringo/RingoDeployBackups/<time>-<sha>/rollback.sh /home/ringo/RingoDeployBackups/<time>-<sha>
```

- Restores the previous backend code, dist and scripts. The DB stays: the upgrade only adds tables, columns and rows,
  and the previous code (356785d) was rehearsed on the upgraded DB with no change.
- `--restore-db` also puts back the pre-deploy DB, after you type `RESTORE`. **Every write made after the deploy is
  lost.** The current DB is saved first to `db-before-rollback-<time>/`.
- Nothing is deleted. The rolled-back release is kept in `rolled-back-<time>/`.

### Manual `.env` changes before this deploy (Amir, on the VPS)

Change these by hand. The scripts never touch `.env`.

| Key | Target |
| --- | --- |
| `PUBLIC_BASE_URL` | `https://ringostrike.ir` |
| `FRONTEND_BASE_URL` | `https://ringostrike.ir` |
| `FRONTEND_ORIGIN` | `https://ringostrike.ir` |
| `JWT_COOKIE_SECURE` | `1` (the site is HTTPS) |
| `FLAS_DEBUG` | rename the key to `FLASK_DEBUG`, value `0` |
| `DB_PATH` | absolute: `/home/ringo/RingoStrike/backend/users.db` (a relative path resolves from the unit's working directory) |

- **JWT_COOKIE_SECURE parsing:** the auth cookie is set in `backend/auth.py` with `os.getenv("JWT_COOKIE_SECURE", "0") == "1"`.
  Only the exact value `1` makes the cookie Secure; `true` or `yes` do not. (`config.py` and `/health` accept
  1/true/yes/on, so `/health` can say secure while the cookie is not. Use `1`.)
- **FLAS_DEBUG typo:** harmless today. The code reads `FLASK_DEBUG` (default `0`), so debug and the reloader are off.
  Rename it so the file says what the code reads.
- **How the URL keys are used:** the CORS allow-list is the localhost defaults plus `CORS_ORIGINS`, `FRONTEND_ORIGIN`
  and `FRONTEND_BASE_URL` (comma-separated). `PUBLIC_BASE_URL` and `FRONTEND_*` otherwise appear only in `/health`. No
  cookie Domain is set. Telegram links are `https://t.me/<bot>?start=<code>`. The site is same-origin through
  `/api-proxy`, so CORS hardly matters, but keep the https values. Add `https://www.ringostrike.ir` to `CORS_ORIGINS`
  only if `www` serves the site.
- **New env vars since 356785d:** none (backend and frontend).
- `FLASK_ENV=production` keeps `/debug/sqlite/*` closed (403) and makes `SECRET_KEY` / `JWT_SECRET` required.

### Cloudflare in front

- SSL/TLS mode **Full (strict)**: Cloudflare -> nginx over HTTPS with a valid origin certificate (a Cloudflare Origin CA
  certificate on nginx is fine). Do not use Flexible: the origin would be plain HTTP.
- After the deploy, check that `https://ringostrike.ir/api-proxy/health` returns `{"ok": true}` in a browser. The smoke
  test decides on the origin (the backend on 127.0.0.1:5005, and nginx through
  `curl --resolve ringostrike.ir:443:127.0.0.1 -k`). The check through Cloudflare is only a warning, so a challenge
  page there cannot fail a healthy deploy (`PUBLIC_STRICT=1` makes it critical).

### Reminders in production

- The backend has **no scheduler, thread or timer**. Reminders are sent only when something calls
  `POST /api/telegram/remind-due-missions` with the header `X-Reminder-Token: <REMINDER_ADMIN_TOKEN>`, or runs
  `scripts/send_telegram_reminders.py --due-missions` on the VPS. The backend then calls `api.telegram.org`.
- On the VPS this needs one of: an n8n schedule (docs/REMINDER_AUTOMATION_RUNBOOK.md), or a cron / systemd timer, for
  example every 5 minutes as `ringo`:
  `cd /home/ringo/RingoStrike && backend/venv/bin/python scripts/send_telegram_reminders.py --due-missions`
- The VPS must be able to reach `api.telegram.org`. Check with `curl -sS -o /dev/null -w '%{http_code}\n' https://api.telegram.org`.
- `POST /api/telegram/test-reminder` has **no auth** and sends to `TELEGRAM_TEST_CHAT_ID` (it exists since before 356785d).
  Leave `TELEGRAM_TEST_CHAT_ID` empty in production until that route is protected.

---

## Backend Environment

Required backend environment file:

```txt
backend/.env
```

Required values:

- [ ] `FLASK_ENV`
- [ ] `FLASK_HOST`
- [ ] `PORT`
- [ ] `FLASK_DEBUG`
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
- [ ] `REMINDER_ADMIN_TOKEN`
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
- [ ] Display-name cleanup (#418), once, after the backup above: save every name containing "@" to a `name_cleanup_backup` table (only rows not already saved), then set those names to the username. It is idempotent, so a second run changes nothing. Rollback restores each saved name from `name_cleanup_backup`. The exact SQL is in the #418 PR body.

---

## Backend Deployment

- [ ] Install Python version compatible with project.
- [ ] Create virtual environment.
- [ ] Install `backend/requirements.txt`.
- [ ] Configure `.env`.
- [ ] Confirm `FLASK_HOST=127.0.0.1`, `PORT=5005`, and `FLASK_DEBUG=0` for production-like VPS usage.
- [ ] Install the release bundle on the VPS with `deploy.sh` (see "Release Bundle Deploy"; never `git pull` there).
- [ ] Restart the backend through `systemd`.
- [ ] Run backend health check.
- [ ] Confirm auth endpoints.
- [ ] Confirm protected endpoints reject unauthenticated requests.
- [ ] Confirm cookie settings for production HTTPS.
- [ ] Confirm CORS/frontend origin behavior.
- [ ] Confirm n8n/cron can call `POST /api/telegram/remind-due-missions` with `X-Reminder-Token`.
- [ ] Confirm reminder diagnostics can be read with `GET /api/telegram/reminder-diagnostics` and `X-Reminder-Token`.
- [ ] Confirm the n8n server runtime follows `docs/REMINDER_AUTOMATION_RUNBOOK.md` and keeps n8n data/secrets outside the repository.

Health check:

```bash
curl http://127.0.0.1:5005/health
```

Systemd commands:

```bash
sudo systemctl status ringostrike-backend
sudo systemctl restart ringostrike-backend
sudo journalctl -u ringostrike-backend -f
```

---

## Frontend Deployment

- [ ] Install Node.js compatible with project.
- [ ] Install dependencies.
- [ ] Copy the focus music into `frontend/public/Musics/` **before** the build (audio is not in git;
      the track list is fixed at build time). See `docs/FOCUS_MEDIA.md`.
- [ ] Build frontend.
- [ ] Confirm generated `dist/`.
- [ ] Serve frontend from correct root/subpath.
- [ ] Confirm the current VPS build uses `VITE_API_BASE=/api-proxy`.
- [ ] Confirm production builds do not contain `VITE_API_BASE=http://localhost:5005`.
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

Use a dedicated API proxy prefix. Do not use nginx `rewrite` rules for this deployment. The trailing slash on `proxy_pass` strips the `/api-proxy/` location prefix and forwards the remaining backend path to Flask:

```nginx
location /api-proxy/ {
    proxy_pass http://127.0.0.1:5005/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
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
FLASK_HOST=127.0.0.1
PORT=5005
FLASK_DEBUG=0
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
REMINDER_ADMIN_TOKEN=<real_admin_token_for_n8n_and_bot_bridge>
```

Switch `JWT_COOKIE_SECURE=1` when the deployment moves to HTTPS. The site is now HTTPS behind Cloudflare: see
"Manual `.env` changes before this deploy" for the current target values (https://ringostrike.ir, the exact value `1`).

---

## Post-Deployment Smoke Test

Run the operator smoke script after a deploy (`deploy.sh` runs it for you), restarting the backend, or changing nginx/backend env.
Its default public URL is still the old IP, so pass the domain:

```bash
PUBLIC_BASE_URL=https://ringostrike.ir bash scripts/vps_smoke_test.sh
```

Override the public base URL when testing another host:

```bash
PUBLIC_BASE_URL=http://example.com bash scripts/vps_smoke_test.sh
```

The script is read-only. It defaults to `PUBLIC_BASE_URL=https://ringostrike.ir`.

- **Critical** (exit non-zero): the systemd unit is active; the backend `/health` on `127.0.0.1:5005`; the origin `/api-proxy/health` through nginx, as `https://ringostrike.ir` resolved to 127.0.0.1 (`--resolve ... -k`), else `http://127.0.0.1/api-proxy`; `REMINDER_ADMIN_TOKEN` is present; the reminder dry-run and the reminder diagnostics, both called **on the backend directly**, so the token never leaves the server.
- **Warning only:** `/api-proxy/health` through Cloudflare (`PUBLIC_STRICT=1` makes it critical); the backend bound to `127.0.0.1:5005`.

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
curl http://82.115.24.10/api-proxy/health
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

Reminder automation smoke checks:

```bash
TOKEN=$(grep REMINDER_ADMIN_TOKEN /home/ringo/RingoStrike/backend/.env | cut -d '=' -f2)

curl -X POST http://82.115.24.10/api-proxy/api/telegram/remind-due-missions \
  -H "Content-Type: application/json" \
  -H "X-Reminder-Token: $TOKEN" \
  -d '{"dry_run": true}'

curl -H "X-Reminder-Token: $TOKEN" \
  "http://82.115.24.10/api-proxy/api/telegram/reminder-diagnostics"
```

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
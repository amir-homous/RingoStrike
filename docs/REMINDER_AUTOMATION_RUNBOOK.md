# Reminder Automation Runbook

## Purpose

This runbook documents the current mission-level Telegram reminder automation path for RingoStrike and the production-like VPS shape for running n8n.

The backend remains the source of truth for reminder selection, Telegram delivery, duplicate prevention, and diagnostics. n8n should trigger backend endpoints; it should not duplicate Telegram sending logic.

## Runtime Shape

```txt
n8n schedule
  -> POST /api-proxy/api/telegram/remind-due-missions
  -> Flask reminder service
  -> existing Telegram service
  -> mission_logs.reminder_sent_at duplicate-prevention marker
```

The action endpoint and diagnostics endpoint are protected with:

```http
X-Reminder-Token: <REMINDER_ADMIN_TOKEN>
```

Do not expose `REMINDER_ADMIN_TOKEN`, `TELEGRAM_BOT_TOKEN`, JWT secrets, cookies, or raw bot configuration in logs or frontend code.

## Server Runtime Options

Use one of these server runtime patterns. Both keep user reminder delivery backend-owned.

### Option A: Managed n8n

Use this when n8n is hosted outside the VPS.

- Create a schedule workflow in the managed n8n workspace.
- Call the VPS public nginx route:

```http
POST http://82.115.24.10/api-proxy/api/telegram/remind-due-missions
```

- Store `REMINDER_ADMIN_TOKEN` in n8n credentials or encrypted workflow variables.
- Do not store backend JWT secrets, database paths, or Telegram bot tokens in n8n.

### Option B: VPS n8n Service

Use this when n8n should run on the same VPS as RingoStrike.

Recommended properties:

- Bind n8n to localhost or protect it behind nginx/auth.
- Keep n8n data outside the git repository.
- Store n8n secrets in a server-only env file.
- Let n8n call the same public `/api-proxy` endpoint or the local nginx endpoint.

Example server paths:

```txt
/opt/ringostrike-n8n/
  .env
  docker-compose.yml
  data/
```

Example `.env`:

```env
N8N_HOST=127.0.0.1
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_ENCRYPTION_KEY=<real_n8n_encryption_key>
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=<admin_user>
N8N_BASIC_AUTH_PASSWORD=<real_admin_password>
GENERIC_TIMEZONE=Asia/Tehran
REMINDER_ADMIN_TOKEN=<same_value_as_backend_REMINDER_ADMIN_TOKEN>
RINGOSTRIKE_BASE_URL=http://127.0.0.1
```

Example `docker-compose.yml`:

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:5678:5678"
    env_file:
      - .env
    volumes:
      - ./data:/home/node/.n8n
```

Start or restart n8n:

```bash
cd /opt/ringostrike-n8n
docker compose up -d
docker compose logs -f n8n
```

If Docker Compose is not available on the VPS, run n8n as a `systemd` service only after Node.js and n8n installation are explicitly managed outside this repository.

## Action Endpoint

Backend route:

```http
POST /api/telegram/remind-due-missions
```

Current VPS public route through nginx:

```http
POST /api-proxy/api/telegram/remind-due-missions
```

Behavior:

- selects `mission_logs.status = "remind_later"` with `reminder_at <= now`
- ignores logs where `reminder_sent_at` is already set
- requires active enrollment, active challenge, and active mission rows
- sends through `backend/services/telegram_service.py`
- skips users without a connected Telegram chat
- skips users with reminders disabled
- supports `dry_run`
- sets `mission_logs.reminder_sent_at` only after successful Telegram send

Dry-run:

```bash
TOKEN=$(grep REMINDER_ADMIN_TOKEN /home/ringo/RingoStrike/backend/.env | cut -d '=' -f2)

curl -X POST http://82.115.24.10/api-proxy/api/telegram/remind-due-missions \
  -H "Content-Type: application/json" \
  -H "X-Reminder-Token: $TOKEN" \
  -d '{"dry_run": true}'
```

Real run:

```bash
curl -X POST http://82.115.24.10/api-proxy/api/telegram/remind-due-missions \
  -H "Content-Type: application/json" \
  -H "X-Reminder-Token: $TOKEN" \
  -d '{"dry_run": false, "limit": 20}'
```

## Diagnostics Endpoint

Backend route:

```http
GET /api/telegram/reminder-diagnostics
```

Current VPS public route through nginx:

```http
GET /api-proxy/api/telegram/reminder-diagnostics
```

Purpose:

- inspect reminder state without sending Telegram messages
- show due reminders
- show scheduled future reminders
- show already sent reminders
- show missing Telegram connection state
- show reminders-disabled state
- show recent reminder logs
- include summary counts and server time

Example:

```bash
curl -H "X-Reminder-Token: $TOKEN" \
  "http://82.115.24.10/api-proxy/api/telegram/reminder-diagnostics"
```

With recent limit:

```bash
curl -H "X-Reminder-Token: $TOKEN" \
  "http://82.115.24.10/api-proxy/api/telegram/reminder-diagnostics?recent_limit=10"
```

Diagnostics must not expose:

- Telegram bot token
- admin reminder token
- JWT secrets
- cookies
- raw Telegram chat IDs
- raw bot configuration
- private credentials

## Recommended n8n Flow

```txt
Schedule trigger every 5 minutes
  -> POST /api-proxy/api/telegram/remind-due-missions
  -> IF sent/skipped/failed > 0
  -> GET /api-proxy/api/telegram/reminder-diagnostics
  -> Admin Telegram summary
```

Endpoint distinction:

```txt
/remind-due-missions = action endpoint
/reminder-diagnostics = visibility/debug endpoint
```

The backend should send user Telegram messages. n8n should trigger the backend job and optionally send a separate admin summary.

Minimum HTTP request node settings:

- Method: `POST`
- URL: `{{$env.RINGOSTRIKE_BASE_URL}}/api-proxy/api/telegram/remind-due-missions`
- Header: `X-Reminder-Token: {{$env.REMINDER_ADMIN_TOKEN}}`
- Header: `Content-Type: application/json`
- Body: `{"dry_run": false, "limit": 20}`

Run a dry-run workflow first with:

```json
{"dry_run": true, "limit": 20}
```

## Duplicate Prevention

`mission_logs.reminder_sent_at` is the delivery marker for mission-level Telegram reminders.

Rules:

- `reminder_sent_at` starts as `NULL`
- the delivery job skips rows where `reminder_sent_at` is already set
- `reminder_sent_at` is set only after successful Telegram send
- dry-run does not set `reminder_sent_at`
- when a mission reminder is changed or replanned, `mission_service` clears `reminder_sent_at` so the new reminder can be delivered later

## Health Checks

Direct backend:

```bash
curl http://127.0.0.1:5005/health
```

Local nginx proxy:

```bash
curl http://127.0.0.1/api-proxy/health
```

Public proxy:

```bash
curl http://82.115.24.10/api-proxy/health
```

n8n container:

```bash
cd /opt/ringostrike-n8n
docker compose ps
docker compose logs --tail=100 n8n
```

## VPS Smoke Test

After deployment, backend restart, nginx changes, reminder env changes, or n8n workflow changes, run:

```bash
bash scripts/vps_smoke_test.sh
```

Override the public host when needed:

```bash
PUBLIC_BASE_URL=http://example.com bash scripts/vps_smoke_test.sh
```

The smoke script is read-only. It checks systemd backend status, direct backend health, local/public `/api-proxy` health, backend bind address, `REMINDER_ADMIN_TOKEN` presence, reminder dry-run, and reminder diagnostics.

The smoke script performs a reminder dry-run only. It must not send real Telegram reminders.

## Server Deployment Checklist

- [ ] Backend `.env` has `REMINDER_ADMIN_TOKEN`.
- [ ] Backend `.env` has `TELEGRAM_BOT_TOKEN` when Telegram delivery is enabled.
- [ ] Backend is running through `systemd`.
- [ ] Nginx `/api-proxy/` forwards to Flask with a trailing slash on `proxy_pass`.
- [ ] n8n is installed through managed hosting or a VPS service.
- [ ] n8n stores `REMINDER_ADMIN_TOKEN` outside the workflow JSON when possible.
- [ ] n8n dry-run returns a successful backend response.
- [ ] n8n real run is tested with a low `limit`.
- [ ] Reminder diagnostics are checked after the first real run.
- [ ] No user Telegram delivery logic is duplicated inside n8n.
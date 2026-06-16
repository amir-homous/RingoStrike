# Reminder Automation Runbook

## Purpose

This runbook covers the current backend-owned mission reminder automation path.

n8n should trigger the backend. It should not duplicate Telegram sending logic or send user Telegram messages directly.

## Protected Endpoints

Action endpoint:

```http
POST /api/telegram/remind-due-missions
```

Current VPS public URL:

```http
POST /api-proxy/api/telegram/remind-due-missions
```

Diagnostics endpoint:

```http
GET /api/telegram/reminder-diagnostics
```

Current VPS public URL:

```http
GET /api-proxy/api/telegram/reminder-diagnostics
```

Both endpoints require:

```http
X-Reminder-Token: <REMINDER_ADMIN_TOKEN>
```

Never print or expose `REMINDER_ADMIN_TOKEN`, `TELEGRAM_BOT_TOKEN`, JWT secrets, cookies, or raw bot configuration.

## Delivery Behavior

`POST /api/telegram/remind-due-missions`:

- selects due mission reminders
- sends through the existing Telegram service
- skips users without a connected Telegram chat
- skips users with reminders disabled
- supports `dry_run`
- sets `mission_logs.reminder_sent_at` only after successful send
- does not resend already-sent reminders

Dry-run:

```bash
TOKEN=$(grep REMINDER_ADMIN_TOKEN /home/ringo/RingoStrike/backend/.env | cut -d '=' -f2)

curl -X POST http://82.115.24.10/api-proxy/api/telegram/remind-due-missions \
  -H "Content-Type: application/json" \
  -H "X-Reminder-Token: $TOKEN" \
  -d '{"dry_run": true}'
```

Diagnostics:

```bash
curl -H "X-Reminder-Token: $TOKEN" \
  "http://82.115.24.10/api-proxy/api/telegram/reminder-diagnostics"
```

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

## VPS Smoke Test

After deployment, backend restart, nginx changes, or reminder env changes, run:

```bash
bash scripts/vps_smoke_test.sh
```

Override the public host when needed:

```bash
PUBLIC_BASE_URL=http://example.com bash scripts/vps_smoke_test.sh
```

The smoke script performs a reminder dry-run only. It must not send real Telegram reminders.


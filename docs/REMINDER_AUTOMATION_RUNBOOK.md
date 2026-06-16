# Reminder Automation Runbook

## Purpose

This runbook documents the current mission-level Telegram reminder automation path for RingoStrike.

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


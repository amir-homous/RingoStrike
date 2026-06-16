# Backend Systemd Runbook

## Purpose

This document explains how the RingoStrike backend is managed on the VPS using `systemd`.

The backend should be managed through `systemd` in production-like environments instead of running manually inside a terminal or tmux session. This prevents the backend from stopping when SSH or Termius disconnects.

## Service name

```bash id="eo95o8"
ringostrike-backend
```

## Project path

```bash id="w6znz5"
/home/ringo/RingoStrike/backend
```

## Backend entrypoint

```bash id="klvy4v"
/home/ringo/RingoStrike/backend/app.py
```

## Python environment

```bash id="c8py1b"
/home/ringo/RingoStrike/backend/venv
```

## Runtime environment

`backend/app.py` reads its runtime binding from environment variables:

```env
FLASK_HOST=127.0.0.1
PORT=5005
FLASK_DEBUG=0
```

Use those values for production-like VPS usage so Flask is bound only to localhost and public access goes through nginx `/api-proxy`.

Local development may use:

```env
FLASK_HOST=0.0.0.0
PORT=5005
FLASK_DEBUG=1
```

Never commit a real `backend/.env`; keep secrets such as `SECRET_KEY`, `JWT_SECRET`, `TELEGRAM_BOT_TOKEN`, and `REMINDER_ADMIN_TOKEN` only on the server or local developer machine.

## Start backend

```bash id="joa50a"
sudo systemctl start ringostrike-backend
```

## Stop backend

```bash id="jllq43"
sudo systemctl stop ringostrike-backend
```

## Restart backend

Use this after backend code changes, `.env` changes, dependency changes, or deployment updates.

```bash id="gyoz91"
sudo systemctl restart ringostrike-backend
```

## Check backend status

```bash id="zycmwc"
sudo systemctl status ringostrike-backend
```

## View live logs

```bash id="g9wt7m"
sudo journalctl -u ringostrike-backend -f
```

## Health checks

Direct backend health check:

```bash id="el923h"
curl http://127.0.0.1:5005/health
```

Nginx local proxy health check:

```bash id="2k7g83"
curl http://127.0.0.1/api-proxy/health
```

Public proxy health check:

```bash id="nr93mx"
curl http://82.115.24.10/api-proxy/health
```

## Reminder dry-run test

```bash id="yngmzb"
TOKEN=$(grep REMINDER_ADMIN_TOKEN /home/ringo/RingoStrike/backend/.env | cut -d '=' -f2)

curl -X POST http://82.115.24.10/api-proxy/api/telegram/remind-due-missions \
  -H "Content-Type: application/json" \
  -H "X-Reminder-Token: $TOKEN" \
  -d '{"dry_run": true}'
```

## Reminder diagnostics

Use this to inspect due, future, sent, missing-Telegram, and reminders-disabled mission reminder state without sending anything:

```bash id="kq9reu"
curl -H "X-Reminder-Token: $TOKEN" \
  "http://82.115.24.10/api-proxy/api/telegram/reminder-diagnostics"
```

## Important rule

Do not run the backend manually with:

```bash id="f2jfkx"
python app.py
```

while the systemd service is active.

If manual testing is needed, first stop the service:

```bash id="lh597a"
sudo systemctl stop ringostrike-backend
```

Then run manually only for short debugging sessions.

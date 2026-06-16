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

## Full VPS smoke test

Run this after deployments, backend restarts, nginx changes, or backend `.env` changes:

```bash id="he5ew3"
bash scripts/vps_smoke_test.sh
```

Override defaults when testing another host or service name:

```bash id="gv2ps9"
PUBLIC_BASE_URL=http://example.com bash scripts/vps_smoke_test.sh
```

The script checks:

- `systemctl is-active ringostrike-backend`
- direct backend `/health`
- local nginx `/api-proxy/health`
- public nginx `/api-proxy/health`
- whether port `5005` appears bound to localhost or a public interface
- `REMINDER_ADMIN_TOKEN` presence without printing it
- reminder dry-run
- reminder diagnostics

The backend binding check is a warning when it cannot confirm localhost-only binding. Critical service, health, token, and reminder endpoint failures exit non-zero.

## Reminder dry-run test

```bash id="yngmzb"
TOKEN=$(grep REMINDER_ADMIN_TOKEN /home/ringo/RingoStrike/backend/.env | cut -d '=' -f2)

curl -X POST http://82.115.24.10/api-proxy/api/telegram/remind-due-missions \
  -H "Content-Type: application/json" \
  -H "X-Reminder-Token: $TOKEN" \
  -d '{"dry_run": true}'
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

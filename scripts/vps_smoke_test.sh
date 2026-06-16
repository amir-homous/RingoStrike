#!/usr/bin/env bash
set -u

APP_ROOT="${APP_ROOT:-/home/ringo/RingoStrike}"
BACKEND_DIR="${BACKEND_DIR:-$APP_ROOT/backend}"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:5005}"
LOCAL_PROXY_URL="${LOCAL_PROXY_URL:-http://127.0.0.1/api-proxy}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://82.115.24.10}"
SERVICE_NAME="${SERVICE_NAME:-ringostrike-backend}"

BACKEND_URL="${BACKEND_URL%/}"
LOCAL_PROXY_URL="${LOCAL_PROXY_URL%/}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL%/}"
PUBLIC_PROXY_URL="$PUBLIC_BASE_URL/api-proxy"
ENV_FILE="$BACKEND_DIR/.env"

failures=0
warnings=0

print_ok() {
  printf '✅ %s\n' "$1"
}

print_warn() {
  warnings=$((warnings + 1))
  printf '⚠️  %s\n' "$1"
}

print_fail() {
  failures=$((failures + 1))
  printf '❌ %s\n' "$1"
}

try_line() {
  printf '   Try: %s\n' "$1"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    print_fail "required command not found: $1"
    try_line "sudo apt-get update && sudo apt-get install -y $2"
    return 1
  fi

  return 0
}

has_ok_true() {
  printf '%s' "$1" | grep -Eq '"ok"[[:space:]]*:[[:space:]]*true'
}

check_json_ok_url() {
  local label="$1"
  local url="$2"
  local response

  if ! response="$(curl -fsS --max-time 12 "$url" 2>/dev/null)"; then
    print_fail "$label failed"
    return 1
  fi

  if has_ok_true "$response"; then
    print_ok "$label ok"
    return 0
  fi

  print_fail "$label did not return ok:true"
  return 1
}

read_reminder_token() {
  if [ ! -f "$ENV_FILE" ]; then
    return 1
  fi

  awk -F= '
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*REMINDER_ADMIN_TOKEN[[:space:]]*=/ {
      value = $0
      sub(/^[^=]*=/, "", value)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      gsub(/^["'\'']|["'\'']$/, "", value)
      print value
      exit
    }
  ' "$ENV_FILE"
}

check_systemd() {
  if ! require_command systemctl systemd; then
    return
  fi

  if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    print_ok "systemd service active"
  else
    print_fail "backend service is not active"
    try_line "sudo systemctl status $SERVICE_NAME"
  fi
}

check_backend_binding() {
  local port="5005"
  local output=""

  if command -v ss >/dev/null 2>&1; then
    output="$(ss -ltn 2>/dev/null | grep ":$port" || true)"
  elif command -v netstat >/dev/null 2>&1; then
    output="$(netstat -ltn 2>/dev/null | grep ":$port" || true)"
  else
    print_warn "could not inspect backend binding; ss/netstat not found"
    return
  fi

  if printf '%s\n' "$output" | grep -Eq '127\.0\.0\.1:5005|localhost:5005'; then
    print_ok "backend bound to 127.0.0.1:5005"
    return
  fi

  if printf '%s\n' "$output" | grep -Eq '0\.0\.0\.0:5005|\*:5005|\[::\]:5005|:::5005'; then
    print_warn "backend appears publicly bound on port 5005"
    try_line "confirm FLASK_HOST=127.0.0.1 in $ENV_FILE and restart $SERVICE_NAME"
    return
  fi

  print_warn "could not confirm backend binding on port 5005"
  try_line "ss -ltn | grep ':5005'"
}

check_reminder_dry_run() {
  local token="$1"
  local response

  if ! response="$(
    curl -fsS --max-time 20 \
      -X POST "$PUBLIC_PROXY_URL/api/telegram/remind-due-missions" \
      -H "Content-Type: application/json" \
      -H "X-Reminder-Token: $token" \
      -d '{"dry_run": true}' 2>/dev/null
  )"; then
    print_fail "reminder dry-run failed"
    try_line "check REMINDER_ADMIN_TOKEN and backend logs with sudo journalctl -u $SERVICE_NAME -f"
    return 1
  fi

  if has_ok_true "$response"; then
    print_ok "reminder dry-run ok"
    return 0
  fi

  print_fail "reminder dry-run did not return ok:true"
  return 1
}

check_reminder_diagnostics() {
  local token="$1"
  local response

  if ! response="$(
    curl -fsS --max-time 20 \
      -H "X-Reminder-Token: $token" \
      "$PUBLIC_PROXY_URL/api/telegram/reminder-diagnostics" 2>/dev/null
  )"; then
    print_fail "reminder diagnostics failed"
    try_line "check REMINDER_ADMIN_TOKEN and backend logs with sudo journalctl -u $SERVICE_NAME -f"
    return 1
  fi

  if has_ok_true "$response"; then
    print_ok "reminder diagnostics ok"
    return 0
  fi

  print_fail "reminder diagnostics did not return ok:true"
  return 1
}

main() {
  printf 'RingoStrike VPS smoke test\n'
  printf 'Service: %s\n' "$SERVICE_NAME"
  printf 'Backend: %s\n' "$BACKEND_URL"
  printf 'Local proxy: %s\n' "$LOCAL_PROXY_URL"
  printf 'Public proxy: %s\n\n' "$PUBLIC_PROXY_URL"

  require_command curl curl || true

  check_systemd
  check_json_ok_url "backend /health" "$BACKEND_URL/health"
  check_json_ok_url "local api-proxy /health" "$LOCAL_PROXY_URL/health"
  if ! check_json_ok_url "public api-proxy /health" "$PUBLIC_PROXY_URL/health"; then
    try_line "sudo nginx -t && sudo systemctl status nginx"
  fi
  check_backend_binding

  local token
  token="$(read_reminder_token || true)"

  if [ -z "${token:-}" ]; then
    print_fail "REMINDER_ADMIN_TOKEN missing in $ENV_FILE"
    try_line "add REMINDER_ADMIN_TOKEN to $ENV_FILE and restart $SERVICE_NAME"
  else
    print_ok "REMINDER_ADMIN_TOKEN found"
    check_reminder_dry_run "$token"
    check_reminder_diagnostics "$token"
  fi

  printf '\n'
  if [ "$failures" -gt 0 ]; then
    printf 'Smoke test failed: %s failure(s), %s warning(s).\n' "$failures" "$warnings"
    exit 1
  fi

  if [ "$warnings" -gt 0 ]; then
    printf 'Smoke test passed with %s warning(s).\n' "$warnings"
    exit 0
  fi

  printf 'Smoke test passed.\n'
}

main "$@"

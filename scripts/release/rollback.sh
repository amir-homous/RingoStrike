#!/bin/bash
# Roll back a RingoStrike deploy made by deploy.sh. Run as user "ringo".
#
# Usage: bash <backup-dir>/rollback.sh <backup-dir> [--dry-run] [--restore-db]
#   <backup-dir>   the folder deploy.sh printed (e.g. /home/ringo/RingoDeployBackups/20261112-090000-7e87f21)
#   --restore-db   ALSO put back the DB taken just before the deploy.
#                  WARNING: every write made after the deploy (check-ins, missions, sign-ups) is LOST.
#                  The current DB is saved first to <backup-dir>/db-before-rollback-<time>/.
#                  Not needed for a normal rollback: the deploy only ADDS tables/columns/rows and the
#                  previous code runs on the upgraded DB (rehearsed in Gate 0).
#
# Nothing is deleted: the code being rolled back is moved to <backup-dir>/rolled-back-<time>/.
# sudo is used only for: systemctl restart <service>
set -euo pipefail

BK=""
DRY_RUN=0
RESTORE_DB=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --restore-db) RESTORE_DB=1; shift ;;
    -h|--help) sed -n 2,15p "$0"; exit 0 ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) BK="$1"; shift ;;
  esac
done

say() { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
die() { printf '\nROLLBACK STOPPED: %s\n' "$*" >&2; exit 1; }

[ -n "$BK" ] || die "give the backup folder: bash rollback.sh <backup-dir> [--restore-db]"
BK="$(cd "$BK" && pwd)"
[ -f "$BK/DEPLOY_INFO" ] && [ -f "$BK/installed_backend.txt" ] && [ -d "$BK/code/backend" ] \
  || die "$BK is not a complete deploy backup (DEPLOY_INFO, installed_backend.txt, code/backend)"
info() { awk -F= -v k="$1" '$1==k {sub(/^[^=]*=/, ""); print; exit}' "$BK/DEPLOY_INFO"; }
APP_DIR="$(info app_dir)"; DB_FILE="$(info db_file)"; SERVICE_NAME="$(info service)"
BACKEND="$APP_DIR/backend"; DIST="$APP_DIR/frontend/dist"; VENV_PY="$BACKEND/venv/bin/python"
[ "$(id -un)" = "ringo" ] || die "run as user ringo (now: $(id -un))"
[ -x "$VENV_PY" ] || die "venv python not found: $VENV_PY"

# A healthy NEW backend: MainPID changed, the unit is active, /health is ok, the process listening on the
# port IS that MainPID (when ss can tell), and all of this still holds STABLE_SECONDS later.
# (A new process that cannot bind dies after a second or two; an old one holding the port would answer /health.)
STABLE_SECONDS="${STABLE_SECONDS:-5}"
listener_pid() { ss -ltnpH "sport = :$1" 2>/dev/null | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2; }
healthy_new() {  # $1 old pid, $2 port; sets NEW_PID
  NEW_PID="$(systemctl show -p MainPID --value "$SERVICE_NAME" 2>/dev/null || echo 0)"
  [ "${NEW_PID:-0}" != 0 ] && [ "$NEW_PID" != "$1" ] || return 1
  systemctl is-active --quiet "$SERVICE_NAME" || return 1
  curl -fsS --max-time 2 "http://127.0.0.1:$2/health" 2>/dev/null | grep -Eq '"ok"[[:space:]]*:[[:space:]]*true' || return 1
  local lp; lp="$(listener_pid "$2")"
  [ -z "$lp" ] || [ "$lp" = "$NEW_PID" ] || { LISTENER_MISMATCH="$lp"; return 1; }
}
wait_healthy_new() {  # $1 old pid, $2 port, $3 timeout (seconds)
  local first="" stable=0
  for _ in $(seq 1 "$3"); do
    if healthy_new "$1" "$2"; then
      if [ "$NEW_PID" = "$first" ]; then stable=$((stable + 1)); else first="$NEW_PID"; stable=0; fi
      [ "$stable" -ge "$STABLE_SECONDS" ] && return 0
    else
      first=""; stable=0
    fi
    sleep 1
  done
  return 1
}

DB_BK="$BK/db/$(basename "$DB_FILE")"
step "Rollback plan$([ $DRY_RUN = 1 ] && echo ' (dry run: nothing will be changed)')"
say "app:      $APP_DIR"
say "from:     $(info new_commit)"
say "back to:  $(info previous_release)"
say "code:     $(wc -l <"$BK/installed_backend.txt") backend item(s) installed by the deploy are moved aside; the previous ones come back"
say "dist:     $([ -d "$BK/code/frontend/dist" ] && echo 'previous frontend/dist comes back' || echo 'no previous dist in the backup')"
if [ "$RESTORE_DB" = 1 ]; then
  [ -f "$DB_BK" ] || die "DB backup not found: $DB_BK"
  (cd "$BK/db" && sha256sum -c --status "$(basename "$DB_BK").sha256") || die "DB backup checksum does NOT match"
  say "DB:       RESTORE $DB_BK -> $DB_FILE"
  say ""
  say "WARNING: restoring the DB loses EVERY write made after the deploy ($(info deployed_at) UTC)."
else
  say "DB:       not touched"
fi
[ "$DRY_RUN" = 1 ] && { step "Dry run finished: nothing was changed"; exit 0; }

if [ "$RESTORE_DB" = 1 ]; then
  printf 'Type RESTORE to confirm the DB restore: '
  read -r answer
  [ "$answer" = "RESTORE" ] || die "not confirmed; nothing was changed"
fi

TS="$(date -u +%Y%m%d-%H%M%S)"
OUT="$BK/rolled-back-$TS"
umask 077
mkdir -p "$OUT/backend" "$OUT/frontend" "$OUT/scripts"

step "Restore code"
while IFS= read -r b; do
  [ -n "$b" ] || continue
  case "$b" in */*|.|..) die "bad name in installed_backend.txt: $b" ;; esac
  [ -e "$BACKEND/$b" ] && mv "$BACKEND/$b" "$OUT/backend/$b"
done <"$BK/installed_backend.txt"
for f in "$BK"/code/backend/* "$BK"/code/backend/.[!.]*; do
  [ -e "$f" ] || continue
  b="$(basename "$f")"
  [ -e "$BACKEND/$b" ] && die "backend/$b already exists; stopping before overwriting it (moved items are in $OUT)"
  mv "$f" "$BACKEND/$b"
done
if [ -d "$BK/code/frontend/dist" ]; then
  [ -d "$DIST" ] && mv "$DIST" "$OUT/frontend/dist"
  mv "$BK/code/frontend/dist" "$DIST"
fi
for s in vps_smoke_test.sh send_telegram_reminders.py release; do
  if [ -e "$BK/code/scripts/$s" ]; then
    [ -e "$APP_DIR/scripts/$s" ] && mv "$APP_DIR/scripts/$s" "$OUT/scripts/$s"
    mv "$BK/code/scripts/$s" "$APP_DIR/scripts/$s"
  fi
done
[ -f "$APP_DIR/RELEASE_VERSION" ] && mv "$APP_DIR/RELEASE_VERSION" "$OUT/RELEASE_VERSION"
[ -f "$BK/code/RELEASE_VERSION" ] && cp -p "$BK/code/RELEASE_VERSION" "$APP_DIR/RELEASE_VERSION"
say "code restored; the rolled-back release is kept in $OUT"

if [ "$RESTORE_DB" = 1 ]; then
  step "Restore DB"
  mkdir -p "$BK/db-before-rollback-$TS"
  "$VENV_PY" - "$DB_FILE" "$BK/db-before-rollback-$TS/$(basename "$DB_FILE")" "$DB_BK" <<'PY' || die "DB restore failed; the code is already rolled back, the DB is unchanged"
import sqlite3, sys
live, save, backup = sys.argv[1], sys.argv[2], sys.argv[3]
# 1) save the current DB, 2) copy the pre-deploy backup into the live file (sqlite backup API, safe while open).
cur = sqlite3.connect(f"file:{live}?mode=ro", uri=True); s = sqlite3.connect(save); cur.backup(s); s.close(); cur.close()
src = sqlite3.connect(f"file:{backup}?mode=ro", uri=True)
if src.execute("pragma integrity_check").fetchone()[0] != "ok":
    sys.exit("integrity_check failed on the pre-deploy backup")
dst = sqlite3.connect(live); src.backup(dst)
ok = dst.execute("pragma integrity_check").fetchone()[0]
dst.close(); src.close()
if ok != "ok":
    sys.exit(f"integrity_check after restore: {ok}")
print("DB restored; integrity_check=ok. The DB as it was before this rollback is saved in", save)
PY
fi

step "Restart $SERVICE_NAME"
OLD_PID="$(systemctl show -p MainPID --value "$SERVICE_NAME" 2>/dev/null || echo 0)"
sudo systemctl restart "$SERVICE_NAME"
PORT="$(awk -F= '/^[[:space:]]*PORT[[:space:]]*=/ {v=$2; gsub(/[[:space:]"\047]/, "", v); print v; exit}' "$BACKEND/.env" 2>/dev/null || true)"
PORT="${PORT:-5005}"
LISTENER_MISMATCH=""
if wait_healthy_new "$OLD_PID" "$PORT" 60; then
  say "backend /health ok (new MainPID $NEW_PID)"
  say "rolled back to: $(info previous_release)"
  exit 0
fi
die "no stable healthy NEW backend process within 60s${LISTENER_MISMATCH:+ (port held by pid $LISTENER_MISMATCH)}; check: sudo journalctl -u $SERVICE_NAME -n 100"

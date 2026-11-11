#!/bin/bash
# Deploy a RingoStrike release bundle on the VPS. Run as user "ringo".
#
# Usage: bash deploy.sh [--dry-run] [--musics <ringostrike-<sha>-musics.tar.gz>] <ringostrike-<sha>.tar.gz>
#
# Needs next to each archive its .sha256 file (from build_bundle.sh).
# sudo is used only for: systemctl restart ringostrike-backend
# It NEVER writes or edits backend/.env or the DB file, and never runs git.
#
# Steps: preflight -> verify checksums -> online backup of the DB (sqlite backup API) + integrity_check
#        -> move the old backend code, dist and scripts into the backup folder (.env, DB files and venv stay)
#        -> install the new files -> pip install only if a requirement is missing -> restart -> health -> smoke test
#        -> print the rollback command.
#
# Settings (env, optional): APP_DIR (/home/ringo/RingoStrike), BACKUP_ROOT (/home/ringo/RingoDeployBackups),
#   SERVICE_NAME (ringostrike-backend), PUBLIC_BASE_URL (https://ringostrike.ir) for the smoke test,
#   MIN_FREE_MB (500), HEALTH_TIMEOUT (60 seconds).
set -euo pipefail

APP_DIR="${APP_DIR:-/home/ringo/RingoStrike}"
BACKUP_ROOT="${BACKUP_ROOT:-/home/ringo/RingoDeployBackups}"
SERVICE_NAME="${SERVICE_NAME:-ringostrike-backend}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-https://ringostrike.ir}"
MIN_FREE_MB="${MIN_FREE_MB:-500}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-60}"

DRY_RUN=0
MUSICS=""
BUNDLE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --musics) MUSICS="$2"; shift 2 ;;
    -h|--help) sed -n 2,18p "$0"; exit 0 ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) BUNDLE="$1"; shift ;;
  esac
done

say() { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
die() { printf '\nDEPLOY STOPPED: %s\n' "$*" >&2; exit 1; }

[ -n "$BUNDLE" ] || die "give the bundle path: bash deploy.sh [--dry-run] ringostrike-<sha>.tar.gz"
BUNDLE="$(cd "$(dirname "$BUNDLE")" && pwd)/$(basename "$BUNDLE")"
[ -n "$MUSICS" ] && MUSICS="$(cd "$(dirname "$MUSICS")" && pwd)/$(basename "$MUSICS")"
BACKEND="$APP_DIR/backend"
VENV_PY="$BACKEND/venv/bin/python"
DIST="$APP_DIR/frontend/dist"

# Backend items that stay in place (never moved, never overwritten).
is_kept() {
  case "$1" in
    .env|.env.*|venv|.venv|backups|logs|cookies.txt|*.db|*.db-*|*.db.*|*.sqlite|*.sqlite3|*.sqlite-*|*backup*) return 0 ;;
    *) return 1 ;;
  esac
}

# Read one key from .env without sourcing it and without printing other values.
env_value() {
  awk -v k="$1" '
    /^[[:space:]]*#/ { next }
    { line = $0; sub(/^[[:space:]]*(export[[:space:]]+)?/, "", line) }
    index(line, k "=") == 1 || line ~ ("^" k "[[:space:]]*=") {
      v = line; sub(/^[^=]*=/, "", v); gsub(/^[[:space:]]+|[[:space:]]+$/, "", v); gsub(/^["\047]|["\047]$/, "", v); print v; exit
    }' "$BACKEND/.env"
}

# ---------------------------------------------------------------- preflight
step "Preflight$([ $DRY_RUN = 1 ] && echo ' (dry run: nothing will be changed)')"
[ "$(id -un)" = "ringo" ] || die "run as user ringo (now: $(id -un))"
[ -d "$APP_DIR" ] || die "APP_DIR not found: $APP_DIR"
[ -x "$VENV_PY" ] || die "venv python not found: $VENV_PY"
[ -f "$BACKEND/.env" ] || die "backend/.env not found (this script never creates it)"
[ -f "$BUNDLE" ] || die "bundle not found: $BUNDLE"
[ -f "$BUNDLE.sha256" ] || die "checksum file not found: $BUNDLE.sha256"
(cd "$(dirname "$BUNDLE")" && sha256sum -c --status "$(basename "$BUNDLE").sha256") || die "bundle checksum does NOT match"
say "bundle checksum ok: $(basename "$BUNDLE")"
if [ -n "$MUSICS" ]; then
  [ -f "$MUSICS" ] && [ -f "$MUSICS.sha256" ] || die "musics archive or its .sha256 not found"
  (cd "$(dirname "$MUSICS")" && sha256sum -c --status "$(basename "$MUSICS").sha256") || die "musics checksum does NOT match"
  say "musics checksum ok: $(basename "$MUSICS")"
fi

# DB path exactly as the app resolves it: DB_PATH from .env (relative to the service's working directory), else backend/users.db.
DB_RAW="$(env_value DB_PATH || true)"
if [ -z "$DB_RAW" ]; then
  DB_FILE="$BACKEND/users.db"
elif [ "${DB_RAW#/}" != "$DB_RAW" ]; then
  DB_FILE="$DB_RAW"
else
  WD="$(systemctl show -p WorkingDirectory --value "$SERVICE_NAME" 2>/dev/null || true)"
  [ -n "$WD" ] || die "DB_PATH is relative ($DB_RAW) and the service has no WorkingDirectory; set an absolute DB_PATH first"
  DB_FILE="$WD/$DB_RAW"
fi
[ -f "$DB_FILE" ] || die "DB file not found: $DB_FILE"
[ -s "$DB_FILE" ] || die "DB file is empty: $DB_FILE"
say "DB file: $DB_FILE ($(du -h "$DB_FILE" | cut -f1))"
case "$DB_FILE" in
  "$BACKEND"/*)
    top="${DB_FILE#"$BACKEND"/}"; top="${top%%/*}"
    is_kept "$top" || die "the DB lives under backend/$top, which a deploy would move; stop and move it or extend is_kept first" ;;
esac

free_mb="$(df -Pm "$APP_DIR" | awk 'NR==2 {print $4}')"
need_mb=$(( $(du -sm "$DB_FILE" | cut -f1) * 2 + $(du -sm "$BUNDLE" | cut -f1) * 4 + MIN_FREE_MB ))
[ "$free_mb" -ge "$need_mb" ] || die "not enough free disk: ${free_mb} MB free, need ${need_mb} MB"
say "free disk: ${free_mb} MB (need ${need_mb} MB)"
sudo -n true 2>/dev/null && say "sudo: available without a password" || say "sudo: will ask for a password at restart"

# Extract to a staging folder on the same filesystem (so moves are instant) and verify every file.
STAGE_PARENT="$(mktemp -d "$APP_DIR/../.ringo-release-stage.XXXXXX")"
cleanup() { rm -rf "$STAGE_PARENT"; }
trap cleanup EXIT
tar -xzf "$BUNDLE" -C "$STAGE_PARENT"
NEW="$(find "$STAGE_PARENT" -mindepth 1 -maxdepth 1 -type d -name 'ringostrike-*' | head -1)"
[ -n "$NEW" ] && [ -f "$NEW/VERSION" ] || die "bundle has no ringostrike-*/VERSION"
(cd "$NEW" && sha256sum -c --quiet MANIFEST.sha256) || die "a file inside the bundle does not match MANIFEST.sha256"
[ -f "$NEW/frontend/dist/index.html" ] && [ -f "$NEW/backend/app.py" ] || die "bundle is missing dist/index.html or backend/app.py"
for f in "$NEW"/backend/* "$NEW"/backend/.[!.]*; do
  [ -e "$f" ] || continue
  is_kept "$(basename "$f")" && die "bundle contains a protected name: backend/$(basename "$f")"
done
NEW_SHORT="$(awk -F= '$1=="short"{print $2}' "$NEW/VERSION")"
say "new release: $(awk -F= '$1=="commit"{print $2}' "$NEW/VERSION") (built $(awk -F= '$1=="built_at"{print $2}' "$NEW/VERSION"))"
[ -f "$APP_DIR/RELEASE_VERSION" ] && say "current release: $(awk -F= '$1=="commit"{print $2}' "$APP_DIR/RELEASE_VERSION")" \
  || say "current release: (no RELEASE_VERSION; git HEAD $(git -C "$APP_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown) + manual changes)"
if [ -n "$MUSICS" ]; then
  tar -xzf "$MUSICS" -C "$NEW/frontend/dist" || die "could not extract musics"
  [ -d "$NEW/frontend/dist/Musics" ] || die "musics archive has no Musics/ folder"
fi
if [ "$(awk -F= '$1=="musics"{print $2}' "$NEW/VERSION")" = "separate-archive" ] && [ -z "$MUSICS" ]; then
  say "note: this build lists music tracks but no --musics archive was given: the focus view will quietly show no music"
fi

# Requirements: only install when something is missing (the server may have no internet).
MISSING="$("$VENV_PY" - "$NEW/backend/requirements.txt" <<'PY'
import re, sys
from importlib import metadata
missing = []
for line in open(sys.argv[1]):
    line = line.split("#")[0].strip()
    if not line:
        continue
    m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(==\s*([^\s;]+))?", line)
    name, want = m.group(1), m.group(3)
    try:
        have = metadata.version(name)
    except metadata.PackageNotFoundError:
        missing.append(line); continue
    if want and have != want:
        missing.append(f"{line} (installed {have})")
print("\n".join(missing))
PY
)"
if [ -n "$MISSING" ]; then say "requirements to install:"; printf '%s\n' "$MISSING" | sed 's/^/  /'; else say "requirements: all satisfied in the venv"; fi

say ""
say "will move into the backup folder:"
for f in "$BACKEND"/* "$BACKEND"/.[!.]*; do [ -e "$f" ] || continue; is_kept "$(basename "$f")" || say "  backend/$(basename "$f")"; done
say "  frontend/dist"; say "  scripts/ (vps_smoke_test.sh, send_telegram_reminders.py, release/)"
say "stays in place:"
for f in "$BACKEND"/* "$BACKEND"/.[!.]*; do [ -e "$f" ] || continue; is_kept "$(basename "$f")" && say "  backend/$(basename "$f")"; done

if [ "$DRY_RUN" = 1 ]; then
  step "Dry run finished: preflight passed, nothing was changed"
  exit 0
fi

# ---------------------------------------------------------------- backup
TS="$(date -u +%Y%m%d-%H%M%S)"
BK="$BACKUP_ROOT/$TS-$NEW_SHORT"
step "Backup -> $BK"
umask 077
mkdir -p "$BK/code/backend" "$BK/code/frontend" "$BK/code/scripts" "$BK/db"
chmod 700 "$BACKUP_ROOT" "$BK"
"$VENV_PY" - "$DB_FILE" "$BK/db/$(basename "$DB_FILE")" <<'PY' || die "DB backup failed (nothing was changed)"
import sqlite3, sys
src = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
dst = sqlite3.connect(sys.argv[2])
src.backup(dst)
ok = dst.execute("pragma integrity_check").fetchone()[0]
n = dst.execute("select count(*) from sqlite_master where type='table'").fetchone()[0]
dst.close(); src.close()
if ok != "ok":
    sys.exit(f"integrity_check on the backup: {ok}")
print(f"DB backup ok: integrity_check=ok, tables={n}")
PY
sha256sum "$BK/db/$(basename "$DB_FILE")" >"$BK/db/$(basename "$DB_FILE").sha256"
{
  echo "app_dir=$APP_DIR"; echo "db_file=$DB_FILE"; echo "service=$SERVICE_NAME"; echo "deployed_at=$TS"
  echo "new_commit=$(awk -F= '$1=="commit"{print $2}' "$NEW/VERSION")"
  echo "previous_release=$( [ -f "$APP_DIR/RELEASE_VERSION" ] && awk -F= '$1=="commit"{print $2}' "$APP_DIR/RELEASE_VERSION" || git -C "$APP_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
} >"$BK/DEPLOY_INFO"
cp "$NEW/scripts/release/rollback.sh" "$BK/rollback.sh"
[ -f "$APP_DIR/RELEASE_VERSION" ] && cp -p "$APP_DIR/RELEASE_VERSION" "$BK/code/RELEASE_VERSION"

# Requirements before touching code: if pip fails here, nothing has changed yet.
if [ -n "$MISSING" ]; then
  step "pip install -r requirements.txt (existing venv)"
  "$VENV_PY" -m pip install -r "$NEW/backend/requirements.txt" || die "pip install failed; code was NOT changed (DB backup is in $BK)"
fi

# ---------------------------------------------------------------- swap
step "Install new code"
: >"$BK/installed_backend.txt"
for f in "$BACKEND"/* "$BACKEND"/.[!.]*; do
  [ -e "$f" ] || continue
  b="$(basename "$f")"
  is_kept "$b" || mv "$f" "$BK/code/backend/$b"
done
for f in "$NEW"/backend/* "$NEW"/backend/.[!.]*; do
  [ -e "$f" ] || continue
  mv "$f" "$BACKEND/"
  basename "$f" >>"$BK/installed_backend.txt"
done
[ -d "$DIST" ] && mv "$DIST" "$BK/code/frontend/dist"
mv "$NEW/frontend/dist" "$DIST"
chmod -R a+rX "$DIST"
for s in vps_smoke_test.sh send_telegram_reminders.py release; do
  [ -e "$APP_DIR/scripts/$s" ] && mv "$APP_DIR/scripts/$s" "$BK/code/scripts/$s"
  mv "$NEW/scripts/$s" "$APP_DIR/scripts/$s"
done
cp "$NEW/VERSION" "$APP_DIR/RELEASE_VERSION"
say "installed $(wc -l <"$BK/installed_backend.txt") backend item(s), frontend/dist, scripts; RELEASE_VERSION written"

ROLLBACK_CMD="bash $BK/rollback.sh $BK"

# ---------------------------------------------------------------- restart + checks
step "Restart $SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME" || { say "restart failed. Roll back with:"; say "  $ROLLBACK_CMD"; exit 1; }
PORT="$(env_value PORT || true)"; PORT="${PORT:-5005}"
ok=0
for _ in $(seq 1 "$HEALTH_TIMEOUT"); do
  if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -Eq '"ok"[[:space:]]*:[[:space:]]*true'; then ok=1; break; fi
  sleep 1
done
if [ "$ok" != 1 ]; then
  say "backend /health did not answer ok within ${HEALTH_TIMEOUT}s. Check: sudo journalctl -u $SERVICE_NAME -n 100"
  say "Roll back with:"; say "  $ROLLBACK_CMD"; exit 1
fi
say "backend /health ok"

step "Smoke test (PUBLIC_BASE_URL=$PUBLIC_BASE_URL)"
smoke=0
PUBLIC_BASE_URL="$PUBLIC_BASE_URL" APP_ROOT="$APP_DIR" SERVICE_NAME="$SERVICE_NAME" BACKEND_URL="http://127.0.0.1:$PORT" bash "$APP_DIR/scripts/vps_smoke_test.sh" || smoke=$?

step "Done"
say "release: $(awk -F= '$1=="commit"{print $2}' "$APP_DIR/RELEASE_VERSION")"
say "backup:  $BK"
[ "$smoke" = 0 ] && say "smoke test: passed" || say "smoke test: FAILED (exit $smoke) - read the lines above before deciding to roll back"
say ""
say "Rollback (code + dist + scripts; the DB stays):"
say "  $ROLLBACK_CMD"
say "Rollback including the DB (LOSES every write made after this deploy):"
say "  $ROLLBACK_CMD --restore-db"
exit "$smoke"

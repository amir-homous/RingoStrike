#!/bin/bash
# Build a RingoStrike release bundle from the TRACKED files of one commit.
#
# Usage: scripts/release/build_bundle.sh [--commit <rev>] [--out <dir>] [--musics <dir>]
#   --commit  commit to build (default: HEAD)
#   --out     output folder (default: $HOME/ringo-release); must be outside the repo
#   --musics  folder with the focus music (the layout of frontend/public/Musics). Optional.
#             The track list is fixed at build time, so music must be given here to be playable.
#             The audio files go into a SEPARATE archive, never into the main bundle.
#
# The build runs in a temporary clean copy (git archive), never in the working directory.
# Output: ringostrike-<short>.tar.gz + .sha256 (and ringostrike-<short>-musics.tar.gz + .sha256).
set -euo pipefail

COMMIT=HEAD
OUT_DIR="${HOME}/ringo-release"
MUSICS_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --commit) COMMIT="$2"; shift 2 ;;
    --out) OUT_DIR="$2"; shift 2 ;;
    --musics) MUSICS_DIR="$2"; shift 2 ;;
    -h|--help) sed -n 2,13p "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

fail() { echo "BUILD FAILED: $*" >&2; exit 1; }

REPO="$(git rev-parse --show-toplevel)"
SHA="$(git -C "$REPO" rev-parse --verify "${COMMIT}^{commit}")" || fail "unknown commit $COMMIT"
SHORT="$(git -C "$REPO" rev-parse --short=7 "$SHA")"
NAME="ringostrike-${SHORT}"

mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
case "$OUT_DIR/" in "$REPO"/*) fail "--out must be outside the repo ($REPO)" ;; esac
if git -C "$OUT_DIR" rev-parse --git-dir >/dev/null 2>&1; then fail "--out must not be inside a git repo"; fi

node_major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
[ "$node_major" -ge 20 ] || fail "Node 20+ required (found: $(node -v 2>/dev/null || echo none))"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
SRC="$WORK/src"
STAGE="$WORK/stage/$NAME"
mkdir -p "$SRC" "$STAGE"

echo "== Building $NAME from $SHA"
git -C "$REPO" archive "$SHA" | tar -x -C "$SRC"

# ---- frontend (built in the clean copy) ----
if [ -n "$MUSICS_DIR" ]; then
  [ -d "$MUSICS_DIR" ] || fail "--musics folder not found: $MUSICS_DIR"
  mkdir -p "$SRC/frontend/public/Musics"
  cp -R "$MUSICS_DIR"/. "$SRC/frontend/public/Musics/"
fi
rm -f "$SRC"/frontend/.env "$SRC"/frontend/.env.*
(
  cd "$SRC/frontend"
  npm ci --include=dev --no-audit --no-fund >"$WORK/npm-ci.log" 2>&1 || { tail -20 "$WORK/npm-ci.log"; exit 1; }
  VITE_API_BASE=/api-proxy VITE_BASE=/ npm run build >"$WORK/vite-build.log" 2>&1 || { tail -30 "$WORK/vite-build.log"; exit 1; }
) || fail "frontend build"
DIST="$SRC/frontend/dist"
[ -f "$DIST/index.html" ] || fail "dist/index.html missing"

# Text files of dist must not point at a dev API or a raw IP.
# Two "localhost" strings are known and harmless, and are removed before the check:
#   axios:            window.location.href||"http://localhost"   (URL-parse fallback, never requested)
#   src/lib/api.js:   /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i   (guard that REJECTS a loopback API base in production)
# Anything else fails: localhost, 127.0.0.1, :5005, an IP inside a URL, or the old server IP.
ALLOW_AXIOS='"http://localhost"'
ALLOW_GUARD='(localhost|127\.0\.0\.1)(:\d+)?$/i'
dist_bad="$(find "$DIST" -type f \( -name '*.js' -o -name '*.css' -o -name '*.html' -o -name '*.json' -o -name '*.svg' -o -name '*.map' \) -print0 \
  | xargs -0 cat | ALLOW_AXIOS="$ALLOW_AXIOS" ALLOW_GUARD="$ALLOW_GUARD" perl -pe 's/\Q$ENV{ALLOW_AXIOS}\E//g; s/\Q$ENV{ALLOW_GUARD}\E//g' \
  | grep -oE '.{0,40}(localhost|127\.0\.0\.1|:5005|https?://([0-9]{1,3}\.){3}[0-9]{1,3}|82\.115\.24\.10).{0,40}' | head -5 || true)"
if [ -n "$dist_bad" ]; then
  echo "$dist_bad" >&2
  fail "dist contains localhost, 127.0.0.1, :5005 or a hard-coded IP"
fi
echo "dist check: no dev API host, :5005 or hard-coded IP (2 known harmless localhost strings allowed)"
grep -rqF '/api-proxy' "$DIST/assets" || fail "dist does not use /api-proxy (VITE_API_BASE not applied?)"

# ---- assemble ----
mkdir -p "$STAGE/frontend" "$STAGE/scripts"
cp -R "$SRC/backend" "$STAGE/backend"
rm -rf "$STAGE/backend/tests"
cp -R "$DIST" "$STAGE/frontend/dist"
cp "$SRC/scripts/vps_smoke_test.sh" "$SRC/scripts/send_telegram_reminders.py" "$STAGE/scripts/"
cp -R "$SRC/scripts/release" "$STAGE/scripts/release"

# Music goes into its own archive.
if [ -d "$STAGE/frontend/dist/Musics" ]; then
  mkdir -p "$WORK/musics"
  mv "$STAGE/frontend/dist/Musics" "$WORK/musics/Musics"
fi

# Strip anything that must never ship (git archive has only tracked files; this is a second guard).
find "$STAGE" \( -name '.env' -o -name '.env.*' -o -name 'venv' -o -name '.venv' -o -name '__pycache__' \
  -o -name '.git' -o -name 'backups' -o -name '.pytest_cache' -o -name 'node_modules' \) -prune -exec rm -rf {} +

{
  echo "commit=$SHA"
  echo "short=$SHORT"
  echo "built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "commit_date=$(git -C "$REPO" show -s --format=%cI "$SHA")"
  echo "vite_api_base=/api-proxy"
  echo "vite_base=/"
  echo "musics=$([ -d "$WORK/musics/Musics" ] && echo separate-archive || echo none)"
} >"$STAGE/VERSION"

(cd "$STAGE" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum) >"$WORK/MANIFEST.sha256"
mv "$WORK/MANIFEST.sha256" "$STAGE/MANIFEST.sha256"

# ---- safety checks on the staged bundle ----
bad_names="$(cd "$STAGE" && find . \( -name '.env' -o -name '.env.*' -o -name '*.db' -o -name '*.db.*' -o -name '*.db-*' \
  -o -name '*.sqlite*' -o -iname '*backup*' -o -name 'cookies.txt' -o -name '__pycache__' -o -name '.git' \
  -o -path './backend/backups*' -o -name '*.mp3' -o -name '*.ogg' -o -name '*.m4a' -o -name '*.wav' -o -name 'venv' \) -print)"
[ -z "$bad_names" ] || { echo "$bad_names" >&2; fail "bundle contains forbidden files"; }
secret_hits="$(grep -rIlE '(TELEGRAM_BOT_TOKEN|JWT_SECRET)[[:space:]]*=[[:space:]]*["'"'"']?[A-Za-z0-9:_-]{8,}' "$STAGE" || true)"
[ -z "$secret_hits" ] || { echo "$secret_hits" >&2; fail "bundle contains a TELEGRAM_BOT_TOKEN= or JWT_SECRET= value"; }

# ---- write archives ----
tar -C "$WORK/stage" -czf "$OUT_DIR/$NAME.tar.gz" "$NAME"
(cd "$OUT_DIR" && sha256sum "$NAME.tar.gz" >"$NAME.tar.gz.sha256")
if [ -d "$WORK/musics/Musics" ]; then
  tar -C "$WORK/musics" -czf "$OUT_DIR/$NAME-musics.tar.gz" Musics
  (cd "$OUT_DIR" && sha256sum "$NAME-musics.tar.gz" >"$NAME-musics.tar.gz.sha256")
fi

echo "== Bundle file list ($NAME)"
tar -tzf "$OUT_DIR/$NAME.tar.gz" | grep -v '/$' | sed 's|^[^/]*/||' | awk -F/ '
  { if ($1 == "frontend") key = (NF > 3) ? $1 "/" $2 "/" $3 "/" : $0; else if (NF > 2) key = $1 "/" $2 "/"; else key = $0; n[key]++ }
  END { for (k in n) printf "  %-48s %d file(s)\n", k, n[k] }' | sort
echo "== Output"
ls -l "$OUT_DIR/$NAME"*
cat "$OUT_DIR/$NAME.tar.gz.sha256"
[ -f "$OUT_DIR/$NAME-musics.tar.gz.sha256" ] && cat "$OUT_DIR/$NAME-musics.tar.gz.sha256"
echo "BUILD OK: $NAME"

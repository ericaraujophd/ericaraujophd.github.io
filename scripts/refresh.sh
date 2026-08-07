#!/usr/bin/env bash
#
# refresh.sh — rebuild the CV, rebuild the site, verify both.
#
# Usage (from anywhere):
#   scripts/refresh.sh              # CV + site + checks
#   scripts/refresh.sh --cv         # CV only
#   scripts/refresh.sh --site       # site only
#   scripts/refresh.sh --check      # checks only, rebuild nothing
#
# Exits non-zero if any step or check fails, so it is safe to run before a push.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv-cv"
DO_CV=1
DO_SITE=1
DO_CHECK=1

case "${1:-}" in
  --cv)    DO_SITE=0; DO_CHECK=0 ;;
  --site)  DO_CV=0;   DO_CHECK=0 ;;
  --check) DO_CV=0;   DO_SITE=0  ;;
  "")      ;;
  *) echo "unknown flag: $1"; sed -n '3,12p' "$0"; exit 2 ;;
esac

bold() { printf '\n\033[1m%s\033[0m\n' "$1"; }
fail() { printf '\033[31m  FAIL  %s\033[0m\n' "$1"; FAILED=1; }
pass() { printf '\033[32m  ok    %s\033[0m\n' "$1"; }
FAILED=0

# ---------------------------------------------------------------- CV
if [ "$DO_CV" = 1 ]; then
  bold "Rebuilding CV"
  if [ ! -x "$VENV/bin/python" ]; then
    echo "  No usable Python at $VENV/bin/python"
    echo "  Create it:  python3 -m venv .venv-cv"
    echo "              .venv-cv/bin/pip install -r rendercv/requirements.txt"
    exit 1
  fi
  # build.py invokes 'rendercv' from PATH and sys.executable for to_rendercv.py,
  # so the venv must be on PATH, not just its python.
  PATH="$VENV/bin:$PATH" "$VENV/bin/python" scripts/build.py
fi

# -------------------------------------------------------------- site
if [ "$DO_SITE" = 1 ]; then
  bold "Rebuilding site"
  [ -d node_modules ] || npm install
  npm run build
fi

# ------------------------------------------------------------- checks
if [ "$DO_CHECK" = 1 ]; then
  bold "Checks"

  # 1. Every slides_url in the data actually ships in public/.
  #    Astro only serves public/ — a PDF sitting in presentations/ is invisible.
  "$VENV/bin/python" - <<'PY' || FAILED=1
import json, pathlib, sys
missing = []
for p in json.load(open("data/presentations.json")):
    u = p.get("slides_url")
    if u and u.startswith("/") and not pathlib.Path("public" + u).is_file():
        missing.append(f'{u}   ({p["event"][:50]})')
if missing:
    print("\033[31m  FAIL  slides_url with no file under public/:\033[0m")
    for m in missing:
        print("          " + m)
    sys.exit(1)
print("\033[32m  ok    every slides_url resolves under public/\033[0m")
PY

  if [ -d dist ]; then
    # 2. Year badges must not be truncated term strings.
    if grep -qE 'class="pub-type-tag">(Fall|Spri|Sprin|Summ|Wint)<' dist/advising/index.html; then
      fail "truncated year badges on /advising/"
    else
      pass "advising year badges intact"
    fi

    # 3. Homepage should present a single address.
    n=$(grep -o 'mailto:[^"]*' dist/index.html | sort -u | wc -l | tr -d ' ')
    [ "$n" = 1 ] && pass "homepage has one email address" \
                 || fail "homepage has $n distinct mailto addresses"
  else
    echo "  (no dist/ — run without --check to build the site first)"
  fi

  # 4. Published CV must not be older than the data it is built from.
  "$VENV/bin/python" - <<'PY' || FAILED=1
import pathlib, sys
pdf = pathlib.Path("public/cv/Eric_Araujo_CV.pdf")
if not pdf.exists():
    print("\033[31m  FAIL  public/cv/Eric_Araujo_CV.pdf is missing\033[0m"); sys.exit(1)
srcs = list(pathlib.Path("data").glob("*.json")) + [pathlib.Path("config/personal.yaml")]
stale = [s.name for s in srcs if s.stat().st_mtime > pdf.stat().st_mtime]
if stale:
    print("\033[31m  FAIL  CV PDF is older than: " + ", ".join(stale) + "\033[0m")
    print("          run: scripts/refresh.sh --cv")
    sys.exit(1)
print("\033[32m  ok    CV PDF is newer than its sources\033[0m")
PY
fi

if [ "$FAILED" = 1 ]; then
  printf '\n\033[31mSome checks failed.\033[0m\n'
  exit 1
fi
printf '\n\033[32mAll good.\033[0m\n'

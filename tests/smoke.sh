#!/usr/bin/env bash
# End-to-end smoke test in a throwaway data dir: install → new → render → sheet → embed.
# Takes ~1 min with a warm uv cache. Usage: tests/smoke.sh [--keep]
set -euo pipefail
cd "$(dirname "$0")/.."
VE="$PWD/skills/visual-explain/manim/ve-manim"
TMP="$(mktemp -d /tmp/ve-smoke.XXXXXX)"
export VE_DATA="$TMP/data"
trap '[ "${1:-}" = "--keep" ] && echo "kept $TMP" || rm -rf "$TMP"' EXIT

"$VE" install
"$VE" status
"$VE" new "$TMP/proj"
"$VE" render "$TMP/proj" s1_example.py S1Example
"$VE" sheet "$TMP/proj" S1Example
cp skills/visual-explain/manim/film-player.html "$TMP/proj/page.html"
"$VE" embed "$TMP/proj/page.html" "$TMP/proj/index.html"
grep -q 'data:video/mp4;base64,' "$TMP/proj/index.html"
grep -q 'data:image/jpeg;base64,' "$TMP/proj/index.html"
[ -s "$TMP/proj/frames/S1Example_sheet.png" ]
echo "smoke: OK"

#!/usr/bin/env bash
# Install 3b1b manim (manimgl) into an isolated venv for the visual-explain skill.
# Usage: install.sh <data-dir> [pip-spec]      (normally called through `ve-manim install`)
#
# - Uses `uv` when available (it can also fetch a Python), else a local python3.9–3.13.
# - Bundles ffmpeg through the `imageio-ffmpeg` wheel: no Homebrew/apt needed.
# - Finishes with a tiny headless render; the venv only counts as ready if that works.
# Env: VE_PYTHON (uv python request, default 3.11), VE_FORCE=1 (reinstall).
set -euo pipefail

DATA="${1:?usage: install.sh <data-dir> [spec]}"
SPEC="${2:-manimgl==1.7.2}"
VENV="$DATA/ve-manim-venv"
# manimgl 1.7.2 imports pkg_resources: uv and python>=3.12 venvs don't ship setuptools,
# and setuptools 81+ drops pkg_resources.
PKGS=("$SPEC" imageio-ffmpeg "setuptools<81")
LOCK="$DATA/.install.lock"
MARK="$VENV/.ve-installed"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

mkdir -p "$DATA"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +30 2>/dev/null)" ]; then
    log "removing stale lock"; rm -rf "$LOCK"; mkdir "$LOCK"
  else
    log "another install is already running ($LOCK)"; exit 3
  fi
fi
trap 'rm -rf "$LOCK"' EXIT
touch "$DATA/.last-attempt"

if [ -f "$MARK" ] && [ "${VE_FORCE:-0}" != "1" ] && grep -q "^spec=$SPEC$" "$MARK" && grep -q "^render=ok$" "$MARK"; then
  log "already installed ($SPEC)"; exit 0
fi

log "installing $SPEC into $VENV"
rm -rf "$VENV"

UV="$(command -v uv || true)"
for c in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv" /opt/homebrew/bin/uv /usr/local/bin/uv; do
  [ -z "$UV" ] && [ -x "$c" ] && UV="$c"
done

if [ -n "$UV" ]; then
  VIA="uv"
  log "creating venv with uv (python ${VE_PYTHON:-3.11})"
  "$UV" venv --quiet --python "${VE_PYTHON:-3.11}" "$VENV"
  "$UV" pip install --quiet --python "$VENV/bin/python" "${PKGS[@]}"
else
  VIA="venv+pip"
  PY=""
  for c in python3.12 python3.11 python3.10 python3.13 python3; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if (3, 9) <= sys.version_info[:2] < (3, 14) else 1)'; then
      PY="$(command -v "$c")"; break
    fi
  done
  [ -n "$PY" ] || { log "ERROR: no Python 3.9-3.13 found. Install uv (https://docs.astral.sh/uv/) or python3.11."; exit 2; }
  log "creating venv with $PY"
  "$PY" -m venv "$VENV"
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  "$VENV/bin/python" -m pip install --quiet "${PKGS[@]}"
fi

FF="$("$VENV/bin/python" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')"
ln -sf "$FF" "$VENV/bin/ffmpeg"
log "ffmpeg: $("$VENV/bin/ffmpeg" -version | head -1)"

# Headless render check: 0.5 s at 480p. Proves OpenGL, Pango text and ffmpeg all work.
CHECK="$DATA/render-check"
rm -rf "$CHECK"; mkdir -p "$CHECK"
cat >"$CHECK/check.py" <<'EOF'
from manimlib import *


class VeCheck(Scene):
    def construct(self):
        self.play(ShowCreation(Square()), FadeIn(Text("ok", font_size=36)), run_time=0.5)
EOF
RENDER="failed"
if ( cd "$CHECK" && PATH="$VENV/bin:$PATH" ${VE_WRAP:-} "$VENV/bin/manimgl" check.py VeCheck -w -l --video_dir "$CHECK" ) >"$CHECK/render.log" 2>&1 \
   && [ -n "$(find "$CHECK" -name 'VeCheck.mp4' -size +0 2>/dev/null)" ]; then
  RENDER="ok"
else
  log "render check FAILED. Tail of $CHECK/render.log:"; tail -n 15 "$CHECK/render.log" || true
  case "$(uname -s)" in Linux) log "hint: headless Linux needs a GL context, e.g. apt install xvfb && export VE_WRAP='xvfb-run -a'";; esac
fi

PYV="$("$VENV/bin/python" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
cat >"$MARK" <<EOF
spec=$SPEC
python=$PYV
via=$VIA
date=$(date '+%Y-%m-%dT%H:%M:%S')
render=$RENDER
EOF
[ "$RENDER" = "ok" ] && rm -f "$DATA/.last-attempt"
log "done: spec=$SPEC python=$PYV via=$VIA render=$RENDER"
[ "$RENDER" = "ok" ]

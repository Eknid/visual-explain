#!/usr/bin/env bash
# SessionStart hook: make sure the optional manim renderer is installed.
#
# - Already installed and current: exits immediately (a few ms).
# - Otherwise: starts the installer in the background and exits, so the session
#   never waits. Progress goes to $CLAUDE_PLUGIN_DATA/install.log.
# - Prints nothing: SessionStart stdout would be added to Claude's context, and
#   films are opt-in, so Claude shouldn't be nudged towards them.
# - Back-off: a version that installed but failed its render check is not retried
#   automatically; an attempt that never finished is retried at most once a day.
# - Opt out with VE_AUTO_INSTALL=0 (then run `ve-manim install` by hand when needed).
set -u
[ "${VE_AUTO_INSTALL:-1}" = "0" ] && exit 0
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
VE="$ROOT/skills/visual-explain/manim/ve-manim"
[ -f "$VE" ] || exit 0
bash "$VE" autoinstall >/dev/null 2>&1
exit 0

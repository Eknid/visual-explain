#!/usr/bin/env bash
# Static checks: shell syntax, Python syntax, JSON, executable bits, and the plugin validator.
set -euo pipefail
cd "$(dirname "$0")/.."
fail=0
for f in skills/visual-explain/manim/ve-manim skills/visual-explain/manim/install.sh scripts/ensure-manim.sh tests/*.sh; do
  bash -n "$f" || { echo "bash syntax: $f"; fail=1; }
done
for f in skills/visual-explain/manim/ve-manim skills/visual-explain/manim/install.sh scripts/ensure-manim.sh; do
  [ -x "$f" ] || { echo "not executable: $f"; fail=1; }
done
# ast.parse instead of py_compile: checks syntax without leaving __pycache__ in the plugin
python3 -c 'import ast, sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]' \
  skills/visual-explain/manim/vetools.py skills/visual-explain/manim/template/*.py \
  skills/visual-explain/manim/examples/spotify-rap/*.py || fail=1
# the film player script must parse
if command -v node >/dev/null; then
  python3 -c 'import re, sys; print(re.findall(r"^<script>(.*?)^</script>", open(sys.argv[1]).read(), re.S | re.M)[0])' \
    skills/visual-explain/manim/film-player.html >"${TMPDIR:-/tmp}/ve-film-player.js"
  node --check "${TMPDIR:-/tmp}/ve-film-player.js" || { echo "film-player.html script"; fail=1; }
fi
for j in .claude-plugin/plugin.json .claude-plugin/marketplace.json hooks/hooks.json; do
  python3 -m json.tool "$j" >/dev/null || { echo "bad JSON: $j"; fail=1; }
done
grep -q '^name: visual-explain$' skills/visual-explain/SKILL.md || { echo "SKILL.md frontmatter"; fail=1; }
if command -v claude >/dev/null; then
  claude plugin validate --strict .claude-plugin/plugin.json || fail=1
  claude plugin validate --strict .claude-plugin/marketplace.json || fail=1
  claude plugin validate skills || fail=1
fi
[ $fail = 0 ] && echo "check: OK" || { echo "check: FAILED"; exit 1; }

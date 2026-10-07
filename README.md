# visual-explain

A Claude Code plugin that answers "explain X" with **one self-contained HTML page of
diagrams and animations** instead of a wall of text. Optionally, it adds rendered
explainer films made with [3b1b manim](https://github.com/3b1b/manim) (`manimgl`).

| Piece                        | What it is                                                          |
|------------------------------|---------------------------------------------------------------------|
| `visual-explain` skill       | How to research, lay out, animate (SVG + JS) and verify the page    |
| `manim/` toolkit             | `ve-manim` CLI, house-style scene template, film player, playbook   |
| SessionStart hook            | Installs the manim renderer in the background, once                 |
| Worked examples              | `reference/example-architecture.html`, `manim/examples/spotify-rap` |

**Films are opt-in.** Claude makes manim films only when you ask for them ("…with manim
films"). If it thinks films would help, it asks first, because they cost many more
tokens and minutes than the default SVG/JS animations.

## Install (local, nothing published)

```bash
claude plugin marketplace add ~/Codes/visual-explain-plugin
claude plugin install visual-explain@visual-explain-local
```

Or inside Claude Code: `/plugin marketplace add ~/Codes/visual-explain-plugin`, then
`/plugin install visual-explain@visual-explain-local`.

At the **first session start**, the hook installs the renderer in the background (about
1–2 min, ~500 MB) into the plugin's data directory, `~/.claude/plugins/data/<id>/`:

- `ve-manim-venv/`: an isolated venv with `manimgl==1.7.2`, `imageio-ffmpeg` (a bundled
  ffmpeg, so no Homebrew or apt needed) and `setuptools<81` (manimgl still imports
  `pkg_resources`)
- `install.log`: progress and the result of a headless render check

The venv is built with `uv` when it's available (uv can also download a Python),
otherwise with a local Python 3.9–3.13. Uninstalling the plugin deletes the data directory.

Opt out of the automatic install with `VE_AUTO_INSTALL=0` in your environment. Claude
will then ask before running `ve-manim install` the first time you want films.

> If you also have the skill as a plain user skill (`~/.claude/skills/visual-explain`),
> remove that copy after installing the plugin so there's only one `visual-explain`.

## Use

```text
/visual-explain:visual-explain how does the ingestion pipeline in this repo work
/visual-explain:visual-explain https://example.com/some-paper with manim films
```

Plain requests also trigger it: "explain me X", "show me how Y works".

## `ve-manim`

The skill drives this; you can run it by hand too
(`~/.claude/plugins/cache/…/skills/visual-explain/manim/ve-manim`, or from this repo):

| Command                                       | Does                                                 |
|-----------------------------------------------|------------------------------------------------------|
| `ve-manim status` / `doctor`                  | readiness / full report (venv, ffmpeg, LaTeX, fonts) |
| `ve-manim install [--background] [--force]`   | (re)install the renderer                             |
| `ve-manim new <dir>`                          | scaffold `<dir>/scenes/` from the template           |
| `ve-manim render <dir> <file.py> [Scene] [--hd]` | headless render (480p draft by default)           |
| `ve-manim sheet <dir> <Scene>`                | one contact-sheet PNG of 6 frames for review         |
| `ve-manim frames <dir> <Scene> 3.5,12`        | single frames                                        |
| `ve-manim embed page.html index.html [--external]` | inline the films (base64) into one HTML file    |

Environment: `VE_DATA` (data dir override), `VE_MANIMGL_SPEC` (pip spec),
`VE_PYTHON` (uv Python version, default 3.11), `VE_WRAP` (e.g. `xvfb-run -a` on
headless Linux), `VE_FONT_SANS` / `VE_FONT_MONO`, `VE_AUTO_INSTALL=0`.

## Requirements

macOS or Linux with bash. Apple Silicon and Intel Macs work out of the box. Linux
needs an OpenGL context: on a headless box install `xvfb` and set `VE_WRAP='xvfb-run -a'`.
LaTeX is optional; without it, avoid `Tex`/`Brace` (the playbook says how). Windows is
not supported.

## Develop

```bash
claude plugin validate .        # manifest + marketplace
tests/check.sh                  # static checks: bash -n, py_compile, JSON
tests/smoke.sh                  # end to end: install → new → render → sheet → embed (temp dir)
claude --plugin-dir .           # try the plugin without installing it
```

Layout:

```text
.claude-plugin/plugin.json        manifest
.claude-plugin/marketplace.json   local marketplace (source "./")
hooks/hooks.json                  SessionStart → scripts/ensure-manim.sh
skills/visual-explain/SKILL.md    the skill
skills/visual-explain/reference/  example page with the two animation engines
skills/visual-explain/manim/      MANIM.md playbook, ve-manim, install.sh, vetools.py,
                                  template/, film-player.html, examples/
tests/                            check.sh, smoke.sh
```

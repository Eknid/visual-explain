# Changelog

## 0.1.0 — 2026-10-07

- First plugin release of the `visual-explain` skill (previously a user skill).
- Opt-in manim films: Claude makes them only when asked, and asks first otherwise
  (token-heavy).
- `ve-manim` CLI: status, doctor, install, new, render, frames, sheet, embed.
- SessionStart hook installs `manimgl==1.7.2` + a bundled ffmpeg into the plugin data
  dir in the background, with a headless render check and back-off on failures.
- Manim playbook (`MANIM.md`), house-style template, film player snippet with a custom
  control bar, and the eight-film Spotify RAP worked example.

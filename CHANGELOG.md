# Changelog

## 0.2.0 — 2026-10-27

- New default visual language, taken from the user's reference images: schematic,
  monochrome, mono labels; blue = new, dashed = modified, dotted = link, amber = active.
- `reference/kit.html`: copy-paste CSS + JS kit and five worked figures (layer matrix,
  stage pipeline, before/after replay, state-machine replay, BPMN replay). Arrows are
  drawn from `data-from`/`data-to` specs on a CSS grid, no coordinates.
- Replay engine in the style of `visual-explainer`'s `replay.gif`: lit routes, travelling
  dots, values and slots that change per step, one caption per step, ← Play slider →.
- BPMN subset: pools, lanes, events, tasks, gateways, sequence/message flows, data stores.
- `tools/ve-check`: script syntax, kit layout report (missing ids, bad steps, overlapping
  boxes, edges crossing boxes) and light/dark/phone screenshots via headless Chrome.
- `example-architecture.html` kept only for the interfaces-player mechanics.

## 0.1.0 — 2026-10-07

- First plugin release of the `visual-explain` skill (previously a user skill).
- Opt-in manim films: Claude makes them only when asked, and asks first otherwise
  (token-heavy).
- `ve-manim` CLI: status, doctor, install, new, render, frames, sheet, embed.
- SessionStart hook installs `manimgl==1.7.2` + a bundled ffmpeg into the plugin data
  dir in the background, with a headless render check and back-off on failures.
- Manim playbook (`MANIM.md`), house-style template, film player snippet with a custom
  control bar, and the eight-film Spotify RAP worked example.

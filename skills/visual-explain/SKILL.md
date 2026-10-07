---
name: visual-explain
description: Use when the user asks to explain, show, walk through or help them understand something — a project, codebase, architecture, system, pipeline, workflow, data flow, paper, concept or process ("explain me X", "how does X work", "show me the structure of X", "I don't get X"). The user understands visually, not textually, so the answer is a self-contained HTML page of diagrams and animations with very few words, not a text explanation. Rendered 3b1b manim films are an opt-in extra, made only when the user asks for them.
user-invocable: true
argument-hint: <what to explain — a repo, a component, a flow, a paper, a concept> [with manim films]
---

# Visual Explain

The user learns from **pictures, not paragraphs**. When they ask for an explanation,
the deliverable is one self-contained HTML page that shows it visually: diagrams,
animated walkthroughs, and a few words on each. Opening it in a browser should be
enough to understand the subject.

A complete worked example lives next to this file:
`reference/example-architecture.html` (the agent-hub architecture page). It contains
two reusable animation engines. **Read the relevant part of it before writing** and
adapt the engines instead of inventing new ones. Landmarks:

| What                          | Where in the example (search for)       |
|-------------------------------|-----------------------------------------|
| Theme tokens, dark mode, CSS  | `<style>` … `</style>`                  |
| "Who's who" cards             | `<!-- CAST -->`                         |
| End-to-end flow player (HTML) | `<!-- E2E PLAYER -->`                   |
| End-to-end flow player (JS)   | `/* ---------- E2E PLAYER ---------- */` |
| Interface / call player (JS)  | `/* ---------- CODE DEEP-DIVE PLAYER`   |
| Wire-level hops to externals  | `const WIRE=` and `function iface`      |

## Manim films: opt-in only

By default, every animation is inline SVG + JS in the page (Steps 3–4). That is fast,
interactive and cheap. **Rendered films made with 3b1b manim (`manimgl`) are an extra.**

- **Make films only when the user asks**: they mention manim / 3b1b / "rendered video" /
  "manim animations", or pass `with manim films` to this skill.
- **Never start manim on your own.** If you judge that films would really help (a paper
  or algorithm with a step-by-step mechanism, a data-layout transformation, maths),
  **ask first** with AskUserQuestion. State the cost plainly: "N films of ~25 s each,
  roughly 150 lines of Python per film plus render-and-review rounds, so this is
  token-heavy and adds several minutes". Offer "SVG/JS page only (recommended default)"
  and "Add N manim films". Go ahead only on a yes.
- Once approved: read `manim/MANIM.md` (in this skill's directory) and follow it. It
  covers the renderer check (`manim/ve-manim status`), the storyboard, house style,
  render → contact-sheet review → final loop, gotchas, and embedding the films in the
  page. Don't read it otherwise, to save context.

## Step 1: Get the facts right first

A beautiful picture of the wrong thing is worse than no picture. Before drawing:

- Read the real source: README/CLAUDE.md, entry points, the main modules, config,
  Dockerfiles, deploy/run scripts. Use an Explore agent for a large codebase. For a
  paper or article, fetch the full text and keep every number and name exactly.
- For every box you plan to draw, know: **what it is**, **what kind of thing** it is
  (script, service, LLM call, database, file, cloud SaaS, human), **where it
  physically runs** (laptop, EC2, container, managed cloud) and **how it runs
  logically** (process, CLI call, container, cron, API).
- For every arrow, know the real mechanism (the actual function, CLI command, HTTP
  route, SQL table). Quote real names: `POST /api/v1/agents`, `gh pr list`, `state.save()`.
- Never invent a component, an EC2 host or a call. If something is unknown, leave it
  out or mark it "?" rather than guess. Label made-up sample values as illustrative.

## Step 2: Choose the views

Pick the views the subject needs, usually 3–6, in this order of priority:

1. **Who's who.** One card per component with a big emoji, a name and a 2–4 word role.
   **Give people-roles only to humans and LLMs.** Deterministic code is shown as a
   machine or object (🚦 traffic light, 🚪 gate, 📒 logbook) with "plain code, no AI".
   Never call a script a "manager" or a "brain".
2. **Big picture.** Every component, placed inside **zones that show where it runs**:
   ☁️ internet / managed services, 💻 local machine or 🖥️ server, 🐳 Docker. Say
   explicitly what is *not* there (e.g. "🚫 No EC2") when that is a natural question.
3. **Animated end-to-end flow.** One real scenario from trigger to finish (see Step 3).
   To compare two approaches (old vs new path), use tabs with one scenario each and
   live counters.
4. **Interfaces.** An animated view of calls **between** components only, plus the calls
   that leave the process to external systems (see Step 4).
5. Optional: a lifecycle/state diagram, a "what you can type/do" grid, a metrics or
   data pipeline, a folder tree, an interactive "toggle the options" explorer.
6. **🎬 Films** only when approved (see *Manim films: opt-in only*): one film per
   concept, each in its own section with a fact-chip row and one 💡 line.

Skip anything that only restates another view. Do not show vanity numbers (lines of
code, file counts): they explain nothing.

## Step 3: The end-to-end flow player

Adapt the E2E player from the example. What makes it clear:

- **A stage** (inline SVG) with the zones from the big picture and one box per component.
- **Each box carries a kind badge**, colour-coded, e.g. 🐍 Python job, 🤖 LLM, ⚙️ server,
  📄 file / DB, ☁️ cloud service, 👤 human, plus a one-line runtime label
  (`python -m app`, `docker compose`, `Claude Code · Haiku`).
- **A packet** (an emoji in a circle) travels along the real route for each step. Routes
  go around boxes and through intermediaries: a dispatch goes via the orchestrator's
  API server to the container, and cloud traffic goes out over a visible network lane.
  Parallel work (one request fanning out to many targets) is drawn as a fan of lines.
- **One caption per step**: a big emoji plus one short sentence. Separate *judgment*
  from *rules* in the wording ("🤖 Reviewer judges: changes needed. Rule: round 1 of 3,
  so back to the developer").
- **Live state on the stage**: the busy component gets a spinning dashed border, the
  current phase lights up in a pill strip, and counters/locks update in place.
  An LLM "thinking" line to the model provider shows while an AI is working.
- **An info card** (right side) for the hovered/active component:
  what it does · 📍 where it physically runs · 🧩 what it logically is.
- **A "what the user sees" feed** when there is a user-facing surface (PR comments,
  Slack messages, UI states), appearing step by step.
- **Controls**: ⏮ ⏯ ⏭, speed (1× / 2× / ½×), clickable coloured chapter blocks,
  space / ← → keys, autoplay once when scrolled into view.
- Include one realistic detour (a rejection and retry, an ambiguous input, a follow-up
  question), not only the happy path.

## Step 4: The interfaces player

Adapt the code deep-dive player. The user wants **interfaces, not internals**:

- One box per module/component listing only its **interface functions** (the ones
  other components call). Hide internal helpers. At most, list them greyed out as
  "internals (hidden)".
- Mark each box ✨ pure (no I/O) or ⚡ I/O, and colour it by layer (entry, parse, decide,
  act, adapter).
- A separate column **outside the process** (behind a dashed divider) for external
  systems: APIs, servers, containers, databases, collectors.
- Write the scenarios as full call sequences, then filter them in code: drop any call
  whose caller and callee are in the same module, and after each adapter call insert
  the wire-level hop to the external system (`WIRE` map: request text and reply).
- Solid line for a call carrying the real argument, dashed for a return carrying the
  real value (`Command(approve-plan)`, `Transition(dev-pending)`).
- A **call stack panel** (newest on top, external frames included) and a **state panel**
  that flashes when persisted state changes.
- 2–3 scenarios in tabs, each with coloured chapters.

## Step 5: Words

- A title, then pictures. Text is labels, captions and at most one `💡` tip line per
  section, stating the single insight of that view.
- Captions are one short sentence. No paragraphs anywhere.
- Prefer an emoji or icon plus 1–3 words over a sentence.

## Step 6: Build rules

- **One self-contained `.html` file.** Inline CSS and JS, inline SVG, no build step, no
  external requests except optionally Google Fonts. Films are inlined as base64 by
  `ve-manim embed` (or kept in a `media/` folder with `--external` if the user wants a
  small HTML file).
- Colours as CSS tokens on `:root`, with a dark theme under
  `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])`
  and again under `:root[data-theme="dark"]`, and a ◐ toggle button. `body` gets an
  explicit background.
- Honour `prefers-reduced-motion`: no animation, the player jumps between steps, films
  don't autoplay.
- Works at phone width: grids collapse, SVGs scale, no horizontal page scroll.
- Animations should carry meaning (flowing arrows show direction, pulses show
  activity). Sections fade in on scroll.

## Step 7: Verify before handing over

- `node --check` the extracted `<script>` contents.
- Run the player data through Node with a stubbed DOM (see the stub pattern:
  a `mk()` object with `setAttribute`, `appendChild`, `classList`,
  `getComputedTextLength`, `getTotalLength`, `getPointAtLength`). Assert:
  - every step references a node/row that exists;
  - every chapter index is valid;
  - in the interfaces player, calls and returns balance, with no leftover
    intra-module calls;
  - counters end at the values the captions claim.
- If Chrome is installed, take a headless screenshot of the page (light and dark) and
  look at it. Kill it after ~90 s, because pages with many films can hang headless Chrome.
- Films: review every final film's contact sheet once (`ve-manim sheet`).
- Re-check each factual claim on the page against the source once more.
- Say plainly that you have not watched it play if you only checked it
  programmatically or through screenshots.

## Step 8: Deliver

- Write the file to the scratchpad directory (or where the user says), then `open` it
  in the browser.
- Reply with a short summary of the sections and anything notable you found while
  reading the source, and offer to save it into the repo (e.g. `docs/architecture.html`)
  or publish it.
- Iterate on feedback by editing the same file. When the user corrects a concept
  (e.g. "that's not a manager, it's pure code"), fix it on **every** view that shows
  it, films included.

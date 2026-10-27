---
name: visual-explain
description: Use when the user asks to explain, show, walk through or help them understand something — a project, codebase, architecture, system, pipeline, workflow, data flow, paper, concept or process ("explain me X", "how does X work", "show me the structure of X", "I don't get X", "spiegami visivamente X"). The user understands visually, not textually, so the answer is a self-contained HTML page of schematic diagrams (layer matrices, stage pipelines, before/after, BPMN processes) and step-by-step animated replays with very few words, not a text explanation. Rendered 3b1b manim films are an opt-in extra, made only when the user asks for them.
user-invocable: true
argument-hint: <what to explain — a repo, a component, a flow, a paper, a concept> [with manim films]
---

# Visual Explain

The user learns from **pictures, not paragraphs**. When they ask for an explanation,
the deliverable is one self-contained HTML page that shows it visually: schematic
diagrams, step-by-step replays, and a few words on each. Opening it in a browser should
be enough to understand the subject.

## The visual language (default for every page)

The user picked this style from their own reference images. Match it:

- **Schematic and quiet.** White (or near-black) background, thin slate outlines, small
  radius, mono labels for real names (`stg_hubspot__owner_history`, `POST /api/v1/x`),
  sans for short titles. Caps eyebrow labels for columns, rows and kinds (`LAKE`,
  `SOURCES`, `DECISION`). **No emoji inside diagrams**, no gradients, no colour per
  component.
- **Colour carries meaning, nothing else.** Blue fill = new / where something starts.
  Blue dashed outline = modified. Grey dotted = link or alias. Grey dashed = off the
  happy path. One highlighted blue rule = a hard boundary (catalog, network, account).
  Amber = what is happening *now* in a replay. Every page has a legend for the
  encodings it uses.
- **Structure from a grid.** Rows and columns mean something (layer × source, stage ×
  flow, today × with-change, lane × time). Boxes in a column share a width, boxes in
  a row share a centre line, so arrows are straight.
- **Motion = a replay you can step through.** The flagship view is a replay in the
  style of `nicobailon/visual-explainer`'s `replay.gif`: the whole picture stays drawn,
  each step lights the route that fired, dots travel along it, counters and slots in
  the boxes update, and one caption says what happened *and why*, with the source
  reference (`retry.ts:22`). Controls: ← Play/Pause slider → speed.

**Start from the kit**: `reference/kit.html` in this skill's directory. Copy its
`VE KIT CSS` and `VE KIT JS` blocks whole into the new page, then copy and adapt the
figures you need. Never invent a new engine or restyle the kit. The kit's JS draws
every arrow from `<i class="ve-e" data-from data-to>` specs, so you place boxes on a
grid and never compute coordinates. It also reports layout errors (see Step 7).

| Figure type          | Use it for                                                             | In `kit.html` (search for)    |
|----------------------|------------------------------------------------------------------------|-------------------------------|
| Layer matrix         | where things live: layers/schemas × sources/domains, a boundary line    | `FIG: LAYER MATRIX`           |
| Stage pipeline       | how data/requests move through stages (zones), one row per flow         | `FIG: STAGE PIPELINE`         |
| Before / after       | a change: "today" row and "with X" row on the same columns              | `FIG: BEFORE / AFTER REPLAY`  |
| State machine replay | a mechanism: facts, decisions, effects, states, queues/slots, retries   | `FIG: STATE MACHINE REPLAY`   |
| BPMN process         | who does what: actors, hand-offs, waits, approvals, splits, messages    | `FIG: BPMN REPLAY`            |

Any static figure becomes a replay by adding `data-replay` to the figure, an
`<ol class="ve-cap">` with one `<li>` per step, `data-s` on what each step lights, and
`<i class="ve-tok">` dots on routes. The attribute reference is the comment at the top
of `VE KIT JS`.

`reference/example-architecture.html` is an older, emoji-heavy page. Use it only for
the **mechanics** of the interfaces player (call stack panel, `WIRE` hops, call/return
balancing; search `CODE DEEP-DIVE PLAYER`, `const WIRE=`, `function iface`) and restyle
whatever you take in the kit's visual language.

### BPMN, when the subject is a process

Use BPMN 2.0 notation (a small, correct subset) whenever the explanation is about a
business or operational process with more than one actor: approvals, on-call, request
handling, release flows, onboarding, an Airflow/dbt run seen from the people around it.
Don't use it for data lineage or code structure (use the matrix or pipeline).

- **Pool** = one participant (team, company, system). **Lane** = a role inside it.
  `bp-pool`, `bp-lane`, `bp-ph` / `bp-lh` headers.
- **Events** `bp-ev`: start (thin), `mid` intermediate (double), `end` (thick); icons
  `data-icon="msg|send|timer|error"`. **Tasks** `bp-task` with `data-icon="user|service|script|send"`
  (`new` fill = automated / new). **Gateways** `bp-gw`: exclusive (×, default), `par` (+),
  `inc` (○); label the question on the gateway (`PII?`) and the answers on the outgoing
  flows (`yes` / `no`). Data: `bp-data`, `bp-store`.
- **Sequence flow** = solid arrow, only inside a pool. **Message flow** = `msg` edge
  (dashed, open circle → open arrow), only between pools. **Association** = `dot noarrow`.
- Every split gateway has a matching join, every path reaches an end event, and the
  replay's dot is the BPMN token: it waits on a user task, splits on `par`, takes one
  branch on ×.

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

1. **Who's who.** One box per component: caps kind eyebrow (`SERVICE`, `LLM`, `TABLE`,
   `HUMAN`, `CRON`), a name and a 2–4 word role. **Give people-roles only to humans and
   LLMs.** Deterministic code is a `SCRIPT` / `RULE` / `TABLE`, "plain code, no AI".
   Never call a script a "manager" or a "brain".
2. **Big picture.** Every component, placed inside **zones that show where it runs**
   (stage pipeline columns or a layer matrix): managed cloud, server, container,
   laptop. Say explicitly what is *not* there ("no EC2") when that is a natural question.
3. **Replay of one real scenario**, trigger to finish (see Step 3). To compare old and
   new, use a before / after figure with both rows on the same columns.
4. **Interfaces.** An animated view of calls **between** components only, plus the calls
   that leave the process to external systems (see Step 4).
5. Optional: a lifecycle/state diagram, a "what you can type/do" grid, a metrics or
   data pipeline, a folder tree, an interactive "toggle the options" explorer.
6. **BPMN** when people or teams hand work to each other (see *BPMN* above).
7. **Films** only when approved (see *Manim films: opt-in only*): one film per
   concept, each in its own section with a fact-chip row and one 💡 line.

Skip anything that only restates another view. Do not show vanity numbers (lines of
code, file counts): they explain nothing.

## Step 3: The replay

Build it on the kit's replay engine (state machine or before / after figure). What
makes it clear:

- **The whole system stays drawn.** Steps never add or remove boxes; they light the
  boxes and edges that fire (`data-s`), so the reader keeps one mental map.
- **Each box says what kind of thing it is** with a caps eyebrow (`FACT`, `DECISION`,
  `EFFECT`, `STATE`, or `SERVICE`, `LLM`, `TABLE`, `HUMAN`) and where it runs in the
  sub-line (`python -m app`, `Airflow · KPO`, `Redshift`, `Claude · Haiku`).
- **Numbered edges** (`data-n`) when order matters, labels for the mechanism
  (`replica`, `ref`, `POST /runs`, `compact`).
- **Dots travel the real route** (`ve-tok`, `data-route="e1 e2"`): through the
  intermediaries, never straight across. Bursts use `data-n`, fan-outs use one token
  per branch, messages between pools use `data-kind="msg"`.
- **Live state in the boxes**: counters (`5 / 8`), slots and rows that fill
  (`ve-rows`, `data-only`), values that change (`ve-val` + `data-since`).
- **One caption per step**, one sentence: what happened, *because* why, and the
  source reference. Separate judgment from rules ("The reviewer judges: changes
  needed. Rule: round 1 of 3, so back to the developer").
- Include one realistic detour (a rejection and retry, a timeout, an unchanged row),
  not only the happy path.
- Autoplay once when scrolled into view, ←/→/space keys; the kit does this.

## Step 4: The interfaces player

Adapt the code deep-dive player. The user wants **interfaces, not internals**:

- Draw it in the kit's visual language (boxes, mono names, amber for the active call).
- One box per module/component listing only its **interface functions** (the ones
  other components call). Hide internal helpers. At most, list them greyed out as
  "internals (hidden)".
- Mark each box `PURE` (no I/O) or `I/O` in its eyebrow, and group boxes by layer
  (entry, parse, decide, act, adapter) in grid columns, not by colour.
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

- A title that states the finding ("A timeout costs one job 2 s, not the whole queue"),
  then pictures. Text is labels, captions and at most one `💡` tip line per section,
  stating the single insight of that view.
- Captions are one short sentence. No paragraphs anywhere.
- Labels are 1–3 words or a real identifier. Mark made-up values "illustrative" in the
  figure caption (`Fig. n`).

## Step 6: Build rules

- **One self-contained `.html` file**, starting from the kit blocks. Inline CSS and JS,
  no build step, no external requests (the kit uses system fonts). Films are inlined as base64 by
  `ve-manim embed` (or kept in a `media/` folder with `--external` if the user wants a
  small HTML file).
- Use the kit's tokens only (light + dark, ◐ toggle, `?theme=dark` for screenshots).
  Add a new token only for a new *meaning*, and add it to the legend.
- `prefers-reduced-motion` is handled by the kit: no dots, the player jumps between
  steps, films don't autoplay.
- Phone width: each figure frame scrolls sideways inside itself (`--min` on the grid);
  the page never scrolls horizontally.
- Motion carries meaning (dots show direction, amber shows activity). No decorative
  animation.

## Step 7: Verify before handing over

- Run `tools/ve-check page.html` (in this skill's directory). It `node --check`s every
  inline script, loads the page in headless Chrome, prints the kit's error report
  (missing ids, steps out of range, overlapping boxes, **edges that cross a box**) and
  writes `light.png`, `dark.png` and `phone.png`. Fix every reported error, then
  **look at the screenshots**: labels on top of boxes, wrapped identifiers, elbows
  where a straight line was meant (row boxes of different heights: add
  `align-items:stretch` on the grid), empty space.
- For the interfaces player (not on the kit engine), run its data through Node with a stubbed DOM (see the stub pattern:
  a `mk()` object with `setAttribute`, `appendChild`, `classList`,
  `getComputedTextLength`, `getTotalLength`, `getPointAtLength`). Assert:
  - every step references a node/row that exists;
  - every chapter index is valid;
  - in the interfaces player, calls and returns balance, with no leftover
    intra-module calls;
  - counters end at the values the captions claim.
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

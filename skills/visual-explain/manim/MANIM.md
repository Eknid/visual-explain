# Manim films for visual-explain (opt-in only)

Rendered explainer films with **3b1b manim** (`manimgl`, the OpenGL version from
github.com/3b1b/manim, *not* Manim Community). Read this file only after the user has
asked for manim, or has said yes when you offered it (see the gate in `SKILL.md`).

Films are expensive: each one is ~120–200 lines of Python, one or two draft renders, a
contact-sheet review and a final render. Budget **≤ 2 review rounds per film**, and look
at contact sheets, not single frames.

`<skill-dir>` below is the "Base directory for this skill" printed when the skill loads.
Run the CLI as `"<skill-dir>/manim/ve-manim" …`, prefixed with `VE_DATA="${CLAUDE_PLUGIN_DATA}"`.
When the skill comes from the plugin, Claude Code fills that path in. Elsewhere it
expands to empty and `ve-manim` finds the venv itself. Shell state doesn't persist
between Bash calls, so repeat the prefix on every call.

## 1. Environment

```bash
VE_DATA="${CLAUDE_PLUGIN_DATA}" "<skill-dir>/manim/ve-manim" status    # "ready · manimgl==1.7.2 …" or why not
VE_DATA="${CLAUDE_PLUGIN_DATA}" "<skill-dir>/manim/ve-manim" doctor    # venv, ffmpeg, LaTeX, fonts, log tail
```

- **Plugin install**: a SessionStart hook installs the renderer in the background the
  first time (about 1–2 min, ~500 MB on disk). If `status` says *installing*, wait and re-check.
  Don't start a second install.
- **Not installed** (plain-skill install, or opted out with `VE_AUTO_INSTALL=0`): ask the
  user before running `ve-manim install`, because it downloads packages.
- The venv holds `manimgl==1.7.2`, `imageio-ffmpeg` (ffmpeg symlinked into `venv/bin`),
  and `manimpango` for text. No LaTeX unless `doctor` says so.
- Headless Linux needs a GL context: `export VE_WRAP='xvfb-run -a'` (with xvfb installed).

## 2. Workflow

1. **Facts first.** Same rule as the page: every number and name in a film comes from the
   source. Label made-up examples (row ids, sample values) as illustrative on the page.
2. **Storyboard before code.** Write a table per film: beat → caption (≤ 1 short
   sentence) → what moves. One concept per film, 4–8 beats, 20–30 s. Typically 4–8
   films per page. Show the storyboard to the user if the scope is unclear.
3. **Scaffold**: `ve-manim new <proj>` creates `<proj>/scenes/` with `common.py`
   (house style), `custom_config.yml` (background, fps) and `s1_example.py`.
   One file per film: `s1_<topic>.py` holding `class S1Topic(Base)`.
4. **Draft render**: `ve-manim render <proj> s1_topic.py S1Topic` (480p). It prints the
   video path or the traceback tail. Full log: `scenes/.last-render.log`.
5. **Review**: `ve-manim sheet <proj> S1Topic` gives one PNG of 6 frames, 2 per row,
   with the timestamps printed. Read that single image. Check for overlaps, text running
   off-frame, captions colliding with content, arrows crossing labels, and wrong facts.
   For one exact moment: `ve-manim frames <proj> S1Topic 7.5,12`.
6. **Fix and re-draft** (at most twice), then the **final**: `ve-manim render <proj> s1_topic.py --hd`.
   Leaving out the scene name renders every scene in the file. A 1080p film runs ~20 s
   to render on Apple Silicon and comes out at ~1–1.5 MB per 25 s.
7. **Embed** (see §6), then run the page checks from `SKILL.md` Step 7.

Render many films in one background Bash call (loop over files with `--hd`) and write
the HTML page while they render.

## 3. manimgl essentials (1.7.x)

**Scene lifecycle.** `manimgl file.py Scene -w`: `config.py` parses flags and merges
`default_config.yml` with `custom_config.yml` from the working directory.
`extract_scene` finds the Scene classes *defined in that file* (imported ones such as
`Base` are skipped). Then `Scene.run()` calls `setup()` → `construct()` → `tear_down()`.
Each `self.play(*anims)` begins the animations, steps through frames calling
`interpolate(alpha)` and the mobject updaters, has the camera capture each frame, and
pipes it to ffmpeg through `SceneFileWriter`.
Library layout: `animation/`, `camera/`, `mobject/` (geometry, `svg/text_mobject`,
numbers, shape_matchers, coordinate_systems, types/vectorized_mobject), `scene/`,
`shaders/` (GLSL), `utils/` (rate_functions, color, space_ops).

**CLI** (always pass `-w`. Without it manimgl opens an interactive window and blocks):
`-w` write file · `-l` 480p · `-m` 720p · `--hd` 1080p · `--uhd` 4K · `-sw` save only the
last frame as PNG (plain `-s` opens a window and hangs) · `-a` all scenes in file · `-n 3,6` render animations 3–6 only · `-t`
transparent · `-r 1280x720` · `--fps 60` · `-c "#000"` background · `--video_dir DIR` ·
`--file_name NAME` · `-i` gif. Never use `-o`/`--finder` (they open apps), `-e`/`self.embed()`
or `checkpoint_paste()` (IPython, interactive only), or `-p` presenter mode.

**Coordinates.** Frame height 8, width ≈ 14.22, origin at the centre. Directions `UP DOWN
LEFT RIGHT UL UR DL DR ORIGIN`. Buffs: `SMALL_BUFF` 0.1, `MED_SMALL_BUFF` 0.25,
`MED_LARGE_BUFF` 0.5, `LARGE_BUFF` 1. `FRAME_WIDTH`, `FRAME_HEIGHT`.

**Mobjects (no LaTeX needed)**: `Rectangle(width, height)`, `RoundedRectangle(…, corner_radius)`,
`Square(side_length)`, `Circle(radius)`, `Dot(point, radius)`, `Line(a, b)`,
`DashedLine(a, b, dash_length)`, `Arrow(a, b, buff, thickness, fill_color)` (filled
arrow), `StrokeArrow`, `Arc`, `ArcBetweenPoints(a, b, angle).add_tip(width=, length=)`,
`Polygon(*pts)`, `VGroup(*mobs)`, `SurroundingRectangle(m, buff)`, `BackgroundRectangle`,
`Cross(m)`, `Underline`, `Text(s, font=, font_size=, weight=BOLD, t2c={"word": color},
t2f=, t2s=, t2w=)`, `MarkupText` (Pango markup), `Integer(n)`, `DecimalNumber(x,
num_decimal_places=)`, `NumberPlane`, `Axes(x_range, y_range, width, height)` with
`c2p`/`p2c`/`get_graph(fn)`, `ValueTracker`, `SVGMobject`, `ImageMobject`.
**Need LaTeX** (avoid unless `doctor` shows it): `Tex`, `TexText`, `Brace`, `BraceLabel`,
`Matrix`/`IntegerMatrix`, axis labels made with Tex, `TransformMatchingTex`.

**Layout**: `.move_to(pt|mob)`, `.shift(vec)`, `.next_to(mob, DIR, buff)`, `.to_edge(DIR, buff)`,
`.to_corner(UL, buff)`, `.align_to(mob|pt, DIR)`, `.arrange(DIR, buff, aligned_edge)`,
`.arrange_in_grid(n_rows, n_cols, buff)`, `.set_width/height`, `.set_max_width`, `.scale`,
`.rotate(angle)`, `.stretch_to_fit_width(w, about_edge=LEFT)`. Getters: `get_center/left/
right/top/bottom/corner(UL)`, `get_x/get_y`, `get_width/height`.
**Style**: `.set_fill(color, opacity)`, `.set_stroke(color, width, opacity)`, `.set_color`,
`.set_opacity` (the whole family: fill *and* stroke). Hex strings are fine.

**Animations**: `ShowCreation`, `Uncreate`, `Write`, `DrawBorderThenFill`, `FadeIn(m, shift=,
scale=)`, `FadeOut(m, shift=)`, `FadeTransform`, `GrowArrow`, `GrowFromCenter`,
`GrowFromEdge(m, LEFT)`, `Transform`, `ReplacementTransform`, `TransformFromCopy`,
`TransformMatchingStrings`, `TransformMatchingShapes`, `Indicate(m, color, scale_factor)`,
`Flash(point, color, flash_radius)`, `FlashAround`, `ShowPassingFlash`, `CircleIndicate`,
`MoveAlongPath(m, path)`, `Rotate`, `ShowIncreasingSubsets`, `ChangeDecimalToValue(num, v)`,
`CountInFrom`, `UpdateFromAlphaFunc(m, lambda m, a: …)`, `LaggedStart(*anims, lag_ratio)`,
`LaggedStartMap(FadeIn, group, lag_ratio)`, `AnimationGroup`, `Succession`.
The `.animate` builder: `m.animate.shift(RIGHT).set_color(RED)`, `m.animate.become(other)`.
`self.play(..., run_time=, rate_func=, lag_ratio=)`. Rate functions: `smooth` (default),
`linear`, `there_and_back`, `rush_into`, `rush_from`, `double_smooth`, `overshoot`, `lingering`.

**Updaters** (things that follow other things): `m.add_updater(lambda m: m.next_to(x, UP))`,
`m.add_updater(lambda m, dt: m.rotate(dt))`, `always_redraw(lambda: Line(a.get_center(), b.get_center()))`,
`always(m.next_to, x, UP)`, `f_always(m.set_x, tracker.get_value)`,
`ValueTracker(0)` animated with `t.animate.set_value(5)`. Call `clear_updaters()` before
moving a mobject by hand.

**Camera**: `self.frame` (a `CameraFrame`): `self.play(self.frame.animate.scale(0.6).move_to(x))`
zooms. `frame.reorient(theta, phi)` / `set_euler_angles` for 3D (rarely useful here).

The official example scenes (`AnimatingMethods`, `TextExample`, `UpdatersExample`,
`CoordinateSystemExample`, `GraphExample`, `OpeningManimExample`) demonstrate the
`.animate` syntax, `t2c`/`t2f` text styling, updaters with `ValueTracker`, and `Axes`
graphs. Most of their math examples need LaTeX.

## 4. House style (`common.py`)

- `class S1Topic(Base)` with `num = "1"` and `title = "…"` draws the numbered title.
  `self.say("caption", *anims)` swaps the bottom caption while playing other animations.
  Every beat gets a caption.
- Palette: dark film background, one meaning per colour across the page: `HILITE` gold =
  the thing we follow (the key), `BAD` red = slow/costly path, `GOOD` green = the better
  path, `DATA` blue = files/storage, `INDEX` violet, `NEUTRAL` slate. Helpers: `T`
  (text), `M` (mono), `box`, `chip`, `card`, `file_icon`, `arrow`, `hop` (small curved
  arrow), `counter`, `band` (highlight several things at once).
- Keep content inside y ∈ [-3.0, 3.0] (the title is above, the caption below) and x ∈ [-6.6, 6.6].
- Fonts: Avenir Next / Menlo on macOS, DejaVu on Linux; override with `VE_FONT_SANS` /
  `VE_FONT_MONO`. `doctor` lists the installed preferred fonts.
- Seed `random` so re-renders are identical.

## 5. Gotchas (all hit in real projects)

- **Two animations on one mobject in one `play`** fight, and the last one wins
  (`ChangeDecimalToValue(n, 5)` + `n.animate.set_color(...)`). Use two `play` calls.
- **Restoring dimmed things**: `set_opacity(1)` makes faint fills fully opaque. Keep a
  `.copy()` from before dimming and swap it back in.
- **Unicode**: write literal characters (`·`, `→`, `①`, `×`) in the source. `\uXXXX`
  escapes get rewritten by editors and break later string replacements.
- **Imports**: `from common import *` works because `ve-manim render` runs inside
  `scenes/` with it on `PYTHONPATH`. Plain `manimgl` from elsewhere fails with
  `No module named 'common'`.
- **Short curved arrows**: `CurvedArrow` tips scale with length and look like blobs. Use
  `hop(a, b)` (`ArcBetweenPoints(...).add_tip(width=0.14, length=0.14)`) and connect
  top-centres, not adjacent corners.
- **Arrows crossing labels**: route around (elbow points), move the label, or replace a
  fan of arrows with one `band([...])` plus a single arrow.
- **Counters** shrink as digits drop: arrange label and number with `aligned_edge=LEFT`.
- **Overlap with the header**: anything above y ≈ 2.9 (including tags that stick out of
  a box's top edge) collides with the title. Shrink or lower the box.
- **Long text**: `set_max_width(…)` captions and labels. Check wraps in the sheet.

## 6. Embedding films in the page

- Use the block from `<skill-dir>/manim/film-player.html`: CSS, one section per film
  with `src="vid:SceneClass"` and `poster="poster:SceneClass"`, and the script.
  **No native `controls`**: they cover the burned-in captions. The snippet adds a bar
  under the video (play, seek, time, speed, fullscreen), autoplays muted at ≥ 60%
  visibility, pauses the others, and honours `prefers-reduced-motion`.
- Under each film: a `facts` chip row (the numbers it shows) and one `💡` tip line.
  No paragraphs.
- `ve-manim embed <proj>/page.html <proj>/index.html` inlines every film as base64, with
  a poster from its last frame, so the page is one self-contained file (expect ≈ 1.3 ×
  the total MP4 size). `--external` writes `media/` next to the output instead, for
  pages over ~25 MB or when the user wants small HTML.
- The films complement the interactive SVG views, they don't replace them: keep the
  who's-who cards and the E2E player when the subject has a flow.

## 7. Worked example

`<skill-dir>/manim/examples/spotify-rap/`: eight films explaining Spotify's
"Indexing the Data Lake for Online Point Queries" (RAP). Patterns worth copying:

| File                | Pattern                                                                   |
|---------------------|---------------------------------------------------------------------------|
| `s1_haystack.py`    | big grid of tiny squares + counter funnel (90,000 → 90 → 12)              |
| `s2_chain.py`       | request/response dots, a timeline of sequential blocks, "waits" hops      |
| `s3_lookup.py`      | O(1) bucket hit, 12 parallel ranged reads, two-lane timeline comparison   |
| `s4_index.py`       | table built row by row, multimap highlight, append-only fragment stack    |
| `s5_concentrate.py` | sort animation, hash-bucket band, co-grouping collapse, 365 → 52 regroup  |
| `s6_bytes.py`       | strip of key runs re-laid as pages / frames, block-alignment padding      |
| `s7_reads.py`       | N reads + slowest-wins bars, blob merge, interleave, covering index       |
| `s8_lake.py`        | secondary-index arrows, range coalescing, scan band, economics cards      |

These use an older `common.py` with different colour names (`KEY`, `SQL`, `RAP`, …).
Copy the patterns, not the palette.

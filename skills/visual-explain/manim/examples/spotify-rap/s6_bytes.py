from common import *

RUNS = [5, 7, 4, 6, 3, 3, 6, 5, 6, 4, 7, 4]       # rows per key, sorted by key
GOLD = 5                                           # index of user 42's run
SHADES = ["#3c4f78", "#4b3f73", "#2f5d63", "#5a4a3a", "#38506a", KEY, "#5b3f5a", "#3f5a45",
          "#4a4f5e", "#3c4f78", "#4b3f73", "#2f5d63"]
PAGE_W = 11.4
X0 = -PAGE_W / 2
Y = 1.05


def strip(unit, x0=X0, y=Y, h=1.0, gaps=None, headers=False, pad=None):
    """One rectangle per key run; optionally gaps + header blocks, or a padding block before GOLD."""
    g, x = VGroup(), x0
    extras = VGroup()
    for i, n in enumerate(RUNS):
        if pad is not None and i == GOLD:
            p = Rectangle(width=pad, height=h).set_stroke(MUTE, 1).set_fill(MUTE, 0.25).move_to([x + pad / 2, y, 0])
            extras.add(p)
            x += pad
        if headers:
            hd = Rectangle(width=0.1, height=h).set_stroke(width=0).set_fill(INK, 0.85).move_to([x + 0.05, y, 0])
            extras.add(hd)
            x += 0.1
        w = n * unit
        r = Rectangle(width=w, height=h).set_stroke(BG, 1).set_fill(SHADES[i], 1).move_to([x + w / 2, y, 0])
        g.add(r)
        x += w + (gaps or 0)
    return g, extras


class S6Bytes(Base):
    num = "6"
    title = "Read fewer bytes"

    def construct(self):
        unit = PAGE_W / sum(RUNS)
        runs, _ = strip(unit)
        page = Rectangle(width=PAGE_W, height=1.0).set_stroke(FILE, 3).move_to([0, Y, 0])
        page_l = T("1 Parquet page · up to ~4 MB · unprepared file", 18, FILE).next_to(page, UP, buff=0.15).align_to(page, LEFT)
        gold = runs[GOLD]
        gold_l = T("~100 bytes for user 42", 17, KEY).next_to(gold, DOWN, buff=0.5)
        gold_ln = Line(gold_l.get_top(), gold.get_bottom(), stroke_width=2).set_stroke(KEY)
        rd = chip("RAP reader", RAP, 20).move_to([-5.4, -1.35, 0])
        self.say("On unmodified files, RAP still fetches the whole page that holds the row.",
                 FadeIn(runs, lag_ratio=0.05), ShowCreation(page), FadeIn(page_l), FadeIn(rd), run_time=1.4)
        self.play(FadeIn(gold_l), ShowCreation(gold_ln), run_time=0.6)
        a = arrow(rd.get_top(), page.get_bottom() + 4.0 * LEFT, SQL)
        amp = T("read amplification: megabytes in, 100 bytes used", 18, SQL).next_to(rd, RIGHT, buff=0.4)
        self.play(GrowArrow(a), page.animate.set_stroke(SQL, 5), FadeIn(amp), run_time=0.9)
        self.wait(1.4)

        # --- one page per key ---------------------------------------------------------
        n_runs = len(RUNS)
        unit2 = (PAGE_W - n_runs * 0.1 - (n_runs - 1) * 0.07) / sum(RUNS)
        runs2, heads = strip(unit2, gaps=0.07, headers=True)
        outlines = VGroup(*[SurroundingRectangle(VGroup(hd, r), buff=0.0).set_stroke(FILE, 2) for hd, r in zip(heads, runs2)])
        self.play(FadeOut(VGroup(a, amp, gold_l, gold_ln)), page.animate.set_stroke(FILE, 3), run_time=0.5)
        self.say("One page per key: the writer starts a new page whenever the key changes.",
                 ReplacementTransform(runs, runs2), FadeOut(page), FadeIn(heads), FadeIn(outlines),
                 page_l.animate.become(T("one page per key · still standard Parquet", 18, FILE).move_to(page_l).align_to(page_l, LEFT)),
                 run_time=1.6)
        hdr_l = T("≈ 20 B page header per key", 16, INK).next_to(heads[0], DOWN, buff=0.55).align_to(outlines, LEFT)
        hdr_ln = Line(hdr_l.get_top() + 0.6 * LEFT + 0.4 * RIGHT, heads[0].get_bottom(), stroke_width=1.5).set_stroke(INK)
        self.play(FadeIn(hdr_l), ShowCreation(hdr_ln), run_time=0.6)
        a2 = arrow(rd.get_top(), outlines[GOLD].get_bottom(), RAP)
        ans = T("the whole page is the answer · its location lives in the index entry", 18, RAP)
        ans.next_to(rd, RIGHT, buff=0.4)
        self.play(GrowArrow(a2), outlines[GOLD].animate.set_stroke(RAP, 4), FadeIn(ans), run_time=0.9)
        self.wait(1.6)

        # --- ZSTD frame resets ------------------------------------------------------------
        runs3, _ = strip(unit)
        page3 = Rectangle(width=PAGE_W, height=1.0).set_stroke(FILE, 3).move_to([0, Y, 0])
        bounds = VGroup(*[Line(r.get_corner(UR), r.get_corner(DR)).set_stroke(INK, 2.5) for r in runs3[:-1]])
        self.play(FadeOut(VGroup(a2, ans, hdr_l, hdr_ln)), run_time=0.4)
        self.say("Or keep normal page sizes and compress each key as its own ZSTD frame.",
                 ReplacementTransform(runs2, runs3), FadeOut(heads), FadeOut(outlines), FadeIn(page3),
                 page_l.animate.become(T("1 conventional page · one ZSTD frame per key", 18, FILE).move_to(page_l).align_to(page_l, LEFT)),
                 run_time=1.4)
        self.play(ShowCreation(bounds, lag_ratio=0.1), run_time=0.8)
        std = chip("standard reader", FILE, 18).move_to([-5.15, 2.35, 0])
        std_a = Arrow(page3.get_corner(UL) + 0.25 * UP, page3.get_corner(UR) + 0.25 * UP, buff=0,
                      fill_color=FILE, thickness=2.5)
        std_l = T("frames simply concatenate: decompresses as normal", 16, FILE).next_to(std, RIGHT, buff=0.3)
        page_l.set_opacity(0)
        self.play(FadeIn(std), GrowArrow(std_a), FadeIn(std_l), run_time=1.0)
        a3 = arrow(rd.get_top(), runs3[GOLD].get_bottom(), RAP)
        r3l = T("RAP jumps to one frame: (offset, size) per column is in the index", 18, RAP).next_to(rd, RIGHT, buff=0.4)
        self.play(GrowArrow(a3), runs3[GOLD].animate.set_stroke(RAP, 4), FadeIn(r3l), run_time=0.9)
        rule = chip("each frame must decode alone → PLAIN or dictionary, no delta / RLE", SQL, 16, fill=0.12, bold=False)
        rule.next_to(r3l, DOWN, buff=0.22).align_to(r3l, LEFT)
        self.play(FadeIn(rule, shift=0.15 * UP), run_time=0.6)
        self.wait(1.6)

        # --- storage alignment -----------------------------------------------------------
        self.play(FadeOut(VGroup(std, std_a, std_l, rule, a3, r3l)), page_l.animate.set_opacity(1), run_time=0.5)
        gx0 = runs3[GOLD].get_left()[0]
        gx1 = runs3[GOLD].get_right()[0]
        bw = 1.25
        boundary = gx0 + 0.8 * (gx1 - gx0)                  # a block boundary cuts through the frame
        start = boundary - bw * np.ceil((boundary - X0) / bw)
        blocks = VGroup()
        x = start
        while x < X0 + PAGE_W + 1.6:
            blocks.add(Rectangle(width=bw, height=0.42).set_stroke(GCS, 1.5).set_fill(GCS, 0.12).move_to([x + bw / 2, -0.15, 0]))
            x += bw
        blk_l = T("storage blocks (e.g. 4 KB)", 16, MUTE).next_to(blocks, DOWN, buff=0.1).align_to(page3, LEFT)
        ticks = VGroup(*[DashedLine([b.get_left()[0], Y - 0.5, 0], [b.get_left()[0], -0.36, 0], dash_length=0.06)
                         .set_stroke(GCS, 1, 0.6) for b in blocks])
        self.say("Storage alignment: a fetch that straddles a block boundary reads two blocks.",
                 FadeIn(blocks), FadeIn(blk_l), FadeIn(ticks), run_time=1.0)
        hit = [b for b in blocks if b.get_right()[0] > gx0 and b.get_left()[0] < gx1]
        two = T(f"{len(hit)} block reads", 20, SQL, bold=True).next_to(rd, RIGHT, buff=0.4)
        self.play(*[b.animate.set_fill(SQL, 0.6).set_stroke(SQL, 2) for b in hit], FadeIn(two), run_time=0.8)
        self.wait(0.8)

        pad = boundary - gx0  # shifting the frame right by `pad` puts its start exactly on `boundary`
        padding = Rectangle(width=pad, height=1.0).set_stroke(MUTE, 1).set_fill(MUTE, 0.35).move_to([gx0 + pad / 2, Y, 0])
        hatch = VGroup(*[Line([gx0 + i * 0.09, Y - 0.5, 0], [gx0 + i * 0.09 + 0.09, Y + 0.5, 0]).set_stroke(INK, 1, 0.5)
                         for i in range(int(pad / 0.09))])
        after = VGroup(*runs3[GOLD:], *bounds[GOLD - 1:])
        pad_l = T("skippable frame (padding)", 16, MUTE).next_to(padding, UP, buff=0.55)
        pad_ln = Line(pad_l.get_bottom(), padding.get_top(), stroke_width=1.5).set_stroke(MUTE)
        self.play(*[b.animate.set_fill(GCS, 0.12).set_stroke(GCS, 1.5) for b in hit], FadeOut(two), run_time=0.4)
        self.say("Pad with a ZSTD skippable frame so the key's data starts on a block boundary.",
                 after.animate.shift(pad * RIGHT), page3.animate.stretch_to_fit_width(PAGE_W + pad, about_edge=LEFT),
                 run_time=1.2)
        self.play(FadeIn(padding), FadeIn(hatch), FadeIn(pad_l), ShowCreation(pad_ln), run_time=0.6)
        g0, g1 = runs3[GOLD].get_left()[0], runs3[GOLD].get_right()[0]
        hit2 = [b for b in blocks if b.get_right()[0] > g0 + 1e-3 and b.get_left()[0] < g1 - 1e-3]
        one = T(f"{len(hit2)} block read · file stays valid Parquet", 20, RAP, bold=True).next_to(rd, RIGHT, buff=0.4)
        self.play(*[b.animate.set_fill(RAP, 0.6).set_stroke(RAP, 2) for b in hit2], FadeIn(one), run_time=0.8)
        self.wait(2.2)

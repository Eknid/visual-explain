from common import *
import random

KEY_COLORS = {11: "#3c4f78", 23: "#4b3f73", 37: "#2f5d63", 42: KEY, 57: "#5a4a3a", 64: "#38506a",
              78: "#5b3f5a", 85: "#3f5a45", 93: "#4a4f5e"}


class S5Concentrate(Base):
    num = "5"
    title = "Concentrate each key's data"

    def construct(self):
        random.seed(11)
        # 24 rows, 4 pages; 7 keys smaller than 42 so sorted 42s land inside page 2
        keys = [57, 23, 42, 85, 11, 64, 93, 37, 78, 42, 57, 23, 64, 42, 85, 11, 78, 93, 37, 64, 11, 57, 42, 85]
        cw, ch, ig, pg = 0.42, 0.62, 0.03, 0.2
        slots = []
        x = -5.6
        for i in range(24):
            slots.append(np.array([x + cw / 2, 1.2, 0]))
            x += cw + (pg if i % 6 == 5 else ig)
        cells = VGroup()
        for k, p in zip(keys, slots):
            r = Rectangle(width=cw, height=ch).set_stroke(width=0).set_fill(KEY_COLORS[k], 1)
            t = M(str(k), 14, BG if k == 42 else INK).move_to(r)
            cells.add(VGroup(r, t).move_to(p))
        pages = VGroup()
        for j in range(4):
            grp = VGroup(*[Rectangle(width=cw, height=ch).move_to(slots[j * 6 + i]) for i in range(6)])
            fr = SurroundingRectangle(grp, buff=0.06).set_stroke(FILE, 2).set_fill(opacity=0)
            pages.add(VGroup(fr, T(f"page {j + 1}", 16, FILE).next_to(fr, UP, buff=0.08)))
        col_l = M("user_id column", 16, MUTE).next_to(pages, LEFT, buff=0.25).shift(0.0 * UP)
        col_l.next_to(pages, UP, buff=0.5).align_to(pages, LEFT)

        cnt = Integer(4, font_size=56).set_color(SQL)
        cnt_l = T("pages to fetch\nfor user 42", 18, MUTE)
        counter = VGroup(cnt, cnt_l).arrange(RIGHT, buff=0.2).move_to([0, -0.5, 0])

        self.say("Unsorted: user 42's rows are spread over every page.",
                 FadeIn(col_l), FadeIn(pages), LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.03), run_time=1.6)
        hot = [j for j in range(4) if any(keys[j * 6 + i] == 42 for i in range(6))]
        self.play(*[pages[j][0].animate.set_stroke(SQL, 4) for j in hot], FadeIn(counter), run_time=0.8)
        self.wait(1.0)

        # --- sort by key -----------------------------------------------------------
        order = sorted(range(24), key=lambda i: (keys[i], i))
        new_pos = {idx: slots[n] for n, idx in enumerate(order)}
        self.say("Sort by key: all of user 42's rows sit together, in as few pages as possible.",
                 *[pages[j][0].animate.set_stroke(FILE, 2) for j in range(4)], run_time=0.6)
        self.play(*[cells[i].animate.move_to(new_pos[i]) for i in range(24)], run_time=2.0)
        self.play(pages[1][0].animate.set_stroke(RAP, 4), ChangeDecimalToValue(cnt, 1), run_time=0.8)
        self.play(cnt.animate.set_color(RAP), run_time=0.3)
        self.wait(1.2)

        # --- hash bucketing ----------------------------------------------------------
        strip = VGroup(cells, pages, col_l, counter)
        self.play(FadeOut(strip, shift=0.3 * UP), run_time=0.6)
        days = ["Mon", "Tue", "Wed"]
        part = VGroup()
        for d in days:
            col = VGroup(*[file_icon(FILE, 0.45, 0.58) for _ in range(4)]).arrange(DOWN, buff=0.12)
            lbl = T(f"day={d}", 16, MUTE).next_to(col, UP, buff=0.12)
            bl = VGroup(*[M(f"bucket {i}", 12, MUTE).next_to(col[i], LEFT, buff=0.1) for i in range(4)])
            part.add(VGroup(col, lbl, bl))
        part.arrange(RIGHT, buff=1.0).move_to([1.6, 0.55, 0])
        k42 = chip("user 42", KEY, 22).move_to([-4.8, 0.55, 0])
        hk = T("hash(42) % 4 = 2", 18, KEY).next_to(k42, DOWN, buff=0.15)
        tools = T("Spark bucketing · Scio SMB · Iceberg bucket transforms", 16, MUTE).move_to([0.6, -2.4, 0])
        self.say("Hash bucketing goes further: each key maps to exactly one file per partition.",
                 FadeIn(part, lag_ratio=0.1), FadeIn(k42), FadeIn(hk), run_time=1.2)
        band = SurroundingRectangle(VGroup(*[VGroup(p[0][2], p[2][2]) for p in part]), buff=0.08).set_stroke(KEY, 2.5)
        arrs = VGroup(arrow(hk.get_right(), band.get_left(), KEY, thickness=2.5))
        self.play(GrowArrow(arrs[0]), ShowCreation(band),
                  *[p[0][2][0].animate.set_fill(KEY, 0.8).set_stroke(KEY) for p in part], FadeIn(tools), run_time=1.2)
        self.wait(1.4)

        # --- co-grouping ---------------------------------------------------------------
        self.play(FadeOut(VGroup(part, k42, hk, arrs, tools, band)), run_time=0.6)
        hdr = ["user_id", "timestamp", "track_uri", "duration_ms"]
        vals = [["42", "08:02", "track:A", "213000"], ["42", "08:06", "track:B", "187000"],
                ["42", "08:09", "track:C", "201000"], ["42", "18:40", "track:D", "176000"]]
        w = [1.25, 1.45, 1.55, 1.75]

        def trow(vs, head=False):
            g = VGroup()
            for v, ww in zip(vs, w):
                r = Rectangle(width=ww, height=0.42).set_stroke(FILE, 1, 0.6).set_fill(FILE, 0.3 if head else 0.06)
                g.add(VGroup(r, (T(v, 15, INK, bold=True) if head else M(v, 15, KEY if v == "42" else INK)).move_to(r)))
            return g.arrange(RIGHT, buff=0)

        tbl = VGroup(trow(hdr, True), *[trow(v) for v in vals]).arrange(DOWN, buff=0).move_to([-3.0, 0.3, 0])
        sql = M("SELECT user_id,\n  ARRAY_AGG(STRUCT(timestamp, track_uri, duration_ms))\nFROM streams GROUP BY user_id",
                15, IDX).move_to([0, 2.45, 0])
        self.say("Co-grouping: one row per key, with the values in a repeated column.",
                 FadeIn(tbl, lag_ratio=0.1), FadeIn(sql), run_time=1.2)
        self.wait(0.5)
        one = VGroup(
            VGroup(Rectangle(width=1.25, height=0.5).set_stroke(RAP, 1.5).set_fill(RAP, 0.1), M("42", 16, KEY)),
            VGroup(Rectangle(width=5.6, height=0.5).set_stroke(RAP, 1.5).set_fill(RAP, 0.1),
                   M("[ {08:02, A, 213000}, {08:06, B, 187000}, … ×4 ]", 14, INK)),
        )
        for g in one:
            g[1].move_to(g[0])
        one.arrange(RIGHT, buff=0)
        one_h = VGroup(T("user_id", 15, INK, bold=True), T("plays: ARRAY<STRUCT<…>>", 15, INK, bold=True))
        one_h[0].next_to(one[0], UP, buff=0.1)
        one_h[1].next_to(one[1], UP, buff=0.1)
        res = VGroup(one_h, one).move_to([3.3, 0.3, 0])
        ar = arrow(tbl.get_right(), res.get_left(), RAP)
        tag = T("1 row per key per file, no sort order needed", 16, RAP).next_to(res, DOWN, buff=0.25)
        self.play(GrowArrow(ar), TransformFromCopy(VGroup(*[r[0] for r in tbl[1:]]), one[0]),
                  TransformFromCopy(VGroup(*[VGroup(*r[1:]) for r in tbl[1:]]), one[1]), FadeIn(one_h), run_time=1.6)
        self.play(FadeIn(tag), run_time=0.5)
        self.wait(1.4)

        # --- coarser partitioning ---------------------------------------------------------
        self.play(FadeOut(VGroup(tbl, sql, one, one_h, ar, tag)), run_time=0.6)
        sq = 0.17
        days_g = VGroup()
        for d in range(365):
            wk, dow = divmod(d, 7)
            days_g.add(Square(side_length=sq).set_stroke(width=0).set_fill(FILE, 0.75)
                       .move_to([-5.6 + wk * (sq + 0.045), 1.2 - dow * (sq + 0.045), 0]))
        days_g.move_to(0.55 * UP)
        yr = T("one year of daily partitions", 17, MUTE).next_to(days_g, UP, buff=0.18).align_to(days_g, LEFT)
        n = Integer(365, font_size=60).set_color(SQL)
        n_l = T("files per key per year", 18, MUTE)
        ctr = VGroup(n, n_l).arrange(RIGHT, buff=0.25).next_to(days_g, DOWN, buff=0.45)
        self.say("Coarser partitions: fewer files per key, so fewer index entries and fewer reads.",
                 ShowIncreasingSubsets(days_g), FadeIn(yr), FadeIn(ctr), run_time=1.8)
        self.wait(0.6)
        weeks = VGroup()
        for wk in range(52):
            grp = VGroup(*days_g[wk * 7:(wk + 1) * 7])
            weeks.add(RoundedRectangle(width=sq, height=grp.get_height() if wk < 52 else 0.1, corner_radius=0.04)
                      .set_stroke(width=0).set_fill(RAP, 0.85).move_to(grp))
        extra = days_g[364:]
        yr2 = T("one year of weekly partitions", 17, MUTE).move_to(yr).align_to(yr, LEFT)
        self.play(*[ReplacementTransform(VGroup(*days_g[wk * 7:(wk + 1) * 7]), weeks[wk]) for wk in range(52)],
                  FadeOut(extra), ChangeDecimalToValue(n, 52),
                  ReplacementTransform(yr, yr2), run_time=1.8)
        self.play(n.animate.set_color(RAP), run_time=0.3)
        trade = T("trade-off: batch queries prune by week instead of by day", 16, MUTE).next_to(ctr, DOWN, buff=0.2)
        self.play(FadeIn(trade), run_time=0.5)
        self.wait(2.0)

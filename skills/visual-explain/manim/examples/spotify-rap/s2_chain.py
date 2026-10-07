from common import *


class S2Chain(Base):
    num = "2"
    title = "Inside one file: a chain of dependent reads"

    def construct(self):
        # --- reader ------------------------------------------------------------
        rbox = box(2.3, 1.15, SQL, fill=0.15)
        rt = VGroup(T("SQL engine", 24, SQL, bold=True), T("Trino / BigQuery", 16, MUTE)).arrange(DOWN, buff=0.06)
        reader = VGroup(rbox, rt.move_to(rbox)).move_to([-5.55, 1.0, 0])
        self.reader = reader

        # --- one Parquet file in GCS --------------------------------------------
        outer = box(7.4, 4.1, FILE, fill=0.05, r=0.18).move_to([1.05, 0.68, 0])
        gcs = chip("GCS object · one of the 12 files", FILE, 18, fill=0.25)
        gcs.next_to(outer, UP, buff=-0.17).align_to(outer, LEFT).shift(0.25 * RIGHT)
        cx0, cw, cg = -0.75, 1.62, 0.13
        col_x = [cx0 + i * (cw + cg) + cw / 2 for i in range(3)]
        heads = VGroup(*[M(n, 16, KEY if i == 0 else MUTE) .move_to([x, 2.38, 0])
                         for i, (n, x) in enumerate(zip(["user_id", "track_uri", "duration_ms"], col_x))])

        def chunk(x, y, color):
            pw = (cw - 3 * 0.06) / 4
            pages = VGroup(*[Rectangle(width=pw, height=0.52).set_stroke(color, 1.5).set_fill(color, 0.18)
                             for _ in range(4)]).arrange(RIGHT, buff=0.06)
            return pages.move_to([x, y, 0])

        rg_y = [1.85, 1.12, 0.39]
        rgs, rg_lbls, stats = [], VGroup(), VGroup()
        for i, y in enumerate(rg_y):
            row = VGroup(*[chunk(x, y, FILE) for x in col_x])
            rgs.append(row)
            rg_lbls.add(T(f"Row group {i + 1}", 18, INK).move_to([-1.95, y + 0.1, 0]))
        stat_txt = ["keys 1–39", "keys 40–77", "keys 78–120"]
        for i, y in enumerate(rg_y):
            stats.add(M(stat_txt[i], 13, MUTE).move_to([-1.95, y - 0.17, 0]))
        pidx = Rectangle(width=3 * cw + 2 * cg, height=0.32).set_stroke(IDX, 1.5).set_fill(IDX, 0.15)
        pidx.move_to([col_x[1], -0.32, 0])
        pidx_l = T("Page indexes", 17, IDX).move_to([-1.95, -0.32, 0])
        footer = Rectangle(width=3 * cw + 2 * cg, height=0.42).set_stroke(GCS, 1.5).set_fill(GCS, 0.35)
        footer.move_to([col_x[1], -0.86, 0])
        footer_l = T("Footer (metadata)", 17, INK).move_to([-1.95, -0.86, 0])
        file_grp = VGroup(outer, gcs, heads, *rgs, rg_lbls, pidx, pidx_l, footer, footer_l)

        self.say("To find user 42 in one file, the engine must discover where to look.",
                 FadeIn(reader, shift=0.3 * RIGHT), FadeIn(file_grp, lag_ratio=0.02), run_time=1.6)
        self.wait(0.6)

        # --- timeline -------------------------------------------------------------
        axis = Arrow([-6.6, -2.38, 0], [6.7, -2.38, 0], buff=0, fill_color=MUTE, thickness=1.5)
        axis_l = T("time", 16, MUTE).next_to(axis.get_end(), DOWN, buff=0.08).shift(0.25 * LEFT)
        legend = T("each red block = 1 round trip to GCS (30–100 ms) · the next can't start until it returns",
                   15, MUTE).move_to([-0.2, -2.68, 0])
        self.play(GrowArrow(axis), FadeIn(axis_l), FadeIn(legend), run_time=0.7)

        self.cursor = -6.45
        self.blocks = VGroup()

        def block(label, w, color=SQL, h=0.44, fill=0.85, ink=BG):
            b = Rectangle(width=w, height=h).set_stroke(color, 1.5).set_fill(color, fill)
            b.move_to([self.cursor + w / 2, -2.1, 0])
            lbl = T(label, 15, ink, bold=True).move_to(b)
            if lbl.get_width() > w - 0.08:
                lbl.set_width(w - 0.08)
            self.cursor += w + 0.04
            g = VGroup(b, lbl)
            self.blocks.add(g)
            return g

        def trip(targets, blk, run_time=1.6, color=SQL):
            if not isinstance(targets, list):
                targets = [targets]
            a = reader.get_right()
            paths = [Line(a, t.get_left() + 0.05 * RIGHT) for t in targets]
            wires = VGroup(*[DashedLine(p.get_start(), p.get_end(), dash_length=0.08).set_stroke(color, 1.5, 0.7)
                             for p in paths])
            dots = VGroup(*[Dot(radius=0.09).set_fill(color, 1).move_to(a) for _ in targets])

            def mover(d, p):
                return lambda m, al: m.move_to(p.point_from_proportion(1 - abs(2 * al - 1)))

            self.add(wires, dots)
            self.play(*[UpdateFromAlphaFunc(d, mover(d, p)) for d, p in zip(dots, paths)],
                      GrowFromEdge(blk, LEFT),
                      *[t.animate.set_stroke(KEY, 3) for t in targets], run_time=run_time)
            self.remove(wires, dots)

        # 1. footer
        b1 = block("① footer", 1.45)
        self.say("① Fetch the footer: one round trip just to read the map.")
        trip(footer, b1)
        self.play(footer.animate.set_fill(KEY, 0.35).set_stroke(GCS, 1.5), run_time=0.4)
        self.wait(0.3)

        # 2. parse row-group metadata (CPU, no I/O)
        b2 = block("parse", 0.4, color=GCS, fill=0.6, ink=INK)
        self.say("Parse the row-group metadata: only row group 2 can hold user 42.",
                 FadeIn(stats, lag_ratio=0.2), GrowFromEdge(b2, LEFT), run_time=1.2)
        rg_frame = SurroundingRectangle(VGroup(rgs[1], rg_lbls[1]), buff=0.07).set_stroke(KEY, 2.5)
        self.play(ShowCreation(rg_frame),
                  *[m.animate.set_opacity(0.25) for m in [rgs[0], rgs[2], rg_lbls[0], rg_lbls[2], stats[0], stats[2]]],
                  run_time=0.8)
        self.wait(0.4)

        # 3. scan the key column
        key_chunk = rgs[1][0]
        b3 = block("② key column", 1.45)
        self.say("② Scan the key column of row group 2 to find user 42's rows.")
        trip(key_chunk, b3)
        scan = Line(key_chunk.get_corner(UL) + 0.05 * UP, key_chunk.get_corner(DL) + 0.05 * DOWN).set_stroke(KEY, 3)
        self.play(scan.animate.move_to(key_chunk.get_right()), run_time=0.9, rate_func=linear)
        hit = key_chunk[2]
        hit_mark = Rectangle(width=hit.get_width() * 0.7, height=0.12).set_fill(KEY, 1).set_stroke(width=0).move_to(hit)
        self.play(FadeOut(scan), FadeIn(hit_mark, scale=0.5), hit.animate.set_stroke(KEY, 3), run_time=0.5)
        rows_l = T("rows found", 14, KEY).next_to(key_chunk, DOWN, buff=0.05)
        self.play(FadeIn(rows_l), run_time=0.3)
        self.wait(0.3)

        # 4. page indexes
        b4 = block("③ page index", 1.45)
        self.say("③ Read the page indexes: which page of each column holds those rows?")
        trip(pidx, b4)
        tgt_a, tgt_b = rgs[1][1][1], rgs[1][2][3]
        pl = VGroup(*[Line(pidx.get_top(), t.get_bottom()).set_stroke(IDX, 2) for t in (tgt_a, tgt_b)])
        self.play(ShowCreation(pl), tgt_a.animate.set_stroke(IDX, 3), tgt_b.animate.set_stroke(IDX, 3), run_time=0.8)
        self.wait(0.3)

        # 5. value pages, one read per column
        b5 = VGroup(block("④ track_uri page", 1.65, h=0.2), )
        self.cursor -= 1.65 + 0.04
        b5b = block("④ duration_ms page", 1.65, h=0.2)
        b5b.shift(0.11 * DOWN)
        b5[0].shift(0.11 * UP)
        self.say("④ Fetch those pages: one more read per value column.")
        self.add(b5b)
        b5b.set_opacity(0)
        trip([tgt_a, tgt_b], b5[0])
        self.play(b5b.animate.set_opacity(1), run_time=0.3)
        self.play(tgt_a.animate.set_fill(KEY, 0.9), tgt_b.animate.set_fill(KEY, 0.9), FadeOut(pl), run_time=0.5)
        self.wait(0.6)

        # waits-for arrows
        rtts = [b1, b3, b4, b5[0]]
        waits = VGroup(*[
            ArcBetweenPoints(rtts[i][0].get_top() + 0.04 * UP, rtts[i + 1][0].get_top() + 0.04 * UP,
                             angle=-PI / 2.5).set_stroke(KEY, 2.5).add_tip(width=0.14, length=0.14)
            for i in range(3)
        ])
        self.say("Every step waits for the one before: 4 round trips in a row, per file.",
                 LaggedStart(*[ShowCreation(w) for w in waits], lag_ratio=0.3), run_time=1.4)
        self.wait(1.4)

        # engine overhead before any read
        shift = 3.55
        over = Rectangle(width=shift - 0.15, height=0.44).set_fill(SQL, 0.25).set_stroke(SQL, 1.5)
        over.move_to([-6.45 + (shift - 0.15) / 2, -2.1, 0])
        over_l = T("scheduling + planning: seconds", 15, SQL, bold=True).move_to(over)
        brk = VGroup(*[Line(ORIGIN, 0.5 * UP).rotate(-0.4).set_stroke(INK, 2) for _ in range(2)]).arrange(RIGHT, buff=0.08)
        brk.move_to(over.get_right() + 0.25 * LEFT)
        self.say("Before any read, a distributed SQL engine spends seconds on scheduling and planning.",
                 VGroup(self.blocks, waits).animate.shift(shift * RIGHT), run_time=1.0)
        self.play(GrowFromEdge(over, LEFT), FadeIn(over_l), FadeIn(brk), run_time=1.0)
        self.wait(1.2)

        # times 12, IOPS contention
        x12 = VGroup(T("× 12 files", 26, SQL, bold=True), T("× every column", 18, SQL)).arrange(DOWN, buff=0.04)
        x12.move_to([5.85, -1.55, 0])
        iops = T("and every round trip competes for IOPS with all the other queries", 15, KEY).move_to(legend)
        self.play(FadeIn(x12, shift=0.2 * LEFT), run_time=0.6)
        self.say("Bucketing and Bloom filters pick the files. They don't fix the reads inside them.",
                 FadeOut(legend), FadeIn(iops), run_time=0.9)
        self.wait(2.2)

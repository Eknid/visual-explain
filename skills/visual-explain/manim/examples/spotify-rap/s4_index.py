from common import *


class S4Index(Base):
    num = "4"
    title = "The external index"

    def construct(self):
        # --- 1. build from existing files -------------------------------------
        files = VGroup(*[file_icon(FILE, 0.62, 0.8) for _ in range(3)]).arrange(DOWN, buff=0.25)
        files.move_to([-5.7, 0.6, 0])
        files_l = T("existing Parquet files\n(unmodified)", 17, FILE).next_to(files, DOWN, buff=0.15)
        bbox = box(2.6, 1.15, GCS, fill=0.2)
        builder = VGroup(bbox, VGroup(T("Index builder", 22, INK, bold=True), T("pipeline step", 15, MUTE))
                         .arrange(DOWN, buff=0.05).move_to(bbox)).move_to([-1.95, 0.6, 0])
        r1 = arrow(files.get_right() + 0.35 * UP, builder.get_left() + 0.25 * UP, FILE)
        r2 = arrow(files.get_right() + 0.35 * DOWN, builder.get_left() + 0.25 * DOWN, KEY)
        r1l = T("reads footers + page locations", 14, FILE).next_to(r1, UP, buff=0.05)
        r2l = T("scans the key column", 14, KEY).next_to(r2, DOWN, buff=0.05)
        self.say("Works on any existing Parquet files. No special preparation needed.",
                 FadeIn(files, lag_ratio=0.2), FadeIn(files_l), FadeIn(builder), run_time=1.2)
        self.play(GrowArrow(r1), FadeIn(r1l), run_time=0.7)
        self.play(GrowArrow(r2), FadeIn(r2l), run_time=0.7)

        # --- 2. the entry table ---------------------------------------------------
        cols = ["key", "file", "row numbers", "value count"]
        data = [["42", "3", "118–131", "14"], ["42", "7", "9–12", "4"], ["42", "12", "501–540", "40"],
                ["77", "3", "132–140", "9"], ["91", "7", "13–30", "18"]]
        widths = [0.9, 0.9, 1.7, 1.55]
        rows = VGroup()
        for r, vals in enumerate([cols] + data):
            cells = VGroup()
            for c, (v, w) in enumerate(zip(vals, widths)):
                rect = Rectangle(width=w, height=0.42).set_stroke(IDX, 1, 0.6)
                rect.set_fill(IDX, 0.3 if r == 0 else 0.06)
                is_key = r > 0 and vals[0] == "42"
                t = (T(v, 16, INK, bold=True) if r == 0 else M(v, 17, KEY if (is_key and c == 0) else INK)).move_to(rect)
                cells.add(VGroup(rect, t))
            cells.arrange(RIGHT, buff=0)
            rows.add(cells)
        rows.arrange(DOWN, buff=0)
        table = rows.move_to([2.55, 0.75, 0])
        frag_l = T("index fragment", 18, IDX, bold=True).next_to(table, UP, buff=0.12).align_to(table, LEFT)
        w1 = arrow(builder.get_right(), table.get_left(), IDX)
        self.say("It writes compact entries: key, file, row numbers, and an optional value count.",
                 GrowArrow(w1), run_time=0.7)
        self.play(FadeIn(frag_l), LaggedStart(*[FadeIn(r, shift=0.15 * DOWN) for r in rows], lag_ratio=0.15), run_time=1.4)
        self.wait(0.5)

        multi = SurroundingRectangle(VGroup(rows[1], rows[3]), buff=0.04).set_stroke(KEY, 3)
        multi_l = T("multimap: one key, entries in many files", 16, KEY).next_to(table, DOWN, buff=0.18).align_to(table, LEFT)
        self.say("It's a multimap: user 42 has entries in files 3, 7 and 12.",
                 ShowCreation(multi), FadeIn(multi_l), run_time=1.0)
        self.wait(0.8)

        file_col = VGroup(*[rows[i][1] for i in range(len(rows))])
        cnt_col = VGroup(*[rows[i][3] for i in range(len(rows))])
        ann_f = VGroup(T("dictionary-encoded ordinal", 15, MUTE),
                       M("7 → day=2026-07-14/bucket-0421.parquet", 13, FILE)).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        ann_f.next_to(table, UP, buff=0.55).align_to(table, LEFT).shift(0.4 * RIGHT)
        ln_f = Line(ann_f.get_bottom() + 0.6 * LEFT, rows[0][1].get_top(), stroke_width=1.5).set_stroke(MUTE)
        ann_c = T("optional: enables pagination", 15, MUTE).next_to(multi_l, DOWN, buff=0.1).align_to(table, LEFT)
        self.play(FadeIn(ann_f), ShowCreation(ln_f), Indicate(file_col, color=FILE, scale_factor=1.05), run_time=1.0)
        self.play(FadeIn(ann_c), Indicate(cnt_col, color=IDX, scale_factor=1.05), run_time=0.9)
        self.wait(1.2)

        # --- 3. append-only fragments ------------------------------------------------
        frag_grp = VGroup(table, frag_l, multi, multi_l, ann_f, ln_f, ann_c)
        def frag_card(day, new=False):
            c = box(2.9, 0.55, IDX, fill=0.25 if new else 0.1)
            return VGroup(c, T(f"fragment · {day}", 17, IDX if not new else INK, bold=new).move_to(c))
        f1 = frag_card("Jul 14")
        f1.move_to([2.55, 1.6, 0])
        self.play(ReplacementTransform(frag_grp, f1), FadeOut(w1), run_time=1.0)
        stack = VGroup(f1)
        for day in ["Jul 15", "Jul 16"]:
            nf = frag_card(day, new=True).move_to(builder)
            tgt = stack[-1].get_center() + 0.7 * DOWN
            run_l = T(f"pipeline run · {day}", 15, MUTE).next_to(builder, DOWN, buff=0.12)
            self.add(nf)
            self.play(FadeIn(run_l), Flash(builder.get_center(), color=IDX, flash_radius=0.9), run_time=0.5)
            if day == "Jul 15":
                self.say("Every pipeline run appends a new fragment. Old fragments are never rewritten.",
                         nf.animate.move_to(tgt), run_time=0.9)
            else:
                self.play(nf.animate.move_to(tgt), run_time=0.9)
            self.play(stack[-1][0].animate.set_fill(IDX, 0.1), stack[-1][1].animate.set_color(IDX), FadeOut(run_l), run_time=0.3)
            stack.add(nf)
        locks = T("unchanged", 14, MUTE).next_to(VGroup(*stack[:2]), RIGHT, buff=0.2)
        self.play(FadeIn(locks), run_time=0.4)
        self.wait(1.0)

        # --- 4. size + hash bucketing -----------------------------------------------
        left_grp = VGroup(files, files_l, builder, r1, r2, r1l, r2l)
        self.play(FadeOut(left_grp), FadeOut(locks), stack.animate.scale(0.8).move_to([4.6, 1.75, 0]), run_time=0.8)
        sz = VGroup()
        for data_l, idx_l in [("terabytes of data", "gigabytes of index"), ("petabytes of data", "terabytes of index")]:
            d = box(4.2, 0.5, FILE, fill=0.35, r=0.06)
            dl = T(data_l, 16, INK, bold=True).move_to(d)
            ar = T("→", 26, MUTE)
            i = box(0.32, 0.5, IDX, fill=0.8, r=0.06)
            il = T(idx_l, 16, IDX, bold=True)
            sz.add(VGroup(VGroup(d, dl), ar, i, il).arrange(RIGHT, buff=0.18))
        sz.arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([-2.6, 1.3, 0])
        rule = T("rule of thumb (not to scale)", 14, MUTE).next_to(sz, UP, buff=0.14).align_to(sz, LEFT)
        self.say("Rule of thumb: terabytes of data give gigabytes of index; petabytes give terabytes.",
                 FadeIn(rule), LaggedStart(*[FadeIn(s, shift=0.2 * RIGHT) for s in sz], lag_ratio=0.4), run_time=1.4)
        self.wait(0.8)

        shards = VGroup(*[box(1.3, 0.75, IDX, fill=0.15) for _ in range(4)]).arrange(RIGHT, buff=0.22)
        for i, s in enumerate(shards):
            s.add(VGroup(T(f"shard {i}", 15, IDX, bold=True), M(f"hash(key) % 4 = {i}", 11, MUTE)).arrange(DOWN, buff=0.06).move_to(s))
        shards.move_to([2.3, -1.0, 0])
        sh_arrows = VGroup(*[Arrow(stack.get_bottom() + 0.1 * DOWN, s.get_top(), buff=0.1, fill_color=IDX, thickness=1.8)
                             for s in shards])
        self.say("Large indexes split naturally into shards by hashing the key.",
                 LaggedStart(*[GrowArrow(a) for a in sh_arrows], lag_ratio=0.1),
                 LaggedStart(*[FadeIn(s, shift=0.2 * DOWN) for s in shards], lag_ratio=0.15), run_time=1.4)
        self.wait(1.4)

        # --- 5. definitive vs probabilistic -------------------------------------------
        self.play(FadeOut(VGroup(sz, rule, shards, sh_arrows, stack)), run_time=0.7)

        def card(title, sub, line, icon, color):
            c = box(5.6, 3.0, color, fill=0.08, r=0.2)
            ic = T(icon, 64, color, bold=True)
            g = VGroup(ic, T(title, 24, color, bold=True), T(sub, 18, INK), M(line, 15, MUTE)).arrange(DOWN, buff=0.16)
            g.move_to(c)
            return VGroup(c, g)

        left = card("Bloom filter / PageIndex", "probabilistic: narrows a scan", "\"user 42 might be in here\"", "?", SQL)
        right = card("External index", "definitive: no scan at all", "\"file 7, rows 9–12\"", "✓", RAP)
        VGroup(left, right).arrange(RIGHT, buff=0.6).move_to(0.35 * UP)
        self.say("Bloom filters and page indexes say \"maybe\". The external index says \"exactly here\".",
                 FadeIn(left, shift=0.3 * RIGHT), run_time=0.9)
        self.play(FadeIn(right, shift=0.3 * LEFT), run_time=0.9)
        self.play(Indicate(right[1][0], color=RAP, scale_factor=1.3), run_time=0.8)
        self.wait(2.2)

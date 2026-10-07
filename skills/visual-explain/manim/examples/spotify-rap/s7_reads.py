from common import *

Y = 1.2


def seg(w, color, fill=0.25, h=0.8, sw=1.5):
    return Rectangle(width=w, height=h).set_stroke(color, sw).set_fill(color, fill)


class S7Reads(Base):
    num = "7"
    title = "Fewer read operations: the biggest single win"

    def construct(self):
        rd = chip("RAP reader", RAP, 20).move_to([-5.2, -1.3, 0])
        cnt = Integer(3, font_size=64).set_color(SQL)
        cnt_l = T("reads per key,\nper file", 18, MUTE)
        counter = VGroup(cnt, cnt_l).arrange(RIGHT, buff=0.2).move_to([5.0, -1.3, 0])

        # --- 1. column-major: N columns -> N reads --------------------------------
        names = ["track_uri", "duration_ms", "timestamp"]
        chunks, golds, labels = VGroup(), VGroup(), VGroup()
        for i, n in enumerate(names):
            c = seg(3.5, FILE, 0.15)
            chunks.add(c)
        chunks.arrange(RIGHT, buff=0.15).move_to([0, Y, 0])
        for i, (c, n) in enumerate(zip(chunks, names)):
            g = seg(0.32, KEY, 1, sw=0).move_to(c.get_left() + (0.9 + 0.7 * i) * RIGHT)
            golds.add(g)
            labels.add(M(n, 16, FILE).next_to(c, UP, buff=0.1))
        disk = T("one file on disk, column by column", 16, MUTE).next_to(chunks, UP, buff=0.5).align_to(chunks, RIGHT)
        self.say("Normal Parquet: a key's values sit in a different place for every column.",
                 FadeIn(chunks), FadeIn(labels), FadeIn(golds), FadeIn(disk), FadeIn(rd), run_time=1.2)
        arrs = VGroup(*[arrow(rd.get_top(), g.get_bottom(), SQL, thickness=2.5) for g in golds])
        self.play(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.2), FadeIn(counter), run_time=1.0)

        # latency of N parallel reads: you wait for the slowest
        lat = [1.3, 1.7, 3.2]
        bars = VGroup()
        for i, L in enumerate(lat):
            b = Rectangle(width=L, height=0.22).set_stroke(width=0).set_fill(SQL, 0.85)
            bars.add(VGroup(M(f"read {i + 1}", 13, MUTE), b).arrange(RIGHT, buff=0.15))
        bars.arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([0.2, -1.35, 0])
        for b in bars:
            b[1].align_to(bars[0][1], LEFT)
        sx = bars[2][1].get_right()[0]
        slow = DashedLine([sx, bars.get_top()[1] + 0.08, 0], [sx, bars.get_bottom()[1] - 0.04, 0],
                          dash_length=0.06).set_stroke(KEY, 2)
        slow_l = T("key is ready only when the slowest returns", 15, KEY).next_to(bars, DOWN, buff=0.12)
        self.say("N columns means N reads: N× the request capacity, and latency drifts toward the tail.",
                 LaggedStart(*[GrowFromEdge(b[1], LEFT) for b in bars], lag_ratio=0.15),
                 FadeIn(VGroup(*[b[0] for b in bars])), run_time=1.4)
        self.play(ShowCreation(slow), FadeIn(slow_l), run_time=0.6)
        self.wait(1.4)

        # --- 2. blob / variant -> 1 read ----------------------------------------------
        self.play(FadeOut(VGroup(bars, slow, slow_l)), FadeOut(arrs), run_time=0.5)
        blob = seg(10.8, IDX, 0.15).move_to([0, Y, 0])
        blob_g = seg(0.9, KEY, 1, sw=0).move_to(blob.get_left() + 3.2 * RIGHT)
        blob_l = M("doc  (JSON · Protobuf · Parquet Variant)", 16, IDX).next_to(blob, UP, buff=0.1)
        self.say("Blobs and Variants: store the served fields as one column, so one read per file.",
                 ReplacementTransform(chunks, blob), ReplacementTransform(golds, blob_g),
                 ReplacementTransform(labels, blob_l), run_time=1.3)
        a1 = arrow(rd.get_top(), blob_g.get_bottom(), RAP, thickness=3)
        self.play(GrowArrow(a1), ChangeDecimalToValue(cnt, 1), run_time=0.8)
        self.play(cnt.animate.set_color(RAP), run_time=0.3)
        trade = T("trade-off: batch analytics loses per-field pruning inside the blob", 16, MUTE).move_to([0.2, -1.35, 0])
        self.play(FadeIn(trade), run_time=0.5)
        self.wait(1.4)

        # --- 3. interleaving columns ------------------------------------------------------
        self.play(FadeOut(VGroup(a1, trade)), run_time=0.4)
        n = 6
        w = 10.8 / (2 * n) - 0.06
        A = VGroup(*[seg(w, FILE, 0.3) for _ in range(n)])
        B = VGroup(*[seg(w, IDX, 0.3) for _ in range(n)])
        col_major = VGroup(*A, *B).arrange(RIGHT, buff=0.06).move_to([0, Y, 0])
        kA, kB = A[2], B[2]
        for m in (kA, kB):
            m.set_fill(KEY, 1).set_stroke(KEY, 1.5)
        tagsA = VGroup(*[M(f"A{i + 1}", 13, INK).move_to(a) for i, a in enumerate(A)])
        tagsB = VGroup(*[M(f"B{i + 1}", 13, INK).move_to(b) for i, b in enumerate(B)])
        tagsA[2].set_color(BG)
        tagsB[2].set_color(BG)
        for t, s in zip([*tagsA, *tagsB], [*A, *B]):
            s.add(t)
        lblA = M("column A", 16, FILE).next_to(VGroup(*A), UP, buff=0.1)
        lblB = M("column B", 16, IDX).next_to(VGroup(*B), UP, buff=0.1)
        self.say("Interleaving: write column A and column B side by side, key by key.",
                 FadeOut(blob), FadeOut(blob_l), FadeOut(blob_g), FadeIn(col_major), FadeIn(lblA), FadeIn(lblB),
                 disk.animate.become(T("before: column A, then column B", 16, MUTE).move_to(disk).align_to(chunks, RIGHT)),
                 run_time=1.0)
        self.wait(0.4)
        inter_pos = VGroup(*[seg(w, INK) for _ in range(2 * n)]).arrange(RIGHT, buff=0.06).move_to([0, Y, 0])
        moves = []
        for i in range(n):
            moves.append(A[i].animate.move_to(inter_pos[2 * i]))
            moves.append(B[i].animate.move_to(inter_pos[2 * i + 1]))
        self.play(*moves, FadeOut(lblA), FadeOut(lblB),
                  disk.animate.become(T("after: A1 B1 A2 B2 …  each B sits inside a ZSTD skippable frame", 16, MUTE)
                                      .move_to(disk).align_to(chunks, RIGHT)), run_time=1.6)
        fresh = VGroup(*A, *B).copy()
        span = SurroundingRectangle(VGroup(kA, kB), buff=0.05).set_stroke(RAP, 3)
        a2 = arrow(rd.get_top(), span.get_bottom(), RAP, thickness=3)
        self.say("RAP reads both columns for a key in one contiguous range.",
                 ShowCreation(span), GrowArrow(a2), run_time=0.9)
        self.wait(0.6)
        conv = chip("conventional reader of A", FILE, 16).move_to([-4.6, 2.6, 0])
        hops = VGroup(*[ArcBetweenPoints(A[i].get_top() + 0.05 * UP, A[i + 1].get_top() + 0.05 * UP, angle=-PI / 2)
                        .set_stroke(FILE, 2.5).add_tip(width=0.12, length=0.12) for i in range(n - 1)])
        self.say("A normal reader of column A still works: the decompressor silently skips B.",
                 FadeIn(conv), LaggedStart(*[ShowCreation(h) for h in hops], lag_ratio=0.2),
                 *[b.animate.set_opacity(0.35) for i, b in enumerate(B) if i != 2], run_time=1.6)
        dead = T("trade-off: for single-column scans, B is dead space", 16, MUTE).move_to([0.2, -1.35, 0])
        self.play(FadeIn(dead), run_time=0.5)
        self.wait(1.4)

        # --- 4. covering index: 0 reads ------------------------------------------------------
        self.play(FadeOut(VGroup(conv, hops, dead, a2, span, *A, *B)), FadeIn(fresh), run_time=0.5)
        kA, kB = fresh[2], fresh[n + 2]
        cells = []
        for txt, ww, col in [("42", 0.8, KEY), ("f07", 0.9, INK), ("rows 9–12", 1.5, INK), ("value", 1.9, MUTE)]:
            r = Rectangle(width=ww, height=0.5).set_stroke(IDX, 1.5).set_fill(IDX, 0.1)
            cells.append(VGroup(r, M(txt, 15, col).move_to(r)))
        entry = VGroup(*cells).arrange(RIGHT, buff=0).move_to([-1.2, -0.55, 0])
        entry_l = T("index entry", 16, IDX, bold=True).next_to(entry, LEFT, buff=0.2)
        self.say("Covering index: hoist small values into the index entry itself.",
                 FadeIn(entry), FadeIn(entry_l), run_time=0.8)
        cargo = VGroup(kA.copy(), kB.copy())
        val_slot = cells[3][0]
        self.play(cargo.animate.arrange(RIGHT, buff=0.04).set_height(0.36).move_to(val_slot), FadeOut(cells[3][1]), run_time=1.2)
        cross = Cross(fresh, stroke_width=4).set_stroke(SQL, 5, 0.8)
        self.play(ChangeDecimalToValue(cnt, 0), ShowCreation(cross), run_time=0.9)
        aggs = VGroup(*[chip(s, IDX, 15, fill=0.15, bold=False) for s in
                        ["per-key event count", "total play time", "category breakdown"]]).arrange(RIGHT, buff=0.18)
        aggs.next_to(entry, DOWN, buff=0.35).align_to(entry, LEFT)
        self.say("Even pre-computed aggregates. No storage read at all; filters run on the index.",
                 LaggedStart(*[FadeIn(a, shift=0.15 * UP) for a in aggs], lag_ratio=0.2), run_time=1.2)
        self.wait(1.4)
        self.say("Together: one ranged read of a few kilobytes, or no read at all.",
                 Indicate(counter, color=RAP, scale_factor=1.15), run_time=1.0)
        self.wait(2.0)

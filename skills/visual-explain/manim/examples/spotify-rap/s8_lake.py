from common import *


class S8Lake(Base):
    num = "8"
    title = "Secondary indexes, and one lake for both workloads"

    def construct(self):
        # --- 1. secondary indexes over the same entries ------------------------------
        hdr = ["buyer_id", "seller_id", "file", "rows"]
        vals = [["b17", "s05", "f02", "40–44"], ["b17", "s31", "f09", "7–9"], ["b42", "s12", "f02", "45–60"],
                ["b88", "s12", "f05", "3–6"], ["b88", "s14", "f11", "90–97"]]
        w = [1.25, 1.25, 0.9, 1.2]

        def row(vs, head=False):
            g = VGroup()
            for v, ww in zip(vs, w):
                r = Rectangle(width=ww, height=0.42).set_stroke(IDX, 1, 0.6).set_fill(IDX, 0.3 if head else 0.06)
                g.add(VGroup(r, (T(v, 15, INK, bold=True) if head else M(v, 15, INK)).move_to(r)))
            return g.arrange(RIGHT, buff=0)

        table = VGroup(row(hdr, True), *[row(v) for v in vals]).arrange(DOWN, buff=0).move_to([0, 0.75, 0])
        tl = T("transactions · index entries", 17, IDX, bold=True).next_to(table, UP, buff=0.12)
        hb = box(2.6, 1.2, KEY, fill=0.1)
        hash_ix = VGroup(hb, VGroup(T("hash on buyer_id", 18, KEY, bold=True), T("O(1) exact lookup", 15, MUTE))
                         .arrange(DOWN, buff=0.05).move_to(hb)).move_to([-4.9, 0.75, 0])
        sb = box(2.6, 1.2, RAP, fill=0.1)
        sort_ix = VGroup(sb, VGroup(T("sorted on seller_id", 18, RAP, bold=True), T("range queries", 15, MUTE))
                         .arrange(DOWN, buff=0.05).move_to(sb)).move_to([4.9, 0.75, 0])
        self.say("One dataset, many lookup keys: e.g. transactions by buyer and by seller.",
                 FadeIn(table, lag_ratio=0.1), FadeIn(tl), run_time=1.1)
        q1 = M("buyer_id = b88", 15, KEY).next_to(hash_ix, DOWN, buff=0.15)
        a_h = VGroup(*[arrow(hash_ix.get_right(), table[i].get_left(), KEY, thickness=2) for i in (4, 5)])
        self.say("Each access structure is built over the same entries: hash for exact keys...",
                 FadeIn(hash_ix), FadeIn(q1), run_time=0.8)
        self.play(LaggedStart(*[GrowArrow(a) for a in a_h], lag_ratio=0.2),
                  *[table[i][0][0].animate.set_fill(KEY, 0.5) for i in (4, 5)], run_time=0.8)
        q2 = M("seller_id in s10..s14", 15, RAP).next_to(sort_ix, DOWN, buff=0.15)
        rng = [3, 4, 5]
        a_s = VGroup(*[arrow(sort_ix.get_left(), table[i].get_right(), RAP, thickness=2) for i in rng])
        self.say("...and sorted indexes for ranges.", FadeIn(sort_ix), FadeIn(q2), run_time=0.8)
        self.play(LaggedStart(*[GrowArrow(a) for a in a_s], lag_ratio=0.2),
                  *[table[i][1][0].animate.set_fill(RAP, 0.5) for i in rng], run_time=0.8)
        serv = chip("add or drop one in the serving layer · no pipeline change · no data rewrite", IDX, 17, fill=0.9)
        serv.next_to(table, DOWN, buff=0.4)
        self.play(FadeIn(serv, shift=0.2 * UP), run_time=0.6)
        self.wait(1.6)

        # --- 2. coalescing scattered ranges -------------------------------------------------
        self.play(FadeOut(VGroup(table, tl, hash_ix, sort_ix, q1, q2, a_h, a_s, serv)), run_time=0.6)
        segs = VGroup(*[Rectangle(width=0.78, height=0.7).set_stroke(FILE, 1.5).set_fill(FILE, 0.15) for _ in range(13)])
        segs.arrange(RIGHT, buff=0.04).move_to([0, 1.0, 0])
        fl = T("file f02, sorted by buyer_id", 16, FILE).next_to(segs, UP, buff=0.12).align_to(segs, LEFT)
        hits = [3, 4, 9]
        for i in hits:
            segs[i].set_fill(RAP, 0.85).set_stroke(RAP, 1.5)
        rd = chip("RAP reader", RAP, 20).move_to([-5.0, -1.25, 0])
        a3 = VGroup(*[arrow(rd.get_top(), segs[i].get_bottom(), SQL, thickness=2) for i in hits])
        n3 = T("3 ranges", 20, SQL, bold=True).next_to(rd, RIGHT, buff=0.4)
        self.say("A seller lookup scatters across the buyer-sorted layout...",
                 FadeIn(segs), FadeIn(fl), FadeIn(rd), run_time=0.9)
        self.play(LaggedStart(*[GrowArrow(a) for a in a3], lag_ratio=0.15), FadeIn(n3), run_time=0.8)
        self.wait(0.5)
        merged = SurroundingRectangle(VGroup(segs[3], segs[4]), buff=0.04).set_stroke(RAP, 3)
        a2 = VGroup(arrow(rd.get_top(), merged.get_bottom(), RAP, thickness=2.5),
                    arrow(rd.get_top(), segs[9].get_bottom(), RAP, thickness=2.5))
        n2 = T("2 reads", 20, RAP, bold=True).move_to(n3).align_to(n3, LEFT)
        self.say("...but the reader coalesces adjacent byte ranges into one read.",
                 ReplacementTransform(a3, a2), ShowCreation(merged), ReplacementTransform(n3, n2), run_time=1.0)
        zl = T("Z-order / Hilbert curves can also improve layout locality for secondary keys", 16, MUTE)
        zl.next_to(segs, DOWN, buff=0.35)
        self.play(FadeIn(zl), run_time=0.5)
        self.wait(1.4)

        # --- 3. one lake, two access patterns ------------------------------------------------
        self.play(FadeOut(VGroup(segs, fl, rd, a2, merged, n2, zl)), run_time=0.6)
        files = VGroup(*[file_icon(FILE, 0.62, 0.8) for _ in range(12)]).arrange(RIGHT, buff=0.32).move_to([0.9, 0.35, 0])
        lake = T("the same Parquet files in the GCS data lake", 17, FILE).next_to(files, UP, buff=0.14)
        bq = chip("BigQuery · weekly aggregate reports", GCS, 18, fill=0.35).move_to([-4.3, 2.3, 0])
        ag = chip("AI agent via RAP · context retrieval", RAP, 18, fill=0.2).move_to([-4.3, -1.55, 0])
        self.say("The files BigQuery scans for weekly reports...",
                 FadeIn(files, lag_ratio=0.05), FadeIn(lake), FadeIn(bq), run_time=1.0)
        band = Rectangle(width=0.5, height=1.25).set_stroke(width=0).set_fill(GCS, 0.55).move_to(files.get_left() + 0.25 * RIGHT)
        band_l = files.get_left()
        self.add(band)
        self.play(band.animate.stretch_to_fit_width(files.get_width() + 0.3, about_edge=LEFT).shift(0.15 * LEFT),
                  rate_func=linear, run_time=1.6)
        sc = T("full scans · column pruning", 15, MUTE).next_to(bq, RIGHT, buff=0.3)
        self.play(FadeIn(sc), band.animate.set_fill(GCS, 0.2), run_time=0.5)
        picks = [1, 4, 6, 10]
        slivers = VGroup(*[Rectangle(width=0.4, height=0.1).set_stroke(width=0).set_fill(KEY, 1).move_to(files[i]) for i in picks])
        arr = VGroup(*[arrow(ag.get_top(), s.get_bottom() + 0.28 * DOWN, RAP, thickness=1.8, buff=0.06) for s in slivers])
        self.say("...are the same files an AI agent reads, a few kilobytes at a time.",
                 FadeIn(ag), run_time=0.8)
        self.play(LaggedStart(*[GrowArrow(a) for a in arr], lag_ratio=0.12),
                  LaggedStart(*[FadeIn(s, scale=0.4) for s in slivers], lag_ratio=0.12), run_time=1.1)
        no = VGroup(*[chip(s, INK, 18, fill=0.08) for s in ["no copy", "no ETL", "no second storage bill"]]).arrange(RIGHT, buff=0.3)
        no.next_to(ag, RIGHT, buff=0.6)
        self.play(LaggedStart(*[FadeIn(n, shift=0.15 * UP) for n in no], lag_ratio=0.2), run_time=1.0)
        self.wait(1.6)

        # --- 4. economics -------------------------------------------------------------------
        self.play(FadeOut(VGroup(files, lake, bq, ag, band, sc, slivers, arr, no)), run_time=0.6)
        kv = box(2.6, 1.6, SQL, fill=0.12)
        kv_g = VGroup(kv, VGroup(T("KV store", 22, SQL, bold=True), T("Bigtable · DynamoDB", 14, MUTE),
                                 T("$ per GB: only the hot data", 15, INK)).arrange(DOWN, buff=0.08).move_to(kv))
        kv_g.move_to([-4.6, 0.6, 0])
        lk = box(7.2, 3.4, FILE, fill=0.1, r=0.25)
        items = VGroup(*[chip(s, FILE, 17, fill=0.2) for s in ["months & years of history", "long-tail entities",
                                                              "low-traffic features"]]).arrange(DOWN, buff=0.2)
        lk_g = VGroup(lk, VGroup(T("GCS data lake + RAP", 24, FILE, bold=True),
                                 T("a point query costs about one storage read", 16, INK), items)
                      .arrange(DOWN, buff=0.22).move_to(lk)).move_to([2.6, 0.6, 0])
        sizes = VGroup(T("petabytes", 16, SQL).next_to(kv_g, DOWN, buff=0.15),
                       T("exabytes", 18, FILE, bold=True).next_to(lk_g, DOWN, buff=0.15))
        self.say("KV stores force you to pick what's worth keeping online. The lake doesn't.",
                 FadeIn(kv_g), FadeIn(sizes[0]), run_time=0.9)
        self.play(FadeIn(lk_g, scale=0.9), FadeIn(sizes[1]), run_time=1.0)
        self.wait(1.4)
        final = T("The data lake is no longer batch-only.", 40, INK, bold=True)
        sub = T("one dataset · two access patterns", 22, RAP)
        end = VGroup(final, sub).arrange(DOWN, buff=0.25).move_to(0.4 * UP)
        self.play(FadeOut(VGroup(kv_g, lk_g, sizes)), run_time=0.6)
        self.say("Analytical and interactive workloads, served from the same storage.",
                 Write(final), FadeIn(sub, shift=0.2 * UP), run_time=1.6)
        self.wait(2.6)

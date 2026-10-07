from common import *
import random


class S3Lookup(Base):
    num = "3"
    title = "RAP: look up instead of scanning"

    def construct(self):
        random.seed(3)
        ids = [3, 7, 12, 19, 26, 33, 41, 48, 55, 62, 71, 84]
        pages = [4, 1, 7, 2, 5, 8, 3, 6, 0, 9, 2, 5]

        # --- cast -----------------------------------------------------------------
        key = chip("user 42", KEY, 24).move_to([-6.05, 1.75, 0])
        rbox = box(2.3, 1.05, RAP, fill=0.15)
        reader = VGroup(rbox, VGroup(T("RAP reader", 24, RAP, bold=True), T("plain code, no engine", 15, MUTE))
                        .arrange(DOWN, buff=0.05).move_to(rbox)).move_to([-3.45, 1.75, 0])

        ibox = box(2.55, 2.0, IDX, fill=0.08)
        ititle = T("External index", 20, IDX, bold=True).next_to(ibox.get_top(), DOWN, buff=0.12)
        buckets = VGroup(*[Rectangle(width=2.1, height=0.18).set_stroke(IDX, 1).set_fill(IDX, 0.12) for _ in range(6)])
        buckets.arrange(DOWN, buff=0.06).next_to(ititle, DOWN, buff=0.12)
        index = VGroup(ibox, ititle, buckets).move_to([-5.0, -0.45, 0])

        mbox = box(2.55, 2.0, GCS, fill=0.12)
        mtitle = T("Cached file metadata", 19, INK, bold=True).next_to(mbox.get_top(), DOWN, buff=0.12)
        mlines = VGroup(M("f03 footer ✓", 14, MUTE), M("f07 footer ✓", 14, MUTE), M("…", 14, MUTE),
                        T("in memory", 15, RAP)).arrange(DOWN, buff=0.07).next_to(mtitle, DOWN, buff=0.12)
        meta = VGroup(mbox, mtitle, mlines).move_to([-2.05, -0.45, 0])

        # 12 files in GCS, each a strip of pages
        files = VGroup()
        for fid, pg in zip(ids, pages):
            segs = VGroup(*[Rectangle(width=0.21, height=0.19).set_stroke(FILE, 1).set_fill(FILE, 0.2) for _ in range(10)])
            segs.arrange(RIGHT, buff=0.025)
            lbl = M(f"f{fid:02d}", 13, FILE).next_to(segs, LEFT, buff=0.1)
            files.add(VGroup(lbl, segs))
        files.arrange(DOWN, buff=0.1).move_to([4.95, 0.75, 0])
        gcs_l = chip("GCS · the 12 Parquet files", FILE, 17, fill=0.22).next_to(files, UP, buff=0.12)

        self.say("RAP keeps the same 12 files, and adds an index that says exactly where user 42 is.",
                 FadeIn(key), FadeIn(reader), FadeIn(index), FadeIn(meta),
                 FadeIn(files, lag_ratio=0.05), FadeIn(gcs_l), run_time=1.6)
        self.wait(0.6)

        # --- 1. key -> reader -> index ---------------------------------------------
        a1 = arrow(key.get_right(), reader.get_left(), KEY)
        self.play(GrowArrow(a1), run_time=0.5)
        a2 = arrow(reader.get_bottom() + 0.9 * LEFT, index.get_top() + 0.35 * RIGHT, IDX)
        hit_b = buckets[3]
        o1 = chip("O(1)", IDX, 18, fill=0.9).next_to(a2, LEFT, buff=0.1)
        self.say("① Hash the key, jump to its bucket in the index: an O(1) lookup.",
                 GrowArrow(a2), run_time=0.8)
        self.play(hit_b.animate.set_fill(KEY, 0.9).set_stroke(KEY, 2), FadeIn(o1, scale=1.4), run_time=0.6)

        # entries appear
        rows = []
        for _ in ids:
            s0 = random.randint(5, 900)
            rows.append(f"{s0}–{s0 + random.randint(3, 40)}")
        entries = VGroup(*[M(f"f{f:02d} · rows {r}", 14, INK) for f, r in zip(ids, rows)])
        for e, f in zip(entries, files):
            e.move_to([1.05, f.get_y(), 0]).align_to(np.array([0.2, 0, 0]), LEFT)
        ent_t = T("index entries", 16, IDX).next_to(entries, UP, buff=0.12)
        self.say("It returns every (file, rows) entry for user 42: 12 entries, one per file.",
                 LaggedStart(*[TransformFromCopy(hit_b, e) for e in entries], lag_ratio=0.06),
                 FadeIn(ent_t), run_time=1.6)
        self.wait(0.5)

        # --- 2. rows -> page locations via cached metadata -------------------------
        a3 = arrow(reader.get_bottom() + 0.75 * RIGHT, meta.get_top() + 0.3 * RIGHT, GCS)
        new_entries = VGroup(*[M(f"f{f:02d} · page {p} → byte range", 14, RAP) for f, p in zip(ids, pages)])
        for n, e in zip(new_entries, entries):
            n.move_to(e).align_to(e, LEFT)
        self.say("② Cached file metadata turns rows into page byte ranges, in memory.",
                 GrowArrow(a3), run_time=0.8)
        self.play(LaggedStart(*[Transform(e, n) for e, n in zip(entries, new_entries)], lag_ratio=0.05),
                  Indicate(mlines[-1], color=RAP), run_time=1.4)
        self.wait(0.4)

        # --- 3. 12 ranged reads, all at once ---------------------------------------
        targets = [f[1][p] for f, p in zip(files, pages)]
        reads = VGroup(*[arrow(e.get_right(), f[0].get_left(), RAP, buff=0.08, thickness=2)
                         for e, f in zip(entries, files)])
        par = chip("all 12 reads in parallel · 1 round trip", RAP, 17, fill=0.9).next_to(files, DOWN, buff=0.15)
        self.say("③ Fire precise ranged reads at all 12 files at once. Nothing waits on anything.",
                 run_time=0.6)
        self.play(LaggedStart(*[GrowArrow(r) for r in reads], lag_ratio=0.02),
                  FadeIn(par, shift=0.2 * DOWN), run_time=0.9)
        self.play(*[t.animate.set_fill(KEY, 1).set_stroke(KEY, 1.5) for t in targets], run_time=0.5)

        result = chip("user 42's listening history", KEY, 18, fill=0.9).next_to(reader, DOWN, buff=0.16).shift(0.3*RIGHT)
        result.move_to([-3.45, 0.95, 0])
        flyers = VGroup(*[t.copy() for t in targets])
        self.play(FadeOut(VGroup(a2, a3, o1)), run_time=0.3)
        self.play(LaggedStart(*[f.animate.move_to(result).set_opacity(0) for f in flyers], lag_ratio=0.03),
                  FadeIn(result, scale=0.6), run_time=1.2)
        self.remove(flyers)
        self.wait(0.8)

        # --- 4. compare the timelines -------------------------------------------------
        y1, y2 = -1.95, -2.6
        u = 0.62  # width of one storage round trip

        def lane(y, items, label, color):
            x = -4.3
            g = VGroup()
            for txt, w, c, fill in items:
                b = Rectangle(width=w, height=0.42).set_stroke(c, 1.5).set_fill(c, fill).move_to([x + w / 2, y, 0])
                t = T(txt, 14, BG if fill > 0.5 else c, bold=True).move_to(b)
                if t.get_width() > w - 0.06:
                    t.set_width(w - 0.06)
                g.add(VGroup(b, t))
                x += w + 0.04
            lbl = T(label, 18, color, bold=True).next_to([-4.45, y, 0], LEFT, buff=0)
            return VGroup(lbl, g)

        sql = lane(y1, [("scheduling + planning: seconds", 4.4, SQL, 0.25), ("①", u, SQL, 0.85), ("", 0.2, GCS, 0.6),
                        ("②", u, SQL, 0.85), ("③", u, SQL, 0.85), ("④", u, SQL, 0.85)],
                   "SQL engine", SQL)
        rap = lane(y2, [("index", 0.62, IDX, 0.85), ("1 round trip", u * 1.6, RAP, 0.85)], "RAP", RAP)
        brk = VGroup(*[Line(ORIGIN, 0.45 * UP).rotate(-0.4).set_stroke(INK, 2) for _ in range(2)]).arrange(RIGHT, buff=0.08)
        brk.move_to(sql[1][0].get_right() + 0.25 * LEFT)
        self.say("Same answer, same files. RAP skips the engine overhead and the dependent chain.",
                 FadeIn(sql[0]), FadeIn(rap[0]),
                 LaggedStart(*[GrowFromEdge(b, LEFT) for b in sql[1]], lag_ratio=0.3), FadeIn(brk),
                 run_time=2.2)
        self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in rap[1]], lag_ratio=0.4), run_time=1.0)
        self.play(Indicate(rap[1], color=RAP, scale_factor=1.15), run_time=0.8)
        self.wait(1.2)

        tiers = T("The chain costs at every tier: tens of ms per hop on cloud, µs on SSD, ns in memory.", 16, MUTE)
        tiers.next_to(rap, RIGHT, buff=0.5).set_y(y2)
        tiers.set_max_width(6.6).align_to(np.array([-0.5, 0, 0]), LEFT)
        self.play(FadeIn(tiers), run_time=0.6)
        self.wait(2.4)

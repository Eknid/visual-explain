from common import *
import random


class S1Haystack(Base):
    num = "1"
    title = "Finding the needle in the haystack"

    def construct(self):
        random.seed(7)

        # --- the question --------------------------------------------------
        agent = chip("AI agent", IDX, 24)
        q = T("“What was I listening to last summer?”", 30, INK)
        top = VGroup(agent, q).arrange(RIGHT, buff=0.35).move_to(2.65 * UP)
        self.say("An AI agent needs one user's listening history, fast.",
                 FadeIn(agent, shift=0.2 * RIGHT), Write(q), run_time=1.4)
        self.wait(0.8)

        # --- 90 days x 1,000 files ----------------------------------------
        n_cols, n_rows, s, g = 90, 20, 0.105, 0.025
        cells = VGroup(*[
            Square(side_length=s).set_stroke(width=0).set_fill(FILE, 0.55)
            for _ in range(n_cols * n_rows)
        ]).arrange_in_grid(n_rows=n_rows, n_cols=n_cols, buff=g)
        cells.move_to(0.15 * UP + 0.2 * RIGHT)
        cols = [VGroup(*[cells[r * n_cols + c] for r in range(n_rows)]) for c in range(n_cols)]

        days_lbl = T("90 days of summer  →", 22, MUTE).next_to(cells, UP, buff=0.12).align_to(cells, LEFT)
        files_lbl = T("1,000 files / day  →", 22, MUTE).rotate(-PI / 2).next_to(cells, LEFT, buff=0.15)
        nts = T("(drawn compressed)", 16, MUTE).next_to(cells, UP, buff=0.12).align_to(cells, RIGHT)

        counter_lbl = T("files to look at", 22, MUTE)
        counter = Integer(90000, font_size=56).set_color(INK)
        ctr = VGroup(counter, counter_lbl).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        ctr.next_to(cells, DOWN, buff=0.25).align_to(cells, LEFT)

        self.say("90 days × 1,000 Parquet files a day = 90,000 files.",
                 LaggedStart(*[FadeIn(c) for c in cols], lag_ratio=0.03),
                 FadeIn(days_lbl), FadeIn(files_lbl), FadeIn(nts), FadeIn(ctr),
                 run_time=2.4)
        self.wait(1.2)

        # --- bucketing by key ---------------------------------------------
        bucket_row = 7
        row = VGroup(*[cells[bucket_row * n_cols + c] for c in range(n_cols)])
        others = VGroup(*[m for i, m in enumerate(cells) if i // n_cols != bucket_row])
        hash_chain = VGroup(
            chip("user 42", KEY, 22),
            T("→ hash →", 22, MUTE),
            chip("bucket 0421", FILE, 22),
        ).arrange(RIGHT, buff=0.15)
        fname = M("day=2026-07-14/bucket-0421.parquet", 20, FILE)
        side = VGroup(hash_chain, fname).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        side.next_to(cells, DOWN, buff=0.25).align_to(cells, RIGHT)
        row_frame = SurroundingRectangle(row, buff=0.03).set_stroke(KEY, 2)

        self.say("Bucket files by key: the filename says if user 42 can be inside.",
                 FadeIn(side, shift=0.2 * UP), run_time=1.0)
        self.play(others.animate.set_fill(FILE, 0.08), row.animate.set_fill(FILE, 1),
                  ShowCreation(row_frame),
                  ChangeDecimalToValue(counter, 90), run_time=2.0)
        self.wait(1.4)

        # --- Bloom filters ------------------------------------------------
        active = sorted(random.sample(range(n_cols), 12))
        bloom = chip("Bloom filters · cached in a metadata store", IDX, 20)
        bloom.next_to(row_frame, UP, buff=0.12).shift(0.4 * UP)
        bl_arrows = VGroup(*[
            Line(bloom.get_bottom(), row[c].get_top(), stroke_width=1).set_stroke(IDX, 1, 0.5)
            for c in range(0, n_cols, 6)
        ])
        self.say("Bloom filters skip files without opening them: 12 active days left.",
                 FadeIn(bloom, shift=0.2 * DOWN), run_time=1.0)
        self.play(ShowCreation(bl_arrows, lag_ratio=0.05), run_time=0.8)
        self.play(
            *[row[c].animate.set_fill(KEY, 1) for c in active],
            *[row[c].animate.set_fill(FILE, 0.15) for c in range(n_cols) if c not in active],
            ChangeDecimalToValue(counter, 12),
            FadeOut(bl_arrows), run_time=1.6)
        self.wait(1.2)

        # --- the 12 files: selection solved, but... -----------------------
        icons = VGroup(*[file_icon(KEY, 0.62, 0.8) for _ in active]).arrange(RIGHT, buff=0.32)
        icons.move_to(0.1 * DOWN)
        qmarks = VGroup(*[T("?", 30, KEY, bold=True).move_to(ic) for ic in icons])
        sel = VGroup(*[row[c] for c in active])
        self.play(
            FadeOut(VGroup(others, row_frame, bloom, side, days_lbl, files_lbl, nts)),
            *[row[c].animate.set_fill(FILE, 0) for c in range(n_cols) if c not in active],
            run_time=0.8)
        self.play(ReplacementTransform(sel, icons), ctr.animate.next_to(icons, DOWN, buff=0.6),
                  run_time=1.4)
        self.say("Picking files is solved. Finding user 42 inside each big file is not.",
                 LaggedStart(*[FadeIn(qm, scale=1.5) for qm in qmarks], lag_ratio=0.08),
                 run_time=1.4)
        self.wait(1.0)

        hint = T("Inside every file: a chain of dependent reads", 28, SQL, bold=True)
        hint.next_to(icons, UP, buff=0.5)
        self.play(Indicate(icons[0], color=SQL, scale_factor=1.3), FadeIn(hint, shift=0.2 * DOWN))
        self.wait(1.6)

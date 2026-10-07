"""Template film: one concept, ~15 s, a caption per beat. Copy, rename, replace the beats."""
from common import *


class S1Example(Base):
    num = "1"
    title = "Scan versus look up"

    def construct(self):
        # beat 1: the cast
        reader = card("Reader", "plain code", GOOD).move_to([-4.6, 1.0, 0])
        files = VGroup(*[file_icon(DATA) for _ in range(8)]).arrange(RIGHT, buff=0.28).move_to([1.8, 1.0, 0])
        self.say("A reader needs one key out of eight files.",
                 FadeIn(reader, shift=0.3 * RIGHT), LaggedStartMap(FadeIn, files, lag_ratio=0.1), run_time=1.2)

        # beat 2: scanning = one read per file, one after another
        reads = counter(0, "reads", BAD).move_to([-4.6, -1.0, 0])
        self.say("Scanning opens every file in turn.", FadeIn(reads))
        for i, f in enumerate(files):
            self.play(f.animate.set_fill(BAD, 0.6), ChangeDecimalToValue(reads[0], i + 1), run_time=0.25)
        self.wait(0.4)

        # beat 3: an index points straight at the right file
        self.play(*[f.animate.set_fill(DATA, 0.18) for f in files], FadeOut(reads), run_time=0.5)
        idx = chip("index: key → file 6", INDEX, 22).next_to(reader, DOWN, buff=0.5)
        hit = files[5]
        self.say("An index says exactly where to read: one read.", FadeIn(idx, shift=0.2 * UP))
        a = arrow(idx.get_right(), hit.get_bottom(), GOOD)  # runs under the row, crosses nothing
        self.play(GrowArrow(a), hit.animate.set_fill(HILITE, 1), run_time=0.8)
        self.play(ShowCreation(band([hit])), run_time=0.5)
        self.wait(1.5)

"""House style for visual-explain films (3b1b manimgl 1.7).

Import with `from common import *` (ve-manim render puts this folder on PYTHONPATH).
Frame: 16:9, 8 units tall, ~14.22 wide, origin at the centre. Keep content inside
y ∈ [-3.0, 3.0]: the title sits above, the caption below.
"""
import os
import platform

from manimlib import *

# --- palette (dark film background; reads well on light and dark pages) -------------
BG = "#0f1420"
INK = "#e7eaf1"
MUTE = "#8a93a6"
C_BLUE = "#4c8dff"
C_GOLD = "#ffc53d"
C_RED = "#ff6b5b"
C_GREEN = "#2dd4a3"
C_VIOLET = "#a78bfa"
C_SLATE = "#64748b"
C_OTHER = "#3c4760"
# semantic aliases: one meaning per colour across all films of a page
HILITE, BAD, GOOD, DATA, INDEX, NEUTRAL = C_GOLD, C_RED, C_GREEN, C_BLUE, C_VIOLET, C_SLATE

_mac = platform.system() == "Darwin"
SANS = os.environ.get("VE_FONT_SANS", "Avenir Next" if _mac else "DejaVu Sans")
MONO = os.environ.get("VE_FONT_MONO", "Menlo" if _mac else "DejaVu Sans Mono")


def T(s, size=28, color=INK, font=None, bold=False, **kw):
    """Text. Write literal unicode (·, →, ①) in the source, not \\u escapes."""
    t = Text(s, font=font or SANS, font_size=size, weight=BOLD if bold else NORMAL, **kw)
    if "t2c" not in kw:
        t.set_color(color)
    return t


def M(s, size=24, color=INK, **kw):
    return T(s, size=size, color=color, font=MONO, **kw)


def box(w, h, color, fill=0.15, r=0.12, sw=2.5):
    return RoundedRectangle(width=w, height=h, corner_radius=r).set_stroke(color, sw).set_fill(color, fill)


def chip(s, color, size=24, font=None, pad=0.22, fill=0.18, bold=True):
    """Rounded label. fill >= 0.5 switches the text to the background colour."""
    t = T(s, size=size, color=color if fill < 0.5 else BG, font=font, bold=bold)
    b = box(t.get_width() + 2 * pad, t.get_height() + 1.4 * pad, color, fill=fill, r=0.14)
    t.move_to(b)
    return VGroup(b, t)


def card(title, sub, color, w=2.4, h=1.1):
    """Box with a bold title and a muted subtitle: one per component."""
    b = box(w, h, color)
    txt = VGroup(T(title, 22, color, bold=True), T(sub, 15, MUTE)).arrange(DOWN, buff=0.06).move_to(b)
    return VGroup(b, txt)


def file_icon(color=C_BLUE, w=0.5, h=0.64):
    return Polygon([-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2 - w * 0.3, 0],
                   [w / 2 - w * 0.3, h / 2, 0], [-w / 2, h / 2, 0]).set_stroke(color, 2).set_fill(color, 0.18)


def arrow(a, b, color=INK, buff=0.12, thickness=3.0, **kw):
    return Arrow(a, b, buff=buff, fill_color=color, thickness=thickness, **kw)


def hop(a, b, color=C_GOLD, angle=-PI / 2.5):
    """Small curved arrow between two points (CurvedArrow tips are too big for short spans)."""
    return ArcBetweenPoints(a, b, angle=angle).set_stroke(color, 2.5).add_tip(width=0.14, length=0.14)


def counter(value, label, color=INK, size=56):
    """Big number + muted label. Animate with ChangeDecimalToValue(group[0], v)."""
    n = Integer(value, font_size=size).set_color(color)
    return VGroup(n, T(label, 18, MUTE)).arrange(RIGHT, buff=0.2, aligned_edge=DOWN)


def band(mobs, color=C_GOLD, buff=0.08):
    """One highlight rectangle around several things: cleaner than many crossing arrows."""
    return SurroundingRectangle(VGroup(*mobs), buff=buff).set_stroke(color, 2.5)


class Base(Scene):
    """Numbered title top-left, one caption line at the bottom (swap it with self.say)."""
    num = ""
    title = ""

    def setup(self):
        super().setup()
        self.cap = None
        badge = Circle(radius=0.24).set_fill(INK, 1).set_stroke(width=0)
        n = T(self.num, 22, BG, bold=True).move_to(badge)
        ttl = T(self.title, 30, INK, bold=True).next_to(badge, RIGHT, buff=0.2)
        self.header = VGroup(badge, n, ttl).to_corner(UL, buff=0.4)
        self.add(self.header)

    def say(self, s, *anims, run_time=0.8):
        """Swap the caption while playing other animations: self.say("…", FadeIn(x))."""
        new = T(s, 30, INK)
        if new.get_width() > FRAME_WIDTH - 1:
            new.set_width(FRAME_WIDTH - 1)
        new.to_edge(DOWN, buff=0.38)
        grp = VGroup(BackgroundRectangle(new, fill_color=BG, fill_opacity=0.85, buff=0.12), new)
        swap = [FadeIn(grp, shift=0.15 * UP)]
        if self.cap is not None:
            swap.append(FadeOut(self.cap, shift=0.15 * UP))
        self.play(*swap, *anims, run_time=run_time)
        self.cap = grp
        return grp

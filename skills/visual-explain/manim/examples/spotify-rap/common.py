"""Shared look & helpers for the RAP (Random Access Parquet) explainer scenes."""
from manimlib import *

BG = "#0f1420"
INK = "#e7eaf1"
MUTE = "#8a93a6"
DIM = "#2a3242"
FILE = "#4c8dff"    # Parquet files / GCS objects
KEY = "#ffc53d"     # user 42 (the target key)
SQL = "#ff6b5b"     # distributed SQL engine path
RAP = "#2dd4a3"     # RAP path
IDX = "#a78bfa"     # external index
GCS = "#64748b"     # storage
OTHER = "#3c4760"   # other keys' data
OTHER2 = "#4a5672"

SANS = "Avenir Next"
MONO = "Menlo"


def T(s, size=28, color=INK, font=SANS, bold=False, **kw):
    t = Text(s, font=font, font_size=size, weight=BOLD if bold else NORMAL, **kw)
    if "t2c" not in kw:
        t.set_color(color)
    return t


def M(s, size=24, color=INK, **kw):
    return T(s, size=size, color=color, font=MONO, **kw)


def box(w, h, color, fill=0.15, r=0.12, sw=2.5):
    return RoundedRectangle(width=w, height=h, corner_radius=r).set_stroke(color, sw).set_fill(color, fill)


def chip(s, color, size=24, font=SANS, pad=0.22, fill=0.18, bold=True):
    t = T(s, size=size, color=color if fill < 0.5 else BG, font=font, bold=bold)
    b = box(t.get_width() + 2 * pad, t.get_height() + 1.4 * pad, color, fill=fill, r=0.14)
    t.move_to(b)
    return VGroup(b, t)


def file_icon(color=FILE, w=0.5, h=0.64, label=None, size=14):
    body = Polygon(
        [-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2 - w * 0.3, 0],
        [w / 2 - w * 0.3, h / 2, 0], [-w / 2, h / 2, 0],
    ).set_stroke(color, 2).set_fill(color, 0.18)
    g = VGroup(body)
    if label:
        g.add(T(label, size=size, color=color).next_to(body, DOWN, buff=0.06))
    return g


def arrow(a, b, color=INK, buff=0.12, thickness=3.0, **kw):
    return Arrow(a, b, buff=buff, fill_color=color, thickness=thickness, **kw)


class Base(Scene):
    """Title in the top-left corner and one short caption line at the bottom."""
    num = ""
    title = ""

    def setup(self):
        super().setup()
        self.cap = None
        hdr = VGroup(
            T(self.num, 22, BG, bold=True),
        )
        badge = Circle(radius=0.24).set_fill(INK, 1).set_stroke(width=0)
        hdr[0].move_to(badge)
        ttl = T(self.title, 30, INK, bold=True).next_to(badge, RIGHT, buff=0.2)
        self.header = VGroup(badge, hdr[0], ttl).to_corner(UL, buff=0.4)
        self.add(self.header)

    def say(self, s, *anims, run_time=0.8, t2c=None):
        """Swap the caption, optionally playing other animations at the same time."""
        new = T(s, 30, INK, t2c=t2c or {}) if t2c else T(s, 30, INK)
        if new.get_width() > FRAME_WIDTH - 1:
            new.set_width(FRAME_WIDTH - 1)
        new.to_edge(DOWN, buff=0.38)
        bg = BackgroundRectangle(new, fill_color=BG, fill_opacity=0.85, buff=0.12)
        grp = VGroup(bg, new)
        cap_anims = [FadeIn(grp, shift=0.15 * UP)]
        if self.cap is not None:
            cap_anims.append(FadeOut(self.cap, shift=0.15 * UP))
        self.play(*cap_anims, *anims, run_time=run_time)
        self.cap = grp
        return grp

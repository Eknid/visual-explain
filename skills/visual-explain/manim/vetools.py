"""Frame extraction, contact sheets and HTML embedding for manim films (stdlib only).

Called through `ve-manim frames|sheet|embed`; the ffmpeg path comes from $VE_FFMPEG.

  frames <dir> <Scene> <t1,t2,...>          -> <dir>/frames/<Scene>_<t>.png (960 px wide)
  sheet  <dir> <Scene> [n] [--width W]      -> <dir>/frames/<Scene>_sheet.png (2 columns, row-major)
  embed  <page.html> [out.html] [--external] [--videos DIR]
         replaces src="vid:NAME" and poster="poster:NAME" with base64 data URIs
         (or, with --external, copies the files into <out dir>/media/ and links them)
"""
import base64
import os
import pathlib
import re
import shutil
import subprocess
import sys

FF = os.environ.get("VE_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def run(cmd):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"ffmpeg failed: {' '.join(map(str, cmd))[:300]}\n{p.stderr[-800:]}")
    return p


def duration(video):
    err = subprocess.run([FF, "-i", str(video)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if not m:
        sys.exit(f"cannot read duration of {video}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def video_of(d, scene):
    v = pathlib.Path(d) / "scenes" / "videos" / f"{scene}.mp4"
    if not v.exists():
        sys.exit(f"no video {v} (render it first)")
    return v


def frames(d, scene, times):
    v = video_of(d, scene)
    out = pathlib.Path(d) / "frames"
    out.mkdir(parents=True, exist_ok=True)
    dur = duration(v)
    for t in [float(x) for x in times.split(",")]:
        t = min(max(t, 0), max(dur - 0.05, 0))
        p = out / f"{scene}_{t:g}.png"
        run([FF, "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", v, "-frames:v", "1", "-vf", "scale=960:-1", p])
        print(p)


def sheet(d, scene, n=6, width=640):
    """n evenly spaced frames, the last one near the end, tiled 2 per row: one image to review."""
    v = video_of(d, scene)
    out = pathlib.Path(d) / "frames"
    out.mkdir(parents=True, exist_ok=True)
    dur = duration(v)
    times = [round(dur * (i + 1) / n, 2) for i in range(n)]
    times[-1] = round(max(dur - 0.3, 0), 2)
    cols, h = 2, int(width * 9 / 16)
    cmd = [FF, "-loglevel", "error", "-y"]
    for t in times:
        cmd += ["-ss", f"{t:.2f}", "-i", v]
    scaled = "".join(f"[{i}:v]scale={width}:{h},setsar=1[s{i}];" for i in range(n))
    layout = "|".join(f"{(i % cols) * width}_{(i // cols) * h}" for i in range(n))
    inputs = "".join(f"[s{i}]" for i in range(n))
    cmd += ["-filter_complex", f"{scaled}{inputs}xstack=inputs={n}:layout={layout}:fill=black[out]",
            "-map", "[out]", "-frames:v", "1", out / f"{scene}_sheet.png"]
    run(cmd)
    print(out / f"{scene}_sheet.png")
    print("frames (row-major, 2 per row) at t =", ", ".join(f"{t:g}s" for t in times), f"of {dur:.1f}s")


def embed(page, out=None, external=False, videos=None):
    page = pathlib.Path(page)
    out = pathlib.Path(out) if out else page.with_name("index.html")
    root = page.parent
    vdir = pathlib.Path(videos) if videos else root / "scenes" / "videos"
    media = (out.parent / "media") if external else (root / "media")
    media.mkdir(parents=True, exist_ok=True)
    html = page.read_text()
    names = sorted(set(re.findall(r'src="vid:([\w-]+)"', html)))
    if not names:
        sys.exit('no src="vid:NAME" placeholders found')
    total = 0
    for n in names:
        mp4 = vdir / f"{n}.mp4"
        if not mp4.exists():
            sys.exit(f"missing video for vid:{n}: {mp4}")
        jpg = media / f"{n}.jpg"
        run([FF, "-loglevel", "error", "-y", "-ss", f"{max(duration(mp4) - 0.4, 0):.2f}", "-i", mp4,
             "-frames:v", "1", "-vf", "scale=960:-1", "-q:v", "5", jpg])
        if external:
            shutil.copy2(mp4, media / mp4.name)
            vsrc, psrc = f"media/{mp4.name}", f"media/{jpg.name}"
        else:
            vsrc = "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode()
            psrc = "data:image/jpeg;base64," + base64.b64encode(jpg.read_bytes()).decode()
        html = html.replace(f'src="vid:{n}"', f'src="{vsrc}"').replace(f'poster="poster:{n}"', f'poster="{psrc}"')
        total += mp4.stat().st_size
        print(f"{n}: {mp4.stat().st_size / 1e6:.2f} MB, {duration(mp4):.1f}s")
    left = re.findall(r'(?:src|poster)="(?:vid|poster):[\w-]+"', html)
    if left:
        sys.exit(f"unresolved placeholders: {left[:5]}")
    out.write_text(html)
    print(f"{out}: {out.stat().st_size / 1e6:.1f} MB ({'external media/' if external else 'self-contained'}; films {total / 1e6:.1f} MB)")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    flags = {a for a in args if a.startswith("--")}
    pos = [a for a in args if not a.startswith("--")]
    if cmd == "frames" and len(pos) == 3:
        frames(*pos)
    elif cmd == "sheet" and len(pos) in (2, 3):
        w = 640
        if "--width" in args:
            w = int(args[args.index("--width") + 1])
            pos = [p for p in pos if p != str(w)]
        sheet(pos[0], pos[1], int(pos[2]) if len(pos) == 3 else 6, w)
    elif cmd == "embed" and len(pos) >= 1:
        videos = None
        if "--videos" in args:
            videos = args[args.index("--videos") + 1]
            pos = [p for p in pos if p != videos]
        embed(pos[0], pos[1] if len(pos) > 1 else None, "--external" in flags, videos)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

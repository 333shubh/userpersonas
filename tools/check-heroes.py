"""3D toy hero check: series lineup and silhouettes (mascot style v3).

    python tools/check-heroes.py

Reads static/NN-slug/NN-mascot-hero.png (all seven). For each render the figure is cut out of its
background by region growing from the image border (gradient-friendly), so the check works on the
light studio sweeps and on Lull's and Mise's dark scene backgrounds.

Writes:
  stress-tests/silhouette/hero-lineup-3584x512.png     the seven heroes side by side, equal figure height
  stress-tests/silhouette/hero-silhouettes-224x32.png  the 32 px solid-black silhouette lineup
Checks:
  - all seven heroes present, square, at least 1024 px
  - Cram's render is achromatic (strict black and white)
  - every pair of silhouettes, normalised to equal height, overlaps by no more than 0.85 IoU
Floor-gradient streaks are trimmed to the width of the feet; soft contact shadows directly under the
feet can remain, which makes silhouettes look slightly more alike (the IoU result errs on the strict side).
Needs Pillow.
"""

import itertools
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

from PIL import Image, ImageOps  # noqa: E402

OUT = tk.ROOT / "stress-tests" / "silhouette"
WORK = 384          # analysis size (px)
STEP_TOL = 3        # max colour step between neighbouring background pixels (0-255, mean over channels)
BG_TOL = 10         # max distance from the nearest border colour sample (tight enough for dark-on-dark renders)
IOU_LIMIT = 0.85
NORM_H = 256


def cutout(path):
    """-> (RGB image at WORK size, mask list 1=figure) using region growing from the border."""
    im = Image.open(path).convert("RGB").resize((WORK, WORK), Image.LANCZOS)
    px = im.load()
    w = h = WORK
    border = [px[x, y] for x in range(0, w, 8) for y in (0, h - 1)] + [px[x, y] for y in range(0, h, 8) for x in (0, w - 1)]
    dist = lambda a, b: (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 3
    near_bg = lambda c: min(dist(c, b) for b in border) <= BG_TOL
    bg = bytearray(w * h)
    q = deque((x, y) for x in range(w) for y in (0, h - 1))
    q += deque((x, y) for y in range(h) for x in (0, w - 1))
    for x, y in q:
        bg[y * w + x] = 1
    while q:
        x, y = q.popleft()
        c = px[x, y]
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not bg[ny * w + nx]:
                n = px[nx, ny]
                if dist(c, n) <= STEP_TOL and near_bg(n):
                    bg[ny * w + nx] = 1
                    q.append((nx, ny))
    mask = [0 if b else 1 for b in bg]
    return im, trim_floor(mask, w, h)


def trim_floor(mask, w, h, band=0.12):
    """Drop floor-gradient streaks: in the bottom band keep only pixels under the figure's feet."""
    rows = [y for y in range(h) if any(mask[y * w:(y + 1) * w])]
    if not rows:
        return mask
    y_end = rows[-1]
    y_cut = y_end - int((y_end - rows[0]) * band)
    ref = [x for y in range(max(rows[0], y_cut - int(h * 0.05)), y_cut) for x in range(w) if mask[y * w + x]]
    if not ref:
        return mask
    lo, hi = min(ref) - 4, max(ref) + 4
    out = list(mask)
    for y in range(y_cut, h):
        for x in range(w):
            if out[y * w + x] and not lo <= x <= hi:
                out[y * w + x] = 0
    return out


def bbox(mask, w):
    xs = [i % w for i, v in enumerate(mask) if v]
    ys = [i // w for i, v in enumerate(mask) if v]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def normalise(mask, w):
    x0, y0, x1, y1 = bbox(mask, w)
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    s = NORM_H / bh
    W = NORM_H * 2
    out = [0] * (W * NORM_H)
    nw = round(bw * s)
    off = (W - nw) // 2
    for yy in range(NORM_H):
        sy = y0 + min(bh - 1, int(yy / s))
        for xx in range(nw):
            sx = x0 + min(bw - 1, int(xx / s))
            if mask[sy * w + sx] and 0 <= off + xx < W:
                out[yy * W + off + xx] = 1
    return out


def iou(a, b):
    inter = sum(1 for p, q in zip(a, b) if p and q)
    union = sum(1 for p, q in zip(a, b) if p or q)
    return inter / union if union else 0.0


def main():
    r = Report("check-heroes", "3D toy hero check",
               "The seven hero renders (mascot style v3): presence, Cram's black-and-white rule, and silhouette distinctness.")
    res = tk.resolve_all(tk.load())
    ps = tk.personas(res)
    files = {pid: tk.ROOT / "static" / p["slug"] / f"{p['number']}-{pid}-hero.png" for pid, p in ps}
    missing = [f.relative_to(tk.ROOT).as_posix() for f in files.values() if not f.exists()]
    if missing:
        r.add("FAIL" if len(missing) < 7 else "INFO", "hero renders present", f"missing: {missing}")
        if len(missing) == 7:
            return r.finish()
    cuts, norms = {}, {}
    for pid, f in files.items():
        if not f.exists():
            continue
        full = Image.open(f)
        r.ok(full.width == full.height and full.width >= 1024, f"{pid}: square render, at least 1024 px", f"{full.width}x{full.height}")
        im, mask = cutout(f)
        share = sum(mask) / len(mask)
        r.ok(0.05 < share < 0.75, f"{pid}: figure separates cleanly from the background", f"figure covers {share:.0%} of the frame")
        cuts[pid] = (im, mask)
        norms[pid] = normalise(mask, WORK)
        if pid == "cram":
            rgb = list(full.convert("RGB").resize((256, 256)).get_flattened_data())
            cast = max(max(p) - min(p) for p in rgb)
            r.ok(cast <= 24, "cram: render is achromatic (strict black and white)",
                 f"strongest colour cast {cast}/255 (converted to pure greyscale for delivery)")
    rows = []
    for a, b in itertools.combinations(norms, 2):
        rows.append((a, b, iou(norms[a], norms[b])))
    for a, b, v in sorted(rows, key=lambda t: -t[2])[:4]:
        r.ok(v <= IOU_LIMIT, f"silhouette IoU {a} vs {b} (most similar)", f"{v:.2f} (limit {IOU_LIMIT})")
    r.ok(all(v <= IOU_LIMIT for *_, v in rows), f"all {len(rows)} pairs distinct at equal height",
         f"worst {max(rows, key=lambda t: t[2])[0]}/{max(rows, key=lambda t: t[2])[1]} {max(v for *_, v in rows):.2f}" if rows else "")

    # lineups, in persona number order
    order = [pid for pid, _ in ps if pid in cuts]
    cell = 512
    colour = Image.new("RGB", (cell * len(order), cell), (255, 255, 255))
    sil = Image.new("RGB", (32 * len(order), 32), (255, 255, 255))
    for i, pid in enumerate(order):
        im, mask = cuts[pid]
        x0, y0, x1, y1 = bbox(mask, WORK)
        crop = im.crop((x0, y0, x1 + 1, y1 + 1))
        m = Image.new("L", (WORK, WORK))
        m.putdata([255 if v else 0 for v in mask])
        m = m.crop((x0, y0, x1 + 1, y1 + 1))
        th = int(cell * 0.86)
        tw = max(1, round(crop.width * th / crop.height))
        if tw > cell - 16:
            tw, th = cell - 16, round(crop.height * (cell - 16) / crop.width)
        crop, m = crop.resize((tw, th), Image.LANCZOS), m.resize((tw, th), Image.LANCZOS)
        colour.paste(crop, (i * cell + (cell - tw) // 2, cell - th - 24), m)
        s = Image.new("RGB", (tw, th), (0, 0, 0))
        tile = Image.new("RGB", (cell, cell), (255, 255, 255))
        tile.paste(s, ((cell - tw) // 2, cell - th - 24), m)
        sil.paste(tile.resize((32, 32), Image.LANCZOS), (i * 32, 0))
    OUT.mkdir(parents=True, exist_ok=True)
    colour.save(OUT / "hero-lineup-3584x512.png")
    sil.save(OUT / "hero-silhouettes-224x32.png")
    r.add("INFO", "lineups written", "stress-tests/silhouette/hero-lineup-3584x512.png, hero-silhouettes-224x32.png")
    table = "| Pair | IoU |\n|---|---|\n" + "\n".join(f"| {a} / {b} | {v:.2f} |" for a, b, v in sorted(rows, key=lambda t: -t[2]))
    r.section("Silhouette overlap, most similar first", table)
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

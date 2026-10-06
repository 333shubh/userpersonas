"""Silhouette lineup check (Gate 1, handoff section A).

    python tools/check-silhouettes.py

Reads stress-tests/silhouette/:
  silhouette-lineup.svg            structure: canvas, 7 groups in day order, black fill only
  silhouette-lineup-3584x512.png   per-cell height vs rig-spec construction target (+/- tolerance),
                                   ground contact, pairwise IoU after normalising to equal height
  silhouette-lineup-224x32.png     pairwise IoU of the 32px cells as rendered (what the eye sees)
Pass: every pair IoU <= 0.85 (rig-spec silhouetteTest). The human naming test stays manual.
"""

import itertools
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import raster  # noqa: E402
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

DIR = tk.ROOT / "stress-tests" / "silhouette"
SVG, BIG, SMALL = DIR / "silhouette-lineup.svg", DIR / "silhouette-lineup-3584x512.png", DIR / "silhouette-lineup-224x32.png"
NORM_H = 256


def cells(mask, w, h, n):
    cw = w // n
    out = []
    for c in range(n):
        out.append([mask[y * w + x] for y in range(h) for x in range(c * cw, (c + 1) * cw)])
    return cw, out


def normalise(cell, cw, ch):
    """Crop to bbox, scale to NORM_H tall (nearest), bottom-aligned and centred on a NORM_H*2 wide canvas."""
    x0, y0, x1, y1 = raster.bbox(cell, cw, ch)
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
            if cell[sy * cw + sx] and 0 <= off + xx < W:
                out[yy * W + off + xx] = 1
    return out


def iou(a, b):
    inter = sum(1 for p, q in zip(a, b) if p and q)
    union = sum(1 for p, q in zip(a, b) if p or q)
    return inter / union if union else 0.0


def main():
    r = Report("check-silhouettes", "Silhouette lineup check",
               "Gate 1 handoff section A. Automated part of the silhouette test; the 10-second naming test is a human review.")
    spec = json.loads((tk.ROOT / "system" / "rig-spec.json").read_text(encoding="utf-8"))
    res = tk.resolve_all(tk.load())
    order = [pid for pid, _ in sorted(tk.personas(res), key=lambda kv: kv[1]["day"]["order"])]
    tol, ground = spec["canvas"]["tolerance"], spec["canvas"]["groundY"]

    missing = [p.name for p in (SVG, BIG, SMALL) if not p.exists()]
    if missing:
        r.add("FAIL", "lineup files present", f"missing: {missing}")
        return r.finish()

    root = ET.parse(SVG).getroot()
    ns = "{http://www.w3.org/2000/svg}"
    r.ok(root.get("viewBox", "").split() == ["0", "0", "7168", "1024"], "SVG canvas 7168 x 1024", root.get("viewBox"))
    groups = [g.get("id") for g in root if g.tag == ns + "g"]
    r.ok(groups == order, "SVG cell groups in Section 18.5 day order", " > ".join(map(str, groups)))
    fills = {el.get("fill") for el in root.iter() if el.get("fill")}
    strokes = [el for el in root.iter() if el.get("stroke") not in (None, "none")]
    r.ok(fills <= {"#000000", "#FFFFFF", "#ffffff", "none"} and not strokes, "SVG uses black fill only, no strokes",
         f"fills {sorted(fills)}, strokes {len(strokes)}")
    bad = sorted({el.tag.replace(ns, "") for el in root.iter()} & {"script", "image", "text", "foreignObject"})
    r.ok(not bad, "SVG has no script/image/text", ", ".join(bad))

    w, h, m = raster.read_png(BIG)
    r.ok((w, h) == (3584, 512), "512px render is 3584 x 512", f"{w} x {h}")
    cw, big = cells(m, w, h, 7)
    k = 1024 / cw  # rig units per pixel
    norm = {}
    for pid, cell in zip(order, big):
        bb = raster.bbox(cell, cw, h)
        if not bb:
            r.add("FAIL", f"{pid}: cell has ink")
            continue
        x0, y0, x1, y1 = bb
        height = round((y1 + 1 - y0) * k)
        target = spec["construction"][pid]["height"]
        dev = (height - target) / target
        r.add("PASS" if abs(dev) <= tol else "WARN", f"{pid}: height vs rig-spec target (+/-{tol:.0%})",
              f"{height} vs {target} rig units ({dev:+.1%})")
        base = round((y1 + 1) * k)
        r.ok(abs(base - ground) <= k, f"{pid}: stands on the ground line y={ground}", f"base y = {base}")
        sx0, sy0, sx1, _ = spec["canvas"]["safeBox"]
        r.ok(x0 * k >= sx0 - k and (x1 + 1) * k <= sx1 + k and y0 * k >= sy0 - k,
             f"{pid}: inside the safe box ({sx0}-{sx1})", f"x {round(x0 * k)}-{round((x1 + 1) * k)}, top y {round(y0 * k)}")
        norm[pid] = normalise(cell, cw, h)

    rows, worst = [], (0, None)
    for a, b in itertools.combinations(order, 2):
        if a in norm and b in norm:
            v = iou(norm[a], norm[b])
            worst = max(worst, (v, f"{a}/{b}"))
            rows.append((a, b, v))
    for a, b, v in sorted(rows, key=lambda t: -t[2])[:5]:
        r.ok(v <= 0.85, f"normalised IoU {a} vs {b} (top-5 most similar)", f"{v:.2f} (limit 0.85)")
    r.ok(all(v <= 0.85 for _, _, v in rows), "all 21 pairs: normalised IoU <= 0.85", f"worst {worst[1]} {worst[0]:.2f}")

    sw, sh, sm = raster.read_png(SMALL)
    r.ok((sw, sh) == (224, 32), "32px render is 224 x 32", f"{sw} x {sh}")
    scw, small = cells(sm, sw, sh, 7)
    srows = [(a, b, iou(small[i], small[j])) for (i, a), (j, b) in itertools.combinations(enumerate(order), 2)]
    a, b, v = max(srows, key=lambda t: t[2])
    r.add("INFO", "32px as rendered: most similar pair (pixel IoU, cell-aligned)", f"{a}/{b} {v:.2f}")
    cs = next(t for t in srows if {t[0], t[1]} == {"cram", "stack"})
    r.add("INFO", "32px as rendered: Cram vs Stack (known risk)", f"{cs[2]:.2f}")
    r.add("INFO", "human naming test (10 s, 32px PNG, key hidden)", "manual: record result in the Gate 1 review")

    names = order
    table = "| | " + " | ".join(names) + " |\n|---|" + "---|" * len(names) + "\n"
    lookup = {(a, b): v for a, b, v in rows} | {(b, a): v for a, b, v in rows}
    for a in names:
        table += f"| **{a}** | " + " | ".join("" if a == b else f"{lookup.get((a, b), 0):.2f}" for b in names) + " |\n"
    r.section("Normalised IoU matrix (equal height, bottom-aligned, centred)", table)
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

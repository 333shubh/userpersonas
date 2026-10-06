"""'2' glyph check (Gate 1, handoff section B).

    python tools/check-glyphs.py

For glyphs/NN-slug/NN-mascot-two.svg (x7) and stress-tests/scale/two-glyph-scale-test.svg:
  - structure: viewBox 0 0 320 400 (1:1.25), id {mascot}__foreground-type__two-mark, no script/image/text
  - colour: fills are exactly the persona role.text (and role.bg for Riot's die-cut) from tokens
  - cap height: ink spans 80% of the box (y 80-400), +/-2%
  - minimum stroke: morphological opening with a disk of diameter = brand.two-mark.min-stroke x cap height.
    Ink that disappears under the opening is thinner than the minimum. Corner slivers are expected:
    a lost region that contains a sharp outline vertex (interior angle < ACUTE_DEG) is a corner, reported
    as INFO. Any other lost region larger than LOST_LIMIT x disk area is a stroke below the minimum (FAIL).
  - open counter: largest empty disk inside the bowl (upper 55% of the cap, ink on left, right and above)
    must have a diameter >= brand.two-mark.min-counter x ink width.
Rasterised at 0.5 px per glyph unit (160 x 200), so results are +/-2 units.
The 16px "reads as a 2" test is a human review.
"""

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import raster  # noqa: E402
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"
SCALE = 0.5  # pixels per glyph unit
BOX_W, BOX_H, CAP_TOP = 320, 400, 80
LOST_LIMIT = 0.5  # largest lost region, as a fraction of the opening disk's area
ACUTE_DEG = 75  # outline vertices sharper than this are corners, not strokes
CORNER_ZONE = 3  # pixels (= 6 glyph units) around an acute vertex that count as "at the corner"
SCALE_TEST = tk.ROOT / "stress-tests" / "scale" / "two-glyph-scale-test.svg"


def ink_paths(root, ink, core_only):
    """d strings of paths filled with the ink colour (inherited from the nearest ancestor with a fill)."""
    out = []

    def walk(el, fill, in_core):
        fill = el.get("fill", fill)
        in_core = in_core or (el.get("id") or "").endswith("__core")
        if el.tag == NS + "path" and (fill or "").upper() == ink.upper() and (in_core or not core_only):
            out.append(el.get("d"))
        for ch in el:
            walk(ch, fill, in_core)
    walk(root, None, False)
    return out


def rasterise(ds):
    w, h = int(BOX_W * SCALE), int(BOX_H * SCALE)
    mask = [0] * (w * h)
    for d in ds:
        raster.fill(raster.path_polys(d), w, h, scale=SCALE, mask=mask)
    return w, h, mask


def acute_vertices(ds, w):
    """Pixel indices of outline vertices whose interior angle is below ACUTE_DEG."""
    out = set()
    for d in ds:
        for poly in raster.path_polys(d):
            pts = [p for i, p in enumerate(poly) if i == 0 or p != poly[i - 1]]
            if len(pts) > 1 and pts[0] == pts[-1]:
                pts = pts[:-1]
            n = len(pts)
            if n < 3:
                continue
            area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
            for i in range(n):
                (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[(i + 1) % n]
                v1, v2 = (ax - bx, ay - by), (cx - bx, cy - by)
                l1, l2 = math.hypot(*v1), math.hypot(*v2)
                if not l1 or not l2:
                    continue
                ang = math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)))))
                convex = (v2[0] * v1[1] - v2[1] * v1[0]) * area > 0
                if convex and ang < ACUTE_DEG:
                    # mark a small zone around the vertex: the sharp tip itself may fall between pixel centres
                    px, py = int(bx * SCALE), int(by * SCALE)
                    for yy in range(py - CORNER_ZONE, py + CORNER_ZONE + 1):
                        for xx in range(px - CORNER_ZONE, px + CORNER_ZONE + 1):
                            if 0 <= xx < w and 0 <= yy < int(BOX_H * SCALE):
                                out.add(yy * w + xx)
    return out


def opening_loss(mask, w, h, radius_px, corners):
    """-> (lost fraction, worst non-corner region (size, thickness px), worst corner region size)."""
    inside = raster.distance(mask, w, h, to=0)          # distance to background
    eroded = [1 if v > radius_px else 0 for v in inside]
    if not any(eroded):
        return 1.0, (sum(mask), 0.0), 0
    reach = raster.distance(eroded, w, h, to=1)          # distance to the eroded core
    opened = [1 if v <= radius_px else 0 for v in reach]
    lost = [1 if a and not b else 0 for a, b in zip(mask, opened)]
    stroke, corner = (0, 0.0), 0
    for size, deep, members in raster.components(lost, w, h, values=inside, pixels=True):
        if corners.intersection(members):
            corner = max(corner, size)
        else:
            # thickness of a lost feature = 2 x its deepest point's distance to background
            stroke = max(stroke, (size, 2 * deep))
    return sum(lost) / max(1, sum(mask)), stroke, corner


def counter_diameter(mask, w, h, bb):
    x0, y0, x1, y1 = bb
    gap = raster.distance(mask, w, h, to=1)              # distance to nearest ink
    best = 0.0
    y_end = y0 + int((y1 - y0) * 0.55)
    for y in range(y0, y_end + 1):
        row = mask[y * w:(y + 1) * w]
        for x in range(x0, x1 + 1):
            if row[x]:
                continue
            left = any(row[x0:x])
            right = any(row[x + 1:x1 + 1])
            above = any(mask[yy * w + x] for yy in range(y0, y))
            if left and right and above:
                best = max(best, gap[y * w + x])
    return 2 * best


def main():
    r = Report("check-glyphs", "'2' glyph check",
               "Gate 1 handoff section B. Measures each persona '2' against `brand.two-mark`. "
               "Raster measurements are at 0.5 px per glyph unit (+/-2 units).")
    res = tk.resolve_all(tk.load())
    tm = res["brand"]["two-mark"]
    min_stroke, min_counter = tm["min-stroke"]["$value"], tm["min-counter"]["$value"]
    rows = []
    for pid, p in tk.personas(res):
        path = tk.ROOT / "glyphs" / p["slug"] / f"{p['number']}-{pid}-two.svg"
        rel = path.relative_to(tk.ROOT).as_posix()
        if not path.exists():
            r.add("FAIL", f"{pid}: glyph file present", rel)
            continue
        root = ET.parse(path).getroot()
        roles = tk.roles(p)
        r.ok(root.get("viewBox", "").split() == ["0", "0", "320", "400"], f"{pid}: viewBox is the 1:1.25 construction box",
             root.get("viewBox"))
        ids = [el.get("id") for el in root.iter() if el.get("id")]
        r.ok(f"{pid}__foreground-type__two-mark" in ids, f"{pid}: group id {pid}__foreground-type__two-mark")
        rx = re.compile(r"^" + pid + r"__foreground-type__two-mark(__[a-z0-9]+(-[a-z0-9]+)*)?$")
        r.ok(all(rx.match(i) for i in ids), f"{pid}: every id follows the rig grammar", ", ".join(i for i in ids if not rx.match(i)))
        bad = sorted({el.tag.replace(NS, "") for el in root.iter()} & {"script", "image", "text", "foreignObject"})
        r.ok(not bad, f"{pid}: no script/image/text (outlined paths only)", ", ".join(bad))
        fills = {(el.get("fill") or "").upper() for el in root.iter() if el.get("fill")}
        allowed = {roles["text"].upper(), roles["bg"].upper()}
        r.ok(fills <= allowed and roles["text"].upper() in fills, f"{pid}: fills are role.text / role.bg only",
             f"{sorted(fills)} vs text {roles['text']}, bg {roles['bg']}")

        core_ds = ink_paths(root, roles["text"], core_only=pid == "riot")
        w, h, core = rasterise(core_ds)
        _, _, outer = rasterise([d for d in ink_paths(root, roles["text"], core_only=False)])
        bb_outer = raster.bbox(outer, w, h)
        bb = raster.bbox(core, w, h)
        top, bottom = bb_outer[1] / SCALE, (bb_outer[3] + 1) / SCALE
        cap = bottom - top
        r.ok(abs(top - CAP_TOP) <= 0.02 * BOX_H and bottom >= BOX_H - 2, f"{pid}: cap height = 80% of box (y 80-400)",
             f"ink y {top:.0f}-{bottom:.0f} (cap {cap:.0f} / {BOX_H} = {cap / BOX_H:.0%})")

        need = min_stroke * (BOX_H - CAP_TOP)
        radius_px = need / 2 * SCALE - 1  # one pixel of slack for rasterisation
        loss, (worst, thick_px), corner = opening_loss(core, w, h, radius_px, acute_vertices(core_ds, w))
        thick = thick_px / SCALE
        disk = 3.14159 * radius_px ** 2
        ok = worst <= LOST_LIMIT * disk
        r.ok(ok, f"{pid}: no stroke thinner than {need:.0f} units ({min_stroke:.1%} of cap height)",
             f"largest sub-minimum stroke region ~{thick:.0f} units thick, {worst / disk:.2f} x disk area "
             f"(limit {LOST_LIMIT}); opening loses {loss:.1%} of ink")
        if corner:
            r.add("INFO", f"{pid}: sharp corners (< {ACUTE_DEG} deg) shaved by the opening",
                  f"largest corner region {corner / disk:.2f} x disk area; corners are not strokes")

        ink_w = (bb[2] - bb[0] + 1) / SCALE
        cd = counter_diameter(core, w, h, bb) / SCALE
        need_c = min_counter * ink_w
        r.ok(cd >= need_c, f"{pid}: open counter >= {min_counter:.0%} of ink width",
             f"{cd:.0f} units vs {need_c:.0f} needed (ink width {ink_w:.0f})")
        rows.append(f"| {p['name']} | {cap:.0f} | {loss:.1%} | {worst / disk:.2f} | ~{thick:.0f} | {corner / disk:.2f} | {cd:.0f} | {need_c:.0f} |")
        r.add("INFO", f"{pid}: reads as '2' at 16px", "human review on stress-tests/scale/two-glyph-scale-test.svg")

    if SCALE_TEST.exists():
        root = ET.parse(SCALE_TEST).getroot()
        nested = [el for el in root.iter(NS + "svg") if el is not root]
        heights = sorted({el.get("height") for el in nested})
        r.ok(len(nested) == 7 * 2 * 4 and heights == ["16", "32", "512", "64"],
             "scale test: 7 glyphs x (colour + black) x 16/32/64/512px", f"{len(nested)} renders, heights {heights}")
        bad = sorted({el.tag.replace(NS, "") for el in root.iter()} & {"script", "image", "text", "foreignObject"})
        r.ok(not bad, "scale test: no script/image/text", ", ".join(bad))
    else:
        r.add("FAIL", "scale test present", SCALE_TEST.relative_to(tk.ROOT).as_posix())

    r.section("Measurements (glyph units; box 320 x 400)",
              "| Glyph | Cap height | Ink lost to opening | Largest lost stroke region (x disk) | Its thickness | Sharp-corner region (x disk) | Counter diameter | Counter needed |\n"
              "|---|---|---|---|---|---|---|---|\n" + "\n".join(rows))
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

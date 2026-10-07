"""Composite each mascot's real MAGGI pack onto the plain pack in its 3D hero render.

    python tools/composite-packs.py [mascot ...] [--scene] [--masks]

Without --scene it works on the hero renders (NN-mascot-hero.png -> NN-mascot-hero-with-pack.png);
with --scene on the eating scenes (NN-mascot-scene.png -> NN-mascot-scene-with-pack.png).

For each mascot (measured layout below), and for each pack it holds:
  1. mask = the measured pack outline, minus hand ellipses, minus pixels coloured unlike the plain pack
  2. warp the real front-of-pack image onto the measured corners: a perspective transform for flat
     packs, or a row-by-row map for a cup (each source row's width comes from the cup's own outline)
  3. re-light it with the render's own shading (luminance ratio inside the masks), so wrinkles and
     light direction carry over
  4. paste only inside the mask, so fingers and anything in front of the pack stay on top
Cram's pack is converted to greyscale (strict black and white). Health badges on real packs are tiny
at hero scale; a light blur over the pack's lower-left badge area keeps them illegible (Section 22).
Writes static/NN-slug/NN-mascot-hero-with-pack.png. --masks also saves the masks for review.
Needs Pillow.
"""

import colorsys
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

PACKS = tk.ROOT / "brief" / "references" / "packs"
# Measured on gridded close-ups of each render (render pixels):
#   quads: pack corners top-left, top-right, bottom-right, bottom-left, one quad per visible pack
#          (hidden corners completed along the pack's edges)
#   hands: ellipses (cx, cy, rx, ry) for fingers in front of the pack
#   sample: a point on the plain pack; tol: colour distance from it that still counts as pack (0-255 mean channel)
#   warp: "perspective" (flat pack) or "rows" (cup: quad top and bottom edges must be horizontal)
#   rows: for "rows", the source rows (top, bottom) of the real cup's straight-walled body
#   hsv: (hue_lo, hue_hi, sat_min) in degrees and 0-1, used instead of sample/tol where the background
#        is close in RGB to the plain pack (Stack: golden packs on a cream sweep, cardboard head above)
#   span: for "rows", the fraction (start, end) of each source row used, to turn the cup's logo to face camera
#   rotate: degrees counter-clockwise applied to the real pack first (Stack's packs lie on their side)
#   src_box: pixel box of the real pack image to use (for images without transparency); default the opaque area
#   badge: area of the real pack image (fractions x0, y0, x1, y1) holding the nutrition badges; default lower-left
#   visible: polygon of the pack's visible part, used instead of colour exclusion where the hand or sleeve
#            in front has the same colour as the pack (Cram: white pack, white glove, white knit sleeve)
#   light: "colour" multiplies the print by the render's own light colour (Lull's warm lamp); default is
#          luminance only, which keeps the real pack's print colours under the neutral studio light
LAYOUT = {
    "cram": dict(quads=[[(781, 525), (936, 572), (857, 772), (702, 725)]], hands=[(852, 722, 54, 54)], sample=(800, 620), tol=70),
    "riot": dict(quads=[[(250, 105), (474, 57), (527, 305), (325, 350)]], hands=[(318, 280, 54, 68)], sample=(410, 160), tol=80),
    "nest": dict(quads=[[(835, 480), (997, 571), (909, 745), (747, 654)]], hands=[(910, 694, 54, 58)], sample=(860, 600), tol=70),
    "sprig": dict(quads=[[(842, 512), (997, 572), (922, 775), (767, 715)]], hands=[(928, 699, 47, 57)], sample=(850, 620), tol=60),
    "lull": dict(quads=[[(712, 537), (868, 537), (828, 668), (745, 668)]], hands=[(737, 605, 40, 50), (864, 610, 34, 46)],
                 sample=(790, 600), tol=70, warp="rows", rows=(250, 725), span=(0.0, 0.72), light="colour",
                 badge=(0.13, 0.69, 0.31, 0.84)),
    "stack": dict(quads=[
        [(688, 500), (978, 528), (970, 610), (657, 553)],
        [(657, 553), (970, 610), (950, 665), (645, 607)],
        [(645, 607), (950, 665), (942, 712), (625, 660)],
        [(625, 660), (942, 712), (910, 757), (607, 705)],
        [(607, 705), (910, 757), (895, 812), (595, 760)],
    ], hands=[], hsv=(34, 56, 0.35), rotate=90),
    # Mise: the real pack is a landscape JPEG on white; take the portrait print panel (logo, name) and map it
    # onto the pack body between the render's own maroon crimps
    "mise": dict(quads=[[(750, 460), (870, 489), (828, 632), (708, 603)]], hands=[(833, 594, 36, 44)], sample=(780, 520), tol=55,
                 src_box=(28, 118, 340, 478), badge=(0.0, 0.82, 0.75, 1.0)),
}

# Eating scenes (system/scene-prompts.md), measured the same way.
SCENES = {
    "cram": dict(quads=[[(1057, 489), (1191, 529), (1130, 699), (996, 659)]], hands=[],
                 visible=[(1057, 489), (1191, 529), (1166, 590), (1135, 578), (1100, 590), (1060, 606), (1017, 602)]),
    "riot": dict(quads=[[(1235, 642), (1427, 645), (1400, 868), (1206, 868)]], hands=[], sample=(1320, 750), tol=70),
    # Nest's pack lies flat on the counter, top edge away from the camera
    "nest": dict(quads=[[(845, 790), (985, 832), (915, 915), (710, 865)]], hands=[], hsv=(30, 58, 0.45)),
    "sprig": dict(quads=[[(930, 470), (1076, 470), (1068, 640), (919, 640)]], hands=[], sample=(1000, 560), tol=50),
    "lull": dict(quads=[[(713, 528), (838, 528), (820, 632), (730, 632)]], hands=[(830, 597, 30, 42)], sample=(760, 580), tol=70,
                 warp="rows", rows=(250, 725), span=(0.0, 0.72), light="colour", badge=(0.13, 0.69, 0.31, 0.84)),
    # Stack's shelf: the 12 packs in plain view (9 on the top shelf, 3 on the middle shelf), lying on their sides
    "stack": dict(quads=[
        [(865, 258), (1080, 258), (1080, 305), (865, 305)],
        [(1062, 258), (1292, 258), (1292, 305), (1062, 305)],
        [(1268, 258), (1482, 258), (1482, 305), (1268, 305)],
        [(865, 302), (1080, 302), (1080, 350), (865, 350)],
        [(1062, 302), (1292, 302), (1292, 350), (1062, 350)],
        [(1268, 302), (1482, 302), (1482, 350), (1268, 350)],
        [(865, 348), (1080, 348), (1080, 398), (865, 398)],
        [(1062, 348), (1292, 348), (1292, 398), (1062, 398)],
        [(1268, 348), (1482, 348), (1482, 398), (1268, 398)],
        [(845, 488), (1085, 488), (1085, 542), (845, 542)],
        [(845, 540), (1085, 540), (1085, 590), (845, 590)],
        [(845, 590), (1085, 590), (1085, 640), (845, 640)],
    ], hands=[], hsv=(34, 56, 0.45), rotate=90),
    "mise": dict(quads=[[(980, 604), (1163, 606), (1156, 833), (967, 832)]], hands=[(1190, 770, 42, 70)], sample=(1060, 720), tol=45,
                 src_box=(28, 118, 340, 478), badge=(0.0, 0.82, 0.75, 1.0)),
}


def pack_mask(im, quad, cfg):
    """Pack outline, minus hand ellipses, minus pixels coloured unlike the plain pack (frills, noodles)."""
    w, h = im.size
    mask = Image.new("L", (w, h))
    if "visible" in cfg:
        ImageDraw.Draw(mask).polygon(cfg["visible"], fill=255)
        return mask
    ImageDraw.Draw(mask).polygon(quad, fill=255)
    px = im.load()
    mp = mask.load()
    x0, y0, x1, y1 = mask.getbbox()
    if "hsv" in cfg:
        lo, hi, smin = cfg["hsv"]
        unlike = lambda c: not (colorsys.rgb_to_hsv(*(v / 255 for v in c))[1] >= smin
                                and lo <= colorsys.rgb_to_hsv(*(v / 255 for v in c))[0] * 360 <= hi)
    else:
        s, tol = px[cfg["sample"]], cfg["tol"]
        unlike = lambda c: (abs(c[0] - s[0]) + abs(c[1] - s[1]) + abs(c[2] - s[2])) / 3 > tol
    for y in range(y0, y1):
        for x in range(x0, x1):
            if mp[x, y] and unlike(px[x, y]):
                mp[x, y] = 0
    d = ImageDraw.Draw(mask)
    for cx, cy, rx, ry in cfg["hands"]:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=0)
    # close specular pinholes, keep edges
    return mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))


def perspective_coeffs(dst, src):
    """Coefficients for Image.transform(PERSPECTIVE) mapping output (dst) points to input (src) points."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    # solve 8x8 by Gaussian elimination
    M = [row + [b] for row, b in zip(A, B)]
    for i in range(8):
        piv = max(range(i, 8), key=lambda r: abs(M[r][i]))
        M[i], M[piv] = M[piv], M[i]
        for r in range(8):
            if r != i and M[i][i]:
                f = M[r][i] / M[i][i]
                M[r] = [a - f * b for a, b in zip(M[r], M[i])]
    return [M[i][8] / M[i][i] for i in range(8)]


def warp_rows(pack, rows, quad, size, span=(0.0, 1.0)):
    """Map a cup photo onto a cup in the render, one output row at a time.
    Output row t (0 top .. 1 bottom of the quad) takes source row rows[0] + t * (rows[1] - rows[0]);
    each source row spans the cup's own opaque width, each output row the quad's width at that height."""
    (xl0, y0), (xr0, _), (xr1, y1), (xl1, _) = quad
    alpha = pack.getchannel("A").load()
    def extent(sy):
        xs = [x for x in range(pack.width) if alpha[x, sy] > 128]
        return (xs[0], xs[-1] + 1) if xs else (0, pack.width)
    mesh = []
    for y in range(y0, y1):
        t = (y - y0 + 0.5) / (y1 - y0)
        dl, dr = xl0 + (xl1 - xl0) * t, xr0 + (xr1 - xr0) * t
        sy = rows[0] + (rows[1] - rows[0]) * t
        sy_next = rows[0] + (rows[1] - rows[0]) * (y + 1 - y0 + 0.5) / (y1 - y0)
        sl, sr = extent(int(sy))
        sl, sr = sl + (sr - sl) * span[0], sl + (sr - sl) * span[1]
        # MESH: output box -> source quad (upper-left, lower-left, lower-right, upper-right)
        mesh.append(((round(dl), y, round(dr), y + 1), (sl, sy, sl, sy_next, sr, sy_next, sr, sy)))
    return pack.transform(size, Image.MESH, mesh, Image.BICUBIC)


def real_pack(p, pid, cfg):
    pack = Image.open(PACKS / p["product"]["packImage"]).convert("RGBA")
    if "src_box" in cfg:
        pack = pack.crop(cfg["src_box"])
    elif cfg.get("warp") != "rows":
        pack = pack.crop(pack.getbbox())   # rows are measured on the uncropped cup image
    if pid == "cram":
        g = pack.convert("L")
        pack = Image.merge("RGBA", (g, g, g, pack.getchannel("A")))
    # soften the lower-left badge area (nutrition badges) so it stays illegible
    w0, h0 = pack.size
    bx0, by0, bx1, by1 = cfg.get("badge", (0.0, 0.55, 0.5, 1.0))
    box = (int(w0 * bx0), int(h0 * by0), int(w0 * bx1), int(h0 * by1))
    pack.paste(pack.crop(box).filter(ImageFilter.GaussianBlur(max(2, w0 // 120))), box[:2])
    if cfg.get("rotate"):
        pack = pack.rotate(cfg["rotate"], expand=True)
    return pack


def composite(pid, save_masks=False, kind="hero"):
    res = tk.resolve_all(tk.load())
    p = res["persona"][pid]
    hero = tk.ROOT / "static" / p["slug"] / f"{p['number']}-{pid}-{kind}.png"
    im = Image.open(hero).convert("RGB")
    cfg = (SCENES if kind == "scene" else LAYOUT)[pid]
    masks = [pack_mask(im, q, cfg) for q in cfg["quads"]]
    union = masks[0]
    for m in masks[1:]:
        union = Image.composite(m, union, m)
    if save_masks:
        union.save(tk.ROOT / "stress-tests" / "qa" / f"pack-mask-{pid}{'-scene' if kind == 'scene' else ''}.png")
    pack = real_pack(p, pid, cfg)
    # relight. Default: render luminance inside the masks, normalised to its median (same factor per channel).
    # "colour": each render channel over the 95th-percentile brightest channel value inside the masks, so the
    # print takes on the light's colour as well as its shading.
    inside = [c for c, m in zip(im.get_flattened_data(), union.get_flattened_data()) if m]
    if cfg.get("light") == "colour":
        tops = sorted(max(c) for c in inside)
        ref = tops[int(len(tops) * 0.95)] or 1
        shades = [ch.point(lambda v: max(0, min(255, int(128 * v / ref)))).load() for ch in im.split()]
    else:
        lum = im.convert("L")
        vals = sorted(v for v, m in zip(lum.get_flattened_data(), union.get_flattened_data()) if m)
        med = vals[len(vals) // 2] or 1
        shades = [lum.point(lambda v: max(0, min(255, int(128 * v / med)))).load()] * 3
    out = im.copy()
    for quad, mask in zip(cfg["quads"], masks):
        if cfg.get("warp") == "rows":
            warped = warp_rows(pack, cfg["rows"], quad, im.size, cfg.get("span", (0.0, 1.0)))
        else:
            w0, h0 = pack.size
            coeffs = perspective_coeffs(quad, [(0, 0), (w0, 0), (w0, h0), (0, h0)])
            warped = pack.transform(im.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
        rgb = warped.convert("RGB")
        x0, y0, x1, y1 = mask.getbbox()
        out_ch = []
        for ch, sh in zip(rgb.split(), shades):
            cp = ch.load()
            o = Image.new("L", im.size)
            op = o.load()
            for y in range(y0, y1):
                for x in range(x0, x1):
                    op[x, y] = min(255, cp[x, y] * sh[x, y] // 128)
            out_ch.append(o)
        relit = Image.merge("RGB", out_ch)
        paste_mask = Image.composite(warped.getchannel("A"), Image.new("L", im.size), mask).filter(ImageFilter.GaussianBlur(0.8))
        out.paste(relit, (0, 0), paste_mask)
    if pid == "cram":
        out = out.convert("L").convert("RGB")   # strict black and white for delivery
    dst = hero.with_name(f"{p['number']}-{pid}-{kind}-with-pack.png")
    out.save(dst)
    return dst, len(cfg["quads"]), sum(1 for v in union.get_flattened_data() if v)


def main(argv):
    save = "--masks" in argv
    kind = "scene" if "--scene" in argv else "hero"
    ids = [a for a in argv if not a.startswith("--")] or list(SCENES if kind == "scene" else LAYOUT)
    for pid in ids:
        dst, nq, n = composite(pid, save, kind)
        print(f"{pid}: {nq} pack(s), mask {n} px -> {dst.relative_to(tk.ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

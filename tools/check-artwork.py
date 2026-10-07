"""Artwork colour and safety check for every SVG in static/ and glyphs/ persona folders.

    python tools/check-artwork.py

Per file (persona taken from its NN-slug folder):
  - every colour (fill, stroke, stop-color, flood-color, lighting-color, and the same inside style="")
    is a hex from that persona's token palette; url(#...) paint servers, none and currentColor are allowed
  - Cram files: every colour is achromatic (strict black and white, Section 18.12)
  - no <script>, <image>, <foreignObject>, <text>, external hrefs or feTurbulence/feColorMatrix
    (filters that would create off-token colours)
  - opacity values are only 1, or the token-defined blends (Riot gloss 0.6 / overlap 0.9)
Exception (system/mascot-style-v2.md section 5): inside a group whose id ends in "__props__pack" the
real MAGGI pack may use off-palette colours and an embedded raster <image> (data: URI only).
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import colour  # noqa: E402
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"
PAINT_ATTRS = ("fill", "stroke", "stop-color", "flood-color", "lighting-color")
OPACITY_ATTRS = ("opacity", "fill-opacity", "stroke-opacity")
FORBIDDEN = {"script", "image", "foreignObject", "text", "feTurbulence", "feColorMatrix"}
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")


def paints(el):
    vals = [el.get(a) for a in PAINT_ATTRS if el.get(a)]
    style = el.get("style") or ""
    for decl in style.split(";"):
        if ":" in decl:
            k, v = (x.strip() for x in decl.split(":", 1))
            if k in PAINT_ATTRS:
                vals.append(v)
    return vals


def opacities(el):
    vals = [el.get(a) for a in OPACITY_ATTRS if el.get(a)]
    for decl in (el.get("style") or "").split(";"):
        if ":" in decl:
            k, v = (x.strip() for x in decl.split(":", 1))
            if k in OPACITY_ATTRS:
                vals.append(v)
    return vals


def outside_pack(root):
    """Yield every element not inside a {mascot}__props__pack group; also return embedded-pack problems."""
    out, problems = [], []

    def walk(el, in_pack):
        in_pack = in_pack or (el.get("id") or "").endswith("__props__pack")
        if in_pack:
            if el.tag == NS + "image":
                href = el.get("href") or el.get("{http://www.w3.org/1999/xlink}href") or ""
                if not href.startswith("data:image/"):
                    problems.append(f"pack image must be embedded (data: URI), got {href[:40]!r}")
        else:
            out.append(el)
        for ch in el:
            walk(ch, in_pack)
    walk(root, False)
    return out, problems


def main():
    r = Report("check-artwork", "Artwork colour and safety check",
               "Every SVG in `static/NN-slug/` and `glyphs/NN-slug/` checked against its persona's token palette.")
    res = tk.resolve_all(tk.load())
    by_slug = {p["slug"]: (pid, p) for pid, p in tk.personas(res)}
    blends = {"1", "1.0", "0.6", "0.9"}
    files = sorted(list(tk.ROOT.glob("static/*/*.svg")) + list(tk.ROOT.glob("glyphs/*/*.svg")))
    if not files:
        r.add("INFO", "artwork files", "none yet")
    for path in files:
        rel = path.relative_to(tk.ROOT).as_posix()
        pid, p = by_slug[path.parent.name]
        palette = {v.upper() for v in tk.palette(p).values()}
        root = ET.parse(path).getroot()
        used, bad_paint, bad_op = set(), set(), set()
        elements, pack_problems = outside_pack(root)
        r.ok(not pack_problems, f"{rel}: real pack layer (if any) is self-contained", "; ".join(pack_problems))
        for el in elements:
            for v in paints(el):
                v = v.strip()
                if v in ("none", "currentColor", "transparent") or v.startswith("url(#"):
                    continue
                m = HEX.fullmatch(v)
                if not m or len(v) != 7:
                    bad_paint.add(v)
                    continue
                used.add(v.upper())
            for v in opacities(el):
                if v.strip() not in blends:
                    bad_op.add(v)
        off = sorted(used - palette) + sorted(bad_paint)
        r.ok(not off, f"{rel}: colours are {pid} tokens only", f"off-token: {off}" if off else f"{len(used)} token colours")
        if pid == "cram":
            # Cram's pack is redrawn in one ink too, so this test covers the pack layer as well
            every = {v.strip().upper() for el in root.iter() for v in paints(el) if HEX.fullmatch(v.strip())}
            chroma = sorted(c for c in every if len(c) == 7 and not colour.is_achromatic(c))
            r.ok(not chroma, f"{rel}: strictly black and white", ", ".join(chroma))
        tags = sorted({el.tag.replace(NS, "") for el in elements} & FORBIDDEN)
        hrefs = sorted({v for el in elements for k, v in el.attrib.items()
                        if k.endswith("href") and not v.startswith("#")})
        r.ok(not tags and not hrefs, f"{rel}: no script/image/text/off-token filters/external refs",
             ", ".join(tags + hrefs))
        r.ok(not bad_op, f"{rel}: opacity only 1 or token blends (0.6 gloss, 0.9 overlap)", ", ".join(sorted(bad_op)))
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

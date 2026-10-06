"""Minimal raster tools for artwork QA, standard library only.

- read_png: 8-bit, non-interlaced greyscale/RGB/RGBA PNG -> ink mask (dark, opaque pixels).
- path_polys / fill: absolute SVG path data (M L H V A Z) -> polygons -> nonzero scanline fill.
- distance: 5-7-11 chamfer distance transform (error vs Euclidean ~2%), in pixel units.
Masks are flat lists of 0/1, row-major, with width w and height h.
"""

import math
import re
import struct
import zlib

# --- PNG -----------------------------------------------------------------------

CHANNELS = {0: 1, 2: 3, 4: 2, 6: 4}


def read_png(path, dark=128, opaque=128):
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos, idat, w = 8, b"", None
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            if depth != 8 or interlace or ctype not in CHANNELS:
                raise ValueError(f"{path}: unsupported PNG (depth {depth}, type {ctype}, interlace {interlace})")
        elif kind == b"IDAT":
            idat += chunk
        pos += 12 + length
    ch = CHANNELS[ctype]
    raw, stride = zlib.decompress(idat), w * ch
    prev, mask, i = bytearray(stride), [], 0
    for _ in range(h):
        f, row = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = row[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1:
                row[x] = (row[x] + a) & 255
            elif f == 2:
                row[x] = (row[x] + b) & 255
            elif f == 3:
                row[x] = (row[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[x] = (row[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        for x in range(w):
            px = row[x * ch:(x + 1) * ch]
            grey = px[0] if ch <= 2 else (px[0] * 299 + px[1] * 587 + px[2] * 114) // 1000
            alpha = px[-1] if ch in (2, 4) else 255
            mask.append(1 if alpha >= opaque and grey < dark else 0)
        prev = row
    return w, h, mask


# --- SVG path -> polygons ---------------------------------------------------------

TOKEN = re.compile(r"[MLHVAZmlhvaz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?")


def _arc(x1, y1, rx, ry, phi, large, sweep, x2, y2, segs=48):
    """SVG endpoint arc -> points (excluding start), per SVG 1.1 F.6.5."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = cp * cxp - sp * cyp + (x1 + x2) / 2, sp * cxp + cp * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(4, int(segs * abs(dt) / math.pi))
    return [(cx + rx * math.cos(t1 + dt * k / n) * cp - ry * math.sin(t1 + dt * k / n) * sp,
             cy + rx * math.cos(t1 + dt * k / n) * sp + ry * math.sin(t1 + dt * k / n) * cp) for k in range(1, n + 1)]


def path_polys(d):
    """Absolute M/L/H/V/A/Z path data -> list of closed polygons."""
    toks, i, polys, cur, x, y, cmd = TOKEN.findall(d), 0, [], [], 0.0, 0.0, None
    num = lambda: float(toks[i])
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            if t.islower() and t != "z":
                raise ValueError(f"relative path command '{t}' not supported")
            cmd = t.upper()
            i += 1
            if cmd == "Z":
                if cur:
                    polys.append(cur)
                cur = []
                continue
        if cmd == "M":
            if cur:
                polys.append(cur)
            x, y = num(), float(toks[i + 1]); i += 2
            cur = [(x, y)]
            cmd = "L"
        elif cmd == "L":
            x, y = num(), float(toks[i + 1]); i += 2
            cur.append((x, y))
        elif cmd == "H":
            x = num(); i += 1
            cur.append((x, y))
        elif cmd == "V":
            y = num(); i += 1
            cur.append((x, y))
        elif cmd == "A":
            rx, ry, phi, large, sweep, nx, ny = (float(toks[i + k]) for k in range(7)); i += 7
            cur += _arc(x, y, rx, ry, phi, int(large), int(sweep), nx, ny)
            x, y = nx, ny
        else:
            raise ValueError(f"unexpected token {t!r}")
    if cur:
        polys.append(cur)
    return polys


def fill(polys, w, h, scale=1.0, ox=0.0, oy=0.0, mask=None):
    """Nonzero scanline fill at pixel centres; ORs into mask (one SVG <path> per call)."""
    mask = mask if mask is not None else [0] * (w * h)
    edges = []
    for poly in polys:
        pts = [((px - ox) * scale, (py - oy) * scale) for px, py in poly]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if y0 != y1:
                edges.append((x0, y0, x1, y1))
    for row in range(h):
        yc = row + 0.5
        xs = []
        for x0, y0, x1, y1 in edges:
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append((x0 + (yc - y0) * (x1 - x0) / (y1 - y0), 1 if y1 > y0 else -1))
        xs.sort()
        wind, start = 0, None
        for xv, dwn in xs:
            prev = wind
            wind += dwn
            if prev == 0 and wind != 0:
                start = xv
            elif prev != 0 and wind == 0:
                a, b = max(0, math.ceil(start - 0.5)), min(w - 1, math.floor(xv - 0.5))
                base = row * w
                for col in range(a, b + 1):
                    mask[base + col] = 1
    return mask


# --- distance transform -------------------------------------------------------------

def distance(mask, w, h, to=0):
    """Chamfer 5-7-11 distance (pixels) from every pixel to the nearest pixel whose value == to."""
    INF = 10 ** 9
    d = [0 if v == to else INF for v in mask]
    fwd = ((-1, 0, 5), (0, -1, 5), (-1, -1, 7), (1, -1, 7), (-2, -1, 11), (-1, -2, 11), (1, -2, 11), (2, -1, 11))
    bwd = tuple((-dx, -dy, c) for dx, dy, c in fwd)
    for offs, rows, cols in ((fwd, range(h), range(w)), (bwd, range(h - 1, -1, -1), range(w - 1, -1, -1))):
        for y in rows:
            for x in cols:
                i = y * w + x
                v = d[i]
                if v == 0:
                    continue
                for dx, dy, c in offs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        n = d[ny * w + nx] + c
                        if n < v:
                            v = n
                d[i] = v
    return [v / 5 for v in d]


def components(mask, w, h, values=None, pixels=False):
    """4-connected components of 1-pixels -> list of sizes, or (size, max value) pairs when values is given,
    or (size, max value, pixel indices) when pixels is True."""
    seen, sizes = bytearray(len(mask)), []
    for s in range(len(mask)):
        if mask[s] and not seen[s]:
            stack, n, top, members = [s], 0, 0.0, []
            seen[s] = 1
            while stack:
                i = stack.pop()
                n += 1
                if pixels:
                    members.append(i)
                if values is not None:
                    top = max(top, values[i])
                x, y = i % w, i // w
                for j, ok in ((i - 1, x > 0), (i + 1, x < w - 1), (i - w, y > 0), (i + w, y < h - 1)):
                    if ok and mask[j] and not seen[j]:
                        seen[j] = 1
                        stack.append(j)
            sizes.append((n, top, members) if pixels else (n, top) if values is not None else n)
    return sizes


def bbox(mask, w, h, x0=0, x1=None):
    x1 = w if x1 is None else x1
    xs = [x for y in range(h) for x in range(x0, x1) if mask[y * w + x]]
    ys = [y for y in range(h) for x in range(x0, x1) if mask[y * w + x]]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _self_test():
    m = fill(path_polys("M2 2H8V8H2Z"), 10, 10)
    assert sum(m) == 36, sum(m)
    circ = fill(path_polys("M0 50A50 50 0 1 1 100 50A50 50 0 1 1 0 50Z"), 100, 100)
    assert abs(sum(circ) - math.pi * 2500) / (math.pi * 2500) < 0.01
    dt = distance(circ, 100, 100, to=0)
    assert abs(max(dt) - 50) <= 1.5, max(dt)


_self_test()

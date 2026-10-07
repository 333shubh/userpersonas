"""Build the task's overview board: maggi-persona-overview.png (brief Section 7, 18.1-18.5).

    python tools/build-overview.py [--html]

Art direction (project lead, 2026-10-07; references brief/references/inspo/layout-v2/): a collector's
sticker-book collage, built in depth planes so the board reads with parallax:
  1. back      planner-grid paper and giant outlined hours, one per persona, in the order of the day
  2. middle    each persona's world as a torn, tilted card, the cards stacked and overlapping: its own eating
               scene out of focus and tinted in its colours, with a solid spine strip carrying the mascot name
  3. thread    the noodle thread (brand.noodle-thread): one continuous line at the mascots' feet, flat where
               it crosses from one world to the next and taking each world's form in between
  4. figures   the seven 3D heroes cut out of their studio sweeps as die-cut stickers, heads breaking out
               above their cards into the hour plane
  5. stickers  per persona: a torn label (persona and motivation), the eating scene as a sharp taped
               polaroid, the real pack as a die-cut sticker, the sachet rule as a handwritten note;
               for the board: the title on torn paper with the red-over-yellow tape, and a wide receipt
               above the worlds that indexes the day; a light paper grain over everything
Colours and copy come from tokens.json. Type is the three shared editorial faces only
(brand.type.editorial): one heading face for the title, every mascot name and the hours, one content face,
one hand face for notes and captions. Rendered by headless Chrome or Edge. --html prints the path of the kept HTML.
"""

import html
import importlib.util
import math
import re
import shutil
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "google-chrome", "chromium", "chrome", "msedge"]
PACKS = tk.ROOT / "brief" / "references" / "packs"
OUT = tk.ROOT / "maggi-persona-overview.png"

COL = 1080                     # one persona per 1080 px column
H = 2560                       # board height
CUT_WORK = 512                 # analysis size for cutting each hero out of its studio sweep
FLOOR_BAND, FLOOR_TOL = 0.78, 45
FIG_H, FIG_W = 1080, 760       # figure box (px): leaves the spine strip clear for the vertical name
LABEL_TOP, POLA_TOP, NOTE_TOP = 1750, 1880, 2010
CARD_TOP, CARD_BOTTOM = 520, 1700
# per-column collage rhythm: card tilt (deg), vertical jitter (px), horizontal jitter (px)
TILT = (-2.2, 1.8, -1.4, 2.4, -2.0, 1.6, -1.2)
JIT_Y = (0, 36, -24, 28, -32, 20, 4)
JIT_X = (-10, 14, -6, 10, -14, 8, -4)
WHITE = "#FFFFFF"              # sticker stock = Cram's role.bg, the system's pure white
VARIABLE = {"Bricolage Grotesque"}


def v(x):
    return x.get("$value", x) if isinstance(x, dict) else x


def stack(fam):
    return ", ".join(f"'{f}'" if " " in f else f for f in v(fam))


def google_fonts(families):
    q = "&".join("family=" + f.replace(" ", "+") + (":wght@400;600;700;800" if f in VARIABLE else "")
                 for f in sorted(families))
    return f"https://fonts.googleapis.com/css2?{q}&display=block"


FONT_CACHE = tk.ROOT / ".cache" / "fonts"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def font_css(families):
    """@font-face CSS with every woff2 downloaded once to .cache/fonts (git-ignored) and referenced as a local
    file, so headless renders never fall back to system fonts when the network is slow."""
    import hashlib
    import urllib.request
    FONT_CACHE.mkdir(parents=True, exist_ok=True)
    url = google_fonts(families)
    key = FONT_CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".css")
    if not key.exists():
        css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode()
        def local(m):
            src = m.group(1)
            dst = FONT_CACHE / (hashlib.sha1(src.encode()).hexdigest()[:16] + ".woff2")
            if not dst.exists():
                dst.write_bytes(urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": UA}), timeout=30).read())
            return f"url({dst.as_uri()})"
        key.write_text(re.sub(r"url\((https://[^)]+)\)", local, css), encoding="utf-8")
    return key.read_text(encoding="utf-8")


# ---------- cutouts ----------

def _check_heroes():
    spec = importlib.util.spec_from_file_location("check_heroes", Path(__file__).parent / "check-heroes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cutout(src, dst):
    """Cut the figure out of its studio sweep (same region growing as check-heroes, at CUT_WORK px). On the
    floor band the colour match is looser: contact shadows are smooth gradients, so growth (in steps of
    STEP_TOL) eats them but stops at the sharp edge of a shoe. Saves an RGBA PNG cropped to the figure."""
    ch = _check_heroes()
    full = Image.open(src).convert("RGB")
    im = full.resize((CUT_WORK, CUT_WORK), Image.LANCZOS)
    px = im.load()
    w = h = CUT_WORK
    border = [px[x, y] for x in range(0, w, 8) for y in (0, h - 1)] + [px[x, y] for y in range(0, h, 8) for x in (0, w - 1)]
    dist = lambda a, b: (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 3
    memo = {}

    def near_bg(c, floor):
        key = (c, floor)
        if key not in memo:
            memo[key] = min(dist(c, b) for b in border) <= (FLOOR_TOL if floor else ch.BG_TOL)
        return memo[key]

    floor_y = int(h * FLOOR_BAND)
    bg = bytearray(w * h)
    q = deque([(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)])
    for x, y in q:
        bg[y * w + x] = 1
    while q:
        x, y = q.popleft()
        c = px[x, y]
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not bg[ny * w + nx]:
                n = px[nx, ny]
                if dist(c, n) <= ch.STEP_TOL and near_bg(n, ny >= floor_y):
                    bg[ny * w + nx] = 1
                    q.append((nx, ny))
    mask = ch.trim_floor([0 if b else 1 for b in bg], w, h)
    m = Image.new("L", (w, h))
    m.putdata([255 if b else 0 for b in mask])
    alpha = m.resize(full.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    rgba = full.convert("RGBA")
    rgba.putalpha(alpha)
    rgba = rgba.crop(alpha.point(lambda a: 255 if a > 128 else 0).getbbox())
    rgba.save(dst)
    return rgba.size


def pack_sticker(p, dst):
    """Real pack as a sticker source, Cram's pack in greyscale, the nutrition badge area softened (Section 22).
    Transparent PNG packs are used as they are. A pack shot on a white mock-up background (JPEG) is cut to
    its printed body: the rows and columns that are mostly saturated or dark pixels, which leaves out the
    white backdrop and the light-grey foil crimps, with slightly rounded corners."""
    src = Image.open(PACKS / v(p["product"]["packImage"]))
    im = src.convert("RGBA")
    badge = (0.0, 0.62, 0.5, 1.0)
    if src.mode == "RGB":
        rgb = src.convert("RGB")
        keep = Image.new("L", rgb.size)
        keep.putdata([255 if (max(c) - min(c) > 60 or max(c) < 110) else 0 for c in rgb.get_flattened_data()])
        keep = keep.filter(ImageFilter.MinFilter(5))            # ignore specks and soft shadows
        w, h = keep.size
        kp = keep.load()
        rows = [y for y in range(h) if sum(1 for x in range(w) if kp[x, y]) > 0.25 * w]
        y0, y1 = rows[0], rows[-1]                               # rows that are mostly print, not foil crimp
        cols = [x for x in range(w) if sum(1 for y in range(y0, y1) if kp[x, y]) > 0.25 * (y1 - y0)]
        x0, x1 = cols[0], cols[-1]
        im = im.crop((x0 + 2, y0 + 10, x1 - 2, y1 - 2))
        mask = Image.new("L", im.size)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=14, fill=255)
        im.putalpha(mask)
        badge = (0.0, 0.81, 0.42, 1.0)                           # this pack's badges sit in the bottom-left corner
    im = im.crop(im.getbbox())
    if p["id"] == "cram":
        g = im.convert("L")
        im = Image.merge("RGBA", (g, g, g, im.getchannel("A")))
    w0, h0 = im.size
    box = (int(w0 * badge[0]), int(h0 * badge[1]), int(w0 * badge[2]), int(h0 * badge[3]))
    im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(max(2, w0 // 120))), box[:2])
    im.save(dst)
    return im.size


# ---------- the noodle thread ----------

ZONES = ((0.04, 0.34), (0.66, 0.96))   # the form plays out in the outer thirds; the mascot stands on the middle


def zone_points(pid, x0, x1, y, side):
    w, n = x1 - x0, 160
    pts = []
    for i in range(n + 1):
        u = i / n
        x, dy = x0 + w * u, 0.0
        if pid == "sprig":       # vine: two soft crests per zone
            dy = -34 * math.sin(2 * math.pi * u) ** 2
        elif pid == "riot":      # flame hair: three pointed tips per zone, tall and short alternating
            k = 3
            tri = 1 - abs(2 * ((k * u) % 1) - 1)
            dy = -(72 if int(k * u) % 2 == 0 else 48) * tri ** 1.6
        elif pid == "nest":      # yarn: two loops per zone
            th = 2 * math.pi * 2 * u
            x -= 46 * math.sin(th)
            dy = -46 * (1 - math.cos(th))
        elif pid == "cram":      # zine underline: marker wobble with one small scribble loop
            dy = 6 * math.sin(7 * math.pi * u) - 3 * math.sin(23 * math.pi * u)
            if 0.7 <= u <= 0.9:
                th = 2 * math.pi * (u - 0.7) / 0.2
                x -= 30 * math.sin(th)
                dy -= 30 * (1 - math.cos(th))
        elif pid == "mise":      # chopstick-lifted ribbon: a gentle drape, then one high lift
            dy = (-150 if side else -36) * math.sin(math.pi * u) ** 2
        elif pid == "lull":      # steam: one leaning wisp per zone
            dy = -52 * math.sin(math.pi * u) ** 2 * (1 + 0.5 * math.sin(2 * math.pi * u))
        pts.append((x, y + dy))
    return pts


def thread_segment(pid, x0, y):
    pts = [(x0, y)]
    for side, (a, b) in enumerate(ZONES):
        pts += [(x0 + COL * a, y)]
        if pid != "stack":
            pts += zone_points(pid, x0 + COL * a, x0 + COL * b, y, side)
        pts += [(x0 + COL * b, y)]
    pts.append((x0 + COL, y))
    return "M" + " L".join(f"{x:.1f} {yy:.1f}" for x, yy in pts)


def thread_svg(ps, res, width, y):
    sw = round(H * v(res["brand"]["noodle-thread"]["stroke"]))
    parts = []
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        d = thread_segment(pid, COL * i, y)
        colour = {"riot": r["accent"], "lull": r["accent"], "sprig": r["key"], "mise": r["text"],
                  "nest": r["accent"]}.get(pid, r["line"])
        if pid == "riot":    # clash: volt keyline plate offset 6 px under the hot-pink thread
            parts.append(f'<path d="{d}" transform="translate(6 6)" stroke="{r["focus"]}" />')
        if pid == "lull":
            parts.append(f'<path d="{d}" stroke="{colour}" stroke-width="{sw * 3}" opacity="0.35" filter="url(#glow)" />')
        parts.append(f'<path d="{d}" stroke="{colour}" />')
        if pid == "sprig":
            for a, b in ZONES:
                for u, lean in ((0.25, -35), (0.75, 35)):
                    x = COL * i + COL * (a + (b - a) * u)
                    parts.append(f'<ellipse cx="{x:.1f}" cy="{y - 62}" rx="13" ry="24" fill="{colour}" stroke="none" '
                                 f'transform="rotate({lean} {x:.1f} {y - 38})" />')
        if pid == "stack":
            for x in range(128, COL - 64, 128):
                parts.append(f'<rect x="{COL * i + x - 4}" y="{y}" width="8" height="24" fill="{colour}" stroke="none" />')
    return (f'<svg class="thread" width="{width}" height="{H}" viewBox="0 0 {width} {H}">'
            f'<defs><filter id="glow" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="10" /></filter></defs>'
            f'<g fill="none" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{"".join(parts)}</g></svg>')


# ---------- page ----------

def torn_rect(w, h, seed, amp=9, step=36):
    """clip-path polygon (px) for a sheet torn on all four edges, deterministic per seed."""
    def j(k):
        return ((seed * 31 + k * 17) % 11 - 5) / 5 * amp
    pts, k = [], 0
    for x in range(0, w + 1, step):
        pts.append((x, amp + j(k))); k += 1
    for y in range(step, h + 1, step):
        pts.append((w - amp - j(k), y)); k += 1
    for x in range(w - step, -1, -step):
        pts.append((x, h - amp - j(k))); k += 1
    for y in range(h - step, 0, -step):
        pts.append((amp + j(k), y)); k += 1
    return "polygon(" + ", ".join(f"{x:.0f}px {y:.0f}px" for x, y in pts) + ")"


def receipt_clip():
    teeth = ", ".join(f'{x}% {"100%" if k % 2 else "calc(100% - 22px)"}' for k, x in enumerate(range(100, -1, -4)))
    return f"polygon(0 0, 100% 0, {teeth})"


def build_html(res, tmp):
    ps = sorted(tk.personas(res), key=lambda t: v(t[1]["day"]["order"]))
    b = res["brand"]
    bc = {k: v(b["color"][k]) for k in ("red", "yellow", "ink", "paper")}
    ed = b["type"]["editorial"]
    f_disp, f_text, f_hand = stack(ed["display"]), stack(ed["text"]), stack(ed["hand"])
    width = COL * len(ps)
    thread_y = round(H * v(b["noodle-thread"]["entry-height"]))
    fams = {v(ed[k])[0] for k in ("display", "text", "hand")}
    card_w, card_h = 1020, CARD_BOTTOM - CARD_TOP

    css = f"""
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ width: {width}px; height: {H}px; position: relative; overflow: hidden; color: {bc['ink']};
            background-color: {bc['paper']};
            background-image: linear-gradient(rgba(28,20,16,.06) 2px, transparent 2px),
                              linear-gradient(90deg, rgba(28,20,16,.06) 2px, transparent 2px);
            background-size: 48px 48px; font-family: {f_text}; }}
    .hour {{ position: absolute; top: 70px; font-family: {f_disp}; font-size: 300px; line-height: 1; color: transparent;
             -webkit-text-stroke: 4px rgba(28,20,16,.2); white-space: nowrap; z-index: 1; }}
    .cardwrap {{ position: absolute; z-index: 2; filter: drop-shadow(0 34px 44px rgba(28,20,16,.32)) drop-shadow(0 4px 8px rgba(28,20,16,.2)); }}
    .card {{ position: relative; width: {card_w}px; height: {card_h}px; overflow: hidden; }}
    .card .world {{ position: absolute; inset: -40px; background-size: cover; background-position: center;
                    filter: blur(9px) saturate(.9); transform: scale(1.06); }}
    .card .tint {{ position: absolute; inset: 0; }}
    .card .spine {{ position: absolute; top: 0; bottom: 0; width: 230px; }}
    .card .name {{ position: absolute; top: 56px; font-family: {f_disp}; font-size: 190px; line-height: .86; white-space: nowrap;
                   writing-mode: vertical-rl; transform: rotate(180deg); }}
    .thread {{ position: absolute; left: 0; top: 0; z-index: 3; }}
    .fig {{ position: absolute; z-index: 4;
            filter: drop-shadow(7px 0 0 {WHITE}) drop-shadow(-7px 0 0 {WHITE}) drop-shadow(0 7px 0 {WHITE})
                    drop-shadow(0 -7px 0 {WHITE}) drop-shadow(0 30px 34px rgba(28,20,16,.4)); }}
    .st {{ position: absolute; z-index: 5; }}
    .shadow {{ filter: drop-shadow(0 18px 24px rgba(28,20,16,.26)); }}
    .tape {{ position: absolute; width: 170px; height: 46px; background: rgba(255,194,14,.6); z-index: 6; mix-blend-mode: multiply; }}
    .label {{ width: 470px; height: 250px; padding: 32px 38px 34px; background: {WHITE}; }}
    .label b {{ display: block; font-size: 38px; font-weight: 800; line-height: 1.05; letter-spacing: -.01em; }}
    .label span {{ display: block; font-size: 30px; line-height: 1.25; margin-top: 8px; }}
    .pola {{ width: 520px; padding: 20px 20px 0; background: {WHITE}; }}
    .pola img {{ width: 480px; height: 320px; object-fit: cover; display: block; }}
    .pola p {{ font-family: {f_hand}; font-size: 34px; line-height: 1.1; padding: 20px 4px 26px; color: {bc['ink']}; }}
    .note {{ width: 430px; padding: 36px 36px 42px; background: {bc['paper']}; font-family: {f_hand}; font-size: 32px; line-height: 1.25; }}
    .pk {{ filter: drop-shadow(6px 0 0 {WHITE}) drop-shadow(-6px 0 0 {WHITE}) drop-shadow(0 6px 0 {WHITE})
                   drop-shadow(0 -6px 0 {WHITE}) drop-shadow(0 18px 22px rgba(28,20,16,.3)); }}
    .title {{ position: absolute; left: 60px; top: 40px; z-index: 6; transform: rotate(-1.8deg); }}
    .title .sheet {{ padding: 54px 70px 60px; background: {WHITE}; }}
    .title h1 {{ font-family: {f_disp}; font-weight: 400; font-size: 118px; line-height: .92; letter-spacing: -.01em; }}
    .title p {{ font-family: {f_hand}; font-size: 44px; margin-top: 22px; }}
    .heritage {{ position: absolute; width: 480px; height: 48px; z-index: 7;
                 background: linear-gradient({bc['red']} 0 50%, {bc['yellow']} 50% 100%); }}
    .receiptwrap {{ position: absolute; right: 70px; top: 46px; z-index: 6; transform: rotate(1.4deg); }}
    .receipt {{ width: 1640px; padding: 30px 40px 52px; background: {WHITE}; font-size: 24px; line-height: 1.35;
                clip-path: {receipt_clip()}; }}
    .receipt .top {{ display: flex; justify-content: space-between; align-items: baseline; }}
    .receipt h2 {{ font-family: {f_disp}; font-weight: 400; font-size: 52px; line-height: 1; }}
    .receipt .top span {{ font-size: 24px; }}
    .receipt hr {{ border: 0; border-top: 3px dashed {bc['ink']}; margin: 18px 0; }}
    .receipt .stubs {{ display: grid; grid-template-columns: repeat({len(ps)}, 1fr); }}
    .receipt .stub {{ padding: 0 16px; border-left: 3px dashed rgba(28,20,16,.35); }}
    .receipt .stub:first-child {{ border-left: 0; padding-left: 0; }}
    .receipt .stub b {{ display: block; font-family: {f_disp}; font-weight: 400; font-size: 34px; line-height: 1.1; }}
    .receipt .stub i {{ display: block; font-style: normal; font-weight: 700; margin-top: 6px; }}
    .receipt .stub span {{ display: block; color: rgba(28,20,16,.7); }}
    .grain {{ position: absolute; inset: 0; z-index: 9; pointer-events: none; mix-blend-mode: multiply; opacity: .22;
              background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .11 0 0 0 0 .08 0 0 0 0 .06 0 0 0 .55 0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E"); }}
    """
    hours, cards, figs, stickers, rows = [], [], [], [], []
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        slug, num = p["slug"], p["number"]
        st = tk.ROOT / "static" / slug
        cx = COL * i + COL // 2 + JIT_X[i]
        time = v(p["day"]["time"])
        name = v(p["name"])
        flip = i % 2
        s_ = -1 if flip else 1
        scene = (st / f"{num}-{pid}-scene-with-pack.png").as_uri()

        # 1. hour plane
        hours.append(f'<div class="hour" style="left:{COL * i + 24}px">{html.escape(time)}</div>')

        # 2. world card: the persona's own eating scene, out of focus and tinted, with a solid spine for the name
        top = CARD_TOP + JIT_Y[i]
        name_colour = r["text"] if pid in ("cram", "mise") else r["accent"]
        spine_side = "left:0" if not flip else "right:0"
        name_side = "left:22px" if not flip else "right:22px"
        cards.append(
            f'<div class="cardwrap" style="left:{cx - card_w // 2}px;top:{top}px;transform:rotate({TILT[i]}deg)">'
            f'<div class="card" style="clip-path:{torn_rect(card_w, card_h, i)}">'
            f'<div class="world" style="background-image:url({scene})"></div>'
            f'<div class="tint" style="background:{r["bg"]};opacity:.42"></div>'
            f'<div class="spine" style="{spine_side};background:{r["bg"]}"></div>'
            f'<div class="name" style="{name_side};color:{name_colour}">{html.escape(name)}</div>'
            f'</div></div>')

        # 4. figure, standing on the thread
        cut = tmp / f"{num}-{pid}-figure.png"
        fw, fh = cutout(st / f"{num}-{pid}-hero-with-pack.png", cut)
        sc = min(FIG_H / fh, FIG_W / fw)
        w2, h2 = round(fw * sc), round(fh * sc)
        figs.append(f'<img class="fig" src="{cut.as_uri()}" alt="" style="width:{w2}px;height:{h2}px;'
                    f'left:{cx - w2 // 2 + s_ * 60}px;top:{thread_y + 8 - h2}px">')

        # 5. stickers under the world: persona label, polaroid of the eating moment, sachet note, real pack
        lx = max(24, min(cx - 235 - s_ * 300, width - 494))
        stickers.append(
            f'<div class="st shadow" style="left:{lx}px;top:{LABEL_TOP + JIT_Y[i] // 3}px;transform:rotate({-1.6 * s_}deg)">'
            f'<div class="label" style="clip-path:{torn_rect(470, 250, i + 3, amp=6, step=30)}">'
            f'<b>{html.escape(v(p["persona"]))}</b><span>{html.escape(v(p["primaryMotivation"]))}</span></div></div>')
        product = v(p["product"]["name"]).replace("MAGGI ", "").split(" (")[0].split(",")[0]
        px_ = cx - 260 + s_ * 250
        stickers.append(
            f'<div class="st pola shadow" style="left:{px_}px;top:{POLA_TOP - JIT_Y[i] // 2}px;transform:rotate({3.2 * s_}deg)">'
            f'<img src="{scene}" alt=""><p>{html.escape(time)}, {html.escape(product)}</p></div>')
        stickers.append(f'<div class="tape" style="left:{px_ + 175}px;top:{POLA_TOP - 24 - JIT_Y[i] // 2}px;'
                        f'transform:rotate({-6 * s_}deg)"></div>')
        nx = cx - 215 - s_ * 250
        stickers.append(
            f'<div class="st shadow" style="left:{nx}px;top:{NOTE_TOP}px;transform:rotate({2 * s_}deg)">'
            f'<div class="note" style="clip-path:{torn_rect(430, 230, i + 7, amp=7, step=26)}">'
            f'&ldquo;{html.escape(v(p["sachet"]))}&rdquo;</div></div>')
        pk = tmp / f"{num}-{pid}-pack.png"
        pw, ph = pack_sticker(p, pk)
        sc_pk = min(260 / ph, 260 / pw)       # fit every pack, portrait or landscape, in a 260 px box,
        pkh, pkw = round(ph * sc_pk), round(pw * sc_pk)   # so neighbouring packs never meet
        pkx = cx + 210 if not flip else cx - 210 - pkw   # tucked by the feet: >= 140 px from the next pack
        stickers.append(f'<img class="st pk" src="{pk.as_uri()}" alt="" style="height:{pkh}px;left:{pkx}px;'
                        f'top:{thread_y + 50 - pkh}px;transform:rotate({9 * s_}deg)">')
        rows.append(f'<div class="stub"><b>{html.escape(time)}</b><i>{html.escape(name)}</i>'
                    f'<span>{html.escape(product.replace("2-Minute Noodles ", "").replace(" Noodles", ""))}</span></div>')

    first, last = v(ps[0][1]["day"]["time"]), v(ps[-1][1]["day"]["time"])
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>{font_css(fams)}</style><style>{css}</style></head><body>
{''.join(hours)}
{''.join(cards)}
{thread_svg(ps, res, width, thread_y)}
{''.join(figs)}
{''.join(stickers)}
<div class="title shadow"><div class="sheet" style="clip-path:{torn_rect(2000, 380, 41, amp=8, step=34)};width:2000px;height:380px">
  <h1>Seven ways<br>to eat one packet</h1><p>One day, seven people, one pack of MAGGI.</p></div></div>
<div class="heritage" style="left:1780px;top:26px;transform:rotate(9deg)"></div>
<div class="receiptwrap shadow"><div class="receipt">
  <div class="top"><h2>The day</h2><span>{first} to {last}, seven stops</span></div><hr>
  <div class="stubs">{''.join(rows)}</div><hr>
  <div class="top"><span>Same pack, same sachet, same steam curl.</span><span>Colour, shape and light change with each person.</span></div>
</div></div>
<div class="grain"></div>
<script>
  // fit each hour to its column and each name to its card height
  document.fonts.ready.then(() => {{
    document.querySelectorAll('.hour').forEach(el => {{ el.style.fontSize = (300 * 1020 / el.scrollWidth) + 'px'; }});
    document.querySelectorAll('.card .name').forEach(el => {{
      const room = el.parentElement.clientHeight - 120;
      el.style.fontSize = Math.min(190, 190 * room / el.scrollHeight) + 'px'; }});
  }});
</script>
</body></html>"""


def find_browser():
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b if Path(b).exists() else shutil.which(b)
    raise SystemExit("Chrome or Edge not found")


def render(html_path, png_path, w, h):
    profile = Path(tempfile.mkdtemp(prefix="overview-profile-"))
    cmd = [find_browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
           "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--allow-file-access-from-files",
           f"--user-data-dir={profile}", "--virtual-time-budget=20000",
           f"--screenshot={png_path}", f"--window-size={w},{h}", html_path.as_uri()]
    try:
        subprocess.run(cmd, check=True, timeout=240, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def main(argv):
    res = tk.resolve_all(tk.load())
    w = COL * len(tk.personas(res))
    tmp = Path(tempfile.mkdtemp(prefix="overview-"))
    page = tmp / "overview.html"
    page.write_text(build_html(res, tmp), encoding="utf-8")
    render(page, OUT, w, H)
    if "--html" in argv:
        print(f"html: {page}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"wrote {OUT.relative_to(tk.ROOT).as_posix()} ({w} x {H})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

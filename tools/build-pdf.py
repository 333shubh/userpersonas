"""Build the task's system PDF: maggi-persona-system.pdf (brief Section 7).

    python tools/build-pdf.py [--preview] [--only cover,contents,riot] [--out file.pdf]

Art direction (project lead, 2026-10-07; references brief/references/inspo/layout-v2/): a collector's zine for
a designer-toy series. 1920 x 1080 landscape pages, built in layers like the overview board: paper, poster
type, die-cut mascots, taped polaroids, torn notes, retro OS windows and ID cards.
  cover      ink page, the seven figures marching in one overlapping line (ref 11) under giant type (ref 02)
  contents   brand-yellow page, chapter list plus the seven mascots as name stickers (ref 01)
  persona    four pages per persona:
             opener  poster splash: giant cropped name, the figure breaking out, OS windows (refs 02, 05, 08)
             file    character file: eater's licence card, profile, needs as torn notes, why MAGGI (refs 03, 04, 10)
             world   visual world: the eating scene, palette as tape spines, type, sachet rule, pack (refs 06, 09, 12)
             market  buying journey as cassette spines, reviews as windows, opportunities receipt (refs 05, 09)
Type is the three shared editorial faces (brand.type.editorial); a persona's own faces appear only in its type
specimen. Colours, copy and numbers come from tokens.json and the persona Markdown files. Rendered by headless
Chrome or Edge to PDF; --preview also writes one PNG per page to stress-tests/qa/pdf-preview/.
"""

import html
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import colour as cl  # noqa: E402
import tokens as tk  # noqa: E402

from PIL import Image  # noqa: E402

OUT = tk.ROOT / "maggi-persona-system.pdf"
PREVIEW = tk.ROOT / "stress-tests" / "qa" / "pdf-preview"
W, H = 1920, 1080
WHITE = "#FFFFFF"


def _overview():
    spec = importlib.util.spec_from_file_location("build_overview", Path(__file__).parent / "build-overview.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


OV = _overview()
v, stack, torn_rect = OV.v, OV.stack, OV.torn_rect
e = html.escape


# ---------- persona Markdown ----------

def md_sections(path):
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^## (\d+)\. .*$", text, flags=re.M)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def clean(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("**", "").replace("*", "").replace("_", "")
    s = s.replace(" [H]", " (hypothesis)").replace(" [§17]", "")
    return s.strip()


def md_rows(text, header=True):
    rows = [l for l in text.splitlines() if l.startswith("|") and not re.match(r"^\|[ :|]*-[-| :]*\|$", l)]
    cells = [[clean(c) for c in r.strip("|").split("|")] for r in rows]
    if header and cells and any(cells[0]):
        cells = cells[1:]
    return [c for c in cells if any(c)]


def first_sentences(text, n):
    para = clean(text.split("\n\n")[0])
    s = re.split(r"(?<=[.!?])\s+", para)
    return " ".join(s[:n])


# ---------- shared pieces ----------

def ink_on(bg, light, dark):
    return dark if cl.contrast(dark, bg) >= cl.contrast(light, bg) else light


def on_light(r, prefer="accent", ground="#FFF8EC", minimum=3.0):
    """Persona colour for text on light paper: the preferred role if it reads (>= 3:1), else the darker of
    text and bg, so cream-on-cream (Mise, Lull) never happens."""
    if cl.contrast(r[prefer], ground) >= minimum:
        return r[prefer]
    return r["text"] if cl.contrast(r["text"], ground) >= cl.contrast(r["bg"], ground) else r["bg"]


def tape(x, y, rot, w=170, colour="rgba(255,194,14,.62)"):
    return f'<i class="tape" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg);background:{colour}"></i>'


def window(title, body, x, y, w, bar, cls="", rot=0):
    return (f'<div class="win {cls}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg)">'
            f'<div class="wbar" style="background:{bar};color:{ink_on(bar, WHITE, "#1C1410")}"><span>{e(title)}</span><b>&times;</b></div>'
            f'<div class="wbody">{body}</div></div>')


def barcode(seed, n=46):
    bars = "".join(f'<i style="width:{1 + (seed * 7 + k * 13) % 4}px"></i>' for k in range(n))
    return f'<div class="barcode">{bars}</div>'


def bake_sticker(im, outline, pad, blur, dy, opacity):
    """Bake the die-cut look into the image once: a white outline (alpha dilated by `outline` px) and a soft
    drop shadow below it. Chrome would otherwise re-rasterize a CSS filter at every use, which multiplies the
    PDF size; a baked PNG is embedded once and reused."""
    from PIL import ImageFilter as F
    im = im.convert("RGBA")
    w, h = im.size
    canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", canvas.size)
    a.paste(im.getchannel("A"), (pad, pad))
    ring = a.filter(F.MaxFilter(outline * 2 + 1)) if outline else a
    shadow = ring.filter(F.GaussianBlur(blur)).point(lambda x: int(x * opacity))
    canvas.paste(Image.new("RGBA", canvas.size, (28, 20, 16, 255)), (0, dy), shadow)
    canvas.paste(Image.new("RGBA", canvas.size, (255, 255, 255, 255)), (0, 0), ring)
    canvas.alpha_composite(Image.new("RGBA", canvas.size, (0, 0, 0, 0)))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(im, (pad, pad))
    return Image.alpha_composite(canvas, layer)


FIG_PAD, PK_PAD = 44, 30


class Assets:
    """Cut-outs and pack stickers, made once per build."""

    def __init__(self, tmp):
        self.tmp = tmp
        self.cache = {}

    def figure(self, p):
        key = ("fig", p["id"])
        if key not in self.cache:
            dst = self.tmp / f"{p['number']}-{p['id']}-figure.png"
            OV.cutout(tk.ROOT / "static" / p["slug"] / f"{p['number']}-{p['id']}-hero-with-pack.png", dst)
            im = Image.open(dst)
            if im.height > 1040:                     # largest use is 1010 px tall
                im = im.resize((round(im.width * 1040 / im.height), 1040), Image.LANCZOS)
            im = bake_sticker(im, outline=8, pad=FIG_PAD, blur=14, dy=22, opacity=.4)
            im.save(dst, optimize=True)
            self.cache[key] = (dst.as_uri(), im.size)
        return self.cache[key]

    def pack(self, p):
        key = ("pack", p["id"])
        if key not in self.cache:
            dst = self.tmp / f"{p['number']}-{p['id']}-pack.png"
            OV.pack_sticker(p, dst)
            im = Image.open(dst)
            if max(im.size) > 420:
                s = 420 / max(im.size)
                im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            im = bake_sticker(im, outline=6, pad=PK_PAD, blur=10, dy=14, opacity=.38)
            im.save(dst, optimize=True)
            self.cache[key] = (dst.as_uri(), im.size)
        return self.cache[key]

    def scene(self, p):
        """Eating scene as a JPEG (quality 86), so the PDF embeds it as a photo, not a lossless bitmap."""
        key = ("scene", p["id"])
        if key not in self.cache:
            dst = self.tmp / f"{p['number']}-{p['id']}-scene.jpg"
            Image.open(tk.ROOT / "static" / p["slug"] / f"{p['number']}-{p['id']}-scene-with-pack.png").convert("RGB").save(
                dst, quality=86, optimize=True)
            self.cache[key] = dst.as_uri()
        return self.cache[key]

    def grain(self):
        """A 256 px tile of soft ink speckle with alpha, tiled over each page (no blend mode, no live filter)."""
        dst = self.tmp / "grain.png"
        if not dst.exists():
            import random
            rnd = random.Random(7)
            im = Image.new("LA", (256, 256))
            im.putdata([(28, rnd.randrange(0, 16) if rnd.random() < .45 else 0) for _ in range(256 * 256)])
            im.save(dst)
        return dst.as_uri()


def fig_img(a, p, h, x, y, cls="fig", extra=""):
    uri, (fw, fh) = a.figure(p)
    w = round(fw * h / fh)
    return f'<img class="{cls}" src="{uri}" alt="" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}">', w


def pack_img(a, p, box, x, y, rot):
    uri, (pw, ph) = a.pack(p)
    s = min(box / pw, box / ph)
    return f'<img class="pk" src="{uri}" alt="" style="left:{x}px;top:{y}px;width:{round(pw * s)}px;height:{round(ph * s)}px;transform:rotate({rot}deg)">'


# ---------- pages ----------

def page_cover(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    figs, x = [], 0
    heights = (540, 575, 550, 545, 590, 585, 535)
    for i, (pid, p) in enumerate(ps):
        uri, (fw, fh) = a.figure(p)
        h = heights[i]
        w = round(fw * h / fh)
        figs.append(f'<img class="fig" src="{uri}" alt="" style="left:{x}px;top:{1046 - h}px;width:{w}px;height:{h}px;z-index:{10 + (i % 2)}">')
        x += round(w * 0.64)
        last_w = w
    shift = (W - (x - round(last_w * 0.64) + last_w)) // 2       # centre the marching line
    figs = [f.replace("left:", "left:calc(" + str(shift) + "px + ", 1).replace("px;top:", "px);top:", 1) for f in figs]
    return f"""
    <section class="page ink" style="background:{bc['ink']};color:{bc['paper']}">
      <div class="corner tl">MAGGI persona system<br>Design system and mascot series</div>
      <div class="corner tr">Vol. 01<br>2026</div>
      <h1 class="cv1"><span class="fit" data-w="1780">Seven ways</span></h1>
      <h1 class="cv2 outline"><span class="fit" data-w="1780">to eat one packet</span></h1>
      {''.join(figs)}
      <div class="heritage" style="left:1560px;top:6px;transform:rotate(-14deg);width:420px"></div>
      <p class="hand" style="position:absolute;left:640px;top:40px;font-size:36px;color:{bc['yellow']};transform:rotate(-4deg);z-index:20">one day, seven people, one pack. collect all seven.</p>
    </section>"""


def page_contents(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    other = [(1, "Research and insight"), (2, "MAGGI brand DNA"), (3, "Persona map")] + \
            [(11, "Visual worlds"), (12, "Motion system"), (13, "Applications"), (14, "Competitors and opportunities")]
    items = "".join(f'<li><b>{n:02d}</b><span>{e(t)}</span></li>' for n, t in other)
    slots = [(820, 120, -4), (1090, 80, 3), (1360, 130, -2), (1630, 90, 3), (900, 590, 2), (1180, 560, -3), (1460, 610, 4)]
    stickers = []
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        x, y, rot = slots[i]
        uri, (fw, fh) = a.figure(p)
        fh2 = 230
        fw2 = round(fw * fh2 / fh)
        nm = r["text"] if pid in ("cram", "mise") else r["accent"]
        stickers.append(
            f'<div class="cstick" style="left:{x}px;top:{y}px;transform:rotate({rot}deg)">'
            f'<img class="fig" src="{uri}" alt="" style="position:relative;width:{fw2}px;height:{fh2}px">'
            f'<div class="ctag" style="background:{r["bg"]};color:{nm};clip-path:{torn_rect(250, 110, i + 20, amp=5, step=24)}">'
            f'<b>{e(v(p["name"]))}</b><span style="color:{r["text"]}">{4 + i:02d} {e(v(p["day"]["time"]))}</span></div></div>')
    return f"""
    <section class="page grid" style="background-color:{bc['yellow']};color:{bc['ink']}">
      <div class="corner tl">MAGGI persona system</div><div class="corner tr">Contents</div>
      <h1 class="ct"><span class="fit" data-w="680">Contents</span></h1>
      <p class="hand" style="position:absolute;left:84px;top:300px;font-size:40px;transform:rotate(-3deg)">read it in the order of the day</p>
      <ol class="toc">{items}</ol>
      <div class="toc-p"><b>04 to 10</b><span>Seven persona chapters, 07:30 to 00:45</span></div>
      {''.join(stickers)}
    </section>"""


def page_opener(ctx, pid, p, md):
    a, bc = ctx["a"], ctx["bc"]
    r = {k: v(x) for k, x in p["role"].items()}
    order = v(p["day"]["order"])
    name, time = v(p["name"]), v(p["day"]["time"])
    nm = r["text"] if pid in ("cram", "mise") else r["accent"]
    plate = f'<h1 class="op-name plate" style="color:{r["focus"]}">{e(name)}</h1>' if pid == "riot" else ""
    # the figure ends at x 1500; the two windows own the column right of it, so nothing sits on the mascot
    _, (fw0, fh0) = a.figure(p)
    fh_ = min(960, round(fh0 * 620 / fw0))
    fx = max(820, 1500 - round(fw0 * fh_ / fh0))
    fig, fw = fig_img(a, p, fh_, fx, 1060 - fh_, extra="z-index:5")
    reviews = md_rows(md[13])
    pos = reviews[0][1].strip('"') if reviews else ""
    scene = a.scene(p)
    gate = v(p["spine"]["gate"]).strip('"')
    win1 = window(f"{pid}_{time.replace(':', '')}.jpg", f'<img src="{scene}" alt="" style="width:100%;height:250px;object-fit:cover;display:block">',
                  1530, 110, 350, r["focus"] if pid != "cram" else "#000000", rot=2)
    win2 = window("review.txt", f'<p class="hand" style="font-size:26px">&ldquo;{e(pos)}&rdquo;</p><small>Synthesised composite, not a real customer quote</small>',
                  1530, 560, 350, r["accent"] if pid not in ("cram", "mise") else r["text"], rot=-2)
    return f"""
    <section class="page" style="background:{r['bg']};color:{r['text']}">
      <div class="op-block" style="background:{r['surface']}"></div>
      <div class="corner tl" style="color:{r['text']}">Chapter {3 + order:02d} &nbsp; {e(time)}</div>
      <div class="corner tr" style="color:{r['text']}">{e(v(p['day']['light']))}</div>
      {plate}<h1 class="op-name" style="color:{nm}">{e(name)}</h1>
      <div class="op-hour outline-ink" style="-webkit-text-stroke-color:{r['text']}">{e(time)}</div>
      {fig}
      <div class="op-text shadow"><div class="sheet" style="clip-path:{torn_rect(760, 400, order + 50, amp=7, step=30)}">
        <h2>{e(v(p['persona']))}</h2>
        <p class="mot">Wants: {e(v(p['primaryMotivation']))}</p>
        <p>{e(first_sentences(md[2], 3))}</p></div></div>
      <div class="op-gate hand" style="color:{r['text']}">The gate: &ldquo;{e(gate)}&rdquo;</div>
      {win1}{win2}
    </section>"""


def page_file(ctx, pid, p, md):
    a, bc = ctx["a"], ctx["bc"]
    r = {k: v(x) for k, x in p["role"].items()}
    name, time = v(p["name"]), v(p["day"]["time"])
    order = v(p["day"]["order"])
    uri, (fw, fh) = a.figure(p)
    prof = md_rows(md[3])
    needs = md_rows(md[5])
    product = v(p["product"]["name"]).replace("MAGGI ", "")
    fields = [("Name", name), ("Class", v(p["persona"])), ("Hour", time), ("Pack", product.split(",")[0].split(" (")[0]),
              ("Buyer", v(p["spine"]["buyer"])), ("Eats with", v(p["spine"]["eater"]))]
    lic = "".join(f'<div><small>{e(k)}</small><b>{e(val)}</b></div>' for k, val in fields)
    prof_html = "".join(f'<div><small>{e(k)}</small><span>{e(val)}</span></div>' for k, val in prof)
    tints = (WHITE, bc["paper"], WHITE, bc["paper"])
    notes = ""
    for k, (label, text) in enumerate(needs[:4]):
        x, y = 900 + (k % 2) * 500, 70 + (k // 2) * 285
        rot = (-2, 1.6, 1.2, -1.8)[k]
        notes += (f'<div class="note-wrap shadow" style="left:{x}px;top:{y}px;transform:rotate({rot}deg)">'
                  f'<div class="note2" style="background:{tints[k]};clip-path:{torn_rect(450, 250, order * 4 + k, amp=6, step=26)}">'
                  f'<h3 style="color:{on_light(r)}">{e(label)}</h3><p>{e(text)}</p></div></div>'
                  + tape(x + 140, y - 16, (-5, 4, 6, -4)[k]))
    why = first_sentences(md[6], 2)
    return f"""
    <section class="page grid" style="background-color:{bc['paper']};color:{bc['ink']}">
      <div class="corner tl">Persona file {order:02d} of 07</div><div class="corner tr">{e(name)}, {e(time)}</div>
      <h1 class="fl-name" style="color:{on_light(r, 'text')}">{e(name)}</h1>
      <p class="fl-sub">{e(v(p['persona']))}. {e(v(p['job']))}.</p>
      <div class="lic shadow" style="transform:rotate(-2deg)">
        <div class="lic-head" style="background:{on_light(r, 'text')};color:{ink_on(on_light(r, 'text'), '#FFFFFF', '#1C1410')}">
          <b>MAGGI eater's licence</b><span>No. {p['number']}-{time.replace(':', '')}</span></div>
        <div class="lic-body">
          <div class="lic-ph" style="background:{r['surface']}"><img src="{uri}" alt=""></div>
          <div class="lic-f">{lic}</div></div>
        <div class="lic-foot"><span class="hand sig">{e(name)}</span>{barcode(order)}</div>
      </div>
      <div class="prof">{prof_html}</div>
      {notes}
      <div class="why-wrap shadow" style="transform:rotate(1.2deg)"><div class="why" style="clip-path:{torn_rect(960, 300, order + 70, amp=7, step=30)}">
        <h3>Why MAGGI</h3><p>{e(why)}</p></div></div>
      <div class="heritage" style="left:1340px;top:676px;transform:rotate(6deg);width:300px"></div>
    </section>"""


def page_world(ctx, pid, p, md):
    a, bc = ctx["a"], ctx["bc"]
    r = {k: v(x) for k, x in p["role"].items()}
    name, time = v(p["name"]), v(p["day"]["time"])
    order = v(p["day"]["order"])
    cons = p["constraint"]
    t = p["type"]
    spines = ""
    cols = [(k, v(c)) for k, c in p["color"].items() if not k.startswith("$")]
    sw = min(110, 820 // max(1, len(cols)))
    for k, (cname, hexv) in enumerate(cols):
        fg = ink_on(hexv, WHITE, "#1C1410")
        hgt = 440 + ((k * 37) % 5) * 18
        spines += (f'<div class="spine" style="left:{1010 + k * (sw + 6)}px;top:{640 - hgt}px;width:{sw}px;height:{hgt}px;background:{hexv};color:{fg}">'
                   f'<b>{e(cname.replace("-", " "))}</b><span>{hexv}</span></div>')
    product = v(p["product"]["name"]).replace("MAGGI ", "")
    disp, text = v(t["display"])[0], v(t["text"])[0]
    world_txt = first_sentences(md[12], 1)
    return f"""
    <section class="page" style="background:{r['bg']};color:{r['text']}">
      <div class="corner tl">{e(name)}'s world</div><div class="corner tr">{e(time)}, {e(v(p['day']['light']))}</div>
      <h1 class="wd-name" style="color:{r['text']}">The world</h1>
      <p class="wd-rule"><b>{e(v(cons['rule']))}.</b> <span class="hand" style="color:{r['accent'] if pid not in ('cram', 'mise') else r['text']}">{e(v(cons['why']))}.</span></p>
      <div class="pola big shadow" style="left:70px;top:300px;transform:rotate(-2.2deg)">
        <img src="{a.scene(p)}" alt=""><p class="hand">{e(time)}, {e(product.split(',')[0].split(' (')[0])}</p></div>
      {tape(380, 280, -4, 220)}
      {pack_img(a, p, 240, 760, 770, -9)}
      {spines}
      <div class="tspec shadow" style="left:1010px;top:670px">
        <div class="aa" style="font-family:'{disp}';color:{on_light(r, 'accent', '#FFFFFF')}">Aa</div>
        <div><b style="font-family:'{disp}'">{e(disp)}</b><span style="font-family:'{text}'">{e(text)}: {e(world_txt)}</span></div></div>
      <div class="sachet-note hand" style="background:{WHITE};clip-path:{torn_rect(820, 130, order + 30, amp=6, step=24)}">The sachet: &ldquo;{e(v(p['sachet']))}&rdquo;</div>
    </section>"""


def page_market(ctx, pid, p, md):
    a, bc = ctx["a"], ctx["bc"]
    r = {k: v(x) for k, x in p["role"].items()}
    name, time = v(p["name"]), v(p["day"]["time"])
    order = v(p["day"]["order"])
    dark = r["text"] if cl.luminance(r["bg"]) > 0.4 else r["bg"]
    light = r["bg"] if dark == r["text"] else r["text"]
    journey = md_rows(md[9])
    cols = [v(c) for k, c in p["color"].items() if not k.startswith("$") and v(c).upper() not in (dark.upper(),)]
    tapes = ""
    for k, (step, what) in enumerate(journey[:7]):
        c = cols[k % len(cols)]
        fg = ink_on(c, WHITE, "#1C1410")
        tapes += (f'<div class="cass" style="left:{70 + k * 255}px;top:{200 + (k % 2) * 24}px;background:{c};color:{fg}">'
                  f'<i>{k + 1}</i><b>{e(step)}</b><p>{e(what)}</p></div>')
    reviews = md_rows(md[13])
    wins = ""
    for k, (tone, text) in enumerate(reviews[:3]):
        wins += window(f"review_{tone.lower()}.txt", f'<p>{e(text.strip(chr(34)))}</p>', 70 + k * 410, 690 + (k % 2) * 30, 390,
                       (r["accent"], r["focus"], r["key"])[k] if pid != "cram" else "#000000", rot=(-1.5, 1, -0.5)[k])
    opp = md_rows(md[16])
    rows = "".join(f'<div class="rrow"><b>{e(k)}</b><span>{e(val)}</span></div>' for k, val in opp)
    rec = clean(re.search(r"\*\*(.+?)\*\*", md[14]).group(1)) if re.search(r"\*\*(.+?)\*\*", md[14]) else ""
    return f"""
    <section class="page" style="background:{dark};color:{light}">
      <div class="corner tl">{e(name)} in the market</div>
      <h1 class="mk-name">How {e(name)} buys</h1>
      {tapes}
      <p class="mk-note">Reviews are synthesised composites written for this persona, not real customer quotes.</p>
      {wins}
      <div class="rc-wrap shadow"><div class="rc">
        <h3>Next for MAGGI</h3>{rows}<hr><p>Recommends: {e(rec)} (design estimate)</p></div></div>
      <div class="burst" style="background:{r['accent'] if pid != 'cram' else WHITE};color:{ink_on(r['accent'] if pid != 'cram' else WHITE, WHITE, '#1C1410')}">
        <span>{e(rec.split(':')[-1].strip())}</span></div>
    </section>"""


# ---------- system chapters ----------

def md_tables_00():
    return (tk.ROOT / "markdown" / "00-maggi-persona-design-system.md").read_text(encoding="utf-8")


def sub_section(text, heading):
    """Body of a '### heading' block (up to the next ### or ##)."""
    m = re.search(rf"^### {re.escape(heading)}.*?$(.*?)(?=^### |^## |\Z)", text, flags=re.M | re.S)
    return m.group(1) if m else ""


def chap_head(num, title, colour, sub=""):
    return (f'<div class="ch-num" style="color:{colour}">{num:02d}</div>'
            f'<h1 class="ch-title shrink" data-w="1320" style="color:{colour}">{e(title)}</h1>'
            + (f'<p class="ch-sub" style="color:{colour}">{e(sub)}</p>' if sub else ""))


def dots(n, of=3):
    return "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(of))


def page_research(ctx):
    bc = ctx["bc"]
    brief = (tk.ROOT / "brief" / "maggi-persona-project-brief-v2.md").read_text(encoding="utf-8")
    sec = brief.split("## 27. Research evidence log", 1)[1].split("## 28.", 1)[0]
    rows = md_rows(sec)
    pick = (0, 1, 2, 3, 4, 5, 6, 7, 9, 12, 17)
    slips = ""
    for k, i in enumerate(pick):
        finding, conf, src = rows[i]
        level = 3 if conf.startswith("High") else 2 if conf.startswith("Medium") else 1
        dom = re.search(r"https?://(?:www\.)?([^/ ]+)", src)
        dom = dom.group(1) if dom else src.split(",")[0]
        x, y = 70 + (k % 4) * 452, 290 + (k // 4) * 252
        rot = ((k * 37) % 7 - 3) * 0.7
        slips += (f'<div class="slip-wrap shadow" style="left:{x}px;top:{y}px;transform:rotate({rot:.1f}deg)">'
                  f'<div class="slip" style="clip-path:{torn_rect(420, 226, k + 120, amp=5, step=24)}">'
                  f'<p>{e(finding)}</p><div class="src"><span>{e(dom)}</span>'
                  f'<span class="stamp"><b>{e(conf)}</b><span class="dots">{dots(level)}</span></span></div></div></div>')
    probs = re.search(r"\*\*Known data problems.*?\*\*(.*?)$", sec, flags=re.S | re.M)
    probs = clean(probs.group(1)).split(".")[0] + "." if probs else ""
    return f"""
    <section class="page grid" style="background-color:{bc['paper']};color:{bc['ink']}">
      <div class="corner tl">Research and insight</div><div class="corner tr">From the brief's evidence log, confidence tags kept</div>
      {chap_head(1, "What we know", bc['ink'], "Twelve findings that shaped the seven personas. Confidence: High, Medium or Low (Low is directional only).")}
      {slips}
      <div class="sticky hand" style="left:1426px;top:790px;font-size:18px;transform:rotate(3deg)">Data problems: {e(probs)} Primary research comes before any commercial number.</div>
    </section>"""


def page_dna(ctx):
    a, ps, bc, res = ctx["a"], ctx["ps"], ctx["bc"], ctx["res"]
    b = res["brand"]
    sach, nt = b["sachet"], b["noodle-thread"]
    fan = ""
    for i, (pid, p) in enumerate(ps):
        ang = -33 + i * 11
        fan += (f'<div class="fan" style="transform:rotate({ang}deg)">'
                + pack_img(a, p, 300, 0, 0, 0).replace('class="pk"', 'class="pk fanpk"') + '</div>')
    consts = [
        ("Red", f'{v(b["color"]["red"])}', v(b["color"]["red"])),
        ("Yellow", f'{v(b["color"]["yellow"])}', v(b["color"]["yellow"])),
        ("Heritage thread", "Red over yellow, once per layout, never a flag", None),
        ("The sachet", f'{v(sach["width"])} × {v(sach["height"])} units, diagonal red and yellow split, a tear notch', None),
        ("Steam curl", f'{v(b["steam-curl"]["wisps"])} wisps, each an S-curve with two turns', None),
        ("Noodle thread", f'One line through all seven worlds, entering at {round(v(nt["entry-height"]) * 100)}% height', None),
        ("Lockup slot", "Top-left, 3 of 12 columns, always left empty for the brand team", None),
    ]
    cards = ""
    for k, (nm, spec, chip) in enumerate(consts):
        sw = f'<i class="chip" style="background:{chip}"></i>' if chip else ""
        cards += (f'<div class="const shadow" style="top:{240 + k * 112}px;transform:rotate({(-1.2, .8, -.6, 1, -.9, .7, -1)[k]}deg)">'
                  f'<div style="clip-path:{torn_rect(620, 96, k + 140, amp=4, step=24)}">{sw}<b>{e(nm)}</b><span>{e(spec)}</span></div></div>')
    return f"""
    <section class="page" style="background:{bc['red']};color:{bc['paper']}">
      <div class="corner tl">MAGGI brand DNA</div><div class="corner tr">The constants in every world</div>
      {chap_head(2, "Same pack, every world", bc['paper'], "Seven worlds re-render these constants through their own rules. None of them redefines them.")}
      <div class="fanbox">{fan}</div>
      {cards}
      <div class="heritage" style="left:-40px;top:1000px;width:2000px;transform:rotate(-1deg)"></div>
    </section>"""


def page_sachets(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    cols = ""
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        x = 40 + i * 264
        fig, fw = fig_img(a, p, 430, 0, 0)
        cols += (f'<div class="sc-col" style="left:{x}px">'
                 f'<div class="sc-note shadow" style="transform:rotate({(-3, 2, -2, 3, -2.5, 2, -1.5)[i]}deg)">'
                 f'<div style="background:{r["bg"]};color:{r["text"]};clip-path:{torn_rect(250, 330, i + 160, amp=5, step=22)}">'
                 f'<b>{e(v(p["name"]))}</b><p class="hand">{e(v(p["sachet"]))}</p><small>{e(v(p["day"]["time"]))}. {e(v(p["feltTime"]))}</small></div></div>'
                 f'<div class="sc-fig" style="width:{fw}px">{fig.replace("position:absolute", "")}</div></div>')
    return f"""
    <section class="page grid" style="background-color:{bc['yellow']};color:{bc['ink']}">
      <div class="corner tl">MAGGI brand DNA</div><div class="corner tr">The sachet rule</div>
      {chap_head(2, "One sachet, seven habits", bc['ink'], "Every mascot uses the same red-and-yellow sachet. What it does with it is the personality.")}
      {cols}
    </section>"""


STAT_KEYS = ("heat", "speed", "comfort", "chaos", "value", "fancy", "wellness")


def page_map(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    rows = ""
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        uri, (fw, fh) = a.figure(p)
        sp = p["spine"]
        meters = "".join(f'<div class="mt">{"".join("<i class=on></i>" if 5 - k <= v(p["stats"][s]) else "<i></i>" for k in range(5))}</div>'
                         for s in STAT_KEYS)
        nm = r["text"] if pid in ("cram", "mise") else r["accent"]
        rows += (f'<div class="mrow shadow" style="top:{250 + i * 112}px;transform:rotate({(-.5, .4, -.3, .5, -.4, .3, -.2)[i]}deg)">'
                 f'<div class="mrow-in" style="background:{r["bg"]};color:{r["text"]};--fg:{r["text"]};clip-path:{torn_rect(1780, 100, i + 200, amp=4, step=30)}">'
                 f'<img src="{uri}" alt="" style="height:96px">'
                 f'<div><b style="color:{nm}">{e(v(p["name"]))}</b><small>{e(v(p["day"]["time"]))}</small></div>'
                 f'<div><strong>{e(v(p["persona"]))}</strong><span>{e(v(p["primaryMotivation"]))}</span></div>'
                 f'<div><span>Buys: {e(v(sp["buyer"]))}</span><span>Eats: {e(v(sp["eater"]))}</span></div>'
                 f'<div class="hand gate">{e(v(sp["gate"]))}</div>'
                 f'<div class="mts">{meters}</div></div></div>')
    heads = "".join(f"<span>{s.capitalize()}</span>" for s in STAT_KEYS)
    return f"""
    <section class="page grid" style="background-color:{bc['paper']};color:{bc['ink']}">
      <div class="corner tl">Persona map</div><div class="corner tr">Stats 1 to 5 are design judgement, to be validated</div>
      {chap_head(3, "The map", bc['ink'], "One motivation each, and a different buyer, eater or gate. That is what keeps seven people from blurring into one.")}
      <div class="mhead">{heads}</div>
      {rows}
    </section>"""


def page_versus(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    P = dict(ps)
    text00 = md_tables_00()
    pairs = md_rows(sub_section(text00, "3.2 Overlap resolutions"))
    ids = [("cram", "lull"), ("nest", "stack"), ("riot", "mise")]
    panels = ""
    for k, ((l, rr), row) in enumerate(zip(ids, pairs)):
        pl, pr = P[l], P[rr]
        rl = {x: v(y) for x, y in pl["role"].items()}
        rrr = {x: v(y) for x, y in pr["role"].items()}
        top = 220 + k * 282
        fl, wl = fig_img(a, pl, 280, 70, top - 14)
        fr, wr = fig_img(a, pr, 280, 0, top - 14)
        fr = fr.replace("left:0px", f"left:{W - 70 - wr}px", 1)
        panels += (f'<div class="vs" style="top:{top}px;background:linear-gradient(100deg, {rl["bg"]} 0 50%, {rrr["bg"]} 50% 100%)"></div>'
                   + fl.replace('class="fig"', 'class="fig vsfig"') + fr.replace('class="fig"', 'class="fig vsfig"') +
                   f'<div class="vs-mid shadow" style="top:{top + 40}px"><div style="clip-path:{torn_rect(980, 190, k + 230, amp=5, step=26)}">'
                   f'<b>{e(v(pl["name"]))} vs {e(v(pr["name"]))}</b><p>{e(row[1])}</p><p class="hand">Test: {e(row[2])}</p></div></div>'
                   f'<div class="vs-badge" style="top:{top + 70}px">VS</div>')
    return f"""
    <section class="page" style="background:{bc['ink']};color:{bc['paper']}">
      <div class="corner tl">Persona map</div><div class="corner tr">The three pairs most likely to blur</div>
      {chap_head(3, "Not the same person", bc['paper'])}
      {panels}
    </section>"""


def page_worlds(ctx):
    ps, bc = ctx["ps"], ctx["bc"]
    cols = ""
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        cons, t = p["constraint"], p["type"]
        strips = "".join(f'<i style="background:{r[k]}"></i>' for k in ("bg", "surface", "text", "accent", "key", "sachet-red"))
        nm = r["text"] if pid in ("cram", "mise") else r["accent"]
        cols += (f'<div class="wcol shadow" style="left:{64 + i * 256}px;top:{250 + (i % 2) * 30}px;transform:rotate({(-1.5, 1.2, -1, 1.4, -1.2, 1, -.8)[i]}deg)">'
                 f'<div class="wcol-in" style="background:{r["bg"]};color:{r["text"]};clip-path:{torn_rect(240, 760, i + 260, amp=5, step=24)}">'
                 f'<b style="color:{nm}">{e(v(p["name"]))}</b><small>{e(v(p["day"]["time"]))}</small>'
                 f'<div class="wstr">{strips}</div>'
                 f'<p>{e(v(cons["rule"]))}.</p><p class="hand">{e(v(cons["why"]))}.</p>'
                 f'<div class="wty"><span style="font-family:\'{v(t["display"])[0]}\'">{e(v(t["display"])[0])}</span>'
                 f'<span style="font-family:\'{v(t["text"])[0]}\'">{e(v(t["text"])[0])}</span></div></div></div>')
    return f"""
    <section class="page grid" style="background-color:{bc['paper']};color:{bc['ink']}">
      <div class="corner tl">Visual worlds</div><div class="corner tr">Each constraint is a machine check, not a mood</div>
      {chap_head(11, "Seven worlds, seven rules", bc['ink'])}
      {cols}
    </section>"""


def page_motion(ctx):
    a, ps, bc, res = ctx["a"], ctx["ps"], ctx["bc"], ctx["res"]
    m = res["motion"]
    x0, x1 = 760, 1560
    ticks = "".join(f'<i style="left:{x0 + (x1 - x0) * f / 48}px;height:{30 if f % 12 == 0 else 12}px"></i>' for f in range(49))
    beats = "".join(f'<span style="left:{x0 + (x1 - x0) * k / 4 - 10}px">{k + 1}</span>' for k in range(4))
    rows = ""
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        mo, so = p["motion"], p["sound"]
        uri, _ = a.figure(p)
        y = 300 + i * 104
        acc = "".join(f'<i class="acc" style="left:{x0 + (x1 - x0) * (bt - 1) / 4 - 14}px;background:{r["accent"] if pid != "cram" else "#000000"}"></i>'
                      for bt in v(mo["accentBeats"]))
        amp = v(mo["amplitude"])
        rows += (f'<div class="mo-row" style="top:{y}px">'
                 f'<img src="{uri}" alt="" style="height:92px">'
                 f'<div class="mo-n"><b>{e(v(p["name"]))}</b><span>{e(v(mo["tempo"]))}</span></div>'
                 f'<div class="mo-amp"><i style="width:{round(amp / 1.4 * 150)}px;background:{r["accent"] if pid != "cram" else "#000000"}"></i><span>{amp}</span></div>'
                 f'<div class="mo-line"></div>{acc}'
                 f'<div class="mo-note"><b>{e(v(so["pitch"]))}</b><span>{e(", ".join(v(so["palette"])))}</span></div></div>')
    safety = m["safety"]
    return f"""
    <section class="page grid" style="background-color:{bc['paper']};color:{bc['ink']}">
      <div class="corner tl">Motion and sound</div><div class="corner tr">{v(m['clock']['bpm'])} BPM, {v(m['frame-rate']['primary'])} fps, one bar = 2 s = the felt two minutes</div>
      {chap_head(12, "One beat, seven tempos", bc['ink'])}
      <div class="ruler">{ticks}{beats}</div>
      <div class="mo-heads"><span style="left:180px">Tempo</span><span style="left:470px">Amplitude</span><span style="left:1620px">Note and sound</span></div>
      <p class="hand" style="position:absolute;left:{x0 + 40}px;top:1010px;font-size:28px;z-index:6">dots = accent beats on the 2-second bar</p>
      {rows}
      <div class="sticky hand" style="left:1500px;top:70px;width:360px;transform:rotate(2deg)">Never more than {v(safety['max-flashes-per-second'])} flashes a second. Reduced motion: poster frame and cross-fades only.</div>
    </section>"""


def page_applications(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    cards = ""
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        pm = p["packMechanic"]
        feas = v(pm["feasibility"])
        level = {"high": 3, "medium": 2, "low": 1}.get(feas.lower().split()[0], 2)
        x = 70 + (i % 4) * 452 + (226 if i >= 4 else 0)
        y = 250 + (i // 4) * 420
        cards += (f'<div class="app shadow" style="left:{x}px;top:{y}px;transform:rotate({(-1.5, 1.2, -.8, 1.6, -1.2, 1, -.6)[i]}deg)">'
                  f'<div class="app-in" style="background:{r["bg"]};color:{r["text"]};clip-path:{torn_rect(420, 330, i + 300, amp=5, step=24)}">'
                  f'<b style="color:{r["text"] if pid in ("cram", "mise") else r["accent"]}">{e(v(p["name"]))}</b>'
                  f'<p>{e(v(pm["concept"]))}</p>'
                  f'<span class="stamp" style="color:{r["text"]};border-color:{r["text"]}"><b>Feasibility: {e(feas)}</b><span class="dots">{dots(level)}</span></span></div></div>'
                  + pack_img(a, p, 150, x + 320, y - (100 if i < 4 else 50), (12, -10, 8, -12, 10, -8, 12)[i]))
    return f"""
    <section class="page grid" style="background-color:{bc['paper']};color:{bc['ink']}">
      <div class="corner tl">Applications</div><div class="corner tr">Pack mechanics are concepts, not production specs</div>
      {chap_head(13, "One pack idea per world", bc['ink'])}
      {cards}
    </section>"""


def page_competitors(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    table = md_rows(sub_section(md_tables_00(), "11.3 Competitor framework"))
    by = {row[0]: row[1:] for row in table}
    rows = ""
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        uri, _ = a.figure(p)
        d = by.get(v(p["name"]), ["", "", "", ""])
        cells = "".join(f'<div>{e(re.sub(r" ?\[[^]]+\]", "", c))}</div>' for c in d)
        rows += (f'<div class="crow" style="top:{240 + i * 112}px">'
                 f'<img src="{uri}" alt="" style="height:92px"><b style="color:{r["accent"] if pid not in ("cram", "mise") else r["text"]};background:{r["bg"]}">{e(v(p["name"]))}</b>{cells}</div>')
    heads = "".join(f"<span>{h}</span>" for h in ("Direct rivals", "Indirect rivals", "Why they switch", "Why they come back"))
    return f"""
    <section class="page" style="background:{bc['ink']};color:{bc['paper']}">
      <div class="corner tl">Competitors and opportunities</div><div class="corner tr">Most cells are hypotheses to test with primary research</div>
      {chap_head(14, "Who else is on the plate", bc['paper'])}
      <div class="chead">{heads}</div>
      {rows}
    </section>"""


def page_back(ctx):
    a, ps, bc = ctx["a"], ctx["ps"], ctx["bc"]
    figs = ""
    spots = [(140, 470, -8), (420, 520, 6), (700, 460, -4), (980, 530, 7), (1260, 470, -6), (1520, 520, 5), (1700, 380, -9)]
    for i, (pid, p) in enumerate(ps):
        x, y, rot = spots[i]
        f, w = fig_img(a, p, 440, x, y, extra=f"transform:rotate({rot}deg);z-index:{5 + i % 3}")
        figs += f
    return f"""
    <section class="page" style="background:{bc['ink']};color:{bc['paper']}">
      <div class="corner tl">MAGGI persona system</div><div class="corner tr">Vol. 01, 2026</div>
      <h1 class="back"><span class="fit" data-w="1780">Collect all seven</span></h1>
      {figs}
      <div class="heritage" style="left:1180px;top:350px;transform:rotate(-8deg);width:700px"></div>
      <p class="back-note">A private design project. Reviews are synthesised composites; market numbers are directional and keep their confidence tags; no health claims.</p>
    </section>"""


CHAPTER_CSS = """
    .ch-num {{ position: absolute; left: 70px; top: 76px; font-family: {f_disp}; font-size: 40px; }}
    .ch-title {{ position: absolute; left: 160px; top: 64px; font-family: {f_disp}; font-weight: 400; font-size: 92px; line-height: .95; white-space: nowrap; }}
    .ch-sub {{ position: absolute; left: 164px; top: 172px; font-size: 24px; line-height: 1.35; max-width: 1200px; font-weight: 500; }}
    .slip-wrap {{ position: absolute; z-index: 5; }}
    .slip {{ width: 420px; height: 226px; padding: 26px 28px; background: #FFFFFF; display: flex; flex-direction: column; justify-content: space-between; }}
    .slip p {{ font-size: 21px; line-height: 1.35; font-weight: 500; }}
    .src {{ display: flex; justify-content: space-between; align-items: center; font-size: 15px; opacity: .85; }}
    .stamp {{ display: inline-flex; gap: 8px; align-items: center; border: 3px solid {red}; color: {red}; padding: 4px 10px; border-radius: 6px; transform: rotate(-4deg); font-size: 15px; }}
    .stamp b {{ font-weight: 800; }}
    .dots {{ display: inline-flex; gap: 3px; }} .dots i {{ width: 10px; height: 10px; border-radius: 50%; border: 2px solid currentColor; display: block; }}
    .dots i.on {{ background: currentColor; }}
    .sticky {{ position: absolute; z-index: 9; width: 420px; padding: 28px 30px; background: {yellow}; color: {ink}; font-size: 25px; line-height: 1.3; box-shadow: 0 16px 24px rgba(28,20,16,.28); }}
    .fanbox {{ position: absolute; left: 260px; top: 610px; width: 0; height: 0; }}
    .fan {{ position: absolute; left: 0; top: 0; transform-origin: 0 520px; }}
    .fan .pk {{ position: absolute; left: -110px; top: -40px; }}
    .const {{ position: absolute; left: 1210px; z-index: 6; }}
    .const > div {{ width: 620px; height: 96px; padding: 18px 26px 18px 26px; background: #FFFFFF; color: {ink}; display: grid; grid-template-columns: auto 1fr; column-gap: 16px; align-content: center; }}
    .const b {{ font-family: {f_disp}; font-weight: 400; font-size: 24px; grid-column: 2; }}
    .const span {{ font-size: 18px; grid-column: 2; }}
    .const .chip {{ grid-row: 1 / span 2; width: 56px; height: 56px; display: block; border: 2px solid {ink}; }}
    .sc-col {{ position: absolute; top: 250px; width: 250px; height: 800px; display: flex; flex-direction: column; align-items: center; }}
    .sc-note > div {{ width: 250px; height: 330px; padding: 28px 24px; }}
    .sc-note b {{ font-family: {f_disp}; font-weight: 400; font-size: 34px; display: block; }}
    .sc-note p {{ font-size: 27px; line-height: 1.2; margin: 12px 0; }}
    .sc-note small {{ font-size: 16px; line-height: 1.35; display: block; font-weight: 600; }}
    .sc-fig {{ position: relative; height: 430px; margin-top: -20px; }}
    .sc-fig .fig {{ position: relative !important; left: auto !important; top: auto !important; }}
    .mhead {{ position: absolute; left: 1488px; top: 222px; display: grid; grid-template-columns: repeat(7, 50px); font-size: 12px; font-weight: 700; text-align: center; }}
    .mrow {{ position: absolute; left: 70px; z-index: 5; }}
    .mrow-in {{ width: 1780px; height: 100px; display: grid; grid-template-columns: 90px 210px 400px 300px 400px 360px; align-items: center; column-gap: 0; padding: 0 20px; }}
    .mrow-in img {{ align-self: end; }}
    .mrow-in b {{ display: block; font-family: {f_disp}; font-weight: 400; font-size: 34px; line-height: 1; }}
    .mrow-in small {{ font-size: 16px; font-weight: 700; }}
    .mrow-in strong {{ display: block; font-size: 22px; }}
    .mrow-in span {{ display: block; font-size: 18px; line-height: 1.3; }}
    .mrow-in .gate {{ font-size: 22px; line-height: 1.2; }}
    .mts {{ display: grid; grid-template-columns: repeat(7, 50px); }}
    .mt {{ display: grid; grid-template-rows: repeat(5, 10px); gap: 3px; width: 26px; margin: 0 auto; }}
    .mt i {{ border: 2px solid var(--fg); opacity: .35; display: block; }} .mt i.on {{ background: var(--fg); opacity: 1; }}
    .vs {{ position: absolute; left: 0; width: 1920px; height: 260px; z-index: 1; }}
    .vsfig {{ z-index: 6; }}
    .vs-mid {{ position: absolute; left: 520px; z-index: 7; }}
    .vs-mid > div {{ width: 980px; height: 190px; padding: 22px 34px; background: #FFFFFF; color: {ink}; }}
    .vs-mid b {{ font-family: {f_disp}; font-weight: 400; font-size: 30px; }}
    .vs-mid p {{ font-size: 19px; line-height: 1.35; margin-top: 6px; }} .vs-mid p.hand {{ font-size: 20px; }}
    .vs-badge {{ position: absolute; left: 330px; z-index: 8; font-family: {f_disp}; font-size: 80px; color: {yellow}; -webkit-text-stroke: 3px {ink}; transform: rotate(-10deg); }}
    .wcol {{ position: absolute; z-index: 5; }}
    .wcol-in {{ width: 240px; height: 760px; padding: 28px 22px; display: flex; flex-direction: column; gap: 14px; }}
    .wcol-in b {{ font-family: {f_disp}; font-weight: 400; font-size: 38px; line-height: 1; }}
    .wcol-in small {{ font-size: 16px; font-weight: 700; margin-top: -8px; }}
    .wstr {{ display: grid; grid-template-rows: repeat(6, 44px); border: 2px solid currentColor; }}
    .wstr i {{ display: block; }}
    .wcol-in p {{ font-size: 18px; line-height: 1.35; }} .wcol-in p.hand {{ font-size: 22px; }}
    .wty {{ margin-top: auto; display: flex; flex-direction: column; gap: 4px; font-size: 22px; }}
    .ruler {{ position: absolute; left: 0; top: 248px; width: 1920px; height: 40px; z-index: 4; }}
    .ruler i {{ position: absolute; top: 0; width: 2px; background: {ink}; display: block; }}
    .ruler span {{ position: absolute; top: -30px; font-family: {f_disp}; font-size: 22px; }}
    .mo-heads span {{ position: absolute; top: 212px; font-size: 15px; font-weight: 700; }}
    .mo-row {{ position: absolute; left: 70px; width: 1780px; height: 96px; z-index: 5; }}
    .mo-row img {{ position: absolute; left: 0; bottom: 0; }}
    .mo-n {{ position: absolute; left: 110px; top: 22px; width: 300px; }}
    .mo-n b {{ display: block; font-family: {f_disp}; font-weight: 400; font-size: 30px; }} .mo-n span {{ font-size: 18px; }}
    .mo-amp {{ position: absolute; left: 400px; top: 34px; display: flex; gap: 10px; align-items: center; font-weight: 700; }}
    .mo-amp i {{ display: block; height: 22px; }}
    .mo-line {{ position: absolute; left: 690px; top: 46px; width: 800px; height: 3px; background: rgba(28,20,16,.25); }}
    .mo-row .acc {{ position: absolute; top: 33px; width: 28px; height: 28px; border-radius: 50%; display: block; margin-left: -70px; }}
    .mo-note {{ position: absolute; left: 1550px; top: 16px; width: 240px; }}
    .mo-note b {{ display: block; font-family: {f_disp}; font-weight: 400; font-size: 30px; }} .mo-note span {{ font-size: 15px; line-height: 1.3; }}
    .app {{ position: absolute; z-index: 5; }}
    .app-in {{ width: 420px; height: 330px; padding: 34px 32px; display: flex; flex-direction: column; gap: 14px; }}
    .app-in > b {{ font-family: {f_disp}; font-weight: 400; font-size: 40px; }}
    .app-in p {{ font-size: 21px; line-height: 1.35; font-weight: 500; flex: 1; }}
    .app-in .stamp {{ align-self: flex-start; }}
    .chead {{ position: absolute; left: 410px; top: 212px; display: grid; grid-template-columns: repeat(4, 360px); font-size: 16px; font-weight: 700; }}
    .crow {{ position: absolute; left: 70px; width: 1780px; height: 100px; display: grid; grid-template-columns: 110px 230px repeat(4, 360px); align-items: center; border-top: 2px dashed rgba(255,248,236,.25); z-index: 5; }}
    .crow img {{ align-self: end; }}
    .crow b {{ font-family: {f_disp}; font-weight: 400; font-size: 30px; padding: 6px 14px; justify-self: start; }}
    .crow div {{ font-size: 18px; line-height: 1.3; padding-right: 24px; }}
    .back {{ position: absolute; left: 70px; top: 110px; font-family: {f_disp}; font-weight: 400; font-size: 200px; line-height: .9; color: {paper}; }}
    .back span {{ display: inline-block; }}
    .back-note {{ position: absolute; left: 70px; bottom: 34px; font-size: 18px; opacity: .75; max-width: 1100px; }}
"""


# ---------- document ----------

def css(ctx):
    bc, f_disp, f_text, f_hand = ctx["bc"], ctx["f_disp"], ctx["f_text"], ctx["f_hand"]
    return f"""
    @page {{ size: {W}px {H}px; margin: 0; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    body {{ width: {W}px; font-family: {f_text}; }}
    .page {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; break-after: page; }}
    .page::after {{ content: ""; position: absolute; inset: 0; z-index: 50; pointer-events: none; background-image: url({ctx["a"].grain()}); }}
    .grid {{ background-image: linear-gradient(rgba(28,20,16,.07) 2px, transparent 2px), linear-gradient(90deg, rgba(28,20,16,.07) 2px, transparent 2px);
             background-size: 48px 48px; }}
    .hand {{ font-family: {f_hand}; }}
    .shadow {{ filter: drop-shadow(0 18px 24px rgba(28,20,16,.28)); }}
    .corner {{ position: absolute; font-size: 20px; line-height: 1.35; z-index: 30; font-weight: 600; letter-spacing: .01em; }}
    .tl {{ left: 70px; top: 34px; }} .tr {{ right: 70px; top: 34px; text-align: right; }}
    .bl {{ left: 70px; bottom: 30px; }} .br {{ right: 70px; bottom: 30px; text-align: right; }}
    .fig {{ position: absolute; }}
    .pk {{ position: absolute; z-index: 12; }}
    .tape {{ position: absolute; height: 44px; z-index: 25; mix-blend-mode: multiply; display: block; }}
    .heritage {{ position: absolute; height: 46px; z-index: 26; background: linear-gradient({bc['red']} 0 50%, {bc['yellow']} 50% 100%); }}
    .outline {{ color: transparent !important; -webkit-text-stroke: 4px {bc['paper']}; }}

    /* cover */
    .cv1 span, .cv2 span, .ct span {{ display: inline-block; }}
    .cv1, .cv2 {{ position: absolute; left: 70px; font-family: {f_disp}; font-weight: 400; line-height: .86; white-space: nowrap; }}
    .cv1 {{ top: 110px; font-size: 250px; color: {bc['paper']}; }}
    .cv2 {{ top: 330px; font-size: 170px; z-index: 1; }}

    /* contents */
    .ct {{ position: absolute; left: 70px; top: 110px; font-family: {f_disp}; font-weight: 400; font-size: 150px; line-height: .9; }}
    .toc {{ position: absolute; left: 84px; top: 420px; list-style: none; width: 640px; }}
    .toc li {{ display: grid; grid-template-columns: 90px 1fr; align-items: baseline; padding: 14px 0; border-top: 3px solid {bc['ink']}; font-size: 34px; font-weight: 600; }}
    .toc li b {{ font-family: {f_disp}; font-weight: 400; font-size: 34px; }}
    .toc-p {{ position: absolute; left: 84px; top: 960px; font-size: 26px; display: grid; grid-template-columns: 170px 1fr; width: 640px; border-top: 3px solid {bc['ink']}; padding-top: 14px; }}
    .toc-p b {{ font-family: {f_disp}; font-weight: 400; }}
    .cstick {{ position: absolute; display: flex; flex-direction: column; align-items: center; z-index: 5; }}
    .ctag {{ width: 250px; height: 110px; margin-top: -26px; padding: 18px 26px; filter: none; position: relative; z-index: 2; }}
    .ctag b {{ display: block; font-family: {f_disp}; font-weight: 400; font-size: 38px; line-height: 1; }}
    .ctag span {{ display: block; font-size: 22px; font-weight: 600; margin-top: 6px; }}

    /* opener */
    .op-block {{ position: absolute; right: 0; top: 0; width: 1010px; height: 1080px; clip-path: polygon(14% 0, 100% 0, 100% 100%, 0 100%); }}
    .op-name {{ position: absolute; left: 50px; top: 60px; font-family: {f_disp}; font-weight: 400; font-size: 420px; line-height: .86; white-space: nowrap; z-index: 2; }}
    .op-name.plate {{ transform: translate(14px, 14px); z-index: 1; }}
    .op-hour {{ position: absolute; right: 70px; bottom: 30px; font-family: {f_disp}; font-size: 150px; line-height: 1; color: transparent; -webkit-text-stroke: 3px; z-index: 3; opacity: .55; }}
    .op-text {{ position: absolute; left: 70px; top: 560px; z-index: 8; transform: rotate(-1.4deg); }}
    .op-text .sheet {{ width: 760px; height: 400px; padding: 40px 48px; background: {WHITE}; color: {bc['ink']}; }}
    .op-text h2 {{ font-family: {f_disp}; font-weight: 400; font-size: 46px; line-height: 1; }}
    .op-text .mot {{ font-size: 26px; font-weight: 700; margin: 14px 0 10px; }}
    .op-text p {{ font-size: 23px; line-height: 1.45; }}
    .op-gate {{ position: absolute; left: 110px; top: 990px; font-size: 34px; z-index: 9; transform: rotate(-2deg); }}
    .win {{ position: absolute; z-index: 20; background: {WHITE}; color: {bc['ink']}; border: 4px solid {bc['ink']}; box-shadow: 10px 10px 0 rgba(28,20,16,.85); }}
    .wbar {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; font-size: 20px; font-weight: 700; border-bottom: 4px solid {bc['ink']}; }}
    .wbar b {{ width: 30px; height: 30px; display: grid; place-items: center; background: {WHITE}; color: {bc['ink']}; border: 3px solid {bc['ink']}; font-size: 24px; line-height: 1; }}
    .wbody {{ padding: 16px 18px; }}
    .wbody p {{ font-size: 24px; line-height: 1.4; }}
    .wbody small {{ display: block; font-size: 15px; margin-top: 10px; opacity: .7; }}

    /* file */
    .fl-name {{ position: absolute; left: 70px; top: 70px; font-family: {f_disp}; font-weight: 400; font-size: 170px; line-height: .9; }}
    .fl-sub {{ position: absolute; left: 76px; top: 240px; width: 760px; font-size: 26px; font-weight: 600; line-height: 1.35; }}
    .lic {{ position: absolute; left: 70px; top: 330px; width: 760px; background: {WHITE}; border-radius: 26px; overflow: hidden; z-index: 6; box-shadow: 0 18px 30px rgba(28,20,16,.3); }}
    .lic-head {{ display: flex; justify-content: space-between; align-items: center; padding: 18px 28px; }}
    .lic-head b {{ font-family: {f_disp}; font-weight: 400; font-size: 34px; }}
    .lic-head span {{ font-size: 20px; font-weight: 700; }}
    .lic-body {{ display: grid; grid-template-columns: 220px 1fr; gap: 26px; padding: 24px 28px 8px; }}
    .lic-ph {{ height: 270px; border-radius: 14px; overflow: hidden; display: flex; align-items: flex-end; justify-content: center; }}
    .lic-ph img {{ height: 258px; }}
    .lic-f {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px 22px; align-content: start; }}
    .lic-f small, .prof small {{ display: block; font-size: 15px; font-weight: 700; opacity: .6; }}
    .lic-f b {{ display: block; font-size: 22px; line-height: 1.2; }}
    .lic-foot {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 28px 20px; }}
    .sig {{ font-size: 46px; color: #1C1410; transform: rotate(-4deg); display: inline-block; }}
    .barcode {{ display: flex; gap: 3px; height: 56px; }}
    .barcode i {{ display: block; background: #1C1410; }}
    .prof {{ position: absolute; left: 76px; top: 818px; width: 780px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px 24px; font-size: 15px; line-height: 1.25; }}
    .note-wrap {{ position: absolute; z-index: 5; }}
    .note2 {{ width: 450px; height: 250px; padding: 34px 36px; }}
    .note2 h3 {{ font-family: {f_disp}; font-weight: 400; font-size: 32px; margin-bottom: 10px; }}
    .note2 p {{ font-size: 22px; line-height: 1.4; }}
    .why-wrap {{ position: absolute; left: 900px; top: 690px; z-index: 6; }}
    .why {{ width: 960px; height: 300px; padding: 40px 50px; background: {WHITE}; }}
    .why h3 {{ font-family: {f_disp}; font-weight: 400; font-size: 34px; margin-bottom: 12px; }}
    .why p {{ font-size: 27px; line-height: 1.4; font-weight: 500; }}

    /* world */
    .wd-name {{ position: absolute; left: 70px; top: 80px; font-family: {f_disp}; font-weight: 400; font-size: 120px; line-height: .9; }}
    .wd-rule {{ position: absolute; left: 76px; top: 205px; width: 900px; font-size: 26px; line-height: 1.35; }}
    .wd-rule .hand {{ font-size: 32px; }}
    .pola {{ position: absolute; padding: 22px 22px 0; background: {WHITE}; z-index: 6; box-shadow: 0 18px 30px rgba(28,20,16,.3); }}
    .pola.shadow, .lic.shadow, .tspec.shadow {{ filter: none; }}
    .pola.big img {{ width: 820px; height: 547px; object-fit: cover; display: block; }}
    .pola p {{ font-size: 34px; color: #1C1410; padding: 18px 4px 22px; }}
    .spine {{ position: absolute; z-index: 4; padding: 14px 0; border: 3px solid rgba(28,20,16,.85); box-shadow: 6px 6px 0 rgba(28,20,16,.5);
              display: flex; flex-direction: column; justify-content: space-between; align-items: center; }}
    .spine b {{ writing-mode: vertical-rl; transform: rotate(180deg); font-family: {f_disp}; font-weight: 400; font-size: 30px; white-space: nowrap; }}
    .spine span {{ writing-mode: vertical-rl; transform: rotate(180deg); font-size: 18px; font-weight: 700; }}
    .tspec {{ position: absolute; z-index: 7; width: 820px; height: 200px; background: {WHITE}; box-shadow: 0 18px 30px rgba(28,20,16,.3); color: #1C1410; display: grid; grid-template-columns: 210px 1fr; gap: 24px; align-items: center; padding: 24px 30px; transform: rotate(-1deg); }}
    .tspec .aa {{ font-size: 150px; line-height: .9; }}
    .tspec b {{ display: block; font-size: 34px; font-weight: 400; }}
    .tspec span {{ display: block; font-size: 20px; line-height: 1.4; margin-top: 8px; }}
    .sachet-note {{ position: absolute; left: 1010px; top: 910px; width: 820px; height: 130px; padding: 30px 40px; font-size: 30px; color: #1C1410; z-index: 9; transform: rotate(1.5deg); }}

    /* market */
    .mk-name {{ position: absolute; left: 70px; top: 70px; font-family: {f_disp}; font-weight: 400; font-size: 64px; line-height: 1; }}
    .cass {{ position: absolute; width: 235px; height: 380px; padding: 20px 18px; border: 4px solid #1C1410; box-shadow: 8px 8px 0 rgba(0,0,0,.45); z-index: 4; }}
    .cass i {{ font-style: normal; font-family: {f_disp}; font-size: 30px; display: block; }}
    .cass b {{ display: block; font-family: {f_disp}; font-weight: 400; font-size: 34px; line-height: 1; margin: 10px 0 14px; white-space: nowrap; }}
    .cass p {{ font-size: 20px; line-height: 1.35; font-weight: 500; }}
    .mk-note {{ position: absolute; left: 70px; top: 640px; font-size: 18px; opacity: .8; }}
    .rc-wrap {{ position: absolute; right: 70px; top: 630px; z-index: 22; transform: rotate(2deg); }}
    .rc {{ width: 560px; padding: 28px 32px 52px; background: {WHITE}; color: #1C1410; font-size: 16px; line-height: 1.35; clip-path: {OV.receipt_clip()}; }}
    .rc h3 {{ font-family: {f_disp}; font-weight: 400; font-size: 34px; margin-bottom: 12px; }}
    .rrow {{ display: grid; grid-template-columns: 120px 1fr; gap: 10px; padding: 7px 0; border-top: 2px dashed rgba(28,20,16,.4); }}
    .rc hr {{ border: 0; border-top: 3px dashed #1C1410; margin: 12px 0; }}
    .burst {{ position: absolute; right: 60px; top: 6px; width: 190px; height: 190px; display: grid; place-items: center; text-align: center; z-index: 23;
              clip-path: polygon(50% 0, 61% 18%, 82% 10%, 80% 32%, 100% 40%, 85% 56%, 96% 76%, 74% 78%, 68% 100%, 50% 86%, 32% 100%, 26% 78%, 4% 76%, 15% 56%, 0 40%, 20% 32%, 18% 10%, 39% 18%);
              transform: rotate(8deg); }}
    .burst span {{ font-family: {f_disp}; font-size: 22px; line-height: 1.05; width: 120px; }}
    """ + CHAPTER_CSS.format(f_disp=f_disp, red=bc["red"], yellow=bc["yellow"], ink=bc["ink"], paper=bc["paper"])


def build_html(res, tmp, only):
    ps = sorted(tk.personas(res), key=lambda t: v(t[1]["day"]["order"]))
    b = res["brand"]
    ed = b["type"]["editorial"]
    ctx = dict(res=res, a=Assets(tmp), ps=ps, bc={k: v(b["color"][k]) for k in ("red", "yellow", "ink", "paper")},
               f_disp=stack(ed["display"]), f_text=stack(ed["text"]), f_hand=stack(ed["hand"]))
    fams = {v(ed[k])[0] for k in ("display", "text", "hand")}
    pages = []
    if not only or "cover" in only:
        pages.append(page_cover(ctx))
    if not only or "contents" in only:
        pages.append(page_contents(ctx))
    front = [("research", page_research), ("dna", page_dna), ("dna", page_sachets), ("map", page_map), ("map", page_versus)]
    back = [("worlds", page_worlds), ("motion", page_motion), ("apps", page_applications), ("rivals", page_competitors), ("back", page_back)]
    pages += [fn(ctx) for key, fn in front if not only or key in only]
    for pid, p in ps:
        fams |= {v(p["type"]["display"])[0], v(p["type"]["text"])[0]}
        if only and pid not in only:
            continue
        md = md_sections(tk.ROOT / "markdown" / f"{p['slug']}.md")
        pages += [page_opener(ctx, pid, p, md), page_file(ctx, pid, p, md), page_world(ctx, pid, p, md), page_market(ctx, pid, p, md)]
    pages += [fn(ctx) for key, fn in back if not only or key in only]
    fit = """
    <script>
    document.fonts.ready.then(() => {
      document.querySelectorAll('.fit').forEach(el => { const w = +el.dataset.w;
        el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * w / el.getBoundingClientRect().width) + 'px'; });
      document.querySelectorAll('.shrink').forEach(el => { const w = +el.dataset.w;
        if (el.scrollWidth > w) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * w / el.scrollWidth) + 'px'; });
      document.querySelectorAll('.cass b').forEach(el => { const room = el.parentElement.clientWidth - 36;
        if (el.scrollWidth > room) el.style.fontSize = (34 * room / el.scrollWidth) + 'px'; });
      document.body.dataset.ready = '1';
    });
    </script>"""
    head = f"""<!doctype html><html><head><meta charset="utf-8">
<style>{OV.font_css(fams)}</style><style>{css(ctx)}</style></head><body>"""
    return head, pages, f"{fit}</body></html>"


def chrome(args, timeout=300):
    profile = Path(tempfile.mkdtemp(prefix="pdf-profile-"))
    cmd = [OV.find_browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
           "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--allow-file-access-from-files",
           f"--user-data-dir={profile}", "--virtual-time-budget=25000", *args]
    try:
        subprocess.run(cmd, check=True, timeout=timeout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def finish_pdf(path):
    """Re-save Chrome's PDF with a real title, unused objects removed and streams compressed (needs PyMuPDF):
    some viewers are slow or refuse Skia's raw output with the default 'system.html' title."""
    try:
        import pymupdf
    except ImportError:
        print("  PyMuPDF not installed: PDF left as Chrome wrote it")
        return
    tmp = Path(str(path) + ".tmp")
    doc = pymupdf.open(path)
    doc.set_metadata({"title": "Seven ways to eat one packet: MAGGI persona system", "author": "MAGGI persona system",
                      "subject": "Seven personas, mascots and visual worlds", "creator": "tools/build-pdf.py"})
    doc.save(tmp, garbage=3, deflate=True, clean=True)
    doc.close()
    tmp.replace(path)


def main(argv):
    only = set()
    if "--only" in argv:
        only = set(argv[argv.index("--only") + 1].split(","))
    res = tk.resolve_all(tk.load())
    tmp = Path(tempfile.mkdtemp(prefix="pdf-"))
    page = tmp / "system.html"
    head, pages, tail = build_html(res, tmp, only)
    n = len(pages)
    page.write_text(head + "".join(pages) + tail, encoding="utf-8")
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else OUT if not only else tmp / "partial.pdf"
    chrome(["--no-pdf-header-footer", f"--print-to-pdf={out}", page.as_uri()])
    finish_pdf(out)
    print(f"wrote {out} ({n} pages)")
    if "--preview" in argv:
        PREVIEW.mkdir(parents=True, exist_ok=True)
        for old in PREVIEW.glob("page-*.png"):
            old.unlink()
        batch = 8                                   # Chrome caps screenshot height near 16k px
        for start in range(0, n, batch):
            part = tmp / f"part-{start}.html"
            chunk = pages[start:start + batch]
            part.write_text(head + "".join(chunk) + tail, encoding="utf-8")
            shot = tmp / f"part-{start}.png"
            chrome([f"--screenshot={shot}", f"--window-size={W},{H * len(chunk)}", part.as_uri()])
            im = Image.open(shot)
            for k in range(len(chunk)):
                im.crop((0, k * H, W, (k + 1) * H)).save(PREVIEW / f"page-{start + k + 1:02d}.png")
        print(f"previews: {PREVIEW.relative_to(tk.ROOT).as_posix()}/page-01..{n:02d}.png")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

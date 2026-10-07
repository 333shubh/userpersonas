"""Build the seven collectible mascot cards and the shared card back (brief Sections 18.7 and 23).

    python tools/build-cards.py [mascot ...]

Writes, at 1260 x 1760 px (63 x 88 mm playing-card ratio, 2x):
  cards/NN-slug/NN-mascot-card-front.png   world art, die-cut mascot breaking out of the frame, name, hour,
                                           motivation, signature move (the sachet rule), real pack sticker
  cards/NN-slug/NN-mascot-card-back.png    the seven-stat radar (card tokens: one series, 2 px stroke, role.key
                                           fill at 25%, labels in role.text), the same numbers as a table,
                                           the gate, felt two minutes and rival pairs
  cards/card-back.png                      the shared back-of-card design
Persona constraints hold on the cards: Cram's card is strictly achromatic, Lull's has no pure white, Mise has
exactly one gold foil element. Type is brand.type.editorial. Rendered by headless Chrome with a transparent
background so the rounded corners stay clean.
"""

import html
import importlib.util
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parent / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BP = _load("build_pdf", "build-pdf.py")
OV = BP.OV
v, e = OV.v, html.escape
CW, CH, SCALE = 630, 880, 2
OUT = tk.ROOT / "cards"


def card_colours(pid, r):
    """Card stock, name colour and small-text colour per persona, readable on the stock (>= 3:1) and
    respecting each world's constraint (Lull: no pure white, so its stock is its own light text colour)."""
    stock = r["text"] if pid == "lull" else "#FFFFFF"
    name = r["text"] if pid == "cram" else BP.on_light(r, "accent", stock)
    small = BP.on_light(r, "text", stock, 4.5)
    return stock, name, small


def foil(pid):
    if pid == "cram":
        return "linear-gradient(115deg, #2b2b2b, #f2f2f2 30%, #6b6b6b 50%, #ffffff 70%, #3a3a3a)"
    if pid == "mise":   # duotone: the chopsticks in the art stay the only gold foil
        return "linear-gradient(115deg, #4A1416, #6C3F3E 40%, #F4EBDC 55%, #6C3F3E 70%, #4A1416)"
    return "linear-gradient(115deg, #ff7ac6, #ffe27a 22%, #8affc1 42%, #7ac8ff 62%, #c08aff 82%, #ff7ac6)"


def radar(p, r, size=420):
    stats = v(tk.load()["card"]["stats"])
    cx = cy = size / 2
    rad = size / 2 - 70
    n = len(stats)
    pt = lambda k, val: (cx + rad * val / 5 * math.sin(2 * math.pi * k / n), cy - rad * val / 5 * math.cos(2 * math.pi * k / n))
    rings = "".join(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, lv) for k in range(n)))}" '
                    f'fill="none" stroke="{r["text"]}" stroke-opacity=".22" stroke-width="1.5"/>' for lv in range(1, 6))
    spokes = "".join(f'<line x1="{cx}" y1="{cy}" x2="{pt(k, 5)[0]:.1f}" y2="{pt(k, 5)[1]:.1f}" stroke="{r["text"]}" stroke-opacity=".22" stroke-width="1.5"/>'
                     for k in range(n))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, v(p["stats"][s])) for k, s in enumerate(stats)))
    dots = "".join(f'<circle cx="{pt(k, v(p["stats"][s]))[0]:.1f}" cy="{pt(k, v(p["stats"][s]))[1]:.1f}" r="5" fill="{r["key"]}" stroke="{r["text"]}" stroke-width="2"/>'
                   for k, s in enumerate(stats))
    labels = ""
    for k, s in enumerate(stats):
        x, y = pt(k, 6.3)
        labels += (f'<text x="{x:.1f}" y="{y:.1f}" fill="{r["text"]}" font-size="17" font-weight="700" text-anchor="middle" '
                   f'dominant-baseline="middle">{s.capitalize()} {v(p["stats"][s])}</text>')
    return (f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="{e(v(p["name"]))} stats radar">'
            f'{rings}{spokes}<polygon points="{poly}" fill="{r["key"]}" fill-opacity="{v(tk.load()["card"]["radar-fill-opacity"])}" '
            f'stroke="{r["key"]}" stroke-width="2" stroke-linejoin="round"/>{dots}{labels}</svg>')


def texture(pid, r):
    return {
        "cram": "background-image: radial-gradient(rgba(0,0,0,.18) 2px, transparent 2.6px); background-size: 14px 14px;",
        "stack": f"background-image: linear-gradient({r['line']}26 2px, transparent 2px), linear-gradient(90deg, {r['line']}26 2px, transparent 2px); background-size: 32px 32px;",
        "riot": "background-image: conic-gradient(from 20deg at 70% 30%, #FF2E8840, #B8F20040, #2B3DFF40, #FF6A1340, #FF2E8840);",
        "lull": "background-image: radial-gradient(60% 50% at 60% 35%, rgba(255,184,102,.32), transparent 70%);",
        "mise": "background-image: radial-gradient(50% 45% at 55% 25%, rgba(201,162,74,.22), transparent 70%);",
        "sprig": "background-image: radial-gradient(45% 40% at 25% 75%, rgba(85,96,58,.18), transparent 70%);",
        "nest": "background-image: radial-gradient(50% 45% at 30% 25%, rgba(255,201,77,.4), transparent 70%);",
    }[pid]


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: transparent; }
body { width: %(W)spx; height: %(H)spx; font-family: %(text)s; }
.card { position: relative; width: %(W)spx; height: %(H)spx; border-radius: 34px; overflow: hidden; }
.hand { font-family: %(hand)s; }
.disp { font-family: %(disp)s; font-weight: 400; }
"""


def front(p, a, ed, idx):
    pid = p["id"]
    r = {k: v(x) for k, x in p["role"].items()}
    stock, namec, small = card_colours(pid, r)
    fig_uri, (fw, fh) = a.figure(p)
    pk_uri, (pw, ph) = a.pack(p)
    fh2 = 500                      # head breaks just above the art window, below the name
    fw2 = round(fw * fh2 / fh)
    if fw2 > 560:
        fw2, fh2 = 560, round(fh * 560 / fw)
    time = v(p["day"]["time"])
    hh, mm = time.split(":")
    sw = min(1, 170 / pw)
    return f"""
<div class="card" style="background:{stock}">
  <div class="art" style="position:absolute;left:26px;right:26px;top:150px;height:470px;border-radius:20px;overflow:hidden;background:{r['bg']};{texture(pid, r)}">
    <div style="position:absolute;inset:-30px;background:url({a.scene(p)}) center/cover;filter:blur(7px) saturate(.9);opacity:.55"></div>
    <div style="position:absolute;inset:0;background:{r['bg']};opacity:.35"></div>
  </div>
  <div class="disp" style="position:absolute;left:30px;top:22px;right:150px;color:{namec};font-size:96px;line-height:1;white-space:nowrap" data-fit="440">{e(v(p['name']))}</div>
  <div style="position:absolute;left:34px;top:116px;font-size:20px;font-weight:700;color:{small}">{e(v(p['persona']))}</div>
  <div style="position:absolute;right:28px;top:22px;width:108px;text-align:center;color:{small}">
    <div class="disp" style="font-size:40px;line-height:.95">{hh}<br>{mm}</div>
    <div style="font-size:15px;font-weight:800;margin-top:6px">No. {idx:02d}/07</div></div>
  <img src="{fig_uri}" alt="" style="position:absolute;left:{(CW - fw2) // 2}px;top:{620 - fh2}px;width:{fw2}px;height:{fh2}px">
  <img src="{pk_uri}" alt="" style="position:absolute;right:26px;top:470px;width:{round(pw * sw)}px;transform:rotate(9deg)">
  <div style="position:absolute;left:26px;right:26px;top:634px;height:18px;border-radius:9px;background:{foil(pid)}"></div>
  <div style="position:absolute;left:34px;right:34px;top:666px;color:{small}">
    <div style="font-size:18px;font-weight:800">Wants: {e(v(p['primaryMotivation']))}</div>
    <div style="margin-top:12px;padding:14px 18px;border-radius:14px;background:{r['bg']};color:{r['text']}">
      <div class="disp" style="font-size:20px;color:{BP.on_light(r, 'accent', r['bg']) if pid != 'cram' else r['text']}">Signature move</div>
      <div class="hand" style="font-size:24px;line-height:1.2;margin-top:4px">{e(v(p['sachet']))}</div></div>
    <div style="display:flex;justify-content:space-between;margin-top:12px;font-size:14px;font-weight:700;opacity:.85">
      <span>{e(time)}, {e(v(p['day']['light']).split(',')[0])}</span><span>MAGGI persona series</span></div>
  </div>
</div>"""


def back(p, ed, rivals):
    pid = p["id"]
    r = {k: v(x) for k, x in p["role"].items()}
    namec = r["text"] if pid == "cram" else BP.on_light(r, "accent", r["bg"])
    stats = v(tk.load()["card"]["stats"])
    rows = "".join(f'<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:2px dotted {r["text"]}55">'
                   f'<span>{s.capitalize()}</span><b>{v(p["stats"][s])}</b></div>' for s in stats)
    riv = "".join(f'<li style="margin-top:4px">{e(x)}</li>' for x in rivals[:2])
    return f"""
<div class="card" style="background:{r['bg']};color:{r['text']};{texture(pid, r)}">
  <div style="position:absolute;inset:14px;border:4px solid {r['line']};border-radius:24px"></div>
  <div class="disp" style="position:absolute;left:40px;top:36px;font-size:62px;color:{namec}">{e(v(p['name']))}</div>
  <div style="position:absolute;right:40px;top:50px;font-size:18px;font-weight:800">{e(v(p['day']['time']))}</div>
  <div style="position:absolute;left:105px;top:108px">{radar(p, r)}</div>
  <div style="position:absolute;left:40px;right:40px;top:540px;display:grid;grid-template-columns:200px 1fr;gap:26px;font-size:17px">
    <div>{rows}<div style="font-size:12px;margin-top:8px;opacity:.8">Scores 1 to 5: design judgement, to be validated.</div></div>
    <div style="font-size:17px;line-height:1.35">
      <div class="disp" style="font-size:18px;color:{namec}">The gate</div>
      <div class="hand" style="font-size:22px;margin:2px 0 10px">{e(v(p['spine']['gate']))}</div>
      <div class="disp" style="font-size:18px;color:{namec}">Felt two minutes</div>
      <div style="margin:2px 0 10px">{e(v(p['feltTime']))}</div>
      <div class="disp" style="font-size:18px;color:{namec}">Rivals</div>
      <ul style="list-style:none">{riv}</ul></div>
  </div>
</div>"""


def shared_back(ps, a, bc):
    cells = ""
    for i, (pid, p) in enumerate(ps):
        r = {k: v(x) for k, x in p["role"].items()}
        ang = i * 360 / 7
        x = 315 + 200 * math.sin(math.radians(ang)) - 34
        y = 480 - 200 * math.cos(math.radians(ang)) - 50
        cells += (f'<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:68px;height:100px;border-radius:6px;'
                  f'background:linear-gradient(160deg,{r["sachet-red"]} 0 52%,{r["sachet-yellow"]} 52% 100%);'
                  f'border:3px solid {bc["paper"]};transform:rotate({ang:.0f}deg)"></div>')
    return f"""
<div class="card" style="background:{bc['red']};color:{bc['paper']}">
  <div style="position:absolute;inset:0;background-image:repeating-linear-gradient(45deg, rgba(255,194,14,.18) 0 14px, transparent 14px 28px)"></div>
  <div style="position:absolute;inset:14px;border:4px solid {bc['yellow']};border-radius:24px"></div>
  {cells}
  <div class="disp" style="position:absolute;left:0;right:0;top:56px;text-align:center;font-size:58px;line-height:.95">Collect<br>all seven</div>
  <div class="disp" style="position:absolute;left:0;right:0;top:410px;text-align:center;font-size:130px;line-height:1;color:{bc['yellow']}">7</div>
  <div style="position:absolute;left:0;right:0;bottom:70px;text-align:center;font-size:20px;font-weight:800">Seven ways to eat one packet</div>
  <div style="position:absolute;left:50%;bottom:40px;width:260px;margin-left:-130px;height:16px;background:linear-gradient({bc['red']} 0 50%,{bc['yellow']} 50% 100%);border:2px solid {bc['paper']}"></div>
</div>"""


FIT = """<script>document.fonts.ready.then(()=>{document.querySelectorAll('[data-fit]').forEach(el=>{const w=+el.dataset.fit;
if(el.scrollWidth>w)el.style.fontSize=(parseFloat(getComputedStyle(el).fontSize)*w/el.scrollWidth)+'px';});});</script>"""


def render(body, out, fonts_css, ed):
    tmp = Path(tempfile.mkdtemp(prefix="card-"))
    page = tmp / "card.html"
    css = CSS % dict(W=CW, H=CH, text=OV.stack(ed["text"]), hand=OV.stack(ed["hand"]), disp=OV.stack(ed["display"]))
    page.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{fonts_css}</style><style>{css}</style></head>"
                    f"<body>{body}{FIT}</body></html>", encoding="utf-8")
    profile = tmp / "profile"
    cmd = [OV.find_browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--force-device-scale-factor={SCALE}",
           "--no-first-run", "--disable-extensions", "--allow-file-access-from-files", f"--user-data-dir={profile}",
           "--default-background-color=00000000", "--virtual-time-budget=10000",
           f"--screenshot={out}", f"--window-size={CW},{CH}", page.as_uri()]
    subprocess.run(cmd, check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    res = tk.resolve_all(tk.load())
    ps = sorted(tk.personas(res), key=lambda t: v(t[1]["day"]["order"]))
    ed = res["brand"]["type"]["editorial"]
    bc = {k: v(res["brand"]["color"][k]) for k in ("red", "yellow", "ink", "paper")}
    fonts_css = OV.font_css({v(ed[k])[0] for k in ("display", "text", "hand")})
    tmp = Path(tempfile.mkdtemp(prefix="cards-"))
    a = BP.Assets(tmp)
    names = {pid: v(p["name"]) for pid, p in ps}
    pairs = res["rivalries"]["pairs"]
    for i, (pid, p) in enumerate(ps, 1):
        if argv and pid not in argv:
            continue
        d = OUT / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        rivals = [f'{names[x["b"] if x["a"] == pid else x["a"]]}: {v(x["dynamic"]).strip(chr(34))}' for x in pairs if pid in (x["a"], x["b"])]
        render(front(p, a, ed, i), d / f"{p['number']}-{pid}-card-front.png", fonts_css, ed)
        render(back(p, ed, rivals), d / f"{p['number']}-{pid}-card-back.png", fonts_css, ed)
        print(f"  {pid}: card front and back")
    if not argv:
        render(shared_back(ps, a, bc), OUT / "card-back.png", fonts_css, ed)
        print("  shared card back")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

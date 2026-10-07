"""Build the mascot sticker packs (brief Section 18.15: one set per mascot, 512 x 512, chat-app ready).

    python tools/build-stickers.py [mascot ...]

Per mascot, six die-cut stickers with transparent backgrounds, in stickers/NN-slug/:
  NN-mascot-sticker-wave.png              the full figure
  NN-mascot-sticker-<reaction 1>.png      big head plus the first reaction word
  NN-mascot-sticker-<reaction 2>.png      the figure with a speech bubble
  NN-mascot-sticker-name.png              the name as a wordmark sticker with its hour
  NN-mascot-sticker-<reaction 3>.png      the real pack with a tag
  NN-mascot-sticker-my-two-minutes.png    a round crop of the eating scene
plus NN-mascot-sticker-sheet.png, the six on a kiss-cut backing sheet in the persona's world colours.
Reaction words are persona.*.stickers.reactions in tokens.json. Outlines are white, except Lull's (no pure
white), which use its own light text colour. Cram's set stays strictly black and white.
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
import tokens as tk  # noqa: E402

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parent / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BP = _load("build_pdf", "build-pdf.py")
OV = BP.OV
v, e = OV.v, html.escape
CELL = 512
OUT = tk.ROOT / "stickers"


def slug(word):
    return re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-")


def bake(im, colour, outline=10, pad=24):
    """Die-cut: dilate the alpha into an outline in `colour`, add a soft shadow, keep the art on top."""
    im = im.convert("RGBA")
    w, h = im.size
    canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", canvas.size)
    a.paste(im.getchannel("A"), (pad, pad))
    ring = a.filter(ImageFilter.MaxFilter(outline * 2 + 1))
    shadow = ring.filter(ImageFilter.GaussianBlur(8)).point(lambda x: int(x * .35))
    canvas.paste(Image.new("RGBA", canvas.size, (20, 14, 10, 255)), (0, 8), shadow)
    rgb = tuple(int(colour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    canvas.paste(Image.new("RGBA", canvas.size, rgb + (255,)), (0, 0), ring)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(im, (pad, pad))
    return Image.alpha_composite(canvas, layer)


def round_scene(p, colour, size=400):
    sc = Image.open(tk.ROOT / "static" / p["slug"] / f"{p['number']}-{p['id']}-scene-with-pack.png").convert("RGB")
    w, h = sc.size
    side = min(w, h)
    sc = sc.crop(((w - side) // 2, 0, (w + side) // 2, side)).resize((size, size), Image.LANCZOS)
    if p["id"] == "cram":
        sc = sc.convert("L").convert("RGB")
    m = Image.new("L", (size, size))
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = sc.convert("RGBA")
    out.putalpha(m)
    return bake(out, colour, outline=12)


def build(p, res, tmp, fonts_css, ed):
    pid, r = p["id"], {k: v(x) for k, x in p["role"].items()}
    ink = r["text"] if pid == "lull" else "#FFFFFF"
    words = v(p["stickers"]["reactions"])
    cut = tmp / f"{pid}-cut.png"
    OV.cutout(tk.ROOT / "static" / p["slug"] / f"{p['number']}-{pid}-hero-with-pack.png", cut)
    fig = Image.open(cut)
    fig.thumbnail((900, 900), Image.LANCZOS)
    head = fig.crop((0, 0, fig.width, int(fig.height * .47)))
    head = head.crop(head.getbbox())
    pk_src = tmp / f"{pid}-pack.png"
    OV.pack_sticker(p, pk_src)
    pk = Image.open(pk_src)
    pk.thumbnail((420, 420), Image.LANCZOS)
    assets = {"fig": bake(fig, ink), "head": bake(head, ink), "pack": bake(pk, ink, outline=8), "scene": round_scene(p, ink)}
    uris = {}
    for k, im in assets.items():
        dst = tmp / f"{pid}-{k}.png"
        im.save(dst)
        uris[k] = (dst.as_uri(), im.size)

    nm = r["text"] if pid == "cram" else BP.on_light(r, "accent", r["bg"])
    word_css = (f"font-family:{OV.stack(ed['display'])};color:{nm};background:{r['bg']};border:6px solid {ink};"
                f"border-radius:18px;padding:10px 22px;line-height:1;white-space:nowrap;box-shadow:0 8px 14px rgba(0,0,0,.3)")

    def img(k, box, x=None, y=None, rot=0):
        uri, (w, h) = uris[k]
        s = min(box / w, box / h)
        w2, h2 = round(w * s), round(h * s)
        x = (CELL - w2) // 2 if x is None else x
        y = (CELL - h2) // 2 if y is None else y
        return f'<img src="{uri}" style="position:absolute;left:{x}px;top:{y}px;width:{w2}px;height:{h2}px;transform:rotate({rot}deg)">'

    cells = [
        ("wave", img("fig", 500)),
        (slug(words[0]), img("head", 400, y=24) +
         f'<div class="w" style="position:absolute;left:50%;bottom:22px;transform:translateX(-50%) rotate(-4deg);{word_css};font-size:56px" data-fit="470">{e(words[0])}</div>'),
        (slug(words[1]), img("fig", 400, x=0, y=100) +
         f'<div style="position:absolute;right:10px;top:22px;transform:rotate(6deg)"><div class="w" style="{word_css};font-size:52px;border-radius:40px" data-fit="300">{e(words[1])}</div>'
         f'<div style="position:absolute;left:44px;bottom:-26px;width:0;height:0;border:16px solid transparent;border-top:26px solid {ink}"></div></div>'),
        ("name", f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-6deg)">'
                 f'<div class="w" style="{word_css};font-size:118px;padding:20px 30px" data-fit="460">{e(v(p["name"]))}</div>'
                 f'<div style="margin-top:14px;font-family:{OV.stack(ed["hand"])};font-size:40px;color:{r["text"]};background:{r["bg"]};border:5px solid {ink};border-radius:12px;padding:4px 18px;transform:rotate(8deg)">{e(v(p["day"]["time"]))} o\'clock</div></div>'),
        (slug(words[2]), img("pack", 380, y=30, rot=-8) +
         f'<div class="w" style="position:absolute;left:50%;bottom:28px;transform:translateX(-50%) rotate(3deg);{word_css};font-size:50px" data-fit="460">{e(words[2])}</div>'),
        ("my-two-minutes", img("scene", 430, y=20) +
         f'<div style="position:absolute;left:50%;bottom:16px;transform:translateX(-50%) rotate(-5deg);font-family:{OV.stack(ed["hand"])};font-size:40px;'
         f'color:{r["text"]};background:{r["bg"]};border:5px solid {ink};border-radius:14px;padding:4px 18px;white-space:nowrap">my two minutes</div>'),
    ]
    body = "".join(f'<div class="cell" style="left:{(k % 3) * CELL}px;top:{(k // 3) * CELL}px">{html_}</div>' for k, (_, html_) in enumerate(cells))
    fit = """<script>document.fonts.ready.then(()=>{document.querySelectorAll('[data-fit]').forEach(el=>{const w=+el.dataset.fit;
      if(el.offsetWidth>w)el.style.fontSize=(parseFloat(getComputedStyle(el).fontSize)*w/el.offsetWidth)+'px';});});</script>"""
    page = tmp / f"{pid}.html"
    page.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts_css}</style><style>
      * {{ margin:0; padding:0; box-sizing:border-box; }} html, body {{ background: transparent; }}
      body {{ width:{CELL * 3}px; height:{CELL * 2}px; position:relative; font-family:{OV.stack(ed['text'])}; }}
      .cell {{ position:absolute; width:{CELL}px; height:{CELL}px; overflow:hidden; }}
    </style></head><body>{body}{fit}</body></html>""", encoding="utf-8")
    shot = tmp / f"{pid}.png"
    subprocess.run([OV.find_browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--no-first-run", "--disable-extensions", "--allow-file-access-from-files", f"--user-data-dir={tmp / 'prof'}",
                    "--default-background-color=00000000", "--virtual-time-budget=10000",
                    f"--screenshot={shot}", f"--window-size={CELL * 3},{CELL * 2}", page.as_uri()],
                   check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    grid = Image.open(shot).convert("RGBA")
    d = OUT / p["slug"]
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob(f"{p['number']}-{pid}-sticker-*.png"):
        old.unlink()
    files = []
    for k, (name, _) in enumerate(cells):
        im = grid.crop(((k % 3) * CELL, (k // 3) * CELL, (k % 3 + 1) * CELL, (k // 3 + 1) * CELL))
        if pid == "cram":
            g = im.convert("LA")
            im = Image.merge("RGBA", (g.getchannel(0),) * 3 + (g.getchannel(1),))
        dst = d / f"{p['number']}-{pid}-sticker-{name}.png"
        im.save(dst, optimize=True)
        files.append(dst)
    sheet(p, r, files, d, ed, fonts_css, tmp, ink)
    return files


def sheet(p, r, files, d, ed, fonts_css, tmp, ink):
    """Kiss-cut sheet: the six stickers on backing paper in the world colours, with a title strip."""
    W, H = 1700, 1260
    imgs = "".join(f'<img src="{f.as_uri()}" style="position:absolute;left:{70 + (k % 3) * 530}px;top:{190 + (k // 3) * 520}px;'
                   f'width:500px;height:500px;transform:rotate({(-4, 3, -2, 4, -3, 2)[k]}deg)">' for k, f in enumerate(files))
    nm = r["text"] if p["id"] == "cram" else BP.on_light(r, "accent", r["bg"])
    page = tmp / f"{p['id']}-sheet.html"
    page.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts_css}</style><style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{ width:{W}px; height:{H}px; position:relative; overflow:hidden; background:{r['bg']}; color:{r['text']};
              font-family:{OV.stack(ed['text'])}; }}
      .grid {{ position:absolute; inset:0; background-image: linear-gradient({r['text']}14 2px, transparent 2px),
               linear-gradient(90deg, {r['text']}14 2px, transparent 2px); background-size: 40px 40px; }}
    </style></head><body><div class="grid"></div>
      <div style="position:absolute;left:70px;top:46px;font-family:{OV.stack(ed['display'])};font-size:96px;line-height:1;color:{nm}">{e(v(p['name']))}</div>
      <div style="position:absolute;left:76px;top:150px;font-size:24px;font-weight:700">{e(v(p['persona']))} sticker pack, six stickers, {v(p['day']['time'])}</div>
      <div style="position:absolute;right:70px;top:60px;font-family:{OV.stack(ed['hand'])};font-size:40px;transform:rotate(-4deg)">peel, stick, slurp</div>
      {imgs}</body></html>""", encoding="utf-8")
    out = d / f"{p['number']}-{p['id']}-sticker-sheet.png"
    subprocess.run([OV.find_browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--no-first-run", "--disable-extensions", "--allow-file-access-from-files", f"--user-data-dir={tmp / 'prof2'}",
                    "--virtual-time-budget=10000", f"--screenshot={out}", f"--window-size={W},{H}", page.as_uri()],
                   check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if p["id"] == "cram":
        Image.open(out).convert("L").convert("RGB").save(out)


def main(argv):
    res = tk.resolve_all(tk.load())
    ed = res["brand"]["type"]["editorial"]
    fonts_css = OV.font_css({v(ed[k])[0] for k in ("display", "text", "hand")})
    tmp = Path(tempfile.mkdtemp(prefix="stickers-"))
    for pid, p in tk.personas(res):
        if argv and pid not in argv:
            continue
        files = build(p, res, tmp, fonts_css, ed)
        print(f"  {pid}: {len(files)} stickers + sheet")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

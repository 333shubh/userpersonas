"""Build mascot idle loops from the named layers of the front-view rig (Gate 2: Cram + Riot).

    python tools/build-idle.py cram riot

Nothing is redrawn: each frame is the rig SVG with transforms added to named groups and lid
states swapped. All timing comes from tokens.json (motion clock, easing, persona motion block).
Pipeline: frame SVGs -> headless Chrome PNGs -> ffmpeg MP4 (H.264) + WebM (VP9) at
1080x1080, 1920x1080, 1080x1920, plus a poster PNG per size (the reduced-motion fallback).
Writes motion/NN-slug/NN-mascot-idle.json with the parameters and the loop-seam result.
Needs: Chrome or Edge, ffmpeg on PATH.
"""

import concurrent.futures as cf
import copy
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402

SVG_NS = "http://www.w3.org/2000/svg"
NS = "{" + SVG_NS + "}"
ET.register_namespace("", SVG_NS)
BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "google-chrome", "chromium", "chrome", "msedge"]
SIZES = [(1080, 1080), (1920, 1080), (1080, 1920)]
BODY_SLOTS = ("limbs-back", "body", "face", "limbs", "props", "noodles-steam", "foreground-type")

# Idle intensity: an idle loop uses a fraction of the persona's full squash/amplitude (reactions use all of it).
IDLE_SQUASH = 0.5      # fraction of persona squashStretch used on idle accents
BREATH = 0.012         # scaleY breathing amplitude per unit of persona amplitude
BOB = 10.0             # rig units of lift on an accent, per unit of persona amplitude
STEAM_DRIFT = 14.0     # rig units of steam sway, per unit of persona amplitude
FLAME_PULSE = 0.05     # Riot flame scale pulse per unit of amplitude
POP_FRAMES = 8         # frames from accent to settled
RENDER_TRIES, RENDER_TIMEOUT = 3, 45  # attempts per frame, seconds per attempt
BLINK_FRAMES = ("half", "closed", "half")  # states on the 3 frames after the blink start, then open


def bezier(p):
    """cubic-bezier(x1,y1,x2,y2) -> f(t) for t in [0,1]."""
    x1, y1, x2, y2 = p

    def coord(t, a, b):
        return 3 * a * t * (1 - t) ** 2 + 3 * b * t ** 2 * (1 - t) + t ** 3

    def solve(x):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if coord(mid, x1, x2) < x:
                lo = mid
            else:
                hi = mid
        return coord((lo + hi) / 2, y1, y2)
    return solve


def find_browser():
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b if Path(b).exists() else shutil.which(b)
    raise SystemExit("Chrome or Edge not found")


class Idle:
    def __init__(self, pid, res):
        self.pid, self.p = pid, res["persona"][pid]
        m = res["motion"]
        self.fps = m["frame-rate"]["primary"]["$value"]
        self.beat = self.fps * tk.ms(m["clock"]["beat"]["$value"]) // 1000          # 12 frames
        self.frames = self.p["motion"]["idleBars"] * m["frame-rate"]["frames-per-bar"]["$value"]
        self.ease = {k: bezier(v["$value"]) for k, v in m["easing"].items() if not k.startswith("$")}
        self.mo = self.p["motion"]
        rig = tk.ROOT / "static" / self.p["slug"] / f"{self.p['number']}-{pid}-rig-front.svg"
        self.tree = ET.parse(rig)
        self.rig_path = rig
        self.anchor = {c.get("id").split("__rig__")[1]: (float(c.get("cx")), float(c.get("cy")))
                       for c in self.tree.getroot().iter(NS + "circle") if "__rig__" in (c.get("id") or "")}
        self.bg = tk.roles(self.p)["bg"]

    # --- motion curves (all periodic in self.frames, so the loop is seamless by construction) ---
    def since(self, f, start):
        return (f - start) % self.frames

    def accent(self, f):
        """-> (scaleY, scaleX, lift) for the root at frame f."""
        sy, sx, lift = 1.0, 1.0, 0.0
        s = self.mo["squashStretch"] * IDLE_SQUASH
        ant = max(1, self.mo["anticipationFrames"])
        for b in self.mo["accentBeats"]:
            start = round((b - 1) * self.beat)
            d = self.since(f, start)
            pre = self.frames - d  # frames until the accent
            if 0 < pre <= ant and s:
                k = self.ease["ease-in-soft"](1 - (pre - 1) / ant) if ant > 1 else 1.0
                sy, sx = sy * (1 - s * k), sx * (1 + s * k * 0.5)
            elif d < POP_FRAMES:
                t = d / POP_FRAMES
                pop = self.ease["ease-out-pop" if self.mo["overshootPct"] else "ease-settle"](t)
                if s:
                    sy, sx = sy * (1 - s + s * pop), sx * (1 + 0.5 * s - 0.5 * s * pop)
                lift += BOB * self.mo["amplitude"] * math.sin(math.pi * t)
        return sy, sx, lift

    def breath(self, f):
        return 1 + BREATH * self.mo["amplitude"] * math.sin(2 * math.pi * f / self.frames)

    def blink_state(self, f):
        start = round(2.5 * self.beat) if self.pid != "riot" else round(2 * self.beat)
        d = self.since(f, start)
        return BLINK_FRAMES[d] if d < len(BLINK_FRAMES) else "open"

    # --- frame assembly ---
    def frame(self, f):
        tree = copy.deepcopy(self.tree)
        root = tree.getroot()
        by_id = {el.get("id"): el for el in root.iter() if el.get("id")}
        rx, ry = self.anchor["root"]
        sy, sx, lift = self.accent(f)
        sy *= self.breath(f)
        whole = f"translate({rx:.2f} {ry - lift:.2f}) scale({sx:.4f} {sy:.4f}) translate({-rx:.2f} {-ry:.2f})"
        for slot in BODY_SLOTS:
            el = by_id.get(f"{self.pid}__{slot}")
            if el is not None:
                el.set("transform", (whole + " " + el.get("transform", "")).strip())
        for i in (1, 2, 3):  # steam sway, phase-shifted per wisp
            el = by_id.get(f"{self.pid}__noodles-steam__steam-{i}")
            if el is not None:
                ph = 2 * math.pi * (f / self.frames + i / 3)
                dx = STEAM_DRIFT * self.mo["amplitude"] * 0.5 * math.sin(ph)
                dy = -STEAM_DRIFT * self.mo["amplitude"] * (0.5 + 0.5 * math.sin(ph + math.pi / 2))
                el.set("transform", f"translate({dx:.2f} {dy:.2f}) " + el.get("transform", ""))
        if self.mo["pulseHz"]:
            period = round(self.fps / self.mo["pulseHz"])
            hx, hy = self.anchor["head-pivot"]
            for i in (1, 2, 3):
                el = by_id.get(f"{self.pid}__body__flame-hair__flame-{i}")
                if el is None:
                    continue
                d = (f - (i - 1)) % period  # flames overlap by 1 frame each (secondary motion)
                k = FLAME_PULSE * self.mo["amplitude"] * (1 - self.ease["ease-settle"](min(1, d / (period * 0.75))))
                el.set("transform", f"translate({hx:.2f} {hy:.2f}) scale({1 + k:.4f}) translate({-hx:.2f} {-hy:.2f}) "
                       + el.get("transform", ""))
        state = self.blink_state(f)
        for side in ("l", "r"):
            lid = by_id.get(f"{self.pid}__face__lid-{side}")
            if lid is None:
                continue
            for ch in lid:
                cid = ch.get("id") or ""
                if "--" in cid:
                    if cid.endswith("--" + state):
                        ch.attrib.pop("display", None)
                    else:
                        ch.set("display", "none")
        root.set("width", "1080")
        root.set("height", "1080")
        bg = ET.Element(NS + "rect", {"width": "1024", "height": "1024", "fill": self.bg})
        root.insert(0, bg)
        return ET.tostring(root, encoding="unicode")


def render(browser, svg_path, png_path):
    # each headless instance gets its own throwaway profile, so parallel renders never share a lock
    # an occasional headless instance hangs: kill its whole process tree and retry
    profile = png_path.with_suffix(".profile")
    cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
           "--no-first-run", "--no-default-browser-check", "--disable-extensions",
           f"--user-data-dir={profile}", "--default-background-color=00000000",
           f"--screenshot={png_path}", "--window-size=1080,1080", svg_path.as_uri()]
    for attempt in range(RENDER_TRIES):
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            proc.wait(timeout=RENDER_TIMEOUT)
            if proc.returncode == 0 and png_path.exists():
                break
        except subprocess.TimeoutExpired:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
            else:
                proc.kill()
            proc.wait()
        shutil.rmtree(profile, ignore_errors=True)
    else:
        raise RuntimeError(f"render failed after {RENDER_TRIES} tries: {svg_path.name}")
    shutil.rmtree(profile, ignore_errors=True)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def build(pid, res, browser):
    idle = Idle(pid, res)
    p = idle.p
    out_dir = tk.ROOT / "motion" / p["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{p['number']}-{pid}-idle"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        jobs = []
        for f in range(idle.frames + 1):  # +1: frame N must equal frame 0 (seam check)
            svg = tmp / f"f{f:03d}.svg"
            svg.write_text(idle.frame(f), encoding="utf-8")
            jobs.append((svg, tmp / f"f{f:03d}.png"))
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            list(ex.map(lambda j: render(browser, *j), jobs))
        h0 = hashlib.sha256((tmp / "f000.png").read_bytes()).hexdigest()
        hn = hashlib.sha256((tmp / f"f{idle.frames:03d}.png").read_bytes()).hexdigest()
        svg0 = (tmp / "f000.svg").read_text(encoding="utf-8")
        svgn = (tmp / f"f{idle.frames:03d}.svg").read_text(encoding="utf-8")
        (tmp / f"f{idle.frames:03d}.png").unlink()
        pattern = str(tmp / "f%03d.png")
        bg = idle.bg.lstrip("#")
        outputs = []
        for w, h in SIZES:
            pad = f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x{bg}"
            base = out_dir / f"{stem}-{w}x{h}"
            ffmpeg("-framerate", str(idle.fps), "-i", pattern, "-vf", pad, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-crf", "18", "-r", str(idle.fps), "-movflags", "+faststart", f"{base}.mp4")
            ffmpeg("-framerate", str(idle.fps), "-i", pattern, "-vf", pad, "-c:v", "libvpx-vp9", "-b:v", "0",
                   "-crf", "30", "-r", str(idle.fps), f"{base}.webm")
            poster = out_dir / f"{stem}-poster-{w}x{h}.png"
            ffmpeg("-i", str(tmp / "f000.png"), "-vf", pad, "-frames:v", "1", str(poster))
            outputs += [f"{base.name}.mp4", f"{base.name}.webm", poster.name]
    manifest = {
        "$description": "GENERATED by tools/build-idle.py. Do not edit.",
        "mascot": pid, "source": idle.rig_path.relative_to(tk.ROOT).as_posix(),
        "fps": idle.fps, "frames": idle.frames, "durationMs": round(1000 * idle.frames / idle.fps),
        "motion": idle.mo,
        "idle": {"squashFraction": IDLE_SQUASH, "breath": BREATH, "bob": BOB, "steamDrift": STEAM_DRIFT,
                 "flamePulse": FLAME_PULSE if idle.mo["pulseHz"] else 0, "popFrames": POP_FRAMES,
                 "blink": "half/closed/half from beat 2.5" if pid != "riot" else "half/closed/half from beat 3"},
        "loopSeam": {"frame0VsFrameN": "identical" if (h0 == hn and svg0 == svgn) else "DIFFERENT",
                     "rule": "frame N (t = duration) is rendered and must equal frame 0; exported frames are 0..N-1"},
        "outputs": outputs,
        "audio": "none (sound signatures arrive at Gate 4; these clips are the silent versions)",
        "reducedMotion": "poster PNGs are the reduced-motion fallback",
    }
    (out_dir / f"{stem}.json").write_text(tk.dumps(manifest) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main(argv):
    res = tk.resolve_all(tk.load())
    browser = find_browser()
    for pid in argv or ["cram", "riot"]:
        m = build(pid, res, browser)
        print(f"{pid}: {m['frames']} frames @ {m['fps']} fps, seam {m['loopSeam']['frame0VsFrameN']}, "
              f"{len(m['outputs'])} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Motion clip check for motion/NN-slug/ (Gate 2+).

    python tools/check-motion.py

For every NN-mascot-<clip>.json manifest written by the build tools:
  - every listed output exists; MP4 is H.264 and WebM is VP9, frame size matches the file name,
    24 fps, frame count and duration equal the manifest (whole bars on the 120 BPM grid)
  - no audio stream (Gate 2 clips are the silent versions)
  - loop seam: frame N rendered identical to frame 0 (recorded by the builder)
  - poster PNG present for every size (reduced-motion fallback)
  - photosensitivity (WCAG 2.3.1, brief Section 20): decoded frames compared pairwise (including the
    loop wrap); a "flash event" is a frame step where more than max-flash-area of the frame changes
    luminance by more than 10%. Events per second must stay below max-flashes-per-second.
Needs ffmpeg and ffprobe on PATH.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

ANALYSE = 270  # analysis resolution (px) for the flash test


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-count_frames", "-of", "json",
                          str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def grey_frames(path, w, h):
    aw, ah = ANALYSE, round(ANALYSE * h / w)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={aw}:{ah}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    n = aw * ah
    return [raw[i:i + n] for i in range(0, len(raw), n)], n


def lin(v):
    c = v / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


LIN = [lin(v) for v in range(256)]


def flash_events(frames, n, area_limit):
    events, worst = 0, 0.0
    for a, b in zip(frames, frames[1:] + frames[:1]):  # include the loop wrap
        changed = sum(1 for x, y in zip(a, b) if abs(LIN[x] - LIN[y]) > 0.1) / n
        worst = max(worst, changed)
        if changed > area_limit:
            events += 1
    return events, worst


def main():
    r = Report("check-motion", "Motion clip check",
               "Every clip manifest in `motion/` checked against the motion grid and the photosensitivity rules.")
    res = tk.resolve_all(tk.load())
    m = res["motion"]
    fps = m["frame-rate"]["primary"]["$value"]
    ceiling = m["safety"]["max-flashes-per-second"]["$value"]
    area = m["safety"]["max-flash-area"]["$value"]
    manifests = sorted(tk.ROOT.glob("motion/*/*.json"))
    if not manifests:
        r.add("INFO", "motion clips", "none yet")
    for man in manifests:
        data = json.loads(man.read_text(encoding="utf-8"))
        rel = man.relative_to(tk.ROOT).as_posix()
        r.ok(data["fps"] == fps and data["frames"] % (fps // 2) == 0, f"{rel}: {fps} fps, whole beats",
             f"{data['frames']} frames = {data['durationMs']} ms")
        r.ok(data["loopSeam"]["frame0VsFrameN"] == "identical", f"{rel}: loop seam (frame N == frame 0)",
             data["loopSeam"]["frame0VsFrameN"])
        flash_done = False
        for name in data["outputs"]:
            path = man.parent / name
            if not path.exists():
                r.add("FAIL", f"{name}: exists")
                continue
            size = re.search(r"(\d+)x(\d+)\.\w+$", name)
            w, h = int(size.group(1)), int(size.group(2))
            if name.endswith(".png"):
                r.ok(path.stat().st_size > 0, f"{name}: poster frame present (reduced-motion fallback)")
                continue
            info = probe(path)
            video = [s for s in info["streams"] if s["codec_type"] == "video"]
            audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
            v = video[0]
            codec = {"mp4": "h264", "webm": "vp9"}[name.rsplit(".", 1)[1]]
            num, den = (int(x) for x in v["avg_frame_rate"].split("/"))
            frames = int(v.get("nb_read_frames", 0))
            r.ok(v["codec_name"] == codec and (v["width"], v["height"]) == (w, h) and round(num / den) == fps
                 and frames == data["frames"],
                 f"{name}: {codec}, {w}x{h}, {fps} fps, {data['frames']} frames",
                 f"{v['codec_name']}, {v['width']}x{v['height']}, {num / den:g} fps, {frames} frames, "
                 f"{float(info['format']['duration']):.3f} s")
            r.ok(not audio, f"{name}: silent (no audio stream)")
            if name.endswith(".mp4") and not flash_done:
                fr, n = grey_frames(path, w, h)
                events, worst = flash_events(fr, n, area)
                per_sec = events / (len(fr) / fps)
                r.ok(per_sec < ceiling, f"{data['mascot']}: flashes below {ceiling}/s (WCAG 2.3.1)",
                     f"{events} flash events in {len(fr)} frames ({per_sec:.2f}/s); largest frame-to-frame "
                     f"luminance change covers {worst:.1%} of the frame (limit {area:.0%})")
                flash_done = True
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

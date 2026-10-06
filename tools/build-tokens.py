"""Generate per-persona token files and the generated tables in the design-system doc.

    python tools/build-tokens.py          write outputs
    python tools/build-tokens.py --check  exit 1 if any output is out of date

Source: system/tokens/tokens.json (the only file a human edits).
Outputs:
  system/tokens/personas/NN-<id>.tokens.json   fully resolved, one per persona
  markdown/00-maggi-persona-design-system.md   blocks between
                                               <!-- generated:NAME:start/end --> markers
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import colour  # noqa: E402
import tokens as tk  # noqa: E402

DOC = tk.ROOT / "markdown" / "00-maggi-persona-design-system.md"
BLOCK_RE = re.compile(r"(<!-- generated:([a-z-]+):start -->\n)(.*?)(<!-- generated:\2:end -->)", re.S)
NOTE_PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
TYPE_STEPS = {"caption": -1, "body": 0, "lead": 1, "h3": 2, "h2": 3, "h1": 4, "display": 5}
STAT_ORDER = ("heat", "speed", "comfort", "chaos", "value", "fancy", "wellness")


def note_hz(note):
    m = re.fullmatch(r"([A-G]#?)(\d)", note)
    midi = 12 * (int(m.group(2)) + 1) + NOTE_PC[m.group(1)]
    return round(440 * 2 ** ((midi - 69) / 12), 2)


def persona_file(raw, resolved, pid):
    p = resolved["persona"][pid]
    sound = dict(p["sound"], hz=note_hz(p["sound"]["pitch"]), chord=resolved["sound"]["chord"]["$value"])
    base = tk.px(resolved["brand"]["type"]["base-size"]["$value"])
    ratio = p["type"]["scale-ratio"]["$value"]
    floor = tk.px(resolved["brand"]["type"]["min-size"]["web-caption"]["$value"])
    scale = {}
    for name, step in TYPE_STEPS.items():
        size = round(base * ratio ** step)
        scale[name] = {"$type": "dimension", "$value": f"{max(size, round(floor))}px"}
        if size < floor:
            scale[name]["$description"] = f"Clamped from {size}px to brand.type.min-size.web-caption."
    return {
        "$description": f"GENERATED from system/tokens/tokens.json by tools/build-tokens.py. Do not edit. "
                        f"Fully resolved tokens for {p['name']} ({p['persona']}).",
        "meta": {"source": "system/tokens/tokens.json", "sourceVersion": raw["meta"]["version"],
                 "gate": raw["meta"]["gate"], "status": raw["meta"]["status"], "persona": pid},
        "brand": resolved["brand"],
        "motion": resolved["motion"],
        "card": resolved["card"],
        "locale": resolved["locale"],
        "rivalries": [r for r in resolved["rivalries"]["pairs"] if pid in (r["a"], r["b"])],
        "persona": dict(p, sound=sound, type=dict(p["type"], scale=scale)),
    }


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def block_persona_map(r):
    rows = []
    for pid, p in tk.personas(r):
        rows.append([p["number"], f"**{p['name']}**", p["persona"], p["primaryMotivation"],
                     p["spine"]["buyer"], p["spine"]["eater"], p["spine"]["gate"],
                     f"{p['day']['order']} · {p['day']['time']}", p["constraint"]["rule"]])
    return md_table(["#", "Mascot", "Persona", "Primary motivation", "Buyer", "Eater", "Decision gate",
                     "Day slot", "Design constraint"], rows)


def block_card_stats(r):
    rows = [[f"**{p['name']}**"] + [p["stats"][s] for s in STAT_ORDER] for _, p in tk.personas(r)]
    return md_table(["Mascot"] + [s.title() for s in STAT_ORDER], rows) + \
        "\n\n_Draft scores: design judgement from brief Section 18.7, to be validated against research._"


def block_palettes(r):
    thresholds = colour.WCAG
    parts = []
    for pid, p in tk.personas(r):
        pal = tk.palette(p)
        level = p["contrast"]["level"]
        names = {v: k for k, v in pal.items()}
        role_list = ", ".join(f"`{role}` = `{names.get(hexv, hexv)}`" for role, hexv in tk.roles(p).items())
        parts.append(f"#### {p['name']} ({p['persona']}), target WCAG {level}\n")
        parts.append(md_table(["Token", "Hex", "WCAG luminance"],
                              [[f"`{k}`", f"`{v}`", f"{colour.luminance(v):.3f}"] for k, v in pal.items()]))
        parts.append(f"\nSemantic roles: {role_list}.\n")
        rows = []
        for pair in p["contrast"]["pairs"]:
            need = thresholds[level][pair["use"]]
            ratio = colour.contrast(pair["fg"], pair["bg"])
            rows.append([f"`{names.get(pair['fg'], pair['fg'])}` on `{names.get(pair['bg'], pair['bg'])}`",
                         pair["use"], f"{ratio:.2f}:1", f"{need}:1", "pass" if ratio >= need else "**FAIL**",
                         pair["where"]])
        parts.append(md_table(["Pair", "Use", "Ratio", "Needs", "Result", "Where"], rows) + "\n")
    return "\n".join(parts).rstrip()


def block_motion(r):
    m = r["motion"]
    ease = [[f"`{k}`", ", ".join(str(x) for x in v["$value"]), v.get("$description", "")]
            for k, v in m["easing"].items()]
    rows = []
    for _, p in tk.personas(r):
        mo = p["motion"]
        rows.append([f"**{p['name']}**", mo["tempo"], f"{mo['idleBars'] * 2} s", mo["amplitude"],
                     mo["squashStretch"], mo["anticipationFrames"],
                     ", ".join(str(b) for b in mo["accentBeats"]), mo["pulseHz"]])
    return (f"Clock **{m['clock']['bpm']['$value']} BPM**, beat {m['clock']['beat']['$value']}, "
            f"bar {m['clock']['bar']['$value']}, **{m['frame-rate']['primary']['$value']} fps** "
            f"({m['frame-rate']['frames-per-beat']['$value']} frames per beat, "
            f"{m['frame-rate']['frames-per-bar']['$value']} per bar). "
            f"Flash ceiling {m['safety']['max-flashes-per-second']['$value']} per second.\n\n"
            + md_table(["Easing token", "cubic-bezier", "Use"], ease) + "\n\n"
            + md_table(["Mascot", "Tempo feel", "Idle loop", "Amplitude", "Squash/stretch", "Anticipation (frames)",
                        "Accent beats", "Pulse Hz"], rows))


def block_sound(r):
    rows = []
    for _, p in sorted(tk.personas(r), key=lambda kv: note_hz(kv[1]["sound"]["pitch"])):
        s = p["sound"]
        rows.append([f"**{p['name']}**", s["pitch"], f"{note_hz(s['pitch'])} Hz", s["role"],
                     ", ".join(s["palette"]), "yes" if s["asmr"] else "no"])
    return md_table(["Mascot", "Pitch", "Frequency", "Role", "Palette", "ASMR layer"], rows)


def _v(tok):
    return tok["$value"] if isinstance(tok, dict) and "$value" in tok else tok


def _flat(group):
    """'k=v' summary of a token group (one level of nesting)."""
    out = []
    for k, v in group.items():
        if k.startswith("$"):
            continue
        if isinstance(v, dict) and "$value" not in v:
            out.append(f"{k}: " + ", ".join(f"{kk}={_v(vv)}" for kk, vv in v.items() if not kk.startswith("$")))
        else:
            out.append(f"{k}={_v(v)}")
    return "; ".join(out)


def block_type_system(r):
    base = tk.px(r["brand"]["type"]["base-size"]["$value"])
    floor = tk.px(r["brand"]["type"]["min-size"]["web-caption"]["$value"])
    rows = []
    for _, p in tk.personas(r):
        t = p["type"]
        ratio = t["scale-ratio"]["$value"]
        steps = " / ".join(f"{max(round(base * ratio ** n), round(floor))}" for n in TYPE_STEPS.values())
        rows.append([f"**{p['name']}**", f"{t['display']['$value'][0]} {_v(t['weight']['display'])}",
                     f"{t['text']['$value'][0]} {_v(t['weight']['text'])}/{_v(t['weight']['text-strong'])}",
                     f"{_v(t['line-height']['display'])} / {_v(t['line-height']['text'])}",
                     f"{_v(t['tracking']['display'])} / {_v(t['tracking']['text'])} / {_v(t['tracking']['label'])}",
                     f"{_v(t['case']['display'])} / {_v(t['case']['text'])}", ratio, steps])
    return md_table(["Mascot", "Display face + weight", "Text face + weights", "Line-height display / text",
                     "Tracking em display / text / label", "Case display / text", "Ratio",
                     "Scale px: " + " / ".join(TYPE_STEPS)], rows)


def block_surface_system(r):
    rows = []
    for _, p in tk.personas(r):
        sh = p["shape"]
        rows.append([f"**{p['name']}**", ", ".join(sh["radius"]["$value"]), sh["stroke"]["$value"], sh["cap"]["$value"],
                     _flat(sh["angles"]), _flat(p["elevation"]), _flat(p["iconography"]), p["density"]["$value"]])
    tex = []
    for _, p in tk.personas(r):
        tex.append([f"**{p['name']}**", _flat(p["texture"])])
    return (md_table(["Mascot", "Radius", "Stroke (rig units)", "Cap", "Angles", "Elevation", "Icons", "Density"], rows)
            + "\n\n" + md_table(["Mascot", "Texture parameters (SVG-filter ready; rig units at 1024)"], tex))


BLOCKS = {
    "type-system": block_type_system,
    "surface-system": block_surface_system,
    "persona-map": block_persona_map,
    "card-stats": block_card_stats,
    "palettes": block_palettes,
    "motion-grid": block_motion,
    "sound-chord": block_sound,
}


def render():
    """Return {path: expected content} for every generated output."""
    raw = tk.load()
    resolved = tk.resolve_all(raw)
    out = {}
    for pid, p in tk.personas(resolved):
        path = tk.PERSONA_DIR / f"{p['number']}-{pid}.tokens.json"
        out[path] = json.dumps(persona_file(raw, resolved, pid), indent=2, ensure_ascii=False) + "\n"
    if DOC.exists():
        text = DOC.read_text(encoding="utf-8")

        def fill(m):
            name = m.group(2)
            if name not in BLOCKS:
                raise KeyError(f"unknown generated block '{name}' in {DOC.name}")
            return f"{m.group(1)}{BLOCKS[name](resolved)}\n{m.group(4)}"

        out[DOC] = BLOCK_RE.sub(fill, text)
    return out


def stale_outputs():
    stale = []
    expected = render()
    for path, content in expected.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(path)
    known = set(expected)
    stray = [p for p in tk.PERSONA_DIR.glob("*.json") if p not in known]
    return stale, stray


def main(argv):
    if "--check" in argv:
        stale, stray = stale_outputs()
        for p in stale:
            print(f"  out of date: {p.relative_to(tk.ROOT).as_posix()}")
        for p in stray:
            print(f"  not generated from tokens.json: {p.relative_to(tk.ROOT).as_posix()}")
        print("build-tokens --check:", "FAIL" if stale or stray else "PASS")
        return 1 if stale or stray else 0
    tk.PERSONA_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in render().items():
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"  wrote {path.relative_to(tk.ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

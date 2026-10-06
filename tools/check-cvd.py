"""Colour-vision-deficiency simulation report for every palette in system/tokens/tokens.json.

    python tools/check-cvd.py

Model: Machado, Oliveira & Fernandes (2009), severity 1.0, linear sRGB.
Metric: OKLab Euclidean distance x100 (dE), same standard as the dataviz skill.

Gated (PASS / WARN / FAIL), for every declared `distinguish` pair and for the
cross-system persona key colours:
  - normal vision dE >= 15                         hard gate (FAIL below)
  - worst of protan/deutan/tritan dE >= 8          PASS
  - 6 <= worst < 8                                 WARN, legal only with a declared
                                                   secondary (non-colour) cue, else FAIL
  - worst < 6                                      FAIL
Informational: simulated hex for every colour, and the closest pair in each palette
(colours that never sit side by side as meaning-carriers may legitimately be close).

Also writes stress-tests/colour-blind/cvd-simulated-palettes.json, the data source
for the visual colour-blind proofs Claude Design produces at Gate 6.
"""

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import colour  # noqa: E402
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

OUT_JSON = tk.ROOT / "stress-tests" / "colour-blind" / "cvd-simulated-palettes.json"
KEY_CUE = "mascot silhouette + persona name always accompany the key colour"


def name_of(palette, hexv):
    return next((k for k, v in palette.items() if v.upper() == hexv.upper()), hexv)


def grade(r, label, a, b, cue, rows):
    normal = colour.delta_e(a, b)
    sims = {k: colour.delta_e(a, b, k) for k in colour.CVD_KINDS}
    worst_kind = min(sims, key=sims.get)
    worst = sims[worst_kind]
    if normal < colour.NORMAL_FLOOR:
        status, why = "FAIL", f"normal-vision dE {normal:.1f} < {colour.NORMAL_FLOOR:g}"
    elif worst >= colour.CVD_TARGET:
        status, why = "PASS", f"worst {worst_kind} dE {worst:.1f} >= {colour.CVD_TARGET:g}"
    elif worst >= colour.CVD_FLOOR and cue:
        status, why = "WARN", f"worst {worst_kind} dE {worst:.1f} in floor band; relies on secondary cue: {cue}"
    else:
        status, why = "FAIL", f"worst {worst_kind} dE {worst:.1f}" + ("" if cue else " and no secondary cue declared")
    r.add(status, label, f"normal {normal:.1f}; {why}")
    rows.append([label, f"{normal:.1f}"] + [f"{sims[k]:.1f}" for k in colour.CVD_KINDS] + [status, cue or ""])


def palette_table(palette):
    head = "| Token | Normal | Protanopia | Deuteranopia | Tritanopia |\n|---|---|---|---|---|\n"
    return head + "\n".join(
        f"| `{k}` | {v} | " + " | ".join(colour.simulate(v, s) for s in colour.CVD_KINDS) + " |"
        for k, v in palette.items())


def main():
    r = Report("check-cvd", "Colour-blind simulation report",
               "Protanopia, deuteranopia and tritanopia simulated for every palette (Machado 2009, severity 1.0). "
               "Distances are OKLab dE x100. Meaning is never carried by colour alone (Section 21): pairs in the "
               "6-8 floor band are legal only with the declared secondary cue.")
    res = tk.resolve_all(tk.load())
    rows, sim_data = [], {}

    brand = res["brand"]
    bpal = {k: v["$value"] for k, v in brand["color"].items() if v.get("$type") == "color"}
    for d in brand["contrast"]["distinguish"]:
        grade(r, f"brand: {name_of(bpal, d['a'])} vs {name_of(bpal, d['b'])} ({d['why']})", d["a"], d["b"],
              d.get("secondaryCue"), rows)
    sim_data["brand"] = {k: {"normal": v, **{s: colour.simulate(v, s) for s in colour.CVD_KINDS}} for k, v in bpal.items()}
    r.section("Brand palette under simulation", palette_table(bpal))

    for pid, p in tk.personas(res):
        pal = tk.palette(p)
        for d in p["contrast"]["distinguish"]:
            grade(r, f"{pid}: {name_of(pal, d['a'])} vs {name_of(pal, d['b'])} ({d['why']})", d["a"], d["b"],
                  d.get("secondaryCue"), rows)
        for kind in colour.CVD_KINDS:
            closest = min(itertools.combinations(pal, 2), key=lambda ab: colour.delta_e(pal[ab[0]], pal[ab[1]], kind))
            dist = colour.delta_e(pal[closest[0]], pal[closest[1]], kind)
            r.add("INFO", f"{pid}: closest pair under {kind}", f"{closest[0]} vs {closest[1]} dE {dist:.1f} "
                  "(not a declared meaning pair)" if not any({name_of(pal, d['a']), name_of(pal, d['b'])} == set(closest)
                                                            for d in p["contrast"]["distinguish"]) else
                  f"{closest[0]} vs {closest[1]} dE {dist:.1f} (declared pair, graded above)")
        sim_data[pid] = {k: {"normal": v, **{s: colour.simulate(v, s) for s in colour.CVD_KINDS}} for k, v in pal.items()}
        r.section(f"{p['name']} palette under simulation", palette_table(pal))

    keys = {pid: tk.roles(p)["key"] for pid, p in tk.personas(res)}
    for a, b in itertools.combinations(keys, 2):
        grade(r, f"key colours: {a} vs {b}", keys[a], keys[b], KEY_CUE, rows)

    r.section("Graded pairs", "| Pair | Normal dE | Protan dE | Deutan dE | Tritan dE | Result | Secondary cue |\n"
              "|---|---|---|---|---|---|---|\n" + "\n".join("| " + " | ".join(row) + " |" for row in rows))
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(tk.dumps({"$description": "GENERATED by tools/check-cvd.py. Machado 2009 severity 1.0 simulations "
                                  "of every token colour, for the Gate 6 colour-blind proofs.", "palettes": sim_data}) + "\n",
                        encoding="utf-8", newline="\n")
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

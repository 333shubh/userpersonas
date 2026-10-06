"""Token schema + semantic check for system/tokens/tokens.json.

    python tools/check-tokens.py

1. Structure: JSON Schema (system/tokens/tokens.schema.json).
2. References: every {alias} resolves, no cycles.
3. Brief fidelity: values the brief fixes (Sections 3, 5, 17, 18.3-18.12, 19, 20)
   are compared against the brief's own tables, read from brief/.
4. Motion and sound maths: 120 BPM / 24 fps grid, durations on the beat grid,
   easing token set, layer order, flash ceiling, chord coverage.
5. Persona design constraints (Section 18.12) as machine checks.
6. Generated files (persona token files, doc tables) are in sync.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import colour  # noqa: E402
import schema  # noqa: E402
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

SECTION_10_SLUGS = ["01-hostel-hungry", "02-maximalist-foodie", "03-practical-parent", "04-conscious-upgrader",
                    "05-midnight-recharger", "06-value-stocking-homemaker", "07-premium-flavor-explorer"]
EASING_NAMES = {"ease-in-soft", "ease-out-pop", "ease-settle", "ease-linear-steam"}
LAYER_ORDER = ["background", "environment", "body", "face", "limbs", "props", "noodles-steam", "foreground-type"]
BOUNCY, CALM = {"riot", "cram"}, {"sprig", "lull", "mise"}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("“", '"').replace("”", '"')).strip().lower().rstrip(".")


def check_structure(r, raw):
    errors = schema.validate(raw, json.loads(tk.SCHEMA.read_text(encoding="utf-8")))
    r.ok(not errors, "schema: tokens.json matches tokens.schema.json",
         "; ".join(errors[:8]) + (f" (+{len(errors) - 8} more)" if len(errors) > 8 else "") if errors else "0 errors")
    return not errors


def check_aliases(r, raw):
    bad = []
    count = 0
    for where, path in tk.iter_aliases(raw):
        count += 1
        try:
            tk.resolve(raw, "{" + path + "}")
        except tk.AliasError as e:
            bad.append(f"{where}: {e}")
    r.ok(not bad, "aliases: every {reference} resolves", "; ".join(bad) if bad else f"{count} aliases resolved")
    return not bad


def check_brief(r, res):
    by_persona = {p["persona"]: (pid, p) for pid, p in tk.personas(res)}

    def table(prefix, label, compare):
        rows = tk.brief_table(prefix)
        problems = []
        covered = {re.sub(r"^The ", "", row.get("Persona", "")) for row in rows}
        missing = sorted(set(by_persona) - covered)
        if missing:
            problems.append(f"brief table has no row for {missing}")
        for row in rows:
            name = re.sub(r"^The ", "", row.get("Persona", ""))
            if name not in by_persona:
                problems.append(f"brief persona '{name}' has no token entry")
                continue
            pid, p = by_persona[name]
            for field, expected, actual in compare(row, p):
                if norm(str(expected)) != norm(str(actual)):
                    problems.append(f"{pid}.{field}: brief '{expected}' vs tokens '{actual}'")
        r.ok(not problems, f"brief {label}", "; ".join(problems) if problems else f"{len(rows)} rows match")

    table("3.", "Section 3 jobs", lambda row, p: [("job", row["Primary Maggi job"], p["job"])])
    table("Non-overlap rule", "Section 3 primary motivations",
          lambda row, p: [("primaryMotivation", row["Primary motivation"], p["primaryMotivation"])])
    table("Mascot personality directions", "Section 5 mascot concepts", lambda row, p: [
        ("mascot.concept", row["Mascot idea"], p["mascot"]["concept"]),
        ("mascot.personality", row["Personality"], p["mascot"]["personality"])])
    table("17.", "Section 17 buyer/eater spine", lambda row, p: [
        ("spine.buyer", row["Buyer"], p["spine"]["buyer"]), ("spine.eater", row["Eater"], p["spine"]["eater"]),
        ("spine.socialUnit", row["Social unit"], p["spine"]["socialUnit"]),
        ("spine.rhythm", row["Purchase rhythm"], p["spine"]["rhythm"]),
        ("spine.gate", row["The gate they must pass"], p["spine"]["gate"])])
    table("18.3", "Section 18.3 sachet rule", lambda row, p: [("sachet", row["Relationship with the sachet"], p["sachet"])])
    table("18.5", "Section 18.5 day order", lambda row, p: [
        ("day.order", row["Order"], p["day"]["order"]), ("day.time", row["Local time"], p["day"]["time"]),
        ("day.light", row["Light and mood"], p["day"]["light"])])
    table("18.7", "Section 18.7 card stats", lambda row, p: [
        (f"stats.{s}", row[s.title()], p["stats"][s]) for s in ("heat", "speed", "comfort", "chaos", "value", "fancy", "wellness")])

    def sound(row, p):
        pitch = row["Pitch"].split(" ")[0]
        palette = [x.strip() for x in row["Sound palette"].split(",")]
        return [("sound.pitch", pitch, p["sound"]["pitch"]),
                ("sound.palette", ", ".join(palette), ", ".join(p["sound"]["palette"]))]
    table("18.8", "Section 18.8 sound signatures", sound)

    def pack(row, p):
        m = re.match(r"(\w+)(?:\s*\((.*)\))?", row["Feasibility"])
        return [("packMechanic.concept", row["Pack mechanic"], p["packMechanic"]["concept"]),
                ("packMechanic.feasibility", m.group(1), p["packMechanic"]["feasibility"]),
                ("packMechanic.note", m.group(2) or "", p["packMechanic"]["note"])]
    table("18.11", "Section 18.11 pack mechanics", pack)
    table("18.12", "Section 18.12 design constraints", lambda row, p: [
        ("constraint.rule", row["Design constraint"], p["constraint"]["rule"]), ("constraint.why", row["Why"], p["constraint"]["why"])])
    table("19.", "Section 19 working names", lambda row, p: [
        ("name", row["Working name"], p["name"]), ("nameIdea", row["Idea"], p["nameIdea"])])

    text = tk.brief_text()
    # 18.4 noodle thread sequence, in persona number order
    m = re.search(r"It transforms per panel: (.+?)\.\n", text)
    seq = [norm(x) for x in m.group(1).split("→")] if m else []
    ours = [norm(p["noodleThread"]) for _, p in sorted(tk.personas(res), key=lambda kv: kv[1]["number"])]
    r.ok(seq == ours, "brief Section 18.4 noodle-thread forms", f"brief {seq} vs tokens {ours}" if seq != ours else "7 forms match")
    # 20 tempo feel
    m = re.search(r"\*\*Persona tempo feel:\*\* (.+)", text)
    tempo = dict(re.findall(r"(\w+) \*([^*]+)\*", m.group(1))) if m else {}
    bad = [f"{p['name']}: brief '{tempo.get(p['name'])}' vs '{p['motion']['tempo']}'" for _, p in tk.personas(res)
           if norm(tempo.get(p["name"], "")) != norm(p["motion"]["tempo"])]
    r.ok(not bad, "brief Section 20 tempo feel", "; ".join(bad) if bad else "7 match")
    # 18.2 felt time: four are fixed by the brief, three are proposals
    fixed = {"Hostel": "cram", "Parent": "nest", "Recharger": "lull", "Premium": "mise"}
    m = re.search(r"Each persona owns a different felt two minutes: (.+?), and so on", text)
    claims = dict(re.findall(r"(\w+) \*([^*]+)\*", m.group(1))) if m else {}
    bad = [f"{pid}: '{claims.get(k)}'" for k, pid in fixed.items()
           if norm(claims.get(k, "")) != norm(res["persona"][pid]["feltTime"])]
    r.ok(not bad, "brief Section 18.2 felt time (Cram, Nest, Lull, Mise)", "; ".join(bad) if bad else "4 match")
    r.add("INFO", "felt time for Riot, Sprig, Stack", "Proposed in Gate 1 (brief says 'and so on'); needs approval")


def check_identity(r, res):
    ps = tk.personas(res)
    r.ok(len(ps) == 7, "seven personas present", ", ".join(pid for pid, _ in ps))
    r.ok([p["slug"] for _, p in ps] == SECTION_10_SLUGS, "slugs match Section 10 file names",
         ", ".join(p["slug"] for _, p in ps))
    r.ok(all(p["id"] == pid for pid, p in ps), "persona id equals its key")
    r.ok(all(p["slug"].startswith(p["number"] + "-") for _, p in ps), "slug starts with persona number")
    orders = sorted(p["day"]["order"] for _, p in ps)
    r.ok(orders == list(range(1, 8)), "day order is a permutation of 1-7", str(orders))
    motivations = [p["primaryMotivation"] for _, p in ps]
    r.ok(len(set(motivations)) == 7, "non-overlap rule: primary motivations unique")
    for pid, p in ps:
        syll = len(re.findall(r"[aeiouy]+", p["name"].lower()))
        r.ok(1 <= syll <= 2, f"{pid}: name is one or two syllables (Section 19)", f"{p['name']}: {syll}")
    fields = ("buyer", "eater", "socialUnit", "rhythm", "gate")
    weak = [f"{a}/{b}" for (a, pa), (b, pb) in ((x, y) for i, x in enumerate(ps) for y in ps[i + 1:])
            if sum(norm(pa["spine"][f]) != norm(pb["spine"][f]) for f in fields) < 2]
    r.ok(not weak, "every persona pair differs on >= 2 of the 5 spine fields (Section 17)", ", ".join(weak) or "21 pairs")
    ids = {pid for pid, _ in ps}
    pairs = res["rivalries"]["pairs"]
    in_pairs = {x for pr in pairs for x in (pr["a"], pr["b"])}
    r.ok(all(pr["a"] != pr["b"] for pr in pairs) and in_pairs <= ids, "rivalry pairs reference valid, distinct personas")
    r.ok(in_pairs == ids, "every persona has at least one rivalry", f"missing: {sorted(ids - in_pairs)}" if in_pairs != ids else "")
    for pid, p in ps:
        for slot in ("display", "text"):
            fam = p["type"][slot]["$value"]
            r.ok(fam[-1] in ("serif", "sans-serif", "monospace") and len(fam) >= 3,
                 f"{pid}: {slot} face has a legible fallback stack (Section 21)", f"{fam[0]} -> {fam[-1]}")


def check_motion(r, res):
    m = res["motion"]
    bpm = m["clock"]["bpm"]["$value"]
    fps = m["frame-rate"]["primary"]["$value"]
    beat, bar = tk.ms(m["clock"]["beat"]["$value"]), tk.ms(m["clock"]["bar"]["$value"])
    r.ok(bpm == 120 and fps == 24, "master clock 120 BPM, 24 fps (Section 20)", f"{bpm} BPM, {fps} fps")
    r.ok(beat == 60000 / bpm, "beat length = 60000 / BPM", f"{beat}ms")
    r.ok(bar == beat * m["clock"]["beats-per-bar"]["$value"] == 2000, "bar = 4 beats = 2 s", f"{bar}ms")
    r.ok(m["frame-rate"]["frames-per-beat"]["$value"] == fps * beat / 1000 == 12, "frames per beat = 12")
    r.ok(m["frame-rate"]["frames-per-bar"]["$value"] == fps * bar / 1000 == 48, "frames per bar = 48")
    for key, unit in (("idle-loop", bar), ("reaction-loop", bar), ("consumption-scene", bar),
                      ("sound-signature", bar), ("micro-animation", beat)):
        vals = m["duration"][key]["$value"]
        vals = vals if isinstance(vals, list) else [vals]
        ok = all(tk.ms(v) % unit == 0 for v in vals)
        r.ok(ok, f"duration {key} is a whole multiple of {'a bar' if unit == bar else 'a beat'}", ", ".join(vals))
    r.ok(tk.ms(m["duration"]["consumption-scene"]["$value"]) == 4 * bar, "consumption scene = 4 bars (8 s)")
    frame = 1000 / fps
    for key, tok in m["ui"].items():
        if key.startswith("$"):
            continue
        v = tk.ms(tok["$value"])
        r.ok(abs(v / frame - round(v / frame)) < 0.05, f"ui.{key} lands on the 24 fps frame grid", f"{v}ms = {v / frame:.2f} frames")
    r.ok(set(m["easing"]) == EASING_NAMES, "easing token names are exactly the four shared tokens", ", ".join(sorted(m["easing"])))
    e = {k: v["$value"] for k, v in m["easing"].items()}
    r.ok(e["ease-out-pop"][1] > 1 or e["ease-out-pop"][3] > 1, "ease-out-pop overshoots (y > 1)", str(e["ease-out-pop"]))
    r.ok(e["ease-linear-steam"] == [0, 0, 1, 1], "ease-linear-steam is linear", str(e["ease-linear-steam"]))
    r.ok(all(0 <= v[0] <= 1 and 0 <= v[2] <= 1 for v in e.values()), "easing x control points within [0,1] (valid cubic-bezier)")
    r.ok(m["layer-order"]["$value"] == LAYER_ORDER, "layer order matches Section 20", " > ".join(m["layer-order"]["$value"]))
    ceiling = m["safety"]["max-flashes-per-second"]["$value"]
    r.ok(ceiling == 3, "flash ceiling is 3 per second (Section 20)")
    idle_ms = {tk.ms(v) for v in m["duration"]["idle-loop"]["$value"]}
    for pid, p in tk.personas(res):
        mo = p["motion"]
        r.ok(mo["pulseHz"] < ceiling, f"{pid}: pulse rate below flash ceiling", f"{mo['pulseHz']} Hz < {ceiling}")
        r.ok(mo["idleBars"] * bar in idle_ms, f"{pid}: idle loop length is an allowed idle duration", f"{mo['idleBars'] * bar}ms")
        if pid in BOUNCY:
            r.ok(mo["squashStretch"] > 0 and mo["overshootPct"] > 0, f"{pid}: bouncy persona uses squash/stretch + overshoot (Section 20)")
        if pid in CALM:
            r.ok(mo["squashStretch"] == 0 and mo["overshootPct"] == 0, f"{pid}: calm persona shows restraint, no squash or overshoot (Section 20)")
        r.ok(all(1 <= b < 5 for b in mo["accentBeats"]), f"{pid}: accent beats fall inside the 4-beat bar", str(mo["accentBeats"]))


def note_index(n):
    return re.fullmatch(r"([A-G]#?)(\d)", n).groups()


def check_sound(r, res):
    chord = res["sound"]["chord"]["$value"]
    r.ok(chord == ["C2", "G2", "E3", "B3", "D4", "A4", "F#4"], "chord is the C lydian stack (Section 18.8)", " ".join(chord))
    pitches = [p["sound"]["pitch"] for _, p in tk.personas(res)]
    r.ok(sorted(pitches) == sorted(chord), "each chord tone is owned by exactly one mascot", ", ".join(pitches))
    r.ok(res["persona"]["riot"]["sound"]["pitch"] == "F#4", "Riot owns the spicy #11 (F#4)")
    asmr = [pid for pid, p in tk.personas(res) if p["sound"]["asmr"]]
    r.ok(asmr == ["lull"], "ASMR layer is used by Lull only (Section 18.8)", ", ".join(asmr) or "none")


def check_constraints(r, res):
    P = res["persona"]
    # Cram: strict black and white, one ink
    pal = tk.palette(P["cram"])
    bad = [k for k, v in pal.items() if not colour.is_achromatic(v)]
    r.ok(not bad, "cram: every colour is achromatic (strict B&W)", f"non-neutral: {bad}" if bad else f"{len(pal)} neutrals")
    roles = tk.roles(P["cram"])
    r.ok(all(colour.is_achromatic(v) for v in roles.values()), "cram: sachet and every role render in one ink",
         f"sachet-red {roles['sachet-red']}, sachet-yellow {roles['sachet-yellow']}")
    # Riot: controlled clash
    rp = set(tk.palette(P["riot"]).values())
    clash = P["riot"]["constraint"]["checks"]["clashPairs"]
    r.ok(all(a in rp and b in rp and a != b for a, b in clash), "riot: clash pairs use palette colours",
         "; ".join(f"{a}x{b}" for a, b in clash))
    used = [c for pair in clash for c in pair]
    r.ok(len(used) == len(set(used)), "riot: each colour belongs to at most one clash pair (grammar is unambiguous)")
    # Nest: no sharp corners, large touch targets
    radii = [tk.px(v) for v in P["nest"]["shape"]["radius"]["$value"]]
    minr = tk.px(P["nest"]["constraint"]["checks"]["minRadius"])
    r.ok(min(radii) >= minr, "nest: no sharp corners (every radius >= minRadius)", f"radii {radii}, min {minr}")
    target = tk.px(P["nest"]["constraint"]["checks"]["minTouchTarget"])
    r.ok(target >= tk.px(res["brand"]["touch-target"]["$value"]), "nest: touch target >= brand touch target",
         f"{target}px >= {res['brand']['touch-target']['$value']}")
    r.ok(P["nest"]["shape"]["cap"]["$value"] == "round", "nest: round caps only")
    # Sprig: low-ink, muted
    cap = P["sprig"]["constraint"]["checks"]["maxSaturation"]
    sat = {k: round(colour.hsv_saturation(v), 2) for k, v in tk.palette(P["sprig"]).items()}
    bad = {k: s for k, s in sat.items() if s > cap}
    r.ok(not bad, f"sprig: every colour HSV saturation <= {cap} (muted, low-ink)", f"over: {bad}" if bad else f"max {max(sat.values())}")
    cov = P["sprig"]["texture"]["ink-coverage-max"]["$value"]
    r.ok(0 < cov <= 0.6, "sprig: ink coverage capped at <= 60%", str(cov))
    # Lull: luminance cap, no pure white, dark backgrounds
    lcap = P["lull"]["constraint"]["checks"]["maxLuminance"]
    lum = {k: round(colour.luminance(v), 3) for k, v in tk.palette(P["lull"]).items()}
    bad = {k: v for k, v in lum.items() if v > lcap}
    r.ok(not bad, f"lull: no colour above relative luminance {lcap} (no pure white)", f"over: {bad}" if bad else f"max {max(lum.values())}")
    bgmax = P["lull"]["constraint"]["checks"]["maxBackgroundLuminance"]
    bgs = {c: round(colour.luminance(c), 4) for c in P["lull"]["backgrounds"]}
    r.ok(all(v <= bgmax for v in bgs.values()), f"lull: backgrounds at or below luminance {bgmax}", str(bgs))
    # Stack: strict grid
    step = tk.px(P["stack"]["constraint"]["checks"]["spacingMultipleOf"])
    spacing = [tk.px(v) for v in P["stack"]["spacing"]["$value"]]
    r.ok(all(v % step == 0 for v in spacing), f"stack: spacing on the {step:g}px grid", str(spacing))
    rmax = tk.px(P["stack"]["constraint"]["checks"]["radiusMax"])
    r.ok(all(tk.px(v) <= rmax for v in P["stack"]["shape"]["radius"]["$value"]), f"stack: radius <= {rmax:g}px (price-tag logic)")
    r.ok(tk.px(P["stack"]["iconography"]["grid"]["$value"]) % step == 0, "stack: icon grid is a multiple of the 8px grid")
    # Mise: duotone + one foil
    chk = P["mise"]["constraint"]["checks"]
    dark, light = chk["duotone"]
    foil, tol = chk["foil"], chk["tintTolerance"]
    bad = []
    for k, v in tk.palette(P["mise"]).items():
        if v in (dark, light, foil):
            continue
        best = min(range(101), key=lambda i: colour.srgb_distance(colour.mix(dark, light, i / 100), v))
        if colour.srgb_distance(colour.mix(dark, light, best / 100), v) > tol:
            bad.append(k)
    r.ok(not bad, "mise: every colour is a duotone tint or the single foil", f"off-system: {bad}" if bad else "duotone + foil only")
    others = [k for k, v in tk.palette(P["mise"]).items() if v not in (dark, light) and not
              any(colour.srgb_distance(colour.mix(dark, light, i / 100), v) <= tol for i in range(101))]
    r.ok(others == ["foil"], "mise: exactly one non-duotone accent", str(others))
    r.ok(colour.contrast(foil, light) < 3 and P["mise"]["role"]["bg"]["$value"] == dark,
         "mise: foil is kept off cream (role.bg is the duotone dark)",
         f"foil on cream {colour.contrast(foil, light):.2f}:1, foil on oxblood {colour.contrast(foil, dark):.2f}:1")


def check_type_and_scale(r, res):
    floor = tk.px(res["brand"]["type"]["min-size"]["web-caption"]["$value"])
    base = tk.px(res["brand"]["type"]["base-size"]["$value"])
    r.ok(base >= tk.px(res["brand"]["type"]["min-size"]["web-body"]["$value"]), "base type size >= web body minimum", f"{base:g}px")
    spec = importlib.util.spec_from_file_location("build_tokens", Path(__file__).parent / "build-tokens.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    for pid, p in tk.personas(res):
        smallest = round(base * p["type"]["scale-ratio"]["$value"] ** min(build.TYPE_STEPS.values()))
        r.add("PASS" if smallest >= floor else "INFO", f"{pid}: caption step vs {floor:g}px minimum",
              f"{smallest}px" + ("" if smallest >= floor else f" -> clamped to {floor:g}px in generated tokens"))
        r.ok(p["type"]["line-height"]["text"]["$value"] >= 1.5, f"{pid}: text line-height >= 1.5 (WCAG 1.4.12)",
             str(p["type"]["line-height"]["text"]["$value"]))
    return build


def check_generated(r, build):
    stale, stray = build.stale_outputs()
    r.ok(not stale and not stray, "generated files in sync with tokens.json (run tools/build-tokens.py)",
         "; ".join(p.relative_to(tk.ROOT).as_posix() for p in stale + stray) or "7 persona files + doc tables up to date")


def main():
    r = Report("check-tokens", "Token schema and semantic check",
               "Validates `system/tokens/tokens.json` against its schema, the brief, the motion grid and each persona's design constraint.")
    raw = tk.load()
    structure_ok = check_structure(r, raw)
    if check_aliases(r, raw) and structure_ok:
        res = tk.resolve_all(raw)
        check_identity(r, res)
        check_brief(r, res)
        check_motion(r, res)
        check_sound(r, res)
        check_constraints(r, res)
        build = check_type_and_scale(r, res)
        check_generated(r, build)
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

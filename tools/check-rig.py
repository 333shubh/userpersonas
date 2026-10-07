"""Rig spec check: system/rig-spec.json consistency, and SVG exports against it.

    python tools/check-rig.py

Now (Gate 1): the spec agrees with tokens.json (layer order, mascots, signature
props, heights), every required id matches the id grammar, and expressions use
real states. Writes system/rig-manifest.json: the exact id list per mascot.
Later (Gate 2+): every static/*/NN-<mascot>-rig-<view>.svg is parsed and checked
for slot order, required ids and states, anchors, and forbidden SVG features.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

SPEC = tk.ROOT / "system" / "rig-spec.json"
MANIFEST = tk.ROOT / "system" / "rig-manifest.json"
SVG_NS = "{http://www.w3.org/2000/svg}"
FORBIDDEN = {"script", "foreignObject", "image"}
TRANSLATE_ONLY = re.compile(r"^\s*translate\(\s*-?[\d.]+(?:[\s,]+-?[\d.]+)?\s*\)\s*$")


def required_ids(spec, mascot):
    """Every id a mascot's rig must contain, with the states each part needs."""
    ids = {}
    for slot in spec["slots"]["order"]:
        if slot not in spec["slots"]["optional"]:
            ids[f"{mascot}__{slot}"] = []
    for slot, parts in spec["requiredParts"].items():
        if slot.startswith("$"):
            continue
        for part, states in parts.items():
            ids[f"{mascot}__{slot}__{part}"] = states
    for rel, states in spec["personaParts"][mascot].items():
        ids[f"{mascot}__{rel}"] = states
    for anchor in spec["anchors"]["list"]:
        ids[f"{mascot}__rig__{anchor}"] = []
    return ids


def expand_states(ids):
    out = []
    for i, states in ids.items():
        out.append(i)
        out += [f"{i}--{s}" for s in states]
    return out


def check_spec(r, spec, res):
    rx = re.compile(spec["id"]["regex"])
    layer = res["motion"]["layer-order"]["$value"]
    slots = [s for s in spec["slots"]["order"] if s not in ("limbs-back", "rig")]
    r.ok(slots == layer, "slot order matches tokens motion.layer-order", " > ".join(slots))
    r.ok(spec["slots"]["order"][-1] == "rig", "rig slot is last")
    pids = [pid for pid, _ in tk.personas(res)]
    r.ok(sorted(k for k in spec["personaParts"] if not k.startswith("$")) == sorted(pids) and sorted(k for k in spec["construction"] if not k.startswith("$")) == sorted(pids),
         "rig covers all seven mascots", ", ".join(pids))
    cv = spec["canvas"]
    r.ok(spec["anchors"]["list"]["root"]["fixed"] == [cv["centreX"], cv["groundY"]], "root anchor sits at (centreX, groundY)",
         str(spec["anchors"]["list"]["root"]["fixed"]))
    manifest = {}
    for pid, p in tk.personas(res):
        ids = expand_states(required_ids(spec, pid))
        bad = [i for i in ids if not rx.match(i)]
        r.ok(not bad, f"{pid}: all {len(ids)} required ids match the id grammar", "; ".join(bad[:5]))
        r.ok(len(ids) == len(set(ids)), f"{pid}: required ids are unique")
        parts = {rel.split("__")[1] if "__" in rel else rel for rel in spec["personaParts"][pid]}
        missing = [sp for sp in p["mascot"]["signatureProps"] if sp not in parts]
        r.ok(not missing, f"{pid}: every token signature prop has a rig part", f"missing {missing}" if missing else ", ".join(sorted(parts)))
        con = spec["construction"][pid]
        target = round(p["mascot"]["heightRatio"] * cv["heightBasis"])
        r.ok(abs(con["height"] - target) <= 1, f"{pid}: construction height = heightRatio x {cv['heightBasis']}",
             f"{con['height']} vs {target}")
        box_w = cv["safeBox"][2] - cv["safeBox"][0]
        r.ok(con["width"] <= box_w and con["height"] <= cv["heightBasis"], f"{pid}: construction fits the safe box",
             f"{con['width']} x {con['height']} within {box_w} x {cv['heightBasis']}")
        manifest[pid] = ids
    states = {k: v for slot in ("face",) for k, v in spec["requiredParts"][slot].items()}
    for name, (lid, brow, mouth) in ((k, v) for k, v in spec["expressions"].items() if not k.startswith("$")):
        ok = lid in states["lid-l"] and brow in states["brow-l"] and mouth in states["mouth"]
        r.ok(ok, f"expression '{name}' uses defined states", f"{lid} / {brow} / {mouth}")
    heights = {pid: spec["construction"][pid]["height"] for pid in pids}
    widths = {pid: spec["construction"][pid]["width"] for pid in pids}
    aspect = {pid: round(widths[pid] / heights[pid], 2) for pid in pids}
    close = [f"{a}/{b}" for i, a in enumerate(pids) for b in pids[i + 1:]
             if abs(aspect[a] - aspect[b]) < 0.03 and abs(heights[a] - heights[b]) < 40]
    r.add("PASS" if not close else "WARN", "silhouette pre-check: no two mascots share both height and aspect",
          f"aspects {aspect}" + (f"; too close: {close}" if close else ""))
    return manifest


def check_svg(r, spec, path, mascot, manifest):
    rel = path.relative_to(tk.ROOT).as_posix()
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        r.add("FAIL", f"{rel}: parses", str(e))
        return
    r.ok(root.get("viewBox", "").split() == [str(v) for v in spec["canvas"]["viewBox"]], f"{rel}: viewBox 0 0 1024 1024", root.get("viewBox"))
    top = [el.get("id") for el in root if el.tag == SVG_NS + "g"]
    expected = [f"{mascot}__{s}" for s in spec["slots"]["order"]]
    required = [f"{mascot}__{s}" for s in spec["slots"]["order"] if s not in spec["slots"]["optional"]]
    r.ok([t for t in top if t in expected] == [e for e in expected if e in top] and set(top) <= set(expected)
         and all(q in top for q in required),
         f"{rel}: slots are direct children of <svg>, in spec order", " > ".join(map(str, top)))
    nested = sorted({el.get("id") for el in root.iter() if el.get("id") in expected} - set(top))
    r.ok(not nested, f"{rel}: no slot group nested below the top level", ", ".join(nested))
    present = {el.get("id") for el in root.iter() if el.get("id")}
    missing = [i for i in manifest[mascot] if i not in present]
    r.ok(not missing, f"{rel}: all required ids present", f"{len(missing)} missing, e.g. {missing[:6]}" if missing else f"{len(manifest[mascot])} ids")
    rx = re.compile(spec["id"]["regex"])
    stray = sorted(i for i in present if not rx.match(i))
    r.ok(not stray, f"{rel}: every id follows the grammar", ", ".join(stray[:6]))
    pack = {id(d) for g in root.iter() if (g.get("id") or "").endswith("__props__pack") for d in g.iter()}
    bad_tags = sorted({el.tag.replace(SVG_NS, "") for el in root.iter() if id(el) not in pack} & (FORBIDDEN | {"text"}))
    r.ok(not bad_tags, f"{rel}: no script/image/foreignObject/text (lettering is outlined)", ", ".join(bad_tags))
    slot_el = next((el for el in root.iter() if (el.get("id") or "").endswith("__lockup-slot")), None)
    if slot_el is not None:
        r.ok(slot_el.tag == SVG_NS + "rect" and len(slot_el) == 0, f"{rel}: lockup slot is an empty <rect>",
             slot_el.tag.replace(SVG_NS, ""))
    bad_tf = [el.get("id") or el.tag for el in root.iter(SVG_NS + "g") if el.get("transform") and not TRANSLATE_ONLY.match(el.get("transform"))]
    r.ok(not bad_tf, f"{rel}: groups use translate() only", ", ".join(map(str, bad_tf[:6])))
    for el in root.iter(SVG_NS + "circle"):
        if (el.get("id") or "").startswith(f"{mascot}__rig__") and el.get("r") not in ("0", "0.0"):
            r.add("FAIL", f"{rel}: anchor {el.get('id')} has r=0", f"r={el.get('r')}")
    root_anchor = next((el for el in root.iter(SVG_NS + "circle") if el.get("id") == f"{mascot}__rig__root"), None)
    if root_anchor is not None:
        r.ok([float(root_anchor.get("cx")), float(root_anchor.get("cy"))] == [float(v) for v in spec["anchors"]["list"]["root"]["fixed"]],
             f"{rel}: root anchor at (512, 896)")


def main():
    r = Report("check-rig", "Rig spec check",
               "Checks `system/rig-spec.json` against `tokens.json`, and any mascot SVG exports against the spec.")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    res = tk.resolve_all(tk.load())
    manifest = check_spec(r, spec, res)
    MANIFEST.write_text(tk.dumps({"$description": "GENERATED by tools/check-rig.py from system/rig-spec.json. "
                                  "Exact ids (including --state variants) each mascot rig SVG must contain.",
                                  "mascots": manifest}) + "\n", encoding="utf-8", newline="\n")
    names = {p["number"]: pid for pid, p in tk.personas(res)}
    exports = sorted(tk.ROOT.glob("static/*/*-rig-*.svg"))
    if not exports:
        r.add("INFO", "SVG exports", "0 rig SVGs in static/ yet (artwork starts at Gate 2); export checks will run automatically")
    for path in exports:
        m = re.match(r"(\d\d)-([a-z]+)-rig-(front|three-quarter|side)\.svg$", path.name)
        if not m or names.get(m.group(1)) != m.group(2) or path.parent.name != res["persona"][m.group(2)]["slug"]:
            r.add("FAIL", f"{path.relative_to(tk.ROOT).as_posix()}: rig file name",
                  "expected static/<slug>/NN-<mascot>-rig-<front|three-quarter|side>.svg with NN, mascot and slug agreeing")
            continue
        check_svg(r, spec, path, m.group(2), manifest)
    r.section("Required id counts", "\n".join(f"- **{pid}**: {len(ids)} ids" for pid, ids in manifest.items())
              + "\n\nFull lists: `system/rig-manifest.json`.")
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

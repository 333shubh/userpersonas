"""Numeric WCAG 2.2 contrast check for every palette in system/tokens/tokens.json.

    python tools/check-contrast.py

Checks, per persona (and the shared brand set):
  - every declared pair in <scope>.contrast.pairs at the scope's level
    (AA everywhere, AAA for Cram, Section 21);
  - automatic semantic-role pairs, so no role combination is left unchecked:
      text / bg, text / surface, text-muted / bg      -> body
      accent / bg                                      -> large text
      focus / bg, focus / surface, line / bg           -> non-text 3:1 (1.4.11, 2.4.11)
  - informational: each persona key colour against the shared brand paper.

Thresholds: body 4.5 (AAA 7), large 3 (AAA 4.5), ui 3. "Large" = at least 24px
regular or 18.66px bold. Ratios use WCAG relative luminance on sRGB hex.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import colour  # noqa: E402
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

ROLE_PAIRS = [
    ("text", "bg", "body"), ("text", "surface", "body"), ("text-muted", "bg", "body"),
    ("accent", "bg", "large"),
    ("focus", "bg", "ui"), ("focus", "surface", "ui"), ("line", "bg", "ui"),
]


def name_of(palette, hexv):
    for k, v in palette.items():
        if v.upper() == hexv.upper():
            return k
    return hexv


def run_scope(r, label, level, pairs, palette, rows):
    need = colour.WCAG[level]
    for fg, bg, use, where, source in pairs:
        ratio = colour.contrast(fg, bg)
        worst_cvd = min(colour.contrast(colour.simulate(fg, k), colour.simulate(bg, k)) for k in colour.CVD_KINDS)
        ok = ratio >= need[use]
        r.add("PASS" if ok else "FAIL", f"{label}: {name_of(palette, fg)} on {name_of(palette, bg)} ({use}, {source})",
              f"{ratio:.2f}:1 needs {need[use]}:1 {level}")
        rows.append([label, f"`{name_of(palette, fg)}` {fg}", f"`{name_of(palette, bg)}` {bg}", use, source,
                     f"{ratio:.2f}", f"{need[use]}", level, "pass" if ok else "**FAIL**", f"{worst_cvd:.2f}", where])


def main():
    r = Report("check-contrast", "WCAG contrast check",
               "Numeric WCAG 2.2 contrast for every declared pair and every semantic-role pair. "
               "AA minimum everywhere; Cram (strict black and white) is held to AAA. "
               "The `worst under CVD` column is the lowest ratio after protan/deutan/tritan simulation (informational).")
    res = tk.resolve_all(tk.load())
    rows = []

    brand = res["brand"]
    bpal = {k: v["$value"] for k, v in brand["color"].items() if v.get("$type") == "color"}
    run_scope(r, "brand", brand["contrast"]["level"],
              [(p["fg"], p["bg"], p["use"], p["where"], "declared") for p in brand["contrast"]["pairs"]], bpal, rows)

    for pid, p in tk.personas(res):
        level = p["contrast"]["level"]
        pal = tk.palette(p)
        roles = tk.roles(p)
        declared = [(x["fg"], x["bg"], x["use"], x["where"], "declared") for x in p["contrast"]["pairs"]]
        seen = {(f.upper(), b.upper(), u) for f, b, u, _, _ in declared}
        auto = []
        for fg_role, bg_role, use in ROLE_PAIRS:
            fg, bg = roles[fg_role], roles[bg_role]
            if (fg.upper(), bg.upper(), use) not in seen:
                auto.append((fg, bg, use, f"role.{fg_role} on role.{bg_role}", "role"))
        run_scope(r, pid, level, declared + auto, pal, rows)
        if level != ("AAA" if pid == "cram" else "AA"):
            r.add("FAIL", f"{pid}: target level", f"expected {'AAA' if pid == 'cram' else 'AA'}, tokens say {level}")
        key = roles["key"]
        ratio = colour.contrast(key, bpal["paper"])
        r.add("INFO", f"{pid}: key colour on brand paper", f"{ratio:.2f}:1. Keys always ship with mascot + name label, "
              "so identity never rests on this contrast (dataviz relief rule).")

    r.section("All pairs", "| Scope | Foreground | Background | Use | Source | Ratio | Needs | Level | Result | Worst under CVD | Where |\n"
              "|---|---|---|---|---|---|---|---|---|---|---|\n" +
              "\n".join("| " + " | ".join(row) + " |" for row in rows))
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

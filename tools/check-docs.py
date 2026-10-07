"""Persona Markdown check (brief Sections 4, 22, 26, 27).

    python tools/check-docs.py

For each of the seven markdown/NN-slug.md files:
  - present, with the 26 numbered sections of brief Section 4 in order ("## 1." ... "## 26.")
  - all generated brand-kit blocks present (kit, spine, motion, stats, sound, pack, rivals);
    their contents are verified by tools/build-tokens.py --check (run by check-tokens.py)
  - sample reviews are labelled as synthesised composites, with one positive, one critical, one balanced
  - "Evidence used": every row quotes a finding from the brief's Section 27 evidence log verbatim,
    with the same confidence tag (market claims come only from the log)
  - no health or nutrition claims (brief Section 22); lines that explicitly discuss the rule are allowed
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

BLOCKS = ("toy", "kit", "spine", "motion", "stats", "sound", "pack", "rivals")
HEALTH = re.compile(r"\b(healthy|healthier|nutritious|guilt[- ]free|low[- ]sodium|high[- ]protein|high[- ]fibre|"
                    r"source of (fibre|iron|protein)|goodness of iron|weight[- ]loss|superfood|wholesome)\b", re.I)
RULE_CONTEXT = re.compile(r"claim|needs nestl|section 22|illegible|guardrail", re.I)


def evidence_log():
    rows = tk.brief_table("27.")
    return {re.sub(r"\s+", " ", r["Finding"]).strip(): r["Confidence"] for r in rows}


def main():
    r = Report("check-docs", "Persona Markdown check",
               "Each persona file against brief Section 4 (26 items), Section 22 (guardrails) and Section 27 (evidence log).")
    res = tk.resolve_all(tk.load())
    log = evidence_log()
    for pid, p in tk.personas(res):
        path = tk.ROOT / "markdown" / f"{p['slug']}.md"
        rel = path.relative_to(tk.ROOT).as_posix()
        if not path.exists():
            r.add("FAIL", f"{rel}: present", "not written yet")
            continue
        text = path.read_text(encoding="utf-8")
        nums = [int(n) for n in re.findall(r"^## (\d+)\. ", text, re.M)]
        r.ok(nums == list(range(1, 27)), f"{p['name']}: all 26 Section 4 items, in order",
             f"found {nums}" if nums != list(range(1, 27)) else "26 sections")
        missing = [b for b in BLOCKS if f"<!-- generated:{b}:start -->" not in text]
        r.ok(not missing, f"{p['name']}: generated brand-kit blocks present", ", ".join(missing))
        reviews = re.search(r"^## 13\..*?(?=^## 14\.)", text, re.M | re.S)
        rv = reviews.group(0) if reviews else ""
        r.ok(bool(re.search(r"synthesi[sz]ed composite", rv, re.I)), f"{p['name']}: reviews labelled as synthesised composites")
        r.ok(all(re.search(k, rv, re.I) for k in (r"\bpositive\b", r"\bcritical\b", r"\bbalanced\b")),
             f"{p['name']}: one positive, one critical, one balanced review")
        ev = re.search(r"^## Evidence used.*?(?=^## |\Z)", text, re.M | re.S)
        rows = re.findall(r"^\| (.+?) \| (High|Medium|Low[^|]*|Medium–High) \|", ev.group(0), re.M) if ev else []
        bad = []
        for finding, conf in rows:
            f = re.sub(r"\s+", " ", finding).strip()
            if f not in log:
                bad.append(f"not in evidence log: {f[:50]}")
            elif log[f].split(" (")[0] != conf.strip().split(" (")[0]:
                bad.append(f"tag mismatch: {f[:40]} ({conf} vs {log[f]})")
        r.ok(ev is not None and rows and not bad, f"{p['name']}: evidence rows quote the Section 27 log with matching tags",
             "; ".join(bad) or f"{len(rows)} findings")
        hits = [ln.strip()[:70] for ln in text.splitlines() if HEALTH.search(ln) and not RULE_CONTEXT.search(ln)]
        r.ok(not hits, f"{p['name']}: no health or nutrition claims", " | ".join(hits[:3]))
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

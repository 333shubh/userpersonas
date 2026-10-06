"""File-naming and folder-structure check against system/naming-rules.md.

    python tools/check-names.py

Reads the ```json naming-rules block in system/naming-rules.md (the machine
source of the rules) and walks the repository.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
import tokens as tk  # noqa: E402
from report import Report  # noqa: E402

RULES_MD = tk.ROOT / "system" / "naming-rules.md"
RIG_SPEC = tk.ROOT / "system" / "rig-spec.json"
SIZE = r"(-\d+x\d+)?"


def load_rules():
    m = re.search(r"```json naming-rules\n(.*?)\n```", RULES_MD.read_text(encoding="utf-8"), re.S)
    if not m:
        raise SystemExit("naming-rules block not found in system/naming-rules.md")
    return json.loads(m.group(1))


def split_ext(name, rules):
    for comp in rules["compoundExtensions"]:
        if name.endswith("." + comp):
            return name[: -len(comp) - 1], comp
    stem, dot, ext = name.rpartition(".")
    return (stem, ext) if dot else (name, "")


def qualifier_re(rules):
    words = list(rules["qualifiers"])
    if rules.get("qualifiersFromRigExpressions"):
        spec = json.loads(RIG_SPEC.read_text(encoding="utf-8"))
        words += [k for k in spec["expressions"] if not k.startswith("$")]
    alt = "|".join(sorted(map(re.escape, set(words)), key=len, reverse=True))
    return f"(-(?:{alt}))*"


def main():
    r = Report("check-names", "File-naming and folder-structure check",
               "Every path in the repository checked against `system/naming-rules.md` (section 7 is the machine source).")
    rules = load_rules()
    seg = re.compile(rules["segment"])
    quals = qualifier_re(rules)
    personas = rules["personas"]
    checked = 0

    for folder in rules["requiredFolders"]:
        r.ok((tk.ROOT / folder).is_dir(), f"folder exists: {folder}/")
    for parent in rules["personaFolders"]:
        for slug in personas:
            r.ok((tk.ROOT / parent / slug).is_dir(), f"persona folder exists: {parent}/{slug}/")
    for parent, subs in rules["fixedSubfolders"].items():
        for sub in subs:
            r.ok((tk.ROOT / parent / sub).is_dir(), f"fixed folder exists: {parent}/{sub}/")

    for path in sorted(tk.ROOT.rglob("*")):
        rel = path.relative_to(tk.ROOT)
        parts = rel.parts
        if any(p in rules["ignoreDirs"] for p in parts):
            continue
        name = path.name
        relp = rel.as_posix()
        if path.is_dir():
            if not seg.match(name):
                r.add("FAIL", f"folder name: {relp}/", "must be lowercase kebab-case")
            elif parts[0] in rules["personaFolders"] and len(parts) == 2 and name not in personas:
                r.add("FAIL", f"persona folder: {relp}/", f"must be one of {list(personas)}")
            elif parts[0] in rules["fixedSubfolders"] and len(parts) == 2 and name not in rules["fixedSubfolders"][parts[0]]:
                r.add("FAIL", f"folder: {relp}/", f"allowed: {rules['fixedSubfolders'][parts[0]]}")
            continue
        checked += 1
        if name in rules["exempt"]:
            continue
        stem, ext = split_ext(name, rules)
        problems = []
        if not name.isascii() or name != name.lower() or " " in name:
            problems.append("not lowercase ASCII without spaces")
        if ext not in rules["extensions"] and ext not in rules["compoundExtensions"]:
            problems.append(f"extension '.{ext}' not allowed")
        if not seg.match(stem):
            problems.append("stem is not kebab-case")
        top = parts[0] if len(parts) > 1 else ""
        if top in rules["reserved"] and len(parts) == 2 and name not in rules["reserved"][top]:
            problems.append(f"only {rules['reserved'][top]} allowed here")
        if top == "" and path.is_file() and name not in rules["reserved"][""]:
            problems.append("only reserved deliverables and exempt files may sit at the repo root")
        if top in rules["personaFolders"] and len(parts) == 3:
            slug = parts[1]
            mascot, num = personas.get(slug), slug[:2]
            vocab = "|".join(map(re.escape, rules["personaFolders"][top]))
            q = r"(-[a-z0-9]+(-[a-z0-9]+)*)?" if top in rules["freeQualifierFolders"] else quals
            pat = rf"^{num}-{mascot}-({vocab}){q}{SIZE}$"
            if not re.match(pat, stem):
                problems.append(f"expected {num}-{mascot}-<{'|'.join(rules['personaFolders'][top])}>[-qualifiers][-WxH]")
        if top == "sound" and len(parts) == 2 and not re.match(rules["soundFile"], name):
            problems.append("sound file pattern: NN-mascot-signature[-silent|-captions].ext, chord.ext or sound-spec.md")
        if problems:
            r.add("FAIL", f"file: {relp}", "; ".join(problems))
    r.add("INFO", "files scanned", str(checked))
    if not any(row[0] == "FAIL" and row[1].startswith(("file:", "folder name:", "persona folder:", "folder:")) for row in r.rows):
        r.add("PASS", "every file and folder name follows the rules", f"{checked} files")
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())

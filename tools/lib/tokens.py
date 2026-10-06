"""Load system/tokens/tokens.json, resolve {alias} references, and read the brief's tables.

Standard library only. Every validator goes through this module so the token file
is parsed one way only.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKENS = ROOT / "system" / "tokens" / "tokens.json"
SCHEMA = ROOT / "system" / "tokens" / "tokens.schema.json"
PERSONA_DIR = ROOT / "system" / "tokens" / "personas"
BRIEF = ROOT / "brief" / "maggi-persona-project-brief-v2.md"
QA_DIR = ROOT / "stress-tests" / "qa"

ALIAS_RE = re.compile(r"^\{([a-z0-9.\-]+)\}$")
PERSONA_ORDER = ("cram", "riot", "nest", "sprig", "lull", "stack", "mise")


def load(path=TOKENS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(value, indent=0, width=120):
    """JSON with short scalar arrays and small leaf objects kept on one line."""
    pad, inner = "  " * indent, "  " * (indent + 1)
    flat = json.dumps(value, ensure_ascii=False)
    is_leaf = (isinstance(value, list) and all(not isinstance(v, (dict, list)) for v in value)) or \
              (isinstance(value, dict) and all(not isinstance(v, (dict, list)) or
                                               (isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v))
                                               for v in value.values()))
    if not isinstance(value, (dict, list)) or (is_leaf and len(flat) + len(pad) <= width):
        return flat
    if isinstance(value, list):
        return "[\n" + ",\n".join(inner + dumps(v, indent + 1, width) for v in value) + "\n" + pad + "]"
    return "{\n" + ",\n".join(f"{inner}{json.dumps(k, ensure_ascii=False)}: {dumps(v, indent + 1, width)}"
                              for k, v in value.items()) + "\n" + pad + "}"


def get(tree, path):
    node = tree
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


class AliasError(ValueError):
    pass


def resolve(tree, value, _seen=()):
    """Resolve a value that may be an alias, a token object, or a list containing aliases."""
    if isinstance(value, str):
        m = ALIAS_RE.match(value)
        if not m:
            return value
        path = m.group(1)
        if path in _seen:
            raise AliasError(f"alias cycle: {' -> '.join(_seen + (path,))}")
        try:
            target = get(tree, path)
        except KeyError:
            raise AliasError(f"unresolved alias {{{path}}}") from None
        if isinstance(target, dict) and "$value" in target:
            target = target["$value"]
        return resolve(tree, target, _seen + (path,))
    if isinstance(value, list):
        out = []
        for item in value:
            r = resolve(tree, item, _seen)
            # a list alias inside a list (font fallback stacks) is spliced in
            if isinstance(item, str) and ALIAS_RE.match(item) and isinstance(r, list):
                out.extend(r)
            else:
                out.append(r)
        return out
    if isinstance(value, dict):
        return {k: resolve(tree, v, _seen) for k, v in value.items()}
    return value


def resolve_all(tree):
    return resolve(tree, tree)


def iter_aliases(node, path=""):
    """Yield (location, alias-path) for every alias string in the tree."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from iter_aliases(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_aliases(v, f"{path}[{i}]")
    elif isinstance(node, str):
        m = ALIAS_RE.match(node)
        if m:
            yield path, m.group(1)


def personas(resolved):
    return [(pid, resolved["persona"][pid]) for pid in PERSONA_ORDER if pid in resolved.get("persona", {})]


def palette(persona):
    """{name: hex} primitive colours of a resolved persona."""
    return {k: v["$value"] for k, v in persona["color"].items() if isinstance(v, dict)}


def roles(persona):
    """{role: hex} semantic colours of a resolved persona."""
    return {k: v["$value"] for k, v in persona["role"].items() if isinstance(v, dict)}


def px(value):
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)px", str(value))
    if not m:
        raise ValueError(f"not a px dimension: {value!r}")
    return float(m.group(1))


def ms(value):
    m = re.fullmatch(r"(\d+)ms", str(value))
    if not m:
        raise ValueError(f"not a ms duration: {value!r}")
    return int(m.group(1))


# --- brief tables -------------------------------------------------------------

def _clean(cell):
    return re.sub(r"\*\*|\*", "", cell).strip()


def brief_text():
    return BRIEF.read_text(encoding="utf-8")


def brief_table(heading_prefix, text=None):
    """First markdown table after the heading that starts with heading_prefix.

    Returns a list of row dicts keyed by the cleaned header cells.
    """
    text = text if text is not None else brief_text()
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.lstrip("#").strip().startswith(heading_prefix)
                  and l.startswith("#")), None)
    if start is None:
        raise KeyError(f"heading not found in brief: {heading_prefix}")
    rows, header = [], None
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        if not line.startswith("|"):
            if header:
                break
            continue
        cells = [_clean(c) for c in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif set("".join(cells)) <= set("-: "):
            continue
        else:
            rows.append(dict(zip(header, cells)))
    if not rows:
        raise KeyError(f"no table under heading: {heading_prefix}")
    return rows

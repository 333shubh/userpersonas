"""Minimal JSON Schema (2020-12 subset) validator, standard library only.

Supports exactly the keywords system/tokens/tokens.schema.json uses: type, enum,
const, pattern, minimum, maximum, minLength, required, minProperties, properties,
patternProperties, additionalProperties, items, minItems, maxItems, $ref (local).
Unknown keywords are rejected so the schema cannot silently outgrow this file.
"""

import re

SUPPORTED = {
    "$schema", "$id", "$defs", "$ref", "title", "description",
    "type", "enum", "const", "pattern", "minimum", "maximum", "minLength",
    "required", "properties", "patternProperties", "additionalProperties",
    "items", "minItems", "maxItems", "minProperties",
}

TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def validate(instance, schema, root=None, path="$"):
    """Return a list of 'path: message' errors."""
    root = root or schema
    errors = []

    unknown = set(schema) - SUPPORTED
    if unknown:
        return [f"{path}: schema uses unsupported keyword(s) {sorted(unknown)}"]

    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: only local $ref supported, got {ref}"]
        target = root
        for part in ref[2:].split("/"):
            target = target[part]
        errors += validate(instance, target, root, path)

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(TYPES[t](instance) for t in types):
            return errors + [f"{path}: expected {'/'.join(types)}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected {schema['const']!r}, got {instance!r}")

    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")

    if TYPES["number"](instance):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, dict):
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            errors.append(f"{path}: fewer than {schema['minProperties']} properties")
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required '{key}'")
        props = schema.get("properties", {})
        pattern_props = schema.get("patternProperties", {})
        for key, value in instance.items():
            matched = False
            if key in props:
                matched = True
                errors += validate(value, props[key], root, f"{path}.{key}")
            for pat, sub in pattern_props.items():
                if re.search(pat, key):
                    matched = True
                    errors += validate(value, sub, root, f"{path}.{key}")
            if not matched and "additionalProperties" in schema:
                extra = schema["additionalProperties"]
                if extra is False:
                    errors.append(f"{path}: unexpected property '{key}'")
                elif isinstance(extra, dict):
                    errors += validate(value, extra, root, f"{path}.{key}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than {schema['maxItems']} items")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += validate(item, schema["items"], root, f"{path}[{i}]")

    return errors


def _self_test():
    s = {"type": "object", "required": ["a"], "additionalProperties": False,
         "properties": {"a": {"type": "integer", "minimum": 1}}}
    assert validate({"a": 2}, s) == []
    assert len(validate({"a": 0, "b": 1}, s)) == 2
    assert validate({}, {"foo": 1}) and "unsupported" in validate({}, {"foo": 1})[0]


_self_test()

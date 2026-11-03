#!/usr/bin/env python3
"""Validate a JSON file against a JSON Schema (standard library only).

usage:  python3 schemacheck.py schema.json data.json [--max 30]
        python3 schemacheck.py --demo
exit:   0 = valid, 1 = errors found, 2 = usage / file error

If the `jsonschema` package is installed it is used (full spec). Otherwise a
built-in subset is used: type, required, properties, additionalProperties(false/schema),
items, enum, const, pattern, format(date/time/date-time, checked loosely),
minimum/maximum/exclusive*, minLength/maxLength, minItems/maxItems, uniqueItems,
$ref (local "#/..."), allOf/anyOf/oneOf. Unknown keywords are reported once as "not checked".
"""
import json, re, sys
from datetime import date, datetime

TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}
KNOWN = {"type", "required", "properties", "additionalProperties", "items", "enum", "const",
         "pattern", "format", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
         "minLength", "maxLength", "minItems", "maxItems", "uniqueItems", "$ref", "allOf",
         "anyOf", "oneOf", "$schema", "$id", "title", "description", "definitions", "$defs",
         "default", "examples", "$comment"}


def _fmt_ok(fmt, v):
    try:
        if fmt == "date":
            date.fromisoformat(v)
        elif fmt == "date-time":
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif fmt == "time":
            if not re.fullmatch(r"\d{2}:\d{2}(:\d{2}(\.\d+)?)?([+-]\d{2}:\d{2}|Z)?", v):
                return False
        return True
    except ValueError:
        return False


class Checker:
    def __init__(self, root):
        self.root, self.errors, self.unchecked = root, [], set()

    def resolve(self, ref):
        if not ref.startswith("#/"):
            raise ValueError(f"only local $ref supported: {ref}")
        node = self.root
        for part in ref[2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
        return node

    def err(self, path, msg):
        self.errors.append(f"{path or '$'}: {msg}")

    def check(self, s, v, path=""):
        if s is True or s == {}:
            return
        if s is False:
            return self.err(path, "not allowed")
        for k in s:
            if k not in KNOWN:
                self.unchecked.add(k)
        if "$ref" in s:
            self.check(self.resolve(s["$ref"]), v, path)
        t = s.get("type")
        if t is not None:
            ts = t if isinstance(t, list) else [t]
            if not any(TYPES[x](v) for x in ts):
                return self.err(path, f"type {type(v).__name__}, expected {t}")
        if "enum" in s and v not in s["enum"]:
            self.err(path, f"{v!r} not in enum {s['enum']}")
        if "const" in s and v != s["const"]:
            self.err(path, f"{v!r} != const {s['const']!r}")
        if isinstance(v, str):
            if "pattern" in s and not re.search(s["pattern"], v):
                self.err(path, f"{v!r} does not match /{s['pattern']}/")
            if "format" in s and not _fmt_ok(s["format"], v):
                self.err(path, f"{v!r} is not format {s['format']}")
            if len(v) < s.get("minLength", 0):
                self.err(path, f"length {len(v)} < minLength {s['minLength']}")
            if "maxLength" in s and len(v) > s["maxLength"]:
                self.err(path, f"length {len(v)} > maxLength {s['maxLength']}")
        if TYPES["number"](v):
            if "minimum" in s and v < s["minimum"]:
                self.err(path, f"{v} < minimum {s['minimum']}")
            if "maximum" in s and v > s["maximum"]:
                self.err(path, f"{v} > maximum {s['maximum']}")
            if "exclusiveMinimum" in s and v <= s["exclusiveMinimum"]:
                self.err(path, f"{v} <= exclusiveMinimum {s['exclusiveMinimum']}")
            if "exclusiveMaximum" in s and v >= s["exclusiveMaximum"]:
                self.err(path, f"{v} >= exclusiveMaximum {s['exclusiveMaximum']}")
        if isinstance(v, dict):
            for r in s.get("required", []):
                if r not in v:
                    self.err(path, f"missing required '{r}'")
            props = s.get("properties", {})
            for k, sub in props.items():
                if k in v:
                    self.check(sub, v[k], f"{path}.{k}")
            ap = s.get("additionalProperties", True)
            extra = [k for k in v if k not in props]
            if ap is False and extra:
                self.err(path, f"unexpected keys {extra}")
            elif isinstance(ap, dict):
                for k in extra:
                    self.check(ap, v[k], f"{path}.{k}")
        if isinstance(v, list):
            if len(v) < s.get("minItems", 0):
                self.err(path, f"{len(v)} items < minItems {s['minItems']}")
            if "maxItems" in s and len(v) > s["maxItems"]:
                self.err(path, f"{len(v)} items > maxItems {s['maxItems']}")
            if s.get("uniqueItems"):
                seen = [json.dumps(x, sort_keys=True) for x in v]
                if len(seen) != len(set(seen)):
                    self.err(path, "items not unique")
            it = s.get("items")
            if isinstance(it, dict) or isinstance(it, bool):
                for i, x in enumerate(v):
                    self.check(it, x, f"{path}[{i}]")
            elif isinstance(it, list):
                for i, (sub, x) in enumerate(zip(it, v)):
                    self.check(sub, x, f"{path}[{i}]")
        for sub in s.get("allOf", []):
            self.check(sub, v, path)
        for key in ("anyOf", "oneOf"):
            if key in s:
                ok = 0
                for sub in s[key]:
                    c = Checker(self.root); c.check(sub, v, path)
                    ok += not c.errors
                if (key == "anyOf" and ok == 0) or (key == "oneOf" and ok != 1):
                    self.err(path, f"{key}: {ok} branches matched")


def validate(schema, data):
    """Return (errors, mode). errors is a list of 'path: message'."""
    try:
        import jsonschema  # type: ignore
        fc = jsonschema.FormatChecker()
        for f in ("date", "time", "date-time"):  # make format checks independent of optional extras
            fc.checks(f)(lambda x, f=f: not isinstance(x, str) or _fmt_ok(f, x))
        v = jsonschema.validators.validator_for(schema)(schema, format_checker=fc)
        errs = [f"${''.join(f'[{p}]' if isinstance(p, int) else '.' + str(p) for p in e.absolute_path)}: {e.message}"
                for e in sorted(v.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))]
        return errs, "jsonschema"
    except ImportError:
        c = Checker(schema); c.check(schema, data)
        if c.unchecked:
            print(f"note: keywords not checked by built-in subset: {sorted(c.unchecked)}", file=sys.stderr)
        return c.errors, "built-in subset"


def demo():
    schema = {
        "type": "object", "required": ["generated_at", "routes"], "additionalProperties": False,
        "properties": {
            "generated_at": {"type": "string", "format": "date-time"},
            "routes": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/route"}},
        },
        "$defs": {"route": {
            "type": "object", "required": ["id", "stops", "load"],
            "properties": {
                "id": {"type": "string", "pattern": "^R\\d+$"},
                "stops": {"type": "array", "items": {"type": "object", "required": ["stop_id", "time"],
                          "properties": {"stop_id": {"type": "string"},
                                         "time": {"type": "string", "pattern": "^\\d{2}:\\d{2}$"}}}},
                "load": {"type": "integer", "minimum": 0, "maximum": 10},
                "kind": {"enum": ["in", "out"]},
            }}},
    }
    good = {"generated_at": "2026-01-02T08:00:00+09:00",
            "routes": [{"id": "R1", "load": 3, "kind": "in", "stops": [{"stop_id": "S1", "time": "07:10"}]}]}
    bad = {"generated_at": "yesterday", "extra": 1,
           "routes": [{"id": "X1", "load": 11, "kind": "up", "stops": [{"stop_id": "S1", "time": "7:10"}, {}]},
                      {"id": "R2", "load": True, "stops": []}]}
    g, mode = validate(schema, good)
    b, _ = validate(schema, bad)
    print(f"[demo] mode={mode} good_errors={len(g)} bad_errors={len(b)}")
    for e in b:
        print("  ", e)
    want = ["generated_at", "extra", "routes[0].id", "routes[0].load", "routes[0].kind",
            "routes[0].stops[0].time", "routes[0].stops[1]", "routes[1].load"]
    missed = [w for w in want if not any(w in e for e in b)]
    ok = not g and not missed
    print("[demo]", "PASS" if ok else f"FAIL missed={missed} good={g}")
    return 0 if ok else 1


def main(argv):
    if argv[1:2] == ["--demo"]:
        return demo()
    args = [a for a in argv[1:] if not a.startswith("--")]
    mx = 30
    if "--max" in argv:
        mx = int(argv[argv.index("--max") + 1]); args = [a for a in args if a != str(mx)]
    if len(args) != 2:
        print(__doc__); return 2
    try:
        schema = json.load(open(args[0], encoding="utf-8"))
        data = json.load(open(args[1], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read: {e}"); return 2
    errs, mode = validate(schema, data)
    print(f"schemacheck ({mode}): {args[1]} vs {args[0]} -> {'PASS' if not errs else 'FAIL'} ({len(errs)} errors)")
    for e in errs[:mx]:
        print("  ", e)
    if len(errs) > mx:
        print(f"   ... {len(errs) - mx} more")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

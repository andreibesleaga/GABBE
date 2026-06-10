#!/usr/bin/env python3
"""Gate 1 harness: dump the public API surface of the gabbe package.

Walks every module in gabbe/ and records {module: {public_name: signature}}.
The output is compared against scripts/gates/baselines/api-surface.json by
run_gates.sh: removed or changed entries fail the gate; additions are allowed
(additive-only policy).

Usage:
    python scripts/gates/dump_api.py            # print to stdout
    python scripts/gates/dump_api.py --write    # overwrite the baseline
"""
import importlib
import inspect
import json
import pkgutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASELINE = Path(__file__).resolve().parent / "baselines" / "api-surface.json"


def describe(obj):
    """Return a stable string description of a public object."""
    if inspect.isclass(obj):
        methods = {}
        for name, member in sorted(vars(obj).items()):
            if name.startswith("_") and name != "__init__":
                continue
            if inspect.isfunction(member):
                try:
                    methods[name] = str(inspect.signature(member))
                except (ValueError, TypeError):
                    methods[name] = "<signature unavailable>"
        return {"kind": "class", "methods": methods}
    if inspect.isfunction(obj):
        try:
            return {"kind": "function", "signature": str(inspect.signature(obj))}
        except (ValueError, TypeError):
            return {"kind": "function", "signature": "<signature unavailable>"}
    return {"kind": type(obj).__name__}


def dump_surface():
    sys.path.insert(0, str(REPO_ROOT))
    import gabbe

    surface = {}
    for info in sorted(pkgutil.iter_modules(gabbe.__path__), key=lambda m: m.name):
        if info.name == "tests" or info.name.startswith("test_"):
            continue
        mod_name = f"gabbe.{info.name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:  # pragma: no cover - import failure is itself a finding
            surface[mod_name] = {"<import-error>": str(exc)}
            continue
        entries = {}
        for name, obj in sorted(vars(mod).items()):
            if name.startswith("_"):
                continue
            if inspect.ismodule(obj):
                continue
            if getattr(obj, "__module__", mod_name) != mod_name:
                continue  # re-exports are not this module's surface
            entries[name] = describe(obj)
        surface[mod_name] = entries
    return surface


def main():
    surface = dump_surface()
    text = json.dumps(surface, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(text)
        print(f"Wrote {BASELINE}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()

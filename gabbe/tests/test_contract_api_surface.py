# SPDX-License-Identifier: Apache-2.0
"""Gate 1 contract test: the public API surface of gabbe/ is additive-only.

Compares the live surface (via scripts/gates/dump_api.py) against the frozen
baseline. Additions are allowed; removals and signature changes fail.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASELINE = REPO_ROOT / "scripts" / "gates" / "baselines" / "api-surface.json"


def test_api_surface_is_superset_of_baseline():
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "gates"))
    import dump_api

    baseline = json.loads(BASELINE.read_text())
    current = dump_api.dump_surface()

    problems = []
    for mod, names in baseline.items():
        if mod not in current:
            problems.append(f"module removed: {mod}")
            continue
        for name, desc in names.items():
            if name not in current[mod]:
                problems.append(f"removed: {mod}.{name}")
            elif current[mod][name] != desc:
                problems.append(f"changed: {mod}.{name}: {desc} -> {current[mod][name]}")
    assert not problems, "API surface regression (additive-only policy):\n" + "\n".join(problems)

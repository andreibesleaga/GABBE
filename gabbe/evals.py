# SPDX-License-Identifier: Apache-2.0
"""Eval harness entrypoint for the CLI (Track E2).

`gabbe eval` runs the kit-layer skill eval harness at
agents/scripts/eval_skills.py. The deterministic self-check runs by default;
`--live` scores skill outputs against the model (nightly; needs GABBE_LIVE_LLM=1).
Kept thin and additive so it never touches baselined signatures.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_evals(live: bool = False, out: str | None = None) -> int:
    """Run the skill eval harness and return its exit code.

    Returns 2 when the harness script is absent (e.g. a packaged install without
    the kit checkout), so CI/scripting sees a failure rather than a false success.
    """
    script = Path(__file__).resolve().parent.parent / "agents" / "scripts" / "eval_skills.py"
    if not script.exists():
        print(
            "Eval harness not found (packaged install): run from a GABBE repo "
            "checkout to use 'gabbe eval'."
        )
        return 2
    cmd = [sys.executable, str(script)]
    if live:
        cmd.append("--live")
    if out:
        cmd += ["--out", out]
    return subprocess.run(cmd, check=False).returncode

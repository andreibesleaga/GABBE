# SPDX-License-Identifier: Apache-2.0
"""Gate 2 contract test: CLI --help output is byte-equal to frozen baselines.

Baselines live in gabbe/tests/baselines/cli_help/ and were captured at
COLUMNS=80. Any diff means the externally observable CLI contract changed;
additive flags require a sanctioned baseline update recorded in the audit
worklog.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

BASELINE_DIR = Path(__file__).parent / "baselines" / "cli_help"

# argparse help formatting changes between Python versions (e.g. "optional
# arguments:" -> "options:" in 3.10, usage reflow in 3.13), so byte-exact
# comparison is only meaningful against the interpreter the baselines were
# captured on. The CI "gates" job pins this version.
BASELINE_PY = (3, 12)
pytestmark = pytest.mark.skipif(
    sys.version_info[:2] != BASELINE_PY,
    reason=f"CLI --help byte-baselines captured on Python {BASELINE_PY[0]}.{BASELINE_PY[1]}",
)

COMMANDS = {
    "root": [],
    "init": ["init"],
    "db": ["db"],
    "sync": ["sync"],
    "verify": ["verify"],
    "status": ["status"],
    "route": ["route"],
    "brain": ["brain"],
    "brain_activate": ["brain", "activate"],
    "brain_evolve": ["brain", "evolve"],
    "brain_heal": ["brain", "heal"],
    "serve-mcp": ["serve-mcp"],
    "forecast": ["forecast"],
    "runs": ["runs"],
    "audit": ["audit"],
    "replay": ["replay"],
    "resume": ["resume"],
    "eval": ["eval"],
    "doctor": ["doctor"],
    "uninstall": ["uninstall"],
    "update": ["update"],
}


@pytest.mark.parametrize("name", sorted(COMMANDS))
def test_help_matches_baseline(name):
    baseline_file = BASELINE_DIR / f"{name}.txt"
    assert baseline_file.exists(), f"missing baseline {baseline_file}"
    env = dict(os.environ, COLUMNS="80")
    result = subprocess.run(
        [sys.executable, "-m", "gabbe.main", *COMMANDS[name], "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    current = result.stdout + result.stderr
    assert current == baseline_file.read_text(), (
        f"--help output for '{name}' diverged from baseline; if this change is "
        f"an intentional additive flag, update the baseline and record it in "
        f"the audit worklog"
    )

# SPDX-License-Identifier: Apache-2.0
"""One-command-install guards (Track E8).

Asserts the published library stays installable with a single simple command on
every channel, and that the installer entrypoints exist so the shell / PowerShell
/ npm / Python paths cannot silently bit-rot.

The LIVE published-registry installs (npx / pip / curl|sh on ubuntu+macos+windows)
are exercised by the CI `install-matrix` and post-publish `release-verify` jobs;
this file guards the contract that those jobs depend on, deterministically and
offline.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_installer_entrypoints_exist():
    for rel in ["install.sh", "install.ps1", "bin/install.js", "scripts/init.py"]:
        assert (REPO / rel).exists(), f"missing installer entrypoint: {rel}"


def test_each_channel_is_a_single_command_in_readme():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    # Each channel must appear as a one-liner the user can paste.
    single_command_channels = [
        r"npx gabbe-kit init",  # Node / npm — zero-Python
        r"curl -fsSL[^\n]*install\.sh[^\n]*\|\s*sh",  # shell bootstrap
        r"\b(?:pipx|pip install)\b",  # Python / PyPI channel
    ]
    for pattern in single_command_channels:
        assert re.search(pattern, readme), f"README missing one-command channel: {pattern}"


def test_doctor_command_is_documented():
    cli_ref = (REPO / "docs" / "CLI_REFERENCE.md").read_text(encoding="utf-8")
    assert "gabbe doctor" in cli_ref

# SPDX-License-Identifier: Apache-2.0
"""Workstream C: when the wizard runs in an EXISTING codebase it asks the
greenfield-vs-refactor Mode question, prefills the detected stack, and (in
refactor mode) scaffolds a brownfield onboarding brief instead of greenfield
mission docs."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

ORIGINAL_KIT_SOURCE = init.KIT_SOURCE


def _run(tmpdir, inputs):
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    init.PROJECT_ROOT = Path(tmpdir)
    init.TECH_MAP = {}
    init.FORCE = False
    init.KIT_SOURCE = ORIGINAL_KIT_SOURCE
    init.SOURCE_AGENTS_DIR = ORIGINAL_KIT_SOURCE / "agents"
    try:
        with patch("builtins.input", side_effect=list(inputs)):
            init.main()
    finally:
        os.chdir(original_cwd)


# Brownfield inputs: identical to the greenfield golden run but with ONE extra
# leading answer — the Mode question (only asked when a project is detected).
REFACTOR_INPUTS = [
    "1",  # Install: Local
    "2",  # Mode: Upgrade / Refactor  <-- the brownfield-only question
    "MyApp",  # Name
    "Existing SaaS",  # Desc
    "2",  # Team: Small
    "2",  # Type: Legacy Modernization
    "1",  # Lang: TypeScript
    "Next.js",  # Framework (default would be detected Next.js)
    "1",  # DB: PostgreSQL
    "4",  # Cloud: Vercel
    "n",  # Dynamic Setup: No
    "n",  # Analytics: No
    "n",  # Meta: No
    "n",  # GABBE CLI: No
    "1",  # PM: npm
    "1",  # Agents: Claude Code
]


def test_brownfield_refactor_scaffolds_onboarding(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    # Make it look like an existing Next.js codebase.
    (proj / "package.json").write_text(
        json.dumps({"name": "my-web", "dependencies": {"next": "^14"}})
    )
    (proj / "index.ts").write_text("export const x = 1\n")

    _run(proj, REFACTOR_INPUTS)

    brief = proj / "BROWNFIELD_ONBOARDING.md"
    assert brief.exists(), "refactor mode did not scaffold the onboarding brief"
    text = brief.read_text()
    assert "Upgrade / Refactor" in text
    assert "Discovery" in text
    # The detected stack is surfaced in the brief.
    assert "TypeScript" in text


def test_greenfield_path_unchanged_in_empty_dir(tmp_path):
    """An empty dir must NOT trigger the Mode question (greenfield input order)."""
    proj = tmp_path / "proj"
    proj.mkdir()
    greenfield_inputs = [
        "1",  # Local
        "Fresh",  # Name
        "New",  # Desc
        "1",  # Team: Solo
        "1",  # Type: Greenfield
        "3",  # Lang: Python
        "FastAPI",  # Framework
        "6",  # DB: None
        "7",  # Cloud: On-Prem
        "n",  # Dynamic: No
        "n",  # Analytics: No
        "n",  # Meta: No
        "n",  # GABBE CLI: No
        "1",  # Agents: Claude Code
    ]
    _run(proj, greenfield_inputs)
    # No Mode question was asked, so no onboarding brief and a normal install.
    assert not (proj / "BROWNFIELD_ONBOARDING.md").exists()
    assert (proj / "agents" / "AGENTS.md").exists()

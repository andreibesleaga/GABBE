# SPDX-License-Identifier: Apache-2.0
"""Workstream B: a wizard install writes a `.gabbe/manifest.json` that
`gabbe uninstall` (gabbe.installer) can fully reverse — including the wiring
symlinks the wizard creates and any user file it backed up."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

# scripts/ importable (mirrors test_init.py).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

from gabbe import installer  # noqa: E402

ORIGINAL_KIT_SOURCE = init.KIT_SOURCE

GREENFIELD_INPUTS = [
    "1",  # Install: Local
    "MyTestProj",  # Name
    "Modern SaaS",  # Desc
    "2",  # Team: Small
    "1",  # Type: Greenfield
    "1",  # Lang: TypeScript
    "Next.js",  # Framework
    "1",  # DB: PostgreSQL
    "4",  # Cloud: Vercel
    "y",  # Dynamic Setup
    "Build a SaaS",  # Problem Statement
    "y",  # Analytics
    "y",  # Meta
    "n",  # GABBE CLI: No
    "1",  # PM: npm
    "1,2",  # Agents: Claude Code, Cursor
]


def _run_wizard(tmpdir, inputs):
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


def test_wizard_writes_reversible_manifest(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    _run_wizard(proj, GREENFIELD_INPUTS)

    manifest_path = proj / ".gabbe" / "manifest.json"
    assert manifest_path.exists(), "wizard did not write an uninstall manifest"
    manifest = json.loads(manifest_path.read_text())
    kinds = {e["kind"] for e in manifest["entries"]}
    # The wizard created copied kit files AND wiring (symlinks / generated trees).
    assert "copy" in kinds
    assert {"symlink", "tree"} & kinds, f"no wiring recorded; kinds={kinds}"

    # Wiring that should exist after selecting Claude Code + Cursor.
    root_agents = proj / "AGENTS.md"
    cursorrules = proj / ".cursorrules"
    assert root_agents.exists() or root_agents.is_symlink()
    assert cursorrules.exists() or cursorrules.is_symlink()

    # Uninstall reverses everything the manifest recorded.
    installer.uninstall(proj, purge=True)
    assert not root_agents.exists() and not root_agents.is_symlink()
    assert not cursorrules.exists() and not cursorrules.is_symlink()
    assert not (proj / ".claude").exists()


def test_wizard_backs_up_and_restores_preexisting_wiring(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    # A pre-existing .cursorrules the user already had (must survive a round-trip).
    (proj / ".cursorrules").write_text("MY EXISTING CURSOR RULES\n")

    _run_wizard(proj, GREENFIELD_INPUTS)

    # The wizard backed up the user's file before wiring its own.
    backup = proj / ".cursorrules.bak"
    assert backup.exists(), "pre-existing .cursorrules was not backed up"
    assert backup.read_text() == "MY EXISTING CURSOR RULES\n"

    # Uninstall restores the user's original from the recorded backup.
    installer.uninstall(proj, purge=True)
    assert (proj / ".cursorrules").read_text() == "MY EXISTING CURSOR RULES\n"

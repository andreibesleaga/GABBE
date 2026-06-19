# SPDX-License-Identifier: Apache-2.0
"""Workstream D: a fully-answered wizard run fills derivable command/config
fields in AGENTS.md; genuinely project-specific fields are kept but tagged
<!-- OPTIONAL --> and reported, never shipped as silent blanks."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

ORIGINAL_KIT_SOURCE = init.KIT_SOURCE

TS_INPUTS = [
    "1",  # Local
    "Web",  # Name
    "A web app",  # Desc
    "2",  # Team: Small
    "1",  # Type: Greenfield
    "1",  # Lang: TypeScript
    "Next.js",  # Framework
    "1",  # DB: PostgreSQL
    "4",  # Cloud: Vercel
    "n",  # Dynamic: No
    "n",  # Analytics: No
    "n",  # Meta: No
    "n",  # GABBE CLI: No
    "1",  # PM: npm
    "1",  # Agents: Claude Code
]


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


def test_derivable_command_fields_are_filled(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    _run(proj, TS_INPUTS)

    agents_md = (proj / "agents" / "AGENTS.md").read_text()
    # npm-derived command placeholders are now concrete, not literal [PLACEHOLDER:].
    assert 'dev: "npm run dev"' in agents_md
    assert 'lint: "eslint ."' in agents_md
    assert 'format: "prettier --write ."' in agents_md
    assert 'typecheck: "tsc --noEmit"' in agents_md
    # These derivable fields must no longer contain a raw placeholder.
    for key in ("dev:", "lint:", "format:", "typecheck:"):
        line = next(line for line in agents_md.splitlines() if line.strip().startswith(key))
        assert "[PLACEHOLDER" not in line, f"{key} still unfilled"


def test_underivable_fields_kept_but_tagged_optional_and_reported(tmp_path, capsys):
    proj = tmp_path / "proj"
    proj.mkdir()
    _run(proj, TS_INPUTS)

    agents_md = (proj / "agents" / "AGENTS.md").read_text()
    # Project-specific fields (no git remote in this temp dir) stay, marked OPTIONAL.
    for line in agents_md.splitlines():
        if "[PLACEHOLDER" in line:
            assert "OPTIONAL" in line, f"unfilled placeholder not tagged OPTIONAL: {line!r}"

    # The installer recorded what remains and warned the user about it.
    assert init._UNFILLED_PLACEHOLDERS, "no unfilled placeholders were recorded"
    out = capsys.readouterr().out
    assert "still need your input" in out
    assert "OPTIONAL" in out

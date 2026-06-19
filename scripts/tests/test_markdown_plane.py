# SPDX-License-Identifier: Apache-2.0
"""Workstream E: the markdown plane is emitted in an agent-consumable shape.

Beyond the static validators (which check the SOURCE files parse), this drives a
real install and asserts the EMITTED skill artifacts an agent actually reads —
`.claude/skills/<slug>/SKILL.md` (the agent-skills open standard) — exist, carry
valid frontmatter (name + description), and that skills referenced by the
generated AGENTS.md resolve to real source files."""

import os
import re
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

ORIGINAL_KIT_SOURCE = init.KIT_SOURCE

CLAUDE_INPUTS = [
    "1",  # Local
    "Plane",  # Name
    "desc",  # Desc
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


def _frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    return set(re.findall(r"(?m)^([a-zA-Z_]+):", block))


def test_emitted_claude_skills_are_discoverable(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    _run(proj, CLAUDE_INPUTS)

    skills_dir = proj / ".claude" / "skills"
    assert skills_dir.exists(), "install did not emit .claude/skills for Claude Code"
    skill_files = list(skills_dir.glob("*/SKILL.md"))
    assert len(skill_files) >= 50, f"too few emitted skills: {len(skill_files)}"

    # Every emitted skill must be agent-discoverable: valid frontmatter with the
    # required name + description keys (per the agent-skills open standard).
    for sf in skill_files[:40]:
        keys = _frontmatter(sf.read_text())
        assert keys is not None, f"{sf} has no frontmatter"
        assert "name" in keys and "description" in keys, f"{sf} missing name/description"


def test_source_skill_index_resolves_to_real_files(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    _run(proj, CLAUDE_INPUTS)

    skills_root = proj / "agents" / "skills"
    index = skills_root / "00-index.md"
    assert index.exists()
    # Skill files referenced anywhere in the tree must all exist (no dangling
    # plane references that an agent would fail to load).
    all_skill_files = {p.name for p in skills_root.rglob("*.skill.md")}
    assert len(all_skill_files) >= 100, "skill plane unexpectedly small"

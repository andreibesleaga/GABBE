# SPDX-License-Identifier: Apache-2.0
"""Kit-only (no `gabbe` CLI) end-to-end: emit skills for a platform into a
temp project and assert the output conforms to the agent-skills standard, so a
real client (Claude Code / Copilot) would discover them.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "agents" / "scripts"))

import compile_skills as cs  # noqa: E402

AGENTS_DIR = REPO_ROOT / "agents"


def _parse_frontmatter(text):
    assert text.startswith("---"), "SKILL.md must start with YAML frontmatter"
    end = text.find("---", 3)
    assert end != -1, "frontmatter must be closed"
    import yaml

    return yaml.safe_load(text[3:end]) or {}


@pytest.mark.parametrize("platform", ["Claude Code", "GitHub Copilot"])
def test_emitted_skills_follow_skill_md_standard(platform, tmp_path):
    target = tmp_path / "skills"
    cs.setup_skills_for_platform(platform, AGENTS_DIR / "skills", target, tmp_path)

    skill_dirs = [p for p in target.iterdir() if p.is_dir()]
    assert len(skill_dirs) >= 100, "expected the full skill catalogue to be emitted"

    for d in skill_dirs[:25]:
        skill_md = d / "SKILL.md"
        assert skill_md.exists(), f"{d.name} missing SKILL.md (not discoverable)"
        fm = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        assert fm.get("name"), f"{d.name}/SKILL.md missing name"
        assert fm.get("description"), f"{d.name}/SKILL.md missing description"
        assert fm.get("gabbe-schema-version") == 1
        # directory name is a clean slug (Claude/Copilot use it as the command)
        assert d.name == d.name.lower()
        assert "/" not in d.name and ".." not in d.name


def test_cursor_rules_are_agent_requested(tmp_path):
    target = tmp_path / "rules"
    cs.setup_skills_for_platform("Cursor", AGENTS_DIR / "skills", target, tmp_path)
    mdc_files = list(target.glob("*.mdc"))
    assert len(mdc_files) >= 100
    sample = mdc_files[0].read_text(encoding="utf-8")
    # Agent-requested: description present, alwaysApply:false, NO globs.
    assert "description:" in sample
    assert "alwaysApply: false" in sample
    assert "globs:" not in sample
    assert "gabbe-schema-version: 1" in sample

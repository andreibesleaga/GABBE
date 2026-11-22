"""The existing-project (brownfield) path: skills, guide, templates and persona exist and are wired."""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"

NEW_SKILLS = [
    "architecture/existing-project-onboarding",
    "architecture/code-archaeology",
    "coding/characterization-tests",
    "coding/safe-refactoring",
    "coding/incremental-feature",
    "ops/dependency-upgrade",
]
TEMPLATES = [
    "architecture/CODEBASE_MAP_TEMPLATE.md",
    "architecture/ASSESSMENT_TEMPLATE.md",
]
GUIDE = "guides/processes/brownfield-lifecycle.md"
PERSONA = "personas/eng-maintainer.md"


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name}: no frontmatter"
    end = text.index("\n---", 4)
    data = yaml.safe_load(text[4:end])
    assert isinstance(data, dict)
    return data


@pytest.mark.parametrize("rel", NEW_SKILLS)
def test_skill_file_is_valid_and_indexed(rel):
    path = AGENTS / "skills" / f"{rel}.skill.md"
    assert path.is_file()
    meta = _frontmatter(path)
    stem = path.name.removesuffix(".skill.md")
    assert meta["name"] == stem
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"])
    assert 0 < len(meta["description"]) < 1024
    assert meta["triggers"]
    index = (AGENTS / "skills/00-index.md").read_text(encoding="utf-8")
    assert f"`{rel}.skill.md`" in index


@pytest.mark.parametrize("rel", NEW_SKILLS)
def test_skill_is_short_and_has_safety_section(rel):
    text = (AGENTS / "skills" / f"{rel}.skill.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 120
    assert "## Limits and safety" in text


def test_guide_names_all_stages_and_skills():
    guide = (AGENTS / GUIDE).read_text(encoding="utf-8")
    for stage in ("B0", "B1", "B2", "B3", "B4"):
        assert re.search(rf"^## {stage} ", guide, re.M), stage
    for rel in NEW_SKILLS:
        assert f"skills/{rel}.skill.md" in guide, rel
    assert GUIDE.removeprefix("guides/") in (AGENTS / "guides/00-index.md").read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize("rel", TEMPLATES)
def test_template_exists_and_is_indexed(rel):
    assert (AGENTS / "templates" / rel).is_file()
    assert f"`{rel}`" in (AGENTS / "templates/00-index.md").read_text(encoding="utf-8")


def test_persona_exists_is_indexed_and_skills_resolve():
    path = AGENTS / PERSONA
    assert path.is_file()
    assert "eng-maintainer" in (AGENTS / "personas/00-index.md").read_text(encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    names = re.findall(r"`([a-z0-9-]+)\.skill`", text)
    assert names
    stems = {p.name.removesuffix(".skill.md") for p in (AGENTS / "skills").rglob("*.skill.md")}
    for name in names:
        assert name in stems, name
    for rel in NEW_SKILLS:
        assert rel.split("/")[1] in names, rel

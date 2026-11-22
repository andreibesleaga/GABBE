# SPDX-License-Identifier: Apache-2.0
"""Assurance ladder: the new skills, templates and guide exist, are indexed, and cite their sources."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"

TECHNIQUES = [
    "mutation-testing",
    "design-by-contract",
    "fuzz-differential-testing",
    "formal-spec-lightweight",
    "proof-core-verification",
    "verification-anti-cheating",
]
SKILLS = ["assurance-ladder"] + TECHNIQUES
TEMPLATES = [
    "core/ASSURANCE_PLAN_TEMPLATE.md",
    "architecture/FORMAL_SPEC_BRIEF_TEMPLATE.md",
    "coding/PROOF_OBLIGATION_TEMPLATE.md",
    "coding/MUTATION_REPORT_TEMPLATE.md",
]
GUIDE = AGENTS / "guides" / "principles" / "assurance-ladder.md"
PERCENT = re.compile(r"\d\s*%")
MARKER = re.compile(r"\[(\d+)\]")


def _skill(name):
    return AGENTS / "skills" / "coding" / f"{name}.skill.md"


def test_skills_exist_indexed_and_named_by_stem():
    index = (AGENTS / "skills" / "00-index.md").read_text()
    for name in SKILLS:
        path = _skill(name)
        assert path.is_file(), name
        text = path.read_text()
        assert re.search(rf"^name: {re.escape(name)}$", text, re.M), name
        assert f"coding/{name}.skill.md" in index, name


def test_skill_description_and_length():
    for name in SKILLS:
        text = _skill(name).read_text()
        desc = re.search(r"^description: (.+)$", text, re.M).group(1)
        assert len(desc) < 1024, name
        assert len(text.splitlines()) <= 130, name


def test_templates_exist_and_indexed():
    index = (AGENTS / "templates" / "00-index.md").read_text()
    for rel in TEMPLATES:
        assert (AGENTS / "templates" / rel).is_file(), rel
        assert f"`{rel}`" in index, rel


def test_ladder_names_levels_and_techniques():
    text = _skill("assurance-ladder").read_text()
    for level in ("Level 0", "Level 1", "Level 2", "Level 3"):
        assert level.lower() in text.lower() or f"| {level[-1]}" in text, level
    for name in TECHNIQUES:
        assert f"{name}.skill.md" in text, name


def test_guide_indexed_and_references_resolve():
    assert "principles/assurance-ladder.md" in (AGENTS / "guides" / "00-index.md").read_text()
    lines = GUIDE.read_text().splitlines()
    assert len(lines) <= 180
    start = next(i for i, line in enumerate(lines) if line.startswith("## References"))
    listed = {m.group(1) for line in lines[start:] for m in [re.match(r"(\d+)\. ", line)] if m}
    assert listed
    for line in lines[start:]:
        if re.match(r"\d+\. ", line):
            assert "http" in line, line
    for line in lines[:start]:
        if PERCENT.search(line):
            markers = set(MARKER.findall(line))
            assert markers, f"figure without reference: {line}"
            assert markers <= listed, line

"""The security baseline path: entry skill, template, guide, wiring and evidence rules.

Deterministic: reads files only, no network. The dates in the guide are checked for
presence, not for truth (a person or agent re-checks the sources on the build day).
"""

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"
SKILLS = AGENTS / "skills"
SECURITY = SKILLS / "security"
ENTRY = SECURITY / "security-baseline.skill.md"
TEMPLATE = AGENTS / "templates" / "security" / "SECURITY_BASELINE_TEMPLATE.md"
GUIDE = AGENTS / "guides" / "principles" / "security-baseline.md"
DATE = "2026-11-21"
PHASES = ["S01", "S02", "S03", "S05", "S06", "S07", "S10", "S11"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _skill_names() -> set[str]:
    return {p.name[: -len(".skill.md")] for p in SKILLS.glob("*/*.skill.md")}


def test_entry_template_guide_exist():
    for path in (ENTRY, TEMPLATE, GUIDE):
        assert path.is_file(), path


def test_files_are_indexed():
    assert "security/security-baseline.skill.md" in _read(SKILLS / "00-index.md")
    assert "security/SECURITY_BASELINE_TEMPLATE.md" in _read(AGENTS / "templates" / "00-index.md")
    assert "principles/security-baseline.md" in _read(AGENTS / "guides" / "00-index.md")


def test_new_security_skills_are_indexed():
    index = _read(SKILLS / "00-index.md")
    for name in ("security-requirements", "agent-tool-review"):
        assert f"security/{name}.skill.md" in index


def test_entry_skill_names_every_phase():
    text = _read(ENTRY)
    for phase in PHASES:
        assert re.search(rf"\b{phase}\b", text), phase


def test_entry_skill_size():
    assert len(_read(ENTRY).splitlines()) <= 135


def test_entry_skill_paths_exist():
    text = _read(ENTRY)
    names = _skill_names()
    missing = []
    for token in re.findall(r"`([^`\n]+)`", text):
        if token.endswith(".skill.md") or token.startswith(("guides/", "personas/")):
            base = SKILLS if token.endswith(".skill.md") and "/" in token else AGENTS
            if not (base / token).exists() and not (AGENTS / token).exists():
                if not (SKILLS / token).exists():
                    missing.append(token)
        elif token.endswith(".md") and token.startswith("templates/"):
            if not (AGENTS / token).exists():
                missing.append(token)
        elif re.fullmatch(r"[a-z]+(-[a-z]+)+", token) and token not in names:
            missing.append(token)
    assert not missing, missing


def test_every_security_skill_has_limits_section():
    spec = importlib.util.spec_from_file_location(
        "check_limits_section", AGENTS / "scripts" / "check_limits_section.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    failures = {
        p.name: module.problems(p)
        for p in sorted(SECURITY.glob("*.skill.md"))
        if module.problems(p)
    }
    assert not failures, failures


def test_every_security_skill_says_where_it_fits():
    skip = {
        "security-baseline.skill.md",
        "security-requirements.skill.md",
        "agent-tool-review.skill.md",
    }
    for path in sorted(SECURITY.glob("*.skill.md")):
        if path.name in skip:
            continue
        text = _read(path)
        assert "## Where it fits" in text, path.name
        assert re.search(r"\bS\d\d\b", text), path.name


def test_guide_urls_carry_the_date():
    lines = [ln for ln in _read(GUIDE).splitlines() if "http" in ln]
    assert lines
    for line in lines:
        assert DATE in line, line


def test_template_has_required_parts():
    text = _read(TEMPLATE)
    for part in ("Tier", "confirmation", "Controls by phase", "Open risks", "pinned"):
        assert part.lower() in text.lower(), part

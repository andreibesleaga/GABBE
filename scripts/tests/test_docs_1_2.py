"""Documents of release 1.2.0: the two new pages, the README line for the MCP Registry, and the counts.

Every count that README.md, llms.txt and the four index files state is computed from disk here.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"
WORKFLOWS = ROOT / "docs" / "WORKFLOWS.md"
UPGRADING = ROOT / "docs" / "UPGRADING.md"
MCP_LINE = "<!-- mcp-name: io.github.andreibesleaga/gabbe -->"


def _text(path):
    return path.read_text(encoding="utf-8")


def count_skills():
    return len(list(AGENTS.glob("skills/*/*.skill.md")))


def count_templates():
    return len(
        [p for p in (AGENTS / "templates").rglob("*") if p.is_file() and p.name != "00-index.md"]
    )


def count_guides():
    return len([p for p in (AGENTS / "guides").rglob("*.md") if p.name != "00-index.md"])


def count_personas():
    return len(
        [p for p in (AGENTS / "personas").iterdir() if p.is_file() and p.name != "00-index.md"]
    )


def count_core_skills():
    return len(
        [
            p
            for p in AGENTS.glob("skills/*/*.skill.md")
            if re.search(r"^core: *true", _text(p), re.M)
        ]
    )


def _first_number(pattern, text):
    match = re.search(pattern, text)
    assert match, f"no match for {pattern!r}"
    return int(match.group(1))


@pytest.mark.parametrize("page", [WORKFLOWS, UPGRADING])
def test_new_page_exists_and_is_short(page):
    assert page.is_file()
    assert len(_text(page).splitlines()) <= 220


@pytest.mark.parametrize("page", [WORKFLOWS, UPGRADING])
def test_links_and_paths_in_new_pages_exist(page):
    text = _text(page)
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        assert (page.parent / target).exists(), f"{page.name}: broken link {target}"
    for path in set(re.findall(r"`((?:agents|docs|project)/[\w./-]+\.\w+)`", text)):
        if path.startswith("project/"):
            continue  # files a project creates, not files of the kit
        if path.startswith("agents/memory/"):
            continue  # files an installed project creates
        assert (ROOT / path).exists(), f"{page.name}: missing path {path}"
    for path in set(re.findall(r"`(agents/[\w./-]+/)`", text)):
        if path.startswith("agents/memory/"):
            continue
        assert (ROOT / path).is_dir(), f"{page.name}: missing folder {path}"


def test_workflows_names_every_situation_and_gate():
    text = _text(WORKFLOWS)
    headings = re.findall(r"^## \d\. (.+)$", text, re.M)
    assert headings == [
        "A new project",
        "An existing codebase",
        "A single small change",
        "Brain mode",
        "Loki mode",
        "Resuming unfinished work",
    ]
    for gate in ("S00", "S01", "S02", "S07", "S08", "S10"):
        assert gate in text


def test_workflows_skills_exist():
    text = _text(WORKFLOWS)
    on_disk = {p.name[: -len(".skill.md")] for p in AGENTS.glob("skills/*/*.skill.md")}
    plugins = {p.name for p in (ROOT / "plugins").iterdir()}
    plugins |= {p.stem for p in (AGENTS / "personas").glob("*.md")}
    for name in re.findall(r"`([a-z]+(?:-[a-z]+)+)`", text):
        assert (
            name in on_disk | plugins
        ), f"WORKFLOWS.md names {name}, which is not a skill, persona or plugin"


def test_new_pages_are_linked():
    assert "docs/WORKFLOWS.md" in _text(ROOT / "README.md")
    assert "WORKFLOWS.md" in _text(ROOT / "docs" / "QUICK_GUIDE.md")
    assert "docs/WORKFLOWS.md" in _text(ROOT / "llms.txt")
    assert "docs/UPGRADING.md" in _text(ROOT / "README.md")
    assert "UPGRADING.md" in _text(ROOT / "docs" / "POST_INSTALL.md")
    assert "docs/UPGRADING.md" in _text(ROOT / "llms.txt")


def test_readme_has_the_mcp_name_line_once():
    lines = _text(ROOT / "README.md").splitlines()
    assert lines.count(MCP_LINE) == 1
    assert lines.index(MCP_LINE) < 10


@pytest.mark.parametrize(
    "path, pattern, counter",
    [
        ("agents/skills/00-index.md", r"\*\*Total Skills\*\*: (\d+)", count_skills),
        ("agents/templates/00-index.md", r"\*\*Total Templates\*\*: (\d+)", count_templates),
        ("agents/guides/00-index.md", r"\*\*Total Guides\*\*: (\d+)", count_guides),
        ("agents/personas/00-index.md", r"full set of \*\*(\d+)\*\*", count_personas),
        ("agents/skills/00-index.md", r"\((\d+) skills flagged `core: true`\)", count_core_skills),
        ("agents/AGENTS.md", r"personas/00-index\.md \((\d+) roles\)", count_personas),
        (
            "agents/templates/coordination/AGENTS_TEMPLATE.md",
            r"personas/00-index\.md \((\d+) roles\)",
            count_personas,
        ),
    ],
)
def test_index_and_agents_counts_match_disk(path, pattern, counter):
    assert _first_number(pattern, _text(ROOT / path)) == counter()


def test_readme_counts_match_disk():
    text = _text(ROOT / "README.md")
    assert _first_number(r"\*\*(\d+) Skills\*\* \(", text) == count_skills()
    assert _first_number(r"\*\*(\d+) Templates\*\* \(", text) == count_templates()
    assert _first_number(r"\*\*(\d+) Guides\*\* \(", text) == count_guides()
    assert _first_number(r"\*\*(\d+) Personas\*\* \(", text) == count_personas()
    assert _first_number(r"├── skills/\s+# (\d+) \.skill\.md files", text) == count_skills()
    assert _first_number(r"All (\d+) skills in the GABBE kit", text) == count_skills()
    assert (
        _first_number(r"one overall plugin, `gabbe`\*\*: (\d+) curated skills", text)
        == count_core_skills()
    )


def test_llms_counts_match_disk():
    text = _text(ROOT / "llms.txt")
    assert _first_number(r"skills/` \((\d+) `\*\.skill\.md`\)", text) == count_skills()
    assert _first_number(r"guides/` \((\d+)\)", text) == count_guides()
    assert _first_number(r"personas/` \((\d+)\)", text) == count_personas()
    assert _first_number(r"templates/` \((\d+)\)", text) == count_templates()
    assert _first_number(r"Skills index\]\([^)]*\): (\d+) specialized", text) == count_skills()
    assert _first_number(r"Guides index\]\([^)]*\): (\d+) language", text) == count_guides()
    assert _first_number(r"Personas index\]\([^)]*\): (\d+) specialized", text) == count_personas()


def test_plugin_skill_count_matches_core_flag():
    assert len(list((ROOT / "plugins" / "gabbe" / "skills").iterdir())) == count_core_skills()

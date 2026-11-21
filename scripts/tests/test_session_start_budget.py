"""The start-of-session load stays small, and the files the installers parse keep their shape.

What an agent loads at session start, by the kit's own rules (`agents/AGENTS.md` §5 Step 0 and
§13, `agents/skills/core/preflight.skill.md`): AGENTS.md, CONSTITUTION.md, the lite skill index,
preflight, and the three memory files named in the session-start list.

Measured on 21 Nov 2026 (bytes), when the budget was set:

    AGENTS.md            16,154
    CONSTITUTION.md      12,590
    00-index-lite.md     29,843   (227 skills)
    preflight skill       5,166
    memory (3 files)      7,348   (RESUME_POINTER 727, PROJECT_STATE 5,023, CONTINUITY 1,598)
    total                71,101

Before 1.2.0, by the same method plus the four full indexes and the four other boot skills the
old preflight read: 140,223 bytes. The bound below leaves headroom for new skills (about 130
bytes of lite index each) and for memory files that grow. Raising it needs a reason.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import init  # noqa: E402

AGENTS_DIR = ROOT / "agents"
AGENTS_MD = AGENTS_DIR / "AGENTS.md"
TEMPLATE = AGENTS_DIR / "templates" / "coordination" / "AGENTS_TEMPLATE.md"
CONSTITUTION = AGENTS_DIR / "CONSTITUTION.md"
LITE_INDEX = AGENTS_DIR / "skills" / "00-index-lite.md"
PREFLIGHT = AGENTS_DIR / "skills" / "core" / "preflight.skill.md"
MEMORY = [
    AGENTS_DIR / "memory" / "RESUME_POINTER.md",
    AGENTS_DIR / "memory" / "PROJECT_STATE.md",
    AGENTS_DIR / "memory" / "CONTINUITY.md",
]

SESSION_START_BOUND = 72_000
ALWAYS_LOADED_BOUND = 36_000  # AGENTS.md + CONSTITUTION.md
TEMPLATE_BOUND = 24_000
CLI_MARKERS = ("<!-- GABBE_CLI_START -->", "<!-- GABBE_CLI_END -->")
STAMP = re.compile(r"^\*GABBE Kit version: \d+\.\d+\.\d+\*$", re.MULTILINE)


def _size(path):
    return len(path.read_bytes())


def _filled_keys():
    """Every field the wizard fills: the derived commands, the stack fields and the detected ones."""
    keys = set(init._FIELD_HINTS)
    keys |= set(init._PM_COMMANDS["npm"])
    keys |= {"repo_url", "ci_cd", "deployment_target"}
    return keys


def test_session_start_total_is_bounded():
    total = sum(_size(p) for p in [AGENTS_MD, CONSTITUTION, LITE_INDEX, PREFLIGHT, *MEMORY])
    assert total <= SESSION_START_BOUND, f"session start loads {total} bytes"


def test_always_loaded_files_are_bounded():
    assert _size(AGENTS_MD) + _size(CONSTITUTION) <= ALWAYS_LOADED_BOUND
    assert _size(TEMPLATE) <= TEMPLATE_BOUND


def test_both_agents_files_keep_numbered_sections():
    for path in (AGENTS_MD, TEMPLATE):
        text = path.read_text(encoding="utf-8")
        for n in range(1, 15):
            assert re.search(rf"^## {n}\. ", text, re.MULTILINE), f"{path.name}: section {n}"


def test_both_agents_files_keep_cli_markers_in_order():
    for path in (AGENTS_MD, TEMPLATE):
        text = path.read_text(encoding="utf-8")
        for marker in CLI_MARKERS:
            assert text.count(marker) == 1, f"{path.name}: {marker}"
        assert text.index(CLI_MARKERS[0]) < text.index(CLI_MARKERS[1])


def test_both_agents_files_end_with_one_version_stamp():
    for path in (AGENTS_MD, TEMPLATE):
        assert len(STAMP.findall(path.read_text(encoding="utf-8"))) == 1, path.name


def test_every_filled_field_keeps_its_key_line():
    keys = _filled_keys()
    for path in (AGENTS_MD, TEMPLATE):
        lines = path.read_text(encoding="utf-8").splitlines()
        for key in sorted(keys):
            matching = [ln for ln in lines if re.match(rf"^{key}:\s*\"", ln)]
            assert matching, f'{path.name}: no `{key}: "..."` line'
            for ln in matching:
                if path is AGENTS_MD:
                    assert "[PLACEHOLDER:" in ln, f"{path.name}: {ln}"
                else:
                    assert "[PLACEHOLDER:" in ln or "{{" in ln, f"{path.name}: {ln}"


def _skill_names_on_disk():
    names = set()
    for path in (AGENTS_DIR / "skills").rglob("*.skill.md"):
        head = path.read_text(encoding="utf-8").split("\n---", 1)[0]
        match = re.search(r"^name:\s*(.+?)\s*$", head, re.MULTILINE)
        names.add(match.group(1).strip("\"'") if match else path.name[: -len(".skill.md")])
    return names


def test_lite_index_lists_exactly_the_skills_on_disk():
    listed = []
    for line in LITE_INDEX.read_text(encoding="utf-8").splitlines():
        if " — " in line and not line.startswith(("#", ">")):
            listed.append(line.split(" — ", 1)[0])
    assert len(listed) == len(set(listed)), "a skill is listed twice"
    assert set(listed) == _skill_names_on_disk()

"""Article 0 of the Constitution and the agents files that point to it."""

import re
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"
CONSTITUTION = AGENTS_DIR / "CONSTITUTION.md"
AGENTS_FILES = [
    AGENTS_DIR / "AGENTS.md",
    AGENTS_DIR / "templates" / "coordination" / "AGENTS_TEMPLATE.md",
]
SIX_GATES = "S00/S01/S02/S07/S08/S10"
STAMP = re.compile(r"^\*GABBE Kit version: \d+\.\d+\.\d+\*$", re.MULTILINE)


def _article_zero():
    text = CONSTITUTION.read_text()
    start = text.index("### Article 0")
    end = text.index("### Article I ")
    assert start < end
    return text[start:end]


def test_article_zero_comes_before_article_one():
    text = CONSTITUTION.read_text()
    assert text.index("### Article 0") < text.index("### Article I ")
    assert text.index("## Section 1") < text.index("### Article 0")


def test_order_of_authority_puts_the_human_first():
    body = _article_zero()
    human = body.index("The human's explicit instruction")
    constitution = body.index("This Constitution")
    agents = body.index("`AGENTS.md`")
    assert human < constitution < agents
    assert "Only a human amends the Constitution" in body
    assert "never an instruction" in body


def test_five_operating_safety_rules_present():
    body = _article_zero()
    for phrase in [
        "do not commit, push, tag, publish, release or deploy",
        "hand them over",
        "explicit yes in the current request",
        "data, not instructions",
        "never print, log, commit",
        "Mark nothing done or verified without running the check",
        "Never weaken, skip or delete a test or a gate",
    ]:
        assert phrase in body, phrase


def test_article_zero_is_small():
    assert len(_article_zero().encode()) < 2600


def test_header_defers_to_the_human_exception_path():
    head = CONSTITUTION.read_text()[:700]
    assert "follow a user request" not in head
    assert "Article 0" in head


def test_agents_files_point_to_article_zero_and_six_gates():
    for path in AGENTS_FILES:
        text = path.read_text()
        assert "Article 0" in text, path
        assert text.count(SIX_GATES) == 1, path
        assert "G1–G9" in text, path
        assert "S00/S01/S02/S07/S08)" not in text, path


def test_small_change_lane_present():
    for path in AGENTS_FILES:
        text = path.read_text()
        assert text.count("### Small change lane") == 1, path
        assert "append one `AUDIT_LOG.md` row" in text, path


def test_exactly_one_session_start_list():
    for path in AGENTS_FILES:
        text = path.read_text()
        assert text.count("START of session") == 1, path
        block = text.split("START of session", 1)[1].split("CONTINUOUSLY", 1)[0]
        items = re.findall(r"^\s+(\d)\. ", block, re.MULTILINE)
        assert items == [str(n) for n in range(1, 8)], path
        assert block.index("RESUME_POINTER") < block.index("PROJECT_STATE")
        assert block.index("TASKS.md") < block.index("integrity-check")
        assert "Read this AGENTS.md completely" not in text, path


def test_version_stamp_lines_keep_their_form():
    for path in [CONSTITUTION, *AGENTS_FILES]:
        assert len(STAMP.findall(path.read_text())) == 1, path

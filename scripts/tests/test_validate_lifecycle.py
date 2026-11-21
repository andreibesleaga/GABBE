# SPDX-License-Identifier: Apache-2.0
"""Tests for agents/scripts/validate_lifecycle.py.

The validator must pass on the repository, and must fail and name the file on a
small temporary tree with one deliberate error each.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "agents" / "scripts" / "validate_lifecycle.py"
CANON = "agents/guides/processes/loki-sdlc-phases.md"
HUMAN = {"S00", "S01", "S02", "S07", "S08", "S10"}


def _canon_table():
    rows = ["| ID | Name | Day | Lead | Skills | Entry | Exit | Gate | Artefacts |"]
    rows.append("|---|---|---|---|---|---|---|---|---|")
    for n in range(14):
        pid = f"S{n:02d}"
        gate = "HUMAN" if pid in HUMAN else "automated"
        rows.append(f"| {pid} | Phase {n} | 1 | x | x | x | x | {gate} | x |")
    return "# Guide\n\n## Lifecycle at a glance (canonical)\n\n" + "\n".join(rows) + "\n"


def _run(root):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    return result.returncode, re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)


def _tree(tmp_path, extra_name=None, extra_text=None):
    canon = tmp_path / CANON
    canon.parent.mkdir(parents=True)
    canon.write_text(_canon_table(), encoding="utf-8")
    if extra_name:
        extra = tmp_path / extra_name
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text(extra_text, encoding="utf-8")
    return tmp_path


def test_repository_passes():
    code, out = _run(ROOT)
    assert code == 0, out


def test_clean_tree_passes(tmp_path):
    root = _tree(tmp_path, "docs/ok.md", "The lifecycle has 14 phases, S00-S13.\n")
    code, out = _run(root)
    assert code == 0, out


@pytest.mark.parametrize(
    "text",
    [
        "Loki runs a 10-phase SDLC.\n",  # A: wrong phase count
        "The lifecycle runs S01-S10 from start to finish.\n",  # A: wrong range
        "Quality is checked by the 7-gate system.\n",  # B: wrong gate count
        "The 10 gates must pass.\n",  # B: wrong gate count
        "Add the S02.5 cost gate.\n",  # C: half-numbered phase
        "Current phase: S1 of the SDLC.\n",  # C: one-digit id
        "Human gates: S00, S01, S02, S07, S08.\n",  # D: five human gates
        "Human gates: S00, S01, S02, S03, S07, S08, S10.\n",  # D: seven
    ],
)
def test_one_error_fails_and_names_the_file(tmp_path, text):
    root = _tree(tmp_path, "docs/bad.md", text)
    code, out = _run(root)
    assert code == 1, out
    assert "docs/bad.md:1" in out


def test_inline_marker_allows_a_justified_exception(tmp_path):
    text = "Old name: the 7-gate system. <!-- lifecycle-validator: ignore -->\n"
    root = _tree(tmp_path, "docs/old.md", text)
    code, out = _run(root)
    assert code == 0, out


def test_skipped_paths_are_not_scanned(tmp_path):
    root = _tree(tmp_path, "plugins/x/old.md", "The 10-phase SDLC and S02.5.\n")
    (root / "CHANGELOG.md").write_text("The 7-gate system.\n", encoding="utf-8")
    code, out = _run(root)
    assert code == 0, out


def test_missing_canonical_table_fails(tmp_path):
    (tmp_path / "README.md").write_text("Hello\n", encoding="utf-8")
    code, out = _run(tmp_path)
    assert code == 1
    assert "loki-sdlc-phases.md" in out


def test_incomplete_canonical_table_fails(tmp_path):
    canon = tmp_path / CANON
    canon.parent.mkdir(parents=True)
    table = _canon_table().replace("| S13 |", "| S14 |")
    canon.write_text(table, encoding="utf-8")
    code, out = _run(tmp_path)
    assert code == 1
    assert "S00..S13" in out

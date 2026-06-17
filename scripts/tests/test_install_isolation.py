# SPDX-License-Identifier: Apache-2.0
"""Isolation tests (Track D): install writes ONLY inside the target, and an
unselected agent receives zero files."""

from pathlib import Path

from gabbe import installer


def _make_source(tmp_path: Path) -> Path:
    src = tmp_path / "kit"
    src.mkdir()
    (src / "AGENTS.md").write_text("# kit\n")
    return src


def test_nothing_written_outside_target(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    # A sibling area outside the target with a sentinel file.
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "DO_NOT_TOUCH"
    sentinel.write_text("untouched")
    outside_before = {
        str(p.relative_to(outside)): p.read_bytes() for p in outside.rglob("*") if p.is_file()
    }

    installer.install_kit(target, source, ["claude"])

    outside_after = {
        str(p.relative_to(outside)): p.read_bytes() for p in outside.rglob("*") if p.is_file()
    }
    assert outside_after == outside_before  # zero writes outside the target


def test_unselected_agent_gets_zero_files(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    installer.install_kit(target, source, ["claude"])
    assert (target / ".gabbe-agents" / "claude.md").exists()
    assert not (target / ".gabbe-agents" / "cursor.md").exists()

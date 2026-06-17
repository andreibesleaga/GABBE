# SPDX-License-Identifier: Apache-2.0
"""Isolation tests (Track D): install writes ONLY inside the target, and an
unselected agent receives zero files."""

import json
from pathlib import Path

import pytest

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


@pytest.mark.parametrize("bad", ["../../etc/passwd", "a/b", "x..y", "", "Bad Name", ".hidden"])
def test_malicious_agent_names_are_rejected(tmp_path, bad):
    """Agent slugs build file paths, so traversal/separator names must be refused."""
    source = _make_source(tmp_path)
    with pytest.raises(ValueError):
        installer.install_kit(tmp_path / "proj", source, [bad])


def test_tampered_manifest_path_cannot_escape_target(tmp_path):
    """A manifest entry pointing outside the target must never be acted on."""
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    installer.install_kit(target, source, ["claude"])

    # A file outside the target that a malicious manifest tries to delete.
    outside = tmp_path / "victim.txt"
    outside.write_text("precious")

    mp = installer.manifest_path(target)
    manifest = json.loads(mp.read_text())
    manifest["entries"].append(
        {"path": "../victim.txt", "kind": "copy", "agent": "claude", "backup_of": None}
    )
    mp.write_text(json.dumps(manifest))

    installer.uninstall(target)  # must NOT follow the escaping path
    assert outside.exists() and outside.read_text() == "precious"

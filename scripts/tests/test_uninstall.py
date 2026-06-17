# SPDX-License-Identifier: Apache-2.0
"""Uninstall tests (Track D): uninstall is byte-reversible (restores `.bak`,
leaves no leftovers), `--dry-run` changes nothing, and double-uninstall is safe."""

from pathlib import Path

from gabbe import installer


def _make_source(tmp_path: Path) -> Path:
    src = tmp_path / "kit"
    (src / "skills").mkdir(parents=True)
    (src / "AGENTS.md").write_text("# KIT AGENTS\n")
    (src / "skills" / "a.skill.md").write_text("kit\n")
    return src


def _snapshot(root: Path):
    return {
        str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()
    }


def test_uninstall_restores_pre_install_state(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    # A pre-existing user file that the install will shadow (must be restored).
    (target / "agents").mkdir(parents=True)
    (target / "agents" / "AGENTS.md").write_text("USER ORIGINAL\n")
    before = _snapshot(target)

    installer.install_kit(target, source, ["claude", "cursor"])
    assert _snapshot(target) != before  # install changed things

    installer.uninstall(target)
    after = _snapshot(target)
    assert after == before  # byte-identical to the pre-install state
    assert (target / "agents" / "AGENTS.md").read_text() == "USER ORIGINAL\n"


def test_dry_run_changes_nothing(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    installer.install_kit(target, source, ["claude"])
    snap = _snapshot(target)
    removed = installer.uninstall(target, dry_run=True)
    assert removed  # reports what it WOULD remove
    assert _snapshot(target) == snap  # but changed nothing


def test_double_uninstall_is_safe(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    installer.install_kit(target, source, ["claude"])
    installer.uninstall(target)
    # Second uninstall on already-clean state must not raise.
    assert installer.uninstall(target) == []

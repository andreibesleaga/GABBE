# SPDX-License-Identifier: Apache-2.0
"""remove-agents tests (Track D): deselecting an agent removes only that agent's
wiring; the shared kit and other agents stay intact."""

from pathlib import Path

from gabbe import installer


def _make_source(tmp_path: Path) -> Path:
    src = tmp_path / "kit"
    src.mkdir()
    (src / "AGENTS.md").write_text("# kit\n")
    return src


def test_remove_agents_scoped(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    installer.install_kit(target, source, ["claude", "cursor", "gemini"])

    removed = installer.remove_agents(target, ["cursor"])

    assert ".gabbe-agents/cursor.md" in removed
    assert not (target / ".gabbe-agents" / "cursor.md").exists()
    # Other agents + shared kit untouched.
    assert (target / ".gabbe-agents" / "claude.md").exists()
    assert (target / ".gabbe-agents" / "gemini.md").exists()
    assert (target / "agents" / "AGENTS.md").exists()
    # Manifest no longer lists the removed agent.
    manifest = installer.read_manifest(target)
    assert "cursor" not in manifest["agents"]
    assert "claude" in manifest["agents"]

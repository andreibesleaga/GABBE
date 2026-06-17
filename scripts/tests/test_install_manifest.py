# SPDX-License-Identifier: Apache-2.0
"""Install-manifest tests (Track D): the manifest records every created path and
re-install is idempotent (no duplicates / orphans)."""

from pathlib import Path

from gabbe import installer


def _make_source(tmp_path: Path) -> Path:
    src = tmp_path / "kit"
    (src / "skills" / "core").mkdir(parents=True)
    (src / "AGENTS.md").write_text("# AGENTS\n")
    (src / "skills" / "core" / "clarify.skill.md").write_text("---\nname: clarify\n---\n")
    return src


def test_manifest_records_every_created_path(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    manifest = installer.install_kit(target, source, ["claude", "cursor"])

    assert installer.manifest_path(target).exists()
    # Every recorded path exists on disk with a hash and a kind.
    for entry in manifest["entries"]:
        assert (target / entry["path"]).exists()
        assert entry["kind"] in {"copy", "skill-emit", "symlink", "dir"}
        assert entry["hash"]
    # The two shared kit files + one wiring stub per agent are all present.
    paths = {e["path"] for e in manifest["entries"]}
    assert "agents/AGENTS.md" in paths
    assert "agents/skills/core/clarify.skill.md" in paths
    assert ".gabbe-agents/claude.md" in paths
    assert ".gabbe-agents/cursor.md" in paths


def test_reinstall_is_idempotent(tmp_path):
    source = _make_source(tmp_path)
    target = tmp_path / "proj"
    installer.install_kit(target, source, ["claude"])
    manifest2 = installer.install_kit(target, source, ["claude"])
    # No duplicate entries for the same path.
    paths = [e["path"] for e in manifest2["entries"]]
    assert len(paths) == len(set(paths))

# SPDX-License-Identifier: Apache-2.0
"""Install, edit, update, uninstall round trips in a project that has its own files.

Release 1.1.4. Each test states one promise of the installers:
  * a file the user wrote is never deleted and never overwritten without a backup;
  * a backup is never overwritten;
  * update keeps the earlier install record and the user's changes;
  * uninstall removes only what an install recorded.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# scripts/ importable (mirrors test_init.py).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

from gabbe import installer  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_KIT_SOURCE = init.KIT_SOURCE


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clean_wizard_recorder():
    """The wizard keeps its install record in module globals (one process = one
    install). Tests share a process, so each starts with an empty recorder."""
    init._MANIFEST_ENTRIES.clear()
    init._RECORDED_PATHS.clear()
    init._PRIOR_CACHE.clear()
    yield


def _kit(tmp_path: Path, version: str = "v1") -> Path:
    """A three-file kit source: an entry file, the constitution, one skill."""
    src = tmp_path / f"kit-{version}"
    (src / "skills").mkdir(parents=True)
    (src / "AGENTS.md").write_text(f"KIT AGENTS {version}\n")
    (src / "CONSTITUTION.md").write_text(f"KIT LAW {version}\n")
    (src / "skills" / "a.skill.md").write_text(f"kit skill {version}\n")
    return src


def _snapshot(root: Path) -> dict:
    """Every file and link under `root`: bytes for files, target for links."""
    snap = {}
    for p in sorted(root.rglob("*")):
        rel = str(p.relative_to(root))
        if p.is_symlink():
            snap[rel] = ("link", os.readlink(p))
        elif p.is_file():
            snap[rel] = ("file", p.read_bytes())
    return snap


def _entries(target: Path) -> dict:
    return {e["path"]: e for e in installer.read_manifest(target)["entries"]}


def _add_entry(target: Path, entry: dict) -> None:
    """Add one entry to the manifest, as another installer would have recorded it."""
    manifest = installer.read_manifest(target)
    manifest["entries"].append(entry)
    installer._write_manifest(target, manifest)


WIZARD_INPUTS = [
    "1",  # Install: Local
    "1",  # Mode: Greenfield build (asked because the project has source files)
    "MyTestProj",  # Name
    "Modern SaaS",  # Desc
    "2",  # Team: Small
    "1",  # Type: Greenfield
    "1",  # Lang: TypeScript
    "Next.js",  # Framework
    "1",  # DB: PostgreSQL
    "4",  # Cloud: Vercel
    "n",  # Dynamic Setup: No (writes SETUP_MISSION.md)
    "y",  # Analytics
    "y",  # Meta
    "n",  # GABBE CLI: No
    "1",  # PM: npm
    "1,2,7",  # Agents: Claude Code, Cursor, Gemini
]


def _run_wizard(project: Path, inputs=WIZARD_INPUTS) -> None:
    original_cwd = os.getcwd()
    os.chdir(project)
    init.PROJECT_ROOT = Path(project)
    init.TECH_MAP = {}
    init.FORCE = False
    init.KIT_SOURCE = ORIGINAL_KIT_SOURCE
    init.SOURCE_AGENTS_DIR = ORIGINAL_KIT_SOURCE / "agents"
    try:
        with patch("builtins.input", side_effect=list(inputs)):
            init.main()
    finally:
        os.chdir(original_cwd)


# --------------------------------------------------------------------------
# Backups
# --------------------------------------------------------------------------


def test_a_backup_is_never_overwritten(tmp_path):
    f = tmp_path / "notes.md"
    f.write_text("first\n")
    first = installer.backup_file(f)
    f.write_text("second\n")
    second = installer.backup_file(f)

    assert first.name == "notes.md.gabbe-bak" and first.read_text() == "first\n"
    assert second.name == "notes.md.gabbe-bak.1" and second.read_text() == "second\n"


def test_wizard_merge_keeps_every_version_the_user_wrote(tmp_path):
    """Two edits between three installs give two backups; none is lost."""
    src = _kit(tmp_path)
    dst = tmp_path / "proj" / "agents"
    init.PROJECT_ROOT = tmp_path / "proj"
    skill = dst / "skills" / "a.skill.md"

    init.safe_merge_directory(src, dst, force=False)
    skill.write_text("EDIT 1\n")
    init.safe_merge_directory(src, dst, force=False)
    skill.write_text("EDIT 2\n")
    init.safe_merge_directory(src, dst, force=False)

    assert skill.read_text() == "kit skill v1\n"
    assert Path(str(skill) + ".gabbe-bak").read_text() == "EDIT 1\n"
    assert Path(str(skill) + ".gabbe-bak.1").read_text() == "EDIT 2\n"


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------


def test_update_keeps_user_edits_to_preserved_files(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    (target / "agents" / "AGENTS.md").write_text("MY PROJECT RULES\n")
    (target / "agents" / "CONSTITUTION.md").write_text("MY LAW\n")

    installer.update_kit(target, _kit(tmp_path, "v2"))

    assert (target / "agents" / "AGENTS.md").read_text() == "MY PROJECT RULES\n"
    assert (target / "agents" / "CONSTITUTION.md").read_text() == "MY LAW\n"


def test_update_refreshes_preserved_files_the_user_never_changed(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])

    installer.update_kit(target, _kit(tmp_path, "v2"))

    assert (target / "agents" / "CONSTITUTION.md").read_text() == "KIT LAW v2\n"
    assert not list(target.rglob("*.gabbe-bak*"))  # nothing was changed, nothing backed up


def test_update_backs_up_an_edited_kit_file_before_replacing_it(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    skill = target / "agents" / "skills" / "a.skill.md"
    skill.write_text("MY EDIT\n")

    installer.update_kit(target, _kit(tmp_path, "v2"))

    assert skill.read_text() == "kit skill v2\n"
    assert Path(str(skill) + ".gabbe-bak").read_text() == "MY EDIT\n"


def test_update_keeps_what_other_installers_recorded(tmp_path):
    """The earlier record is merged, not replaced: links, generated skill files and
    a directory recorded by an old release all survive, on disk and in the record."""
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    (target / ".claude" / "skills" / "tdd").mkdir(parents=True)
    emitted = target / ".claude" / "skills" / "tdd" / "SKILL.md"
    emitted.write_text("---\ngabbe-schema-version: 1\n---\n")
    os.symlink("agents/AGENTS.md", target / ".cursorrules")
    for entry in (
        {"path": ".cursorrules", "kind": "symlink", "agent": "shared", "backup_of": None},
        {"path": ".claude/skills", "kind": "tree", "agent": "claude-code", "backup_of": None},
    ):
        _add_entry(target, entry)

    installer.update_kit(target, _kit(tmp_path, "v2"))  # raised IsADirectoryError in 1.1.3

    assert (target / ".cursorrules").is_symlink()
    assert emitted.exists()
    recorded = _entries(target)
    assert recorded[".cursorrules"]["kind"] == "symlink"
    assert recorded[".claude/skills"]["kind"] == "tree"
    assert not (target / ".gabbe-agents").exists()  # no stub files invented for other installers


def test_update_adopts_an_unrecorded_install_without_backups(tmp_path):
    """An install made before installers wrote a record: same bytes, so no backups."""
    target = tmp_path / "proj"
    kit = _kit(tmp_path)
    installer.install_kit(target, kit, [])
    installer.manifest_path(target).unlink()

    installer.update_kit(target, kit)

    assert not list(target.rglob("*.bak")) and not list(target.rglob("*.gabbe-bak*"))
    assert "agents/skills/a.skill.md" in _entries(target)


def test_update_removes_a_dropped_kit_file_only_if_unchanged(tmp_path):
    kit_v1 = _kit(tmp_path)
    (kit_v1 / "skills" / "old.skill.md").write_text("old\n")
    (kit_v1 / "skills" / "old-edited.skill.md").write_text("old\n")
    target = tmp_path / "proj"
    installer.install_kit(target, kit_v1, [])
    (target / "agents" / "skills" / "old-edited.skill.md").write_text("MY EDIT\n")

    installer.update_kit(target, _kit(tmp_path, "v2"))

    assert not (target / "agents" / "skills" / "old.skill.md").exists()
    assert (target / "agents" / "skills" / "old-edited.skill.md").read_text() == "MY EDIT\n"


# --------------------------------------------------------------------------
# Uninstall
# --------------------------------------------------------------------------


def test_uninstall_of_an_old_tree_record_removes_only_generated_files(tmp_path):
    """Releases before 1.1.4 recorded `.claude/skills` as one directory and removed
    all of it, the user's own skills included."""
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    skills = target / ".claude" / "skills"
    (skills / "kit-skill").mkdir(parents=True)
    (skills / "kit-skill" / "SKILL.md").write_text("---\ngabbe-schema-version: 1\n---\nkit\n")
    (skills / "mine").mkdir()
    (skills / "mine" / "SKILL.md").write_text("MY OWN SKILL\n")
    _add_entry(
        target,
        {"path": ".claude/skills", "kind": "tree", "agent": "claude-code", "backup_of": None},
    )

    installer.uninstall(target)

    assert (skills / "mine" / "SKILL.md").read_text() == "MY OWN SKILL\n"
    assert not (skills / "kit-skill").exists()


def test_purge_keeps_memory_backups_and_the_users_own_files(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    kit = target / "agents"
    (kit / "memory").mkdir()
    (kit / "memory" / "notes.md").write_text("MY NOTES\n")
    (kit / "skills" / "mine.skill.md").write_text("MY SKILL\n")
    (kit / "skills" / "a.skill.md").write_text("MY EDIT\n")
    (kit / "AGENTS.md").write_text("MY PROJECT RULES\n")

    installer.uninstall(target, purge=True)

    left = {str(p.relative_to(target)) for p in target.rglob("*") if p.is_file()}
    assert left == {
        "agents/AGENTS.md",  # preserved file the user changed
        "agents/memory/notes.md",
        "agents/skills/mine.skill.md",
        "agents/skills/a.skill.md.gabbe-bak",  # the user's edit of a kit file
    }
    assert (kit / "skills" / "a.skill.md.gabbe-bak").read_text() == "MY EDIT\n"
    assert installer.remaining_kit_files(target) == sorted(left)


def test_purge_of_an_untouched_install_leaves_nothing(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    (target / "app.py").write_text("print(1)\n")
    before = _snapshot(target)
    installer.install_kit(target, _kit(tmp_path), ["claude"])

    installer.uninstall(target, purge=True)

    assert _snapshot(target) == before
    assert not (target / "agents").exists() and not (target / ".gabbe").exists()


def test_plain_uninstall_removes_preserved_kit_files_nobody_changed(tmp_path):
    """1.1.3 left `agents/CONSTITUTION.md` behind after every uninstall."""
    target = tmp_path / "proj"
    target.mkdir()
    (target / "app.py").write_text("print(1)\n")
    before = _snapshot(target)
    installer.install_kit(target, _kit(tmp_path), [])

    installer.uninstall(target)

    assert _snapshot(target) == before


def test_uninstall_keeps_a_file_the_user_put_where_a_link_was(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    os.symlink("agents/AGENTS.md", target / ".cursorrules")
    _add_entry(
        target, {"path": ".cursorrules", "kind": "symlink", "agent": "shared", "backup_of": None}
    )
    (target / ".cursorrules").unlink()
    (target / ".cursorrules").write_text("MY OWN RULES NOW\n")

    installer.uninstall(target)

    assert (target / ".cursorrules").read_text() == "MY OWN RULES NOW\n"


def test_dry_run_lists_exactly_what_a_real_run_removes(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), ["claude"])
    (target / "agents" / "AGENTS.md").write_text("MY PROJECT RULES\n")
    before = _snapshot(target)

    planned = installer.uninstall(target, dry_run=True, purge=True)

    assert _snapshot(target) == before
    assert planned == installer.uninstall(target, purge=True)
    assert "agents/AGENTS.md" not in planned  # changed by the user: kept


def test_uninstall_takes_the_pointer_block_out_and_restores_the_original(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    original = "MY RULES\nno trailing newline"
    own = target / "AGENTS.md"
    own.write_text(original)
    init.PROJECT_ROOT = target
    init.add_pointer_block(own, "agents/AGENTS.md")
    assert init.POINTER_BEGIN in own.read_text() and own.read_text().startswith(original)
    init.write_install_manifest()

    installer.uninstall(target)

    assert own.read_text() == original
    assert not (target / "AGENTS.md.gabbe-bak").exists()


def test_uninstall_keeps_edits_made_after_the_pointer_block_was_added(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    own = target / "AGENTS.md"
    own.write_text("MY RULES\n")
    init.PROJECT_ROOT = target
    init.add_pointer_block(own, "agents/AGENTS.md")
    init.write_install_manifest()
    own.write_text("NEW FIRST LINE\n" + own.read_text())

    installer.uninstall(target)

    assert own.read_text() == "NEW FIRST LINE\nMY RULES\n"
    assert (target / "AGENTS.md.gabbe-bak").read_text() == "MY RULES\n"  # backup kept


def test_cli_uninstall_without_a_record_fails_and_removes_nothing(tmp_path):
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "AGENTS.md").write_text("an install nobody recorded\n")
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT))

    result = subprocess.run(
        [sys.executable, "-m", "gabbe.main", "uninstall", "--dir", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 1
    assert "No install record" in result.stderr
    assert (tmp_path / "agents" / "AGENTS.md").exists()


# --------------------------------------------------------------------------
# The wizard in a project that already has its own files
# --------------------------------------------------------------------------


@pytest.fixture
def existing_project(tmp_path):
    proj = tmp_path / "proj"
    (proj / ".claude" / "skills" / "mine").mkdir(parents=True)
    (proj / ".cursor" / "rules").mkdir(parents=True)
    (proj / ".gemini").mkdir()
    (proj / "AGENTS.md").write_text("MY AGENTS FILE\n")
    (proj / ".cursorrules").write_text("MY CURSOR RULES\n")
    (proj / ".claude" / "skills" / "mine" / "SKILL.md").write_text("MY OWN SKILL\n")
    (proj / ".cursor" / "rules" / "mine.mdc").write_text("MY OWN RULE\n")
    (proj / ".gemini" / "settings.json").write_text('{"mcpServers": {"x": 1}}')
    (proj / "SETUP_MISSION.md").write_text("MY OWN MISSION NOTES\n")
    (proj / "app.js").write_text("console.log(1)\n")
    return proj


def test_wizard_keeps_the_users_instruction_files_and_points_them_at_the_kit(existing_project):
    _run_wizard(existing_project)

    for name in ("AGENTS.md", ".cursorrules"):
        own = existing_project / name
        assert not own.is_symlink()
        assert own.read_text().startswith("MY ")
        assert "`agents/AGENTS.md`" in own.read_text()
    assert (
        existing_project / ".gemini" / "settings.json"
    ).read_text() == '{"mcpServers": {"x": 1}}'
    assert (existing_project / "SETUP_MISSION.md.gabbe-bak").read_text() == "MY OWN MISSION NOTES\n"


def test_wizard_install_then_purge_gives_the_project_back_unchanged(existing_project):
    before = _snapshot(existing_project)

    _run_wizard(existing_project)
    assert (existing_project / "agents" / "skills").is_dir()
    installer.uninstall(existing_project, purge=True)

    after = _snapshot(existing_project)
    # The wizard fills in the kit's AGENTS.md and the project state file; a purge
    # keeps files that differ from what was copied. Everything else is as before.
    kept = {"agents/AGENTS.md", "agents/memory/PROJECT_STATE.md"}
    assert {k: v for k, v in after.items() if k not in kept} == before
    assert set(after) - set(before) <= kept


def test_wizard_install_edit_update_keeps_edits_and_wiring(existing_project):
    """`gabbe update` on a wizard install: stopped with an error in 1.1.3 after it
    had replaced AGENTS.md and CONSTITUTION.md and removed a wiring link."""
    _run_wizard(existing_project)
    kit = existing_project / "agents"
    with open(kit / "AGENTS.md", "a") as f:
        f.write("USER-EDIT\n")
    with open(kit / "CONSTITUTION.md", "a") as f:
        f.write("USER-LAW\n")
    wired_before = {
        k: v for k, v in _snapshot(existing_project).items() if not k.startswith("agents/")
    }
    recorded_before = set(_entries(existing_project))

    installer.update_kit(existing_project, ORIGINAL_KIT_SOURCE / "agents")

    assert (kit / "AGENTS.md").read_text().endswith("USER-EDIT\n")
    assert (kit / "CONSTITUTION.md").read_text().endswith("USER-LAW\n")
    wired_after = {
        k: v for k, v in _snapshot(existing_project).items() if not k.startswith("agents/")
    }
    wired_after.pop(".gabbe/manifest.json")
    wired_before.pop(".gabbe/manifest.json")
    assert wired_after == wired_before
    assert recorded_before <= set(_entries(existing_project))


def test_wizard_records_generated_skills_per_file_never_as_a_directory(existing_project):
    _run_wizard(existing_project)

    manifest = json.loads((existing_project / ".gabbe" / "manifest.json").read_text())
    assert not [e for e in manifest["entries"] if e["kind"] == "tree"]
    recorded = {e["path"] for e in manifest["entries"]}
    assert ".claude/skills/mine/SKILL.md" not in recorded
    assert any(p.startswith(".claude/skills/") and p.endswith("/SKILL.md") for p in recorded)


def test_second_wizard_run_keeps_the_link_to_the_users_original(existing_project):
    _run_wizard(existing_project)
    _run_wizard(existing_project, ["1", "y"] + WIZARD_INPUTS[1:])  # "y": merge into agents/

    assert _entries(existing_project)["AGENTS.md"]["backup_of"] == "AGENTS.md.gabbe-bak"
    installer.uninstall(existing_project, purge=True)
    assert (existing_project / "AGENTS.md").read_text() == "MY AGENTS FILE\n"
    assert (existing_project / ".cursorrules").read_text() == "MY CURSOR RULES\n"


# --------------------------------------------------------------------------
# Repository address written into AGENTS.md
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "remote, expected",
    [
        ("https://user:ghp_SECRETTOKEN1234567890@github.com/o/r.git", "https://github.com/o/r"),
        (
            "https://x-access-token:abc@gitlab.example.com:8443/g/p.git",
            "https://gitlab.example.com:8443/g/p",
        ),
        ("https://github.com/o/r.git", "https://github.com/o/r"),
        ("git@github.com:o/r.git", "https://github.com/o/r"),
        ("ssh://git@github.com/o/r.git", "ssh://github.com/o/r"),
        ('https://github.com/o/r"\nevil: "x', None),
        ("", None),
    ],
)
def test_repo_url_never_carries_credentials(remote, expected):
    assert init._clean_repo_url(remote) == expected

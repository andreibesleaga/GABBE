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
import shutil
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


def test_update_on_an_unrecorded_install_makes_no_backups_and_claims_nothing(tmp_path):
    """Files that were there before any record and equal the kit's: no backup, and
    not recorded, so a later uninstall leaves them (it removes only what it wrote)."""
    target = tmp_path / "proj"
    kit = _kit(tmp_path)
    installer.install_kit(target, kit, [])
    installer.manifest_path(target).unlink()
    before = _snapshot(target)

    installer.update_kit(target, kit)

    assert not list(target.rglob("*.bak")) and not list(target.rglob("*.gabbe-bak*"))
    assert "agents/skills/a.skill.md" not in _entries(target)
    installer.uninstall(target, purge=True)
    assert _snapshot(target) == before


def test_install_never_writes_through_a_link_at_a_kit_path(tmp_path):
    outside = tmp_path / "elsewhere.md"
    outside.write_text("A FILE OUTSIDE THE PROJECT\n")
    target = tmp_path / "proj"
    (target / "agents" / "skills").mkdir(parents=True)
    link = target / "agents" / "skills" / "a.skill.md"
    os.symlink(outside, link)

    installer.install_kit(target, _kit(tmp_path), [])
    installer.update_kit(target, _kit(tmp_path, "v2"))

    assert outside.read_text() == "A FILE OUTSIDE THE PROJECT\n"
    assert link.is_symlink() and "agents/skills/a.skill.md" not in _entries(target)
    installer.uninstall(target, purge=True)
    assert link.is_symlink() and outside.exists()


def test_install_refuses_a_kit_folder_that_links_outside_the_project(tmp_path):
    shared = tmp_path / "shared-agents"
    shared.mkdir()
    target = tmp_path / "proj"
    target.mkdir()
    os.symlink(shared, target / "agents")

    with pytest.raises(ValueError, match="outside"):
        installer.install_kit(target, _kit(tmp_path), [])

    assert list(shared.iterdir()) == []


def test_a_file_already_at_a_stub_path_is_backed_up_and_restored(tmp_path):
    target = tmp_path / "proj"
    (target / ".gabbe-agents").mkdir(parents=True)
    own = target / ".gabbe-agents" / "claude.md"
    own.write_text("MY OWN NOTES\n")

    installer.install_kit(target, _kit(tmp_path), ["claude"])
    assert own.read_text().startswith("# GABBE wiring")
    installer.uninstall(target)

    assert own.read_text() == "MY OWN NOTES\n"


def test_uninstall_leaves_a_link_the_user_put_where_a_kit_file_was(tmp_path):
    outside = tmp_path / "elsewhere.md"
    outside.write_text("OUTSIDE\n")
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    skill = target / "agents" / "skills" / "a.skill.md"
    skill.unlink()
    os.symlink(outside, skill)

    installer.uninstall(target)

    assert skill.is_symlink() and outside.read_text() == "OUTSIDE\n"


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
        "agents/skills/a.skill.md",  # the user's edit of a kit file stays where it is
    }
    assert (kit / "skills" / "a.skill.md").read_text() == "MY EDIT\n"
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


def test_wizard_merge_never_copies_through_a_link(tmp_path):
    outside_file = tmp_path / "elsewhere.md"
    outside_file.write_text("OUTSIDE FILE\n")
    outside_dir = tmp_path / "elsewhere"
    outside_dir.mkdir()
    src = _kit(tmp_path)
    dst = tmp_path / "proj" / "agents"
    dst.mkdir(parents=True)
    init.PROJECT_ROOT = tmp_path / "proj"
    os.symlink(outside_file, dst / "CONSTITUTION.md")
    os.symlink(outside_dir, dst / "skills")

    init.safe_merge_directory(src, dst, force=True)

    assert outside_file.read_text() == "OUTSIDE FILE\n"
    assert list(outside_dir.iterdir()) == []
    assert (dst / "CONSTITUTION.md").is_symlink() and (dst / "skills").is_symlink()
    assert (dst / "AGENTS.md").read_text() == "KIT AGENTS v1\n"  # the rest is installed


def test_wizard_never_writes_a_generated_file_through_a_link(tmp_path):
    outside = tmp_path / "elsewhere.md"
    outside.write_text("OUTSIDE FILE\n")
    proj = tmp_path / "proj"
    proj.mkdir()
    init.PROJECT_ROOT = proj
    os.symlink(outside, proj / "SETUP_MISSION.md")

    init.write_generated_file(proj / "SETUP_MISSION.md", "the mission\n")

    assert outside.read_text() == "OUTSIDE FILE\n"
    assert (proj / "SETUP_MISSION.md").is_symlink()


def test_wizard_keeps_a_link_of_the_users_at_a_wiring_path(tmp_path):
    """`AGENTS.md -> CLAUDE.md` is a common setup; 1.1.3 removed the link."""
    proj = tmp_path / "proj"
    (proj / "agents").mkdir(parents=True)
    (proj / "agents" / "AGENTS.md").write_text("KIT AGENTS\n")
    (proj / "CLAUDE.md").write_text("MY RULES\n")
    os.symlink("CLAUDE.md", proj / "AGENTS.md")
    init.PROJECT_ROOT = proj

    init.create_symlink(proj / "agents" / "AGENTS.md", proj / "AGENTS.md")

    assert os.readlink(proj / "AGENTS.md") == "CLAUDE.md"
    assert (proj / "CLAUDE.md").read_text() == "MY RULES\n"


def test_wizard_stops_when_a_backup_cannot_be_made(tmp_path):
    """Without a backup the file would be the user's only copy: nothing is overwritten."""
    # One file only: the order in which a folder is listed differs between filesystems,
    # and the failing copy below must be the backup, not an ordinary kit copy.
    src = tmp_path / "kit-one-file"
    src.mkdir()
    (src / "README.md").write_text("KIT README\n")
    dst = tmp_path / "proj" / "agents"
    dst.mkdir(parents=True)
    init.PROJECT_ROOT = tmp_path / "proj"
    (dst / "README.md").write_text("MY README\n")

    with patch("shutil.copy2", side_effect=OSError("disk full")):
        with pytest.raises(SystemExit, match="Could not back up"):
            init.safe_merge_directory(src, dst, force=False)

    assert (dst / "README.md").read_text() == "MY README\n"


# --------------------------------------------------------------------------
# Findings of the independent test round (21 Nov 2026)
# --------------------------------------------------------------------------


def test_wizard_skill_compiler_never_writes_through_a_link(existing_project, tmp_path):
    """A link at a skill or rule path is the user's; 1.1.3 overwrote its target."""
    outside = tmp_path / "outside"
    (outside / "adir").mkdir(parents=True)
    (outside / "rule.md").write_text("OUTSIDE RULE\n")
    (outside / "notes.md").write_text("OUTSIDE NOTES\n")
    (existing_project / ".claude" / "skills" / "tdd-cycle").mkdir()
    os.symlink(outside / "rule.md", existing_project / ".cursor" / "rules" / "tdd-cycle.mdc")
    os.symlink(
        outside / "notes.md", existing_project / ".claude" / "skills" / "tdd-cycle" / "SKILL.md"
    )
    os.symlink(outside / "adir", existing_project / ".claude" / "skills" / "research")

    _run_wizard(existing_project)

    assert (outside / "rule.md").read_text() == "OUTSIDE RULE\n"
    assert (outside / "notes.md").read_text() == "OUTSIDE NOTES\n"
    assert list((outside / "adir").iterdir()) == []
    assert (existing_project / ".cursor" / "rules" / "tdd-cycle.mdc").is_symlink()


def test_wizard_copies_nothing_into_an_agents_folder_that_is_a_link(tmp_path):
    shared = tmp_path / "shared-kit"
    shared.mkdir()
    (shared / "mine.txt").write_text("MINE\n")
    proj = tmp_path / "proj"
    proj.mkdir()
    os.symlink(shared, proj / "agents")

    try:
        _run_wizard(proj, WIZARD_INPUTS[:1] + WIZARD_INPUTS[2:])  # empty project: no Mode question
    except (SystemExit, Exception):
        pass  # with no kit behind the link the wizard may stop; it must not copy first

    assert not (shared / "skills").exists() and not (shared / "guides").exists()
    assert (shared / "mine.txt").read_text() == "MINE\n"


def test_a_read_only_instruction_file_is_left_alone_and_the_install_goes_on(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    init.PROJECT_ROOT = proj
    own = proj / "AGENTS.md"
    own.write_text("READ ONLY RULES\n")
    own.chmod(0o444)
    if os.access(own, os.W_OK):
        pytest.skip("running as a user for whom read-only files are writable")

    init.add_pointer_block(own, "agents/AGENTS.md")

    assert own.read_text() == "READ ONLY RULES\n"
    assert not (proj / "AGENTS.md.gabbe-bak").exists()


@pytest.mark.parametrize(
    "original",
    [
        b"MY RULES\n",
        b"a\r\nb\r\n",  # Windows line ends
        b"caf\xe9 latin-1\n",  # not UTF-8
        b"",
    ],
)
def test_pointer_block_round_trip_is_exact_to_the_byte(tmp_path, original):
    blocked = init.with_pointer_block(original, "agents/AGENTS.md")
    assert blocked.startswith(original) and init.POINTER_BEGIN.encode() in blocked
    assert (b"\r\n" in blocked) == (b"\r\n" in original)  # the file's own line end is used

    assert installer.strip_pointer_block(blocked) == original
    assert init.without_pointer_block(blocked) == original


def test_uninstall_keeps_the_bytes_of_text_added_around_the_pointer_block(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    init.PROJECT_ROOT = target
    own = target / "AGENTS.md"
    own.write_bytes(b"a\r\nb\r\n")
    init.add_pointer_block(own, "agents/AGENTS.md")
    init.write_install_manifest()
    own.write_bytes(own.read_bytes() + b"caf\xe9\r\n")

    installer.uninstall(target)

    assert own.read_bytes() == b"a\r\nb\r\ncaf\xe9\r\n"


def test_force_after_a_pointer_block_restores_the_original_on_uninstall(tmp_path):
    """A second run with --force replaced the file by a link and backed up the copy
    that carried the block; uninstall then put the block back."""
    proj = tmp_path / "proj"
    (proj / "agents").mkdir(parents=True)
    kit_file = proj / "agents" / "AGENTS.md"
    kit_file.write_text("KIT AGENTS\n")
    own = proj / "AGENTS.md"
    own.write_text("MY RULES\n")
    init.PROJECT_ROOT = proj
    init.create_symlink(kit_file, own)
    init.write_install_manifest()
    assert init.POINTER_BEGIN in own.read_text()

    init._MANIFEST_ENTRIES.clear()
    init._RECORDED_PATHS.clear()
    init.FORCE = True
    try:
        init.create_symlink(kit_file, own)
        init.write_install_manifest()
    finally:
        init.FORCE = False
    assert own.is_symlink()

    installer.uninstall(proj)

    assert not own.is_symlink() and own.read_text() == "MY RULES\n"
    assert not list(proj.glob("AGENTS.md.*"))


def test_a_recorded_file_that_became_a_folder_stops_nothing(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    skill = target / "agents" / "skills" / "a.skill.md"
    skill.unlink()
    skill.mkdir()
    (skill / "note.txt").write_text("MINE\n")

    installer.update_kit(target, _kit(tmp_path, "v2"))  # raised IsADirectoryError
    planned = installer.uninstall(target, dry_run=True)
    removed = installer.uninstall(target)

    assert planned == removed and "agents/skills/a.skill.md" not in removed
    assert (skill / "note.txt").read_text() == "MINE\n"


@pytest.mark.parametrize("damaged", ['{"entries": [', "", '{"entries": "x"}', "[1, 2]"])
def test_a_damaged_record_is_never_acted_on_and_never_deleted(tmp_path, damaged):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    record = installer.manifest_path(target)
    record.write_text(damaged)
    before = _snapshot(target)

    assert installer.uninstall(target, purge=True) == []
    with pytest.raises(ValueError, match="damaged"):
        installer.update_kit(target, _kit(tmp_path, "v2"))
    result = subprocess.run(
        [sys.executable, "-m", "gabbe.main", "uninstall", "--dir", str(target)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=dict(os.environ, PYTHONPATH=str(REPO_ROOT)),
    )

    assert result.returncode == 1 and "damaged" in result.stderr
    assert _snapshot(target) == before


def test_cli_dry_run_prints_every_path(tmp_path):
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])

    result = subprocess.run(
        [sys.executable, "-m", "gabbe.main", "uninstall", "--dry-run", "--dir", str(target)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=dict(os.environ, PYTHONPATH=str(REPO_ROOT)),
    )

    assert result.returncode == 0
    assert "  agents/skills/a.skill.md" in result.stdout.splitlines()
    assert "Would remove 3 path(s)" in result.stdout
    assert (target / "agents" / "skills" / "a.skill.md").exists()


def test_plain_uninstall_leaves_no_empty_kit_folders(tmp_path):
    kit = _kit(tmp_path)
    (kit / "memory" / "episodic").mkdir(parents=True)  # the kit ships some empty folders
    target = tmp_path / "proj"
    target.mkdir()
    shutil.copytree(kit, target / "agents")  # as the wizard's first copy does
    installer.update_kit(target, kit)
    for p in sorted((target / "agents").rglob("*")):
        if p.is_file():
            p.unlink()

    installer.uninstall(target)

    assert not (target / "agents").exists()


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


# --------------------------------------------------------------------------
# 1.2.0: the Node `uninstall` agrees with the Python CLI; per-agent records
# --------------------------------------------------------------------------

INSTALL_JS = REPO_ROOT / "bin" / "install.js"


def _node_or_skip() -> str:
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available")
    return node


def _python_cli_or_skip() -> None:
    probe = subprocess.run(
        [sys.executable, "-m", "gabbe.main", "uninstall", "--help"],
        capture_output=True,
        cwd=REPO_ROOT,
        env=dict(os.environ, PYTHONPATH=str(REPO_ROOT)),
    )
    if probe.returncode != 0:
        pytest.skip("the Python CLI dependencies are not installed")


def _node_cli(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_node_or_skip(), str(INSTALL_JS), *args],
        capture_output=True,
        text=True,
        cwd=project,
        env=dict(os.environ, HOME=str(project.parent / "home")),
    )


def _python_cli(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "gabbe.main", "uninstall", "--dir", str(project), *args],
        capture_output=True,
        text=True,
        cwd=project.parent,
        env=dict(os.environ, PYTHONPATH=str(REPO_ROOT)),
    )


def _path_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.startswith("  ")]


def _count_line(output: str) -> str:
    """The "Removed N path(s)" / "Would remove N path(s)" line without the folder."""
    line = next(x for x in output.splitlines() if x.startswith(("Removed ", "Would remove ")))
    return line.split(" from ")[0]


def _record_of(tree: dict):
    """Pop the install record out of a `_snapshot` and return it parsed (or None)."""
    entry = tree.pop(".gabbe/manifest.json", None)
    return json.loads(entry[1]) if entry else None


@pytest.fixture
def node_project(tmp_path):
    """A project with files of its own, installed by the Node installer for three agents."""
    _node_or_skip()
    proj = tmp_path / "proj"
    (proj / ".claude" / "skills" / "mine").mkdir(parents=True)
    (proj / ".claude" / "skills" / "mine" / "SKILL.md").write_text("MY OWN SKILL\n")
    (proj / "AGENTS.md").write_text("MY AGENTS FILE\n")
    (proj / ".cursorrules").write_text("MY CURSOR RULES\r\n")
    (proj / "app.js").write_text("console.log(1)\n")
    done = _node_cli(proj, "init", "--yes", "--agents", "claude,cursor,windsurf")
    assert done.returncode == 0, done.stderr
    # An edit of a kit file and of a memory file: both must survive an uninstall.
    skill = proj / ".agents" / "skills" / "tdd-cycle" / "SKILL.md"
    skill.write_text(skill.read_text() + "MY EDIT\n")
    (proj / "agents" / "memory" / "PROJECT_STATE.md").write_text("MY NOTES\n")
    return proj


def test_node_and_python_uninstall_dry_runs_list_the_same_paths(node_project, tmp_path):
    _python_cli_or_skip()
    twin = tmp_path / "twin" / "proj"
    shutil.copytree(node_project, twin, symlinks=True)

    node = _node_cli(node_project, "uninstall", "--dry-run")
    py = _python_cli(twin, "--dry-run")

    assert node.returncode == 0 and py.returncode == 0, (node.stderr, py.stderr)
    assert _path_lines(node.stdout) == _path_lines(py.stdout)
    assert _count_line(node.stdout) == _count_line(py.stdout)
    assert len(_path_lines(node.stdout)) > 1000


@pytest.mark.parametrize("agents", [None, "cursor", "claude-code,windsurf"])
def test_node_and_python_uninstall_leave_the_same_tree(node_project, tmp_path, agents):
    _python_cli_or_skip()
    twin = tmp_path / "twin" / "proj"
    shutil.copytree(node_project, twin, symlinks=True)
    extra = ["--agents", agents] if agents else []

    node = _node_cli(node_project, "uninstall", *extra)
    py = _python_cli(twin, *extra)

    assert node.returncode == 0 and py.returncode == 0, (node.stderr, py.stderr)
    node_tree, py_tree = _snapshot(node_project), _snapshot(twin)
    # The record may differ in key order and line ends: compare what it says.
    assert _record_of(node_tree) == _record_of(py_tree)
    assert node_tree == py_tree
    assert _count_line(node.stdout) == _count_line(py.stdout)
    assert node.stderr == py.stderr
    if agents is None:
        assert (node_project / "AGENTS.md").read_text() == "MY AGENTS FILE\n"
        assert (node_project / "agents" / "memory" / "PROJECT_STATE.md").read_text() == "MY NOTES\n"
        # the user's edit of an installed file stays in place (it is not the recorded bytes)
        assert (
            "MY EDIT"
            in (node_project / ".agents" / "skills" / "tdd-cycle" / "SKILL.md").read_text()
        )


def test_node_and_python_refuse_a_damaged_or_missing_record_alike(tmp_path):
    _python_cli_or_skip()
    for name, content in (("missing", None), ("damaged", "{ not json")):
        proj = tmp_path / name
        proj.mkdir()
        if content is not None:
            (proj / ".gabbe").mkdir()
            (proj / ".gabbe" / "manifest.json").write_text(content)
        node = _node_cli(proj, "uninstall")
        py = _python_cli(proj)
        assert node.returncode == py.returncode == 1
        first = "damaged" if content else "No install record"
        assert first in node.stderr and first in py.stderr


def test_wizard_records_instruction_links_per_agent(existing_project):
    """`gabbe uninstall --agents cursor` must take the Cursor link and skills with it
    and leave Claude Code's: the links used to be recorded as `shared`."""
    (existing_project / ".cursorrules").unlink()  # a link, not the user's file
    _run_wizard(existing_project)
    recorded = _entries(existing_project)
    assert recorded[".claude/CLAUDE.md"]["agent"] == "claude-code"
    assert recorded[".cursorrules"]["agent"] == "cursor"
    assert recorded["AGENTS.md"]["agent"] == "shared"

    installer.uninstall(existing_project, agents=["cursor"])

    assert not (existing_project / ".cursorrules").is_symlink()
    assert not (existing_project / ".cursorrules").exists()
    assert not [
        p for p in (existing_project / ".cursor" / "rules").glob("*.mdc") if p.name != "mine.mdc"
    ]
    assert (existing_project / ".claude" / "CLAUDE.md").is_symlink()
    assert (existing_project / ".claude" / "skills" / "tdd-cycle" / "SKILL.md").is_file()
    assert (existing_project / ".claude" / "skills" / "mine" / "SKILL.md").is_file()


WIZARD_THREE_AGENTS = WIZARD_INPUTS[:-1] + ["3,4,6"]  # Windsurf, Cline, Devin / Cognition


def test_wizard_emits_skill_folders_for_windsurf_cline_and_devin(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "app.js").write_text("1\n")
    _run_wizard(proj, WIZARD_THREE_AGENTS)

    for folder, slug in (
        (".windsurf", "windsurf"),
        (".cline", "cline"),
        (".devin", "devin---cognition"),
    ):
        skills = proj / folder / "skills"
        assert skills.is_dir() and not skills.is_symlink(), folder
        assert (skills / "tdd-cycle" / "SKILL.md").is_file(), folder
        assert _entries(proj)[f"{folder}/skills/tdd-cycle/SKILL.md"]["agent"] == slug
    assert _entries(proj)[".devinrules"]["agent"] == "devin---cognition"


def test_wizard_replaces_its_own_old_skills_link_by_a_folder(tmp_path):
    """Before 1.2.0 the wizard linked `.windsurf/skills` to `agents/skills`. That link is
    the kit's own (recorded): a new run replaces it by skill folders, the user's own
    folder that the link had replaced is put back, and an uninstall removes it all."""
    proj = tmp_path / "proj"
    (proj / ".windsurf").mkdir(parents=True)
    (proj / "app.js").write_text("1\n")
    _run_wizard(proj, WIZARD_THREE_AGENTS)
    # Rebuild what a 1.1.4 wizard left: a link, the user's folder moved to a backup name.
    manifest = installer.read_manifest(proj)
    manifest["entries"] = [
        e for e in manifest["entries"] if not e["path"].startswith(".windsurf/skills/")
    ]
    manifest["entries"].append(
        {
            "path": ".windsurf/skills",
            "kind": "symlink",
            "agent": "shared",
            "backup_of": ".windsurf/skills.bak",
        }
    )
    installer._write_manifest(proj, manifest)
    shutil.rmtree(proj / ".windsurf" / "skills")
    (proj / ".windsurf" / "skills").symlink_to("../agents/skills")
    (proj / ".windsurf" / "skills.bak" / "mine").mkdir(parents=True)
    (proj / ".windsurf" / "skills.bak" / "mine" / "SKILL.md").write_text("MY OWN SKILL\n")

    # The second run finds the first run's files: it asks to merge, and no package-manager
    # question (the "1" before the agents answer).
    _run_wizard(proj, ["1", "y"] + WIZARD_INPUTS[1:-2] + ["3,4,6"])

    skills = proj / ".windsurf" / "skills"
    assert skills.is_dir() and not skills.is_symlink()
    assert (skills / "tdd-cycle" / "SKILL.md").is_file()
    assert (skills / "mine" / "SKILL.md").read_text() == "MY OWN SKILL\n"
    assert ".windsurf/skills" not in _entries(proj)

    installer.uninstall(proj)
    assert (skills / "mine" / "SKILL.md").read_text() == "MY OWN SKILL\n"
    assert not (skills / "tdd-cycle").exists()


# --------------------------------------------------------------------------
# Renamed skills: stale generated copies are removed (wizard)
# --------------------------------------------------------------------------

_OLD_SKILL = "---\nname: old-name\ngabbe-schema-version: 1\n---\nold body\n"


def _add_old_generated(proj: Path, rel: str, text: str, recorded_text=None) -> None:
    """Simulate a 1.1.4 install: a generated file on disk and its record entry."""
    import hashlib

    path = proj / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    _add_entry(
        proj,
        {
            "path": rel,
            "kind": "copy",
            "agent": "claude-code",
            "backup_of": None,
            "hash": hashlib.sha256((recorded_text or text).encode()).hexdigest(),
        },
    )


def test_wizard_removes_a_stale_generated_skill_and_keeps_the_rest(existing_project, capsys):
    proj = existing_project
    _run_wizard(proj)
    _add_old_generated(proj, ".claude/skills/old-name/SKILL.md", _OLD_SKILL)
    _add_old_generated(proj, ".claude/skills/edited/SKILL.md", _OLD_SKILL + "MY EDIT\n", _OLD_SKILL)
    # Under a folder this second run does not emit into (the agents are Claude, Cursor, Gemini).
    _add_old_generated(proj, ".windsurf/skills/old-name/SKILL.md", _OLD_SKILL)
    capsys.readouterr()

    _run_wizard(proj, ["1", "y"] + WIZARD_INPUTS[1:])

    out = capsys.readouterr().out
    assert not (proj / ".claude" / "skills" / "old-name").exists()
    assert ".claude/skills/old-name/SKILL.md" not in _entries(proj)
    assert "Removed 1 generated file(s)" in out
    assert "MY EDIT" in (proj / ".claude" / "skills" / "edited" / "SKILL.md").read_text()
    assert ".claude/skills/edited/SKILL.md" in _entries(proj)
    assert "Kept 1 old generated file(s) you changed: .claude/skills/edited/SKILL.md" in out
    assert (proj / ".claude" / "skills" / "mine" / "SKILL.md").read_text() == "MY OWN SKILL\n"
    assert (proj / ".windsurf" / "skills" / "old-name" / "SKILL.md").is_file()
    assert ".windsurf/skills/old-name/SKILL.md" in _entries(proj)


# --------------------------------------------------------------------------
# `gabbe uninstall --agents` takes the short names of the Node installer
# --------------------------------------------------------------------------


def _node_alias_table() -> dict:
    import re

    text = INSTALL_JS.read_text()
    block = re.search(r"const AGENT_ALIASES = \{(.*?)\n\};", text, re.DOTALL).group(1)
    return dict(re.findall(r"^\s*'?([a-z-]+)'?:\s*'([^']+)',?\s*$", block, re.MULTILINE))


def test_python_agent_aliases_equal_the_node_table_and_slugs():
    node = _node_alias_table()
    assert node and node == installer.AGENT_ALIASES
    for alias, full in node.items():
        slug = "".join(c if (c.isalnum() or c in "-_") else "-" for c in full.lower())
        assert installer.agent_slug(alias) == slug.strip("-")
        assert installer.agent_slug(alias.upper()) == slug.strip("-")
    assert installer.agent_slug("Some-Other") == "Some-Other"
    assert installer.agent_slug("claude") == "claude-code"


def test_cli_uninstall_accepts_a_short_agent_name(node_project, tmp_path):
    _python_cli_or_skip()
    done = _python_cli(node_project, "--agents", "claude")
    assert done.returncode == 0, done.stderr
    assert not (node_project / ".claude" / "skills" / "tdd-cycle").exists()
    assert (node_project / ".cursorrules").exists()
    assert "no recorded agent matches" not in done.stdout


def test_cli_uninstall_names_the_recorded_agents_when_nothing_matches(node_project):
    _python_cli_or_skip()
    done = _python_cli(node_project, "--agents", "zed")
    assert done.returncode == 0, done.stderr
    assert "no recorded agent matches zed" in done.stdout
    assert "claude-code" in done.stdout
    assert "Removed 0 path(s)" in done.stdout


# --------------------------------------------------------------------------
# 1.2.0: optional hooks (--hooks), both installers, both uninstallers
# --------------------------------------------------------------------------

USER_SETTINGS = (
    '{\n  "model": "x",\n  "hooks": {"PreToolUse": '
    '[{"matcher":"Bash","hooks":[{"type":"command","command":"mine.sh"}]}]}\n}\n'
)
USER_GIT_HOOK = "#!/bin/sh\necho mine\n"


def _git_repo_with_user_hooks(proj: Path, settings: bool = True) -> None:
    proj.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=proj, check=True)
    (proj / "app.js").write_text("console.log(1)\n")
    (proj / ".git" / "hooks" / "pre-commit").write_text(USER_GIT_HOOK)
    if settings:
        (proj / ".claude").mkdir()
        (proj / ".claude" / "settings.json").write_text(USER_SETTINGS)


@pytest.fixture(params=["user-settings", "no-settings"])
def hooks_project(request, tmp_path):
    _node_or_skip()
    proj = tmp_path / "proj"
    _git_repo_with_user_hooks(proj, settings=request.param == "user-settings")
    done = _node_cli(proj, "init", "--yes", "--agents", "claude,cursor", "--hooks")
    assert done.returncode == 0, done.stderr
    return proj


def test_hooks_install_is_recorded_as_hook_merge_and_git_copy(hooks_project):
    entries = _entries(hooks_project)
    merge = entries[".claude/settings.json"]
    assert merge["kind"] == "hook-merge" and merge["agent"] == "claude-code"
    assert merge["fragment"] == "agents/hooks/claude-code/settings.fragment.json"
    if merge["created"]:
        assert merge["backup_of"] is None
    else:
        backup = hooks_project / merge["backup_of"]
        assert backup.read_text() == USER_SETTINGS  # the old CLI restores exactly this
    assert entries[".git/hooks/pre-push"]["kind"] == "copy"
    assert ".git/hooks/pre-commit" not in entries


def test_node_and_python_uninstall_dry_runs_agree_with_hooks(hooks_project, tmp_path):
    _python_cli_or_skip()
    twin = tmp_path / "twin" / "proj"
    shutil.copytree(hooks_project, twin, symlinks=True)
    node = _node_cli(hooks_project, "uninstall", "--dry-run")
    py = _python_cli(twin, "--dry-run")
    assert node.returncode == 0 and py.returncode == 0, (node.stderr, py.stderr)
    assert _path_lines(node.stdout) == _path_lines(py.stdout)
    assert "  .claude/settings.json" in _path_lines(node.stdout)
    assert "  .git/hooks/pre-push" in _path_lines(node.stdout)


def test_node_and_python_uninstall_leave_the_same_tree_with_hooks(hooks_project, tmp_path):
    _python_cli_or_skip()
    twin = tmp_path / "twin" / "proj"
    shutil.copytree(hooks_project, twin, symlinks=True)
    node = _node_cli(hooks_project, "uninstall")
    py = _python_cli(twin)
    assert node.returncode == 0 and py.returncode == 0, (node.stderr, py.stderr)
    node_tree, py_tree = _snapshot(hooks_project), _snapshot(twin)
    assert node_tree == py_tree
    assert node.stderr == py.stderr
    for tree in (node_tree, py_tree):
        assert tree[".git/hooks/pre-commit"] == ("file", USER_GIT_HOOK.encode())
        assert ".git/hooks/pre-push" not in tree
        assert ".cursor/hooks.json" not in tree
        if ".claude/settings.json" in tree:  # the user's file: back to its exact bytes
            assert tree[".claude/settings.json"] == ("file", USER_SETTINGS.encode())
        else:
            assert not (hooks_project / ".claude").exists()


def test_python_uninstall_keeps_what_the_user_added_to_the_settings_since(hooks_project):
    _python_cli_or_skip()
    settings = hooks_project / ".claude" / "settings.json"
    doc = json.loads(settings.read_text())
    doc["permissions"] = {"allow": ["Bash(ls)"]}
    doc["hooks"]["PreToolUse"].append({"matcher": "Write", "hooks": [{"command": "mine2.sh"}]})
    mine = sorted(
        h["command"]
        for g in doc["hooks"]["PreToolUse"]
        for h in g["hooks"]
        if "agents/hooks" not in h["command"]
    )
    settings.write_text(json.dumps(doc))
    done = _python_cli(hooks_project)
    assert done.returncode == 0, done.stderr
    left = json.loads(settings.read_text())
    assert left["permissions"] == {"allow": ["Bash(ls)"]}
    commands = [h["command"] for g in left["hooks"]["PreToolUse"] for h in g["hooks"]]
    assert sorted(commands) == mine and "mine2.sh" in mine
    assert not any("agents/hooks" in c for c in commands)


def test_old_cli_worst_case_restores_the_settings_the_user_had_before(hooks_project):
    """gabbe 1.1.4 does not know `hook-merge`: it deletes the path, then moves backup_of back.
    Whenever the file pre-existed, backup_of holds its exact bytes, so nothing is lost."""
    entry = _entries(hooks_project)[".claude/settings.json"]
    settings = hooks_project / ".claude" / "settings.json"
    if entry["created"]:
        pytest.skip("the installer created the file: nothing of the user's to lose")
    settings.unlink()
    shutil.move(str(hooks_project / entry["backup_of"]), str(settings))
    assert settings.read_text() == USER_SETTINGS


def test_wizard_hooks_flag_round_trip(tmp_path):
    proj = tmp_path / "proj"
    _git_repo_with_user_hooks(proj)
    (proj / "SETUP_MISSION.md").write_text("MY OWN MISSION NOTES\n")
    before = _snapshot(proj)

    with patch.object(sys, "argv", ["init.py", "--hooks"]):
        _run_wizard(proj)

    entries = _entries(proj)
    assert entries[".claude/settings.json"]["kind"] == "hook-merge"
    assert entries[".cursor/hooks.json"]["created"] is True
    assert entries[".git/hooks/pre-push"]["kind"] == "copy"
    settings = json.loads((proj / ".claude" / "settings.json").read_text())
    assert settings["model"] == "x" and len(settings["hooks"]["PreToolUse"]) == 3
    assert (proj / ".git" / "hooks" / "pre-commit").read_text() == USER_GIT_HOOK
    assert "GABBE-HOOK" in (proj / ".git" / "hooks" / "pre-push").read_text()

    installer.uninstall(proj, purge=True)
    after = _snapshot(proj)
    kept = {"agents/AGENTS.md", "agents/memory/PROJECT_STATE.md"}
    assert {k: v for k, v in after.items() if k not in kept and not k.startswith(".git/")} == {
        k: v for k, v in before.items() if not k.startswith(".git/")
    }
    assert after[".claude/settings.json"] == ("file", USER_SETTINGS.encode())
    assert after[".git/hooks/pre-commit"] == ("file", USER_GIT_HOOK.encode())
    assert ".git/hooks/pre-push" not in after


def test_wizard_without_the_flag_installs_no_hooks(tmp_path):
    proj = tmp_path / "proj"
    _git_repo_with_user_hooks(proj)
    with patch.object(sys, "argv", ["init.py"]):
        _run_wizard(proj)
    assert (proj / ".claude" / "settings.json").read_text() == USER_SETTINGS
    assert not (proj / ".cursor" / "hooks.json").exists()
    assert not (proj / ".git" / "hooks" / "pre-push").exists()
    assert not any(e["kind"] == "hook-merge" for e in _entries(proj).values())


# --------------------------------------------------------------------------
# The record is untrusted: honest installs still come back byte for byte
# --------------------------------------------------------------------------


def _tree_with_dirs(root: Path) -> dict:
    """`_snapshot` plus the folders (an empty folder left behind is a difference)."""
    snap = _snapshot(root)
    snap.update(
        {
            f"{p.relative_to(root)}/": ("dir", "")
            for p in root.rglob("*")
            if p.is_dir() and not p.is_symlink()
        }
    )
    snap.pop(".git/", None)
    return {k: v for k, v in snap.items() if not k.startswith(".git/") or k.endswith("pre-commit")}


@pytest.mark.parametrize("agents", ["claude", "claude,cursor,windsurf,cline"])
def test_python_uninstall_gives_back_a_node_install_with_hooks_byte_for_byte(tmp_path, agents):
    _node_or_skip()
    _python_cli_or_skip()
    proj = tmp_path / "proj"
    _git_repo_with_user_hooks(proj)
    (proj / "AGENTS.md").write_text("MY AGENTS FILE\n")
    before = _tree_with_dirs(proj)
    done = _node_cli(proj, "init", "--yes", "--agents", agents, "--hooks")
    assert done.returncode == 0, done.stderr

    undone = _python_cli(proj)

    assert undone.returncode == 0, undone.stderr
    assert "kept " not in undone.stdout and "skipped " not in undone.stdout, undone.stdout
    assert _tree_with_dirs(proj) == before


def test_python_uninstall_gives_back_a_python_install_byte_for_byte(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    (target / "app.py").write_text("print(1)\n")
    (target / ".gabbe-agents").mkdir()
    (target / ".gabbe-agents" / "claude.md").write_text("the user's own stub\n")
    before = _tree_with_dirs(target)
    installer.install_kit(target, _kit(tmp_path), ["claude", "cursor"])

    installer.uninstall(target)

    assert _tree_with_dirs(target) == before


def test_uninstall_keeps_a_wiring_link_that_points_outside_agents(tmp_path, capsys):
    """A recorded link is removed only when it points into the project's `agents/` folder."""
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    (tmp_path / "elsewhere.md").write_text("not the kit\n")
    os.symlink("../elsewhere.md", target / ".cursorrules")
    os.symlink("agents/AGENTS.md", target / "CLAUDE.md")
    for name in (".cursorrules", "CLAUDE.md"):
        _add_entry(target, {"path": name, "kind": "symlink", "agent": "shared", "backup_of": None})

    installer.uninstall(target)

    assert (target / ".cursorrules").is_symlink()  # kept
    assert not (target / "CLAUDE.md").is_symlink()  # the kit's own link: removed
    assert (
        "kept .cursorrules: the link does not point into the project's agents/"
        in capsys.readouterr().out
    )


def test_uninstall_restores_a_folder_backup_for_a_recorded_link(tmp_path):
    """The wizard moves a folder of the user's aside (`skills.bak`): a link entry may name it."""
    target = tmp_path / "proj"
    installer.install_kit(target, _kit(tmp_path), [])
    (target / ".windsurf" / "skills.bak" / "mine").mkdir(parents=True)
    (target / ".windsurf" / "skills.bak" / "mine" / "SKILL.md").write_text("MY SKILL\n")
    os.symlink("../agents/skills", target / ".windsurf" / "skills")
    _add_entry(
        target,
        {
            "path": ".windsurf/skills",
            "kind": "symlink",
            "agent": "windsurf",
            "backup_of": ".windsurf/skills.bak",
        },
    )

    installer.uninstall(target)

    assert (target / ".windsurf" / "skills" / "mine" / "SKILL.md").read_text() == "MY SKILL\n"
    assert not (target / ".windsurf" / "skills").is_symlink()

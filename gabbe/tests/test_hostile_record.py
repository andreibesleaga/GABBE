# SPDX-License-Identifier: Apache-2.0
"""A tampered `.gabbe/manifest.json` must never reach outside the project.

One table of hostile record entries (a path that climbs out, an absolute path, a path
through a planted link, a `backup_of` that points outside), each as a `tree`, `copy`,
`block` and `hook-merge` entry. For each: a sentinel-filled sibling folder next to the
project and a file above it. `uninstall`, `uninstall --dry-run` and `update` must leave
everything outside the project byte for byte as it was, the dry-run list must name nothing
outside, and the record's one honest entry must still be removed. The same table then runs
through the Node installer (skipped when `node` is not on PATH).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from gabbe import installer

REPO = Path(__file__).resolve().parents[2]
NODE = shutil.which("node")
SENTINEL = b"SENTINEL gabbe-schema-version: 1 keep me\n"
HOOK = {"matcher": "Bash", "hooks": [{"type": "command", "command": "node x.js"}]}
FRAGMENT = {"hooks": {"PreToolUse": [HOOK]}}
KINDS = ["tree", "copy", "block", "hook-merge"]
# path form -> the recorded path; {v} = the sibling folder, {leaf} = what to name inside it
PATH_FORMS = {
    "dotdot": "..",
    "x-dotdot-dotdot": "x/../..",
    "absolute": "{v}/{leaf}",
    "skills-climb": ".agents/skills/../../../victim/{leaf}",
    "agents-climb": "agents/../../victim/{leaf}",
    "stale-skill": ".agents/skills/../../../victim/SKILL.md",
    "through-link": "link/{leaf}",
}
BACKUP_FORMS = {
    "backup-absolute": "{v}/f.md",
    "backup-climb": "../victim/f.md",
    "backup-link": "link/f.md",
}


class World:
    """`world/proj` (the target), `world/victim` (sentinels), `world/top.txt`."""

    def __init__(self, tmp: Path):
        self.root = tmp / "world"
        self.proj = self.root / "proj"
        self.victim = self.root / "victim"
        for d in (self.proj / ".gabbe", self.proj / "agents", self.victim / "sub"):
            d.mkdir(parents=True)
        (self.root / "top.txt").write_bytes(SENTINEL)
        (self.victim / "f.md").write_bytes(SENTINEL)
        (self.victim / "SKILL.md").write_bytes(SENTINEL)
        (self.victim / "sub" / "g.md").write_bytes(SENTINEL)
        (self.victim / "settings.json").write_text(json.dumps({**FRAGMENT, "own": 1}))
        os.symlink("../victim", self.proj / "link")
        (self.proj / "agents" / "mine.md").write_bytes(b"honest kit file\n")

    def snapshot(self) -> dict[str, bytes | tuple[str, str]]:
        """Everything in the world except the project folder."""
        seen: dict[str, bytes | tuple[str, str]] = {}
        for p in sorted(self.root.rglob("*")):
            if self.proj in p.parents or p == self.proj:
                continue
            key = str(p.relative_to(self.root))
            if p.is_symlink():
                seen[key] = ("link", os.readlink(p))
            else:
                seen[key] = b"" if p.is_dir() else p.read_bytes()
        return seen

    def write_record(self, hostile: dict) -> None:
        honest = {
            "path": "agents/mine.md",
            "kind": "copy",
            "agent": "shared",
            "hash": hashlib.sha256(b"honest kit file\n").hexdigest(),
        }
        record = {"schema_version": 1, "agents": [], "entries": [hostile, honest]}
        (self.proj / ".gabbe" / "manifest.json").write_text(json.dumps(record))


def _entry(world: World, kind: str, path: str, backup_of: str | None = None) -> dict:
    entry: dict = {"path": path, "kind": kind, "agent": "shared", "backup_of": backup_of}
    if kind == "copy":
        entry["hash"] = hashlib.sha256(SENTINEL).hexdigest()
    if kind == "hook-merge":
        entry.update(fragment_doc=FRAGMENT, fragment="agents/hooks/x.json", created=False)
    return entry


def _cases():
    for name, form in PATH_FORMS.items():
        for kind in KINDS:
            if name == "stale-skill" and kind != "copy":
                continue  # the stale-file removal step only looks at copy entries
            leaf = "" if kind == "tree" else ("settings.json" if kind == "hook-merge" else "f.md")
            yield pytest.param(kind, form, leaf, None, id=f"{kind}-{name}")
    for name, form in BACKUP_FORMS.items():
        for kind in KINDS:
            yield pytest.param(kind, "agents/AGENTS.md", "", form, id=f"{kind}-{name}")


def _build(tmp_path: Path, kind: str, form: str, leaf: str, backup: str | None) -> World:
    world = World(tmp_path)
    path = form.format(v=world.victim, leaf=leaf).rstrip("/")
    backup_of = backup.format(v=world.victim) if backup else None
    (world.proj / "agents" / "AGENTS.md").write_bytes(SENTINEL)
    world.write_record(_entry(world, kind, path, backup_of))
    return world


def _small_kit(tmp_path: Path) -> Path:
    kit = tmp_path / "kit"
    (kit / "skills").mkdir(parents=True)
    (kit / "mine.md").write_text("new kit text\n")
    return kit


@pytest.mark.parametrize("kind,form,leaf,backup", list(_cases()))
def test_python_installer_never_touches_anything_outside(tmp_path, kind, form, leaf, backup):
    world = _build(tmp_path, kind, form, leaf, backup)
    before = world.snapshot()

    listed = installer.uninstall(world.proj, dry_run=True)
    for rel in listed:
        inside = (world.proj / rel).parent.resolve() / Path(rel).name
        assert world.proj.resolve() in inside.parents, f"dry run names {rel}"
    assert world.snapshot() == before

    installer.update_kit(world.proj, _small_kit(tmp_path))
    assert world.snapshot() == before

    installer.uninstall(world.proj)
    assert world.snapshot() == before
    # a single hostile entry does not stop the honest rest from being removed
    assert not (world.proj / "agents" / "mine.md").exists()


def _node(world: World, home: Path, *args: str) -> subprocess.CompletedProcess:
    env = {"HOME": str(home), "PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}
    assert NODE is not None  # the callers are skipped when node is not on PATH
    return subprocess.run(
        [NODE, str(REPO / "bin" / "install.js"), *args],
        cwd=world.proj,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


@pytest.mark.skipif(NODE is None, reason="node is not on PATH: the Node half is skipped")
@pytest.mark.parametrize("kind,form,leaf,backup", list(_cases()))
@pytest.mark.parametrize(
    "command", [["uninstall", "--dry-run"], ["update"], ["init"], ["uninstall"]]
)
def test_node_installer_never_touches_anything_outside(tmp_path, kind, form, leaf, backup, command):
    world = _build(tmp_path, kind, form, leaf, backup)
    home = tmp_path / "home"
    home.mkdir()
    before = world.snapshot()
    done = _node(world, home, *command)
    assert world.snapshot() == before, done.stdout[-600:] + done.stderr[-600:]
    if command[-1] == "--dry-run":
        assert "victim" not in done.stdout, "the dry-run list names a path outside"


def test_the_cli_uninstall_skips_the_hostile_entry_and_names_it(tmp_path):
    world = _build(tmp_path, "tree", "..", "", None)
    before = world.snapshot()
    env = {"HOME": str(tmp_path), "PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(REPO)}
    done = subprocess.run(
        [os.sys.executable, "-m", "gabbe.main", "uninstall"],
        cwd=world.proj,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    assert "skipped record entry '..'" in done.stderr
    assert world.snapshot() == before


# --- `update` writes the kit's new version beside a kept, changed file ---------------


def _kit(tmp_path: Path, constitution: str) -> Path:
    kit = tmp_path / "kit"
    kit.mkdir(exist_ok=True)
    (kit / "CONSTITUTION.md").write_text(constitution)
    (kit / "AGENTS.md").write_text("agents v1\n")
    (kit / "TASKS.md").write_text("tasks v1\n")
    return kit


def _installed(tmp_path: Path) -> tuple[Path, Path]:
    target = tmp_path / "proj"
    target.mkdir()
    kit = _kit(tmp_path, "constitution v1\n")
    installer.install_kit(target, kit, [])
    return target, kit


def test_update_writes_the_new_kit_version_beside_a_changed_constitution(tmp_path, capsys):
    target, kit = _installed(tmp_path)
    mine = target / "agents" / "CONSTITUTION.md"
    mine.write_text("my constitution\n")
    (kit / "CONSTITUTION.md").write_text("constitution v2\n")
    manifest = installer.update_kit(target, kit)
    new = target / "agents" / "CONSTITUTION.md.gabbe-new"
    assert mine.read_text() == "my constitution\n"
    assert new.read_text() == "constitution v2\n"
    assert capsys.readouterr().out.strip() == (
        "kept your agents/CONSTITUTION.md; the kit's new version is "
        "agents/CONSTITUTION.md.gabbe-new (compare, merge, then delete it)"
    )
    entry = next(e for e in manifest["entries"] if e["path"].endswith(".gabbe-new"))
    assert entry["kind"] == "copy" and entry["agent"] == "shared"
    assert "agents/CONSTITUTION.md.gabbe-new" in installer.uninstall(target, dry_run=True)
    installer.uninstall(target)
    assert not new.exists()


def test_update_writes_nothing_for_equal_files_memory_files_or_unrecorded_files(tmp_path):
    target, kit = _installed(tmp_path)
    (target / "agents" / "TASKS.md").write_text("my tasks\n")  # changed, kit changed too
    (kit / "TASKS.md").write_text("tasks v2\n")
    (target / "agents" / "memory").mkdir()
    (target / "agents" / "memory" / "AGENTS.md").write_text("mine\n")
    (kit / "memory").mkdir()
    (kit / "memory" / "AGENTS.md").write_text("kit memory\n")
    installer.update_kit(target, kit)
    found = sorted(p.name for p in (target / "agents").rglob("*.gabbe-new"))
    assert found == ["TASKS.md.gabbe-new"]  # a preserved file, not the equal ones, not memory/
    (target / "agents" / "CONSTITUTION.md").write_text("constitution v1\n")  # equals the kit
    installer.update_kit(target, kit)
    assert not (target / "agents" / "CONSTITUTION.md.gabbe-new").exists()


def test_update_writes_nothing_beside_a_file_the_record_does_not_name(tmp_path):
    target = tmp_path / "proj"
    (target / "agents").mkdir(parents=True)
    (target / "agents" / "CONSTITUTION.md").write_text("mine from before the kit\n")
    kit = _kit(tmp_path, "constitution v1\n")
    installer.update_kit(target, kit)  # no record yet: the file is the user's, unrecorded
    assert not (target / "agents" / "CONSTITUTION.md.gabbe-new").exists()


def test_update_removes_the_copy_once_the_user_file_matches_the_kit(tmp_path):
    target, kit = _installed(tmp_path)
    mine = target / "agents" / "CONSTITUTION.md"
    mine.write_text("my constitution\n")
    (kit / "CONSTITUTION.md").write_text("constitution v2\n")
    installer.update_kit(target, kit)
    mine.write_text("constitution v2\n")  # the user merged
    installer.update_kit(target, kit)
    assert not (target / "agents" / "CONSTITUTION.md.gabbe-new").exists()


def test_update_replaces_an_unchanged_copy_and_keeps_a_changed_or_foreign_one(tmp_path):
    target, kit = _installed(tmp_path)
    mine = target / "agents" / "CONSTITUTION.md"
    new = target / "agents" / "CONSTITUTION.md.gabbe-new"
    mine.write_text("my constitution\n")
    (kit / "CONSTITUTION.md").write_text("constitution v2\n")
    installer.update_kit(target, kit)
    (kit / "CONSTITUTION.md").write_text("constitution v3\n")
    installer.update_kit(target, kit)
    assert new.read_text() == "constitution v3\n"  # recorded and unchanged: replaced
    new.write_text("my notes on v3\n")
    (kit / "CONSTITUTION.md").write_text("constitution v4\n")
    installer.update_kit(target, kit)
    assert new.read_text() == "my notes on v3\n"  # changed since the record: kept


def test_update_never_overwrites_a_gabbe_new_the_record_does_not_own(tmp_path):
    target, kit = _installed(tmp_path)
    (target / "agents" / "CONSTITUTION.md").write_text("my constitution\n")
    new = target / "agents" / "CONSTITUTION.md.gabbe-new"
    new.write_text("something of mine\n")
    (kit / "CONSTITUTION.md").write_text("constitution v2\n")
    installer.update_kit(target, kit)
    assert new.read_text() == "something of mine\n"
    assert "agents/CONSTITUTION.md.gabbe-new" not in installer.uninstall(target, dry_run=True)


def test_update_says_when_it_leaves_a_gabbe_new_alone(tmp_path, capsys):
    target, kit = _installed(tmp_path)
    (target / "agents" / "CONSTITUTION.md").write_text("my constitution\n")
    (target / "agents" / "CONSTITUTION.md.gabbe-new").write_text("something of mine\n")
    (kit / "CONSTITUTION.md").write_text("constitution v2\n")
    installer.update_kit(target, kit)
    assert capsys.readouterr().out.strip() == (
        "kept your agents/CONSTITUTION.md; agents/CONSTITUTION.md.gabbe-new is not ours "
        "or was changed: left alone"
    )


def test_update_writes_nothing_through_a_link_on_the_gabbe_new_path(tmp_path):
    target, kit = _installed(tmp_path)
    (target / "agents" / "CONSTITUTION.md").write_text("my constitution\n")
    os.symlink(tmp_path / "victim.txt", target / "agents" / "CONSTITUTION.md.gabbe-new")
    (kit / "CONSTITUTION.md").write_text("constitution v2\n")
    installer.update_kit(target, kit)
    assert not (tmp_path / "victim.txt").exists()


@pytest.mark.skipif(NODE is None, reason="node is not on PATH: the parity case is skipped")
def test_python_and_node_update_write_the_same_gabbe_new_files_and_entries(tmp_path):
    """Same starting install (made by Node), same user edits, then `update` by each."""
    base = tmp_path / "base"
    base.mkdir()
    env = {"HOME": str(tmp_path), "PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}
    run = [NODE, str(REPO / "bin" / "install.js")]
    init = subprocess.run([*run, "init"], cwd=base, env=env, capture_output=True, text=True)
    assert init.returncode == 0, init.stderr[-500:]
    (base / "agents" / "CONSTITUTION.md").write_text("my constitution\n")
    (base / "agents" / "AGENTS.md").write_text("my agents file\n")
    (base / "agents" / "memory").mkdir(exist_ok=True)
    (base / "agents" / "memory" / "AGENTS.md").write_text("my memory file\n")
    py_copy, node_copy = tmp_path / "py", tmp_path / "node"
    for copy in (py_copy, node_copy):
        shutil.copytree(base, copy, symlinks=True)
    installer.update_kit(py_copy, REPO / "agents")
    done = subprocess.run([*run, "update"], cwd=node_copy, env=env, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr[-500:]

    def news(project: Path) -> tuple[dict[str, bytes], dict[str, dict]]:
        files = {
            str(p.relative_to(project)): p.read_bytes()
            for p in (project / "agents").rglob("*.gabbe-new")
        }
        record = json.loads((project / ".gabbe" / "manifest.json").read_text())
        entries = {e["path"]: e for e in record["entries"] if e["path"].endswith(".gabbe-new")}
        return files, entries

    py_files, py_entries = news(py_copy)
    node_files, node_entries = news(node_copy)
    assert sorted(py_files) == ["agents/AGENTS.md.gabbe-new", "agents/CONSTITUTION.md.gabbe-new"]
    assert py_files == node_files
    assert py_entries == node_entries


# --- a record inside the project is untrusted too (RA-01, RA-02) ----------------------
# One record, in a project that also holds the user's own files: nothing of the user's may
# change, whichever command runs. The honest entry (agents/mine.md, with its hash) is
# still removed by `uninstall`.

USER_HOOK = {"matcher": "Bash", "hooks": [{"type": "command", "command": "my-own-guard.sh"}]}
USER_FILES = {
    ".env": b"SECRET=1\n",
    "notes-uncommitted.md": b"my notes\n",
    ".git/config": b"[core]\n\tbare = false\n",
    ".git/hooks/pre-commit": b"#!/bin/sh\necho my own hook\n",
    ".claude/settings.json": json.dumps({"hooks": {"PreToolUse": [USER_HOOK]}}).encode(),
    ".claude/settings.local.json": json.dumps(
        {
            "permissions": {"deny": ["Bash(git push:*)", "Read(./.env)"]},
            "hooks": {"PreToolUse": [USER_HOOK]},
        }
    ).encode(),
    "docs/example-settings.json": b'{"permissions": {"defaultMode": "bypassPermissions"}}\n',
}


def _user_copy(path: str, **more: object) -> dict:
    return {"path": path, "kind": "copy", "agent": "shared", **more}


def _hook_merge(path: str, **more: object) -> dict:
    return {
        "path": path,
        "kind": "hook-merge",
        "agent": "claude-code",
        "fragment": "agents/hooks/claude-code/settings.fragment.json",
        "fragment_doc": {"hooks": {"PreToolUse": [USER_HOOK]}},
        **more,
    }


def _digest(path: str) -> str:
    return hashlib.sha256(USER_FILES[path]).hexdigest()


RECORD_CASES = {
    # RA-01: the record names a planted link as the backup; later entries lead through it
    "backup-link-move": lambda: [
        _user_copy("d", backup_of="link"),
        _user_copy("d/f.md"),
        {"path": "d/sub", "kind": "tree", "agent": "shared"},
    ],
    "backup-link-move-by-name": lambda: [
        _user_copy("d", backup_of="d.gabbe-bak"),  # a correct name, but the file is a link
        _user_copy("d/f.md"),
        {"path": "d/sub", "kind": "tree", "agent": "shared"},
    ],
    # RA-02
    "hashless-copy-env": lambda: [_user_copy(".env")],
    "empty-hash-copy-env": lambda: [_user_copy(".env", hash="")],
    "wrong-hash-copy-env": lambda: [_user_copy(".env", hash="0" * 64)],
    "unknown-kind-notes": lambda: [
        {"path": "notes-uncommitted.md", "kind": "weird-kind", "agent": "shared"}
    ],
    "kind-not-text": lambda: [{"path": "notes-uncommitted.md", "kind": ["copy"], "agent": "x"}],
    "git-config-with-its-hash": lambda: [_user_copy(".git/config", hash=_digest(".git/config"))],
    "git-hook-without-mark": lambda: [
        _user_copy(".git/hooks/pre-commit", hash=_digest(".git/hooks/pre-commit"))
    ],
    "hook-merge-created-true": lambda: [_hook_merge(".claude/settings.json", created=True)],
    "hook-merge-user-hook-in-record": lambda: [_hook_merge(".claude/settings.json")],
    "hook-merge-local-settings": lambda: [_hook_merge(".claude/settings.local.json")],
    "copy-backup-of-another-file": lambda: [
        _user_copy(".claude/settings.local.json", backup_of="docs/example-settings.json")
    ],
}


class UserWorld(World):
    """A `World` whose project also holds the user's own files, and a planted link."""

    def __init__(self, tmp: Path):
        super().__init__(tmp)
        for rel, data in USER_FILES.items():
            (self.proj / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.proj / rel).write_bytes(data)
        (self.victim / "sub" / "SKILL.md").write_bytes(SENTINEL)
        (self.proj / "d.gabbe-bak").symlink_to("../victim")

    def user_snapshot(self) -> dict[str, bytes | tuple[str, str]]:
        """The user's own files and the planted links (`update` and `init` write other files)."""
        seen: dict[str, bytes | tuple[str, str]] = {}
        for key in [*USER_FILES, "link", "d.gabbe-bak", "d", "d.sub"]:
            p = self.proj / key
            if p.is_symlink():
                seen[key] = ("link", os.readlink(p))
            elif p.is_file():
                seen[key] = p.read_bytes()
            else:
                seen[key] = b"<absent>"
        return seen


def _user_world(tmp_path: Path, case: str) -> UserWorld:
    world = UserWorld(tmp_path)
    honest = {
        "path": "agents/mine.md",
        "kind": "copy",
        "agent": "shared",
        "hash": hashlib.sha256(b"honest kit file\n").hexdigest(),
    }
    record = {"schema_version": 1, "agents": [], "entries": [*RECORD_CASES[case](), honest]}
    (world.proj / ".gabbe" / "manifest.json").write_text(json.dumps(record))
    return world


@pytest.mark.parametrize("case", list(RECORD_CASES))
def test_python_installer_leaves_the_users_files_alone(tmp_path, case):
    world = _user_world(tmp_path, case)
    outside, inside = world.snapshot(), world.user_snapshot()

    installer.uninstall(world.proj, dry_run=True)
    assert (world.snapshot(), world.user_snapshot()) == (outside, inside)

    installer.update_kit(world.proj, _small_kit(tmp_path))
    assert (world.snapshot(), world.user_snapshot()) == (outside, inside)

    installer.uninstall(world.proj)
    assert (world.snapshot(), world.user_snapshot()) == (outside, inside), case
    assert not (world.proj / "agents" / "mine.md").exists()  # the honest entry still goes


@pytest.mark.skipif(NODE is None, reason="node is not on PATH: the Node half is skipped")
@pytest.mark.parametrize("case", list(RECORD_CASES))
@pytest.mark.parametrize("command", [["uninstall", "--dry-run"], ["update"], ["uninstall"]])
def test_node_installer_leaves_the_users_files_alone(tmp_path, case, command):
    world = _user_world(tmp_path, case)
    home = tmp_path / "home"
    home.mkdir()
    outside, inside = world.snapshot(), world.user_snapshot()
    done = _node(world, home, *command)
    assert (world.snapshot(), world.user_snapshot()) == (outside, inside), (
        done.stdout[-600:] + done.stderr[-600:]
    )


def test_a_planted_link_named_as_the_backup_is_not_moved_into_place(tmp_path, capsys):
    world = _user_world(tmp_path, "backup-link-move")
    installer.uninstall(world.proj)
    assert (world.proj / "link").is_symlink() and not (world.proj / "d").exists()
    assert "backup_of" in capsys.readouterr().err  # the refusal is named once


def test_the_lines_that_name_a_kept_entry(tmp_path, capsys):
    world = _user_world(tmp_path, "hashless-copy-env")
    installer.uninstall(world.proj)
    assert "kept .env: the record holds no hash for it" in capsys.readouterr().out
    world = _user_world(tmp_path / "b", "unknown-kind-notes")
    installer.uninstall(world.proj)
    out = capsys.readouterr().out
    assert "kept notes-uncommitted.md: unknown record kind 'weird-kind'" in out


def test_the_dry_run_lists_what_a_real_run_removes(tmp_path):
    for case in RECORD_CASES:
        world = _user_world(tmp_path / case, case)
        listed = installer.uninstall(world.proj, dry_run=True)
        assert listed == installer.uninstall(world.proj), case


def test_a_link_that_appears_between_plan_and_action_is_not_followed(tmp_path, monkeypatch, capsys):
    """RA-01: every path is checked again right before it is acted on."""
    world = _user_world(tmp_path, "hashless-copy-env")
    (world.proj / "agents" / "sub").mkdir()
    (world.proj / "agents" / "sub" / "x.md").write_bytes(b"x\n")
    record = json.loads((world.proj / ".gabbe" / "manifest.json").read_text())
    record["entries"] = [
        {
            "path": "agents/sub/x.md",
            "kind": "copy",
            "agent": "shared",
            "hash": hashlib.sha256(b"x\n").hexdigest(),
        }
    ]
    (world.proj / ".gabbe" / "manifest.json").write_text(json.dumps(record))
    (world.victim / "x.md").write_bytes(b"x\n")
    real_plan = installer._removal_plan

    def plan_then_plant(*args, **kwargs):
        planned = real_plan(*args, **kwargs)
        shutil.rmtree(world.proj / "agents" / "sub")
        os.symlink("../../victim", world.proj / "agents" / "sub")  # planted after the plan
        return planned

    monkeypatch.setattr(installer, "_removal_plan", plan_then_plant)
    installer.uninstall(world.proj)
    assert (world.victim / "x.md").read_bytes() == b"x\n"
    assert "skipped agents/sub/x.md" in capsys.readouterr().out

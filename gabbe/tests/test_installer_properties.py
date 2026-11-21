# SPDX-License-Identifier: Apache-2.0
"""Property tests for the reversible installer (assurance ladder level 1).

Small kit trees and user files are generated, then random sequences of install,
update, uninstall and user edits are run in a temporary folder. After every step:
nothing outside the target changed, nothing the user wrote is lost, and no backup was
overwritten. Further properties cover uninstall round trips, the dry run, the path
guard and damaged install records.
"""

import json
import os
import posixpath
import shutil
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from gabbe import installer

_SETTINGS = settings(max_examples=40, derandomize=True, deadline=None, database=None)

_PRESERVE_NAMES = ["AGENTS.md", "CONSTITUTION.md", "TASKS.md", "policies.yml", "config.json"]
_plain = st.text(alphabet="abc12 .", min_size=1, max_size=6).filter(
    lambda s: s == s.strip() and set(s) != {"."} and not s.endswith(".")
)
_file_name = st.one_of(_plain, st.sampled_from(_PRESERVE_NAMES))
_dir_name = st.one_of(_plain, st.sampled_from(["memory", "project"]))
_rel_path = st.builds(
    lambda dirs, name: "/".join(dirs + [name]),
    st.lists(_dir_name, max_size=2),
    _file_name,
)
_AGENT_SETS = st.lists(st.sampled_from(["claude", "cursor", "windsurf"]), max_size=3, unique=True)


def _prefix_free(paths):
    """Drop paths that would need a name to be both a file and a folder."""
    kept = []
    for p in sorted(set(paths), key=lambda x: (x.count("/"), x)):
        if not any(k.startswith(p + "/") or p.startswith(k + "/") for k in kept):
            kept.append(p)
    return kept


_kit_paths = st.lists(_rel_path, min_size=1, max_size=5).map(_prefix_free)


class _Counter:
    """Unique bytes per write, so a lost write can never hide behind an equal one."""

    def __init__(self):
        self.n = 0

    def user(self):
        self.n += 1
        return b"USER-%d\n" % self.n

    def kit(self):
        self.n += 1
        return b"KIT-%d\n" % self.n


def _snapshot(path):
    """Every file under `path` (relative name -> bytes, links as ('link', target)) and every folder."""
    files, dirs = {}, set()
    if not path.exists():
        return files, dirs
    for root, dnames, fnames in os.walk(path):
        for d in dnames:
            dirs.add(str((Path(root) / d).relative_to(path)))
        for f in fnames:
            p = Path(root) / f
            key = str(p.relative_to(path))
            files[key] = ("link", os.readlink(p)) if p.is_symlink() else p.read_bytes()
    return files, dirs


def _all_bytes(target):
    return [v for v in _snapshot(target)[0].values() if isinstance(v, bytes)]


class _World:
    """A temporary root holding `src` (the kit), `proj` (the target) and `outside`."""

    def __init__(self, kit_paths, counter):
        self.root = Path(tempfile.mkdtemp(prefix="gabbe-inst-"))
        self.src, self.target, self.outside = (self.root / n for n in ("src", "proj", "outside"))
        self.counter = counter
        self.kit_paths = list(kit_paths)
        self.target.mkdir()
        self.outside.mkdir()
        (self.outside / "sentinel.txt").write_bytes(b"outside")
        for rel in kit_paths:
            self.write_source(rel, counter.kit())
        self.user_bytes = []  # bytes the user wrote or edited and that must never vanish
        self.backups = {}  # backup path -> bytes seen

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write_source(self, rel, data):
        path = self.src / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def user_write(self, path):
        data = self.counter.user()
        if path.is_file() and path.read_bytes() in self.user_bytes:
            self.user_bytes.remove(path.read_bytes())  # the user overwrote their own text
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.user_bytes.append(data)

    def dest(self, rel):
        return self.target / "agents" / rel

    def outside_view(self):
        """Everything in the root except the target and the (test-owned) source tree."""
        files, dirs = _snapshot(self.root)
        keep = lambda k: not (k.startswith("proj") or k.startswith("src"))  # noqa: E731
        return {k: v for k, v in files.items() if keep(k)}, {d for d in dirs if keep(d)}

    def check(self, before_outside):
        assert self.outside_view() == before_outside, "something outside the target changed"
        present = _all_bytes(self.target)
        for data in self.user_bytes:
            assert data in present, f"user bytes {data!r} are gone from the target"
        files, _ = _snapshot(self.target)
        for key, data in list(self.backups.items()):
            if key not in files:
                del self.backups[key]  # restored or removed by the user's own step
            else:
                assert files[key] == data, f"backup {key} was overwritten"
        for key, data in files.items():
            if ".gabbe-bak" in key and isinstance(data, bytes):
                self.backups.setdefault(key, data)


_OPS = ["install", "update", "uninstall", "user_write", "user_edit", "source_change"]


def _run_op(world, op, data, agents):
    target, src = world.target, world.src
    if op == "install":
        installer.install_kit(target, src, agents)
    elif op == "update":
        installer.update_kit(target, src, agents or None)
    elif op == "uninstall":
        dry = installer.uninstall(target, dry_run=True)
        files_before = _snapshot(target)
        assert installer.uninstall(target, dry_run=True) == dry
        assert _snapshot(target) == files_before, "a dry run changed the target"
        real = installer.uninstall(target)
        assert real == dry, "the dry run listed something other than the real run removed"
    elif op == "user_write":
        rel = data.draw(st.sampled_from(world.kit_paths + ["notes/own.txt"]))
        dest = world.dest(rel) if rel != "notes/own.txt" else target / rel
        if dest.is_dir() or dest.is_symlink():
            return
        world.user_write(dest)
    elif op == "user_edit":
        files = sorted(
            p
            for p in (target / "agents").rglob("*")
            if p.is_file() and not p.is_symlink() and ".gabbe-bak" not in p.name
        )
        if files:
            world.user_write(data.draw(st.sampled_from(files)))
    elif op == "source_change":
        rel = data.draw(st.sampled_from(world.kit_paths + ["extra/new.txt"]))
        if data.draw(st.booleans()) and rel == "extra/new.txt" and (src / rel).exists():
            (src / rel).unlink()
        else:
            world.write_source(rel, world.counter.kit())


@given(_kit_paths, st.lists(st.sampled_from(_OPS), max_size=10), st.data())
@settings(max_examples=80, derandomize=True, deadline=None, database=None)
def test_sequences_keep_isolation_user_files_and_backups(kit_paths, ops, data):
    """For any sequence of install, update, uninstall, user writes, user edits and kit
    changes: nothing outside the target changes, every byte the user wrote is still
    somewhere under the target, and an existing backup is never overwritten."""
    world = _World(kit_paths, _Counter())
    try:
        for rel in data.draw(st.lists(st.sampled_from(kit_paths), max_size=2, unique=True)):
            world.user_write(world.dest(rel))  # a file the user already had at a kit path
        before = world.outside_view()
        for op in ops:
            agents = data.draw(_AGENT_SETS)
            _run_op(world, op, data, agents)
            world.check(before)
    finally:
        world.close()


@given(_kit_paths, _kit_paths, _AGENT_SETS)
@_SETTINGS
def test_install_then_uninstall_restores_every_pre_existing_file(kit_paths, own_paths, agents):
    """With no user changes in between, install followed by uninstall leaves every file
    that existed before install with exactly its old bytes, and removes the kit's files."""
    world = _World(kit_paths, _Counter())
    try:
        existing = {}
        for rel in own_paths:
            if any(rel.startswith(k + "/") or k.startswith(rel + "/") for k in kit_paths):
                continue  # a name that would have to be both a file and a folder
            dest = world.dest(rel)
            if dest.exists() or any(
                q.is_file() for q in dest.parents if q != world.target and q.exists()
            ):
                continue
            world.user_write(dest)
            existing[str(dest.relative_to(world.target))] = dest.read_bytes()
        installer.install_kit(world.target, world.src, agents)
        installer.uninstall(world.target)
        files, _ = _snapshot(world.target)
        for rel, data_bytes in existing.items():
            assert files.get(rel) == data_bytes, f"{rel} was not restored"
        assert set(files) == set(existing), "install then uninstall left other files behind"
    finally:
        world.close()


@given(
    st.lists(st.sampled_from(["a", "b", "..", ".", "c d"]), min_size=0, max_size=6),
    st.booleans(),
    st.sampled_from(["", "/etc/x", "/tmp"]),
)
@_SETTINGS
def test_resolve_within_refuses_every_path_that_escapes(parts, nested, absolute):
    """An absolute path, a path with any `..` part, and an empty or `.` path are refused
    with ValueError; every other relative path resolves to the same place posix normpath gives."""
    with tempfile.TemporaryDirectory() as d:
        base = Path(d).resolve() / "proj"
        base.mkdir()
        rel = absolute or "/".join((["x"] if nested else []) + parts)
        parts_of_rel = [x for x in rel.split("/")]
        if absolute or ".." in parts_of_rel or all(x in ("", ".") for x in parts_of_rel):
            with pytest.raises(ValueError):
                installer._resolve_within(base, rel)
            return
        expected = posixpath.normpath(posixpath.join(str(base), rel))
        assert Path(posixpath.normpath(str(installer._resolve_within(base, rel)))) == Path(expected)


_corrupt_records = st.one_of(
    st.binary(max_size=40),
    st.just(b""),
    st.just(b"[]"),
    st.just(b'{"entries": 5}'),
    st.just(b'{"schema_version": 1}'),
    st.just(b"\xff\xfe\x00{"),
    st.just(b"null"),
)


@given(_corrupt_records, _kit_paths, st.lists(_rel_path, max_size=3).map(_prefix_free))
@_SETTINGS
def test_a_damaged_install_record_is_never_acted_on_and_never_deleted(record, kit_paths, own_paths):
    """With an unreadable or wrongly shaped record, install, update and uninstall change
    nothing and keep the record's bytes; uninstall removes no file."""
    world = _World(kit_paths, _Counter())
    try:
        mp = installer.manifest_path(world.target)
        mp.parent.mkdir()
        mp.write_bytes(record)
        if installer.manifest_problem(world.target) is None:
            return  # a usable record: not this property
        for rel in own_paths:
            world.user_write(world.target / "own" / rel)
        before = _snapshot(world.target)
        with pytest.raises(ValueError):
            installer.install_kit(world.target, world.src, ["claude"])
        with pytest.raises(ValueError):
            installer.update_kit(world.target, world.src)
        assert installer.uninstall(world.target) == []
        assert installer.uninstall(world.target, dry_run=True) == []
        assert _snapshot(world.target) == before
    finally:
        world.close()


_odd_paths = st.one_of(
    st.sampled_from(
        ["../outside/sentinel.txt", "/etc/hostname", "a/../../outside/sentinel.txt", ""]
    ),
    _rel_path,
)


@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "path": _odd_paths,
                "kind": st.sampled_from(["copy", "tree", "block", "symlink", "skill-emit"]),
            },
            optional={
                "agent": st.sampled_from(["shared", "claude"]),
                "hash": st.text(max_size=5),
                "backup_of": _odd_paths,
            },
        ),
        max_size=4,
    )
)
@_SETTINGS
def test_a_tampered_record_never_touches_anything_outside_the_target(entries):
    """A record whose paths point outside the target (or at the target itself) never
    makes uninstall delete, move or write outside it."""
    world = _World(["a.txt"], _Counter())
    try:
        mp = installer.manifest_path(world.target)
        mp.parent.mkdir()
        mp.write_text(json.dumps({"schema_version": 1, "entries": entries, "agents": []}))
        before = world.outside_view()
        sentinel = world.outside / "sentinel.txt"
        installer.uninstall(world.target)
        assert sentinel.read_bytes() == b"outside"
        assert world.outside_view() == before
    finally:
        world.close()


@given(_plain, st.integers(0, 4), st.binary(min_size=1, max_size=8))
@_SETTINGS
def test_free_backup_path_never_returns_an_existing_name(name, taken, data):
    """The backup name is always unused, however many earlier backups exist."""
    with tempfile.TemporaryDirectory() as d:
        base = Path(d) / name
        base.write_bytes(data)
        first = installer.free_backup_path(base)
        for i in range(taken):
            first.write_bytes(b"old-%d" % i)
            first = installer.free_backup_path(base)
        assert not first.exists()
        installer.backup_file(base)
        assert base.read_bytes() == data


@pytest.mark.parametrize("rel", ["..", "a/../.."])
def test_resolve_within_refuses_a_last_segment_that_climbs_out(rel):
    """`..` and `a/../..` leave the target and must raise ValueError."""
    with tempfile.TemporaryDirectory() as d:
        base = Path(d).resolve() / "proj"
        base.mkdir()
        with pytest.raises(ValueError):
            installer._resolve_within(base, rel)


def test_tampered_tree_entry_cannot_delete_files_above_the_target():
    """An entry pointing at `..` must not delete files outside the target."""
    world = _World(["a.txt"], _Counter())
    try:
        marked = world.outside / "skill.md"
        marked.write_bytes(b"x gabbe-schema-version: 1 x")
        mp = installer.manifest_path(world.target)
        mp.parent.mkdir()
        entry = {"path": "..", "kind": "tree", "agent": "shared"}
        mp.write_text(json.dumps({"schema_version": 1, "entries": [entry], "agents": []}))
        installer.uninstall(world.target)
        assert marked.exists()
    finally:
        world.close()

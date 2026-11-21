# SPDX-License-Identifier: Apache-2.0
"""Stateful model test of `gabbe sync` (TASKS.md <-> SQLite), assurance ladder level 1.

The rule (gabbe.sync.sync_tasks): a task that exists on one side only is carried to the
other side (union); for a task on both sides the status of the newer side wins, a tie
goes to the file; after one sync both sides are equal and a second sync changes nothing.
Stamps are UTC instants on both sides.

The model below is the simplest in-memory description of that promise. The clock is
controlled: file modification times are set with `os.utime`, and the database
timestamps come from a patched `datetime.now`, so the "newer side" is decided by the
model, never by the real clock.

Each defect found by the 2026-11-21 audit has its own test at the bottom; the one
remaining limit (deletions are not propagated) is asserted as documented behaviour.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    precondition,
    rule,
)

from gabbe import sync
from gabbe.database import get_db, init_db

_START = sync._MARKER_START
_END = sync._MARKER_END
_BASE = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp()  # fixed instant
_TITLES = ["alpha", "beta", "gamma", "delta"]
_STATUSES = ["TODO", "IN_PROGRESS", "DONE"]
_CHAR = {"TODO": " ", "IN_PROGRESS": "/", "DONE": "x"}


class _Clock:
    """Model clock: seconds after _BASE. Patched in as `gabbe.sync.datetime`."""

    seconds = 0

    @classmethod
    def stamp(cls, seconds):
        return datetime.fromtimestamp(_BASE + seconds, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _fake_datetime(clock):
    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.fromtimestamp(_BASE + clock.seconds, tz)

    return FakeDatetime


@contextlib.contextmanager
def _workspace():
    """A temporary project with the sync module's paths and clock patched."""
    root = Path(tempfile.mkdtemp(prefix="gabbe-sync-"))
    clock = _Clock()
    gdir = root / "project"
    try:
        with contextlib.ExitStack() as stack:
            for name, value in [
                ("gabbe.config.GABBE_DIR", gdir),
                ("gabbe.database.GABBE_DIR", gdir),
                ("gabbe.database.DB_PATH", gdir / "state.db"),
                ("gabbe.sync.TASKS_FILE", gdir / "TASKS.md"),
                ("gabbe.sync.datetime", _fake_datetime(clock)),
            ]:
                stack.enter_context(patch(name, value))
            gdir.mkdir(parents=True)
            init_db()
            yield root, clock
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _file_text(tasks):
    lines = "".join(f"- [{_CHAR[s]}] {t}\n" for t, s in tasks)
    return f"# Project Tasks\n\n{_START}\n{lines}{_END}\n"


def _write_file(root, tasks, seconds):
    path = root / "project" / "TASKS.md"
    path.write_text(_file_text(tasks), encoding="utf-8")
    os.utime(path, (_BASE + seconds, _BASE + seconds))


def _db_rows():
    conn = get_db()
    try:
        return [(r["title"], r["status"]) for r in conn.execute("SELECT * FROM tasks ORDER BY id")]
    finally:
        conn.close()


def _db_exec(sql, args=()):
    conn = get_db()
    try:
        conn.execute(sql, args)
        conn.commit()
    finally:
        conn.close()


def _run_sync():
    sync.sync_tasks()


def _file_rows(root):
    return [(t["title"], t["status"]) for t in sync.parse_markdown_tasks(_read(root))]


def _read(root):
    return (root / "project" / "TASKS.md").read_text(encoding="utf-8")


class SyncMachine(RuleBasedStateMachine):
    """Random edits on either side, with sync runs in between, checked against a model."""

    def __init__(self):
        super().__init__()
        self._cm = _workspace()
        self.root, self.clock = self._cm.__enter__()
        # model: file = ordered list of [title, status]; db = ordered dict title -> [status, t]
        self.file = []
        self.db = {}
        self.file_mtime = 0
        self._write()
        self.just_synced = False

    def teardown(self):
        self._cm.__exit__(None, None, None)

    # -- helpers ---------------------------------------------------------
    def _tick(self):
        self.clock.seconds += 10

    def _write(self):
        _write_file(self.root, [tuple(x) for x in self.file], self.clock.seconds)
        self.file_mtime = self.clock.seconds

    def _db_mtime(self):
        return max((t for _, t in self.db.values()), default=0)

    def _model_sync(self):
        """The rule, one sync run, on the model. Returns "same", "file" (the file changed)
        or "db" (only the database changed)."""
        file_map = {t: s for t, s in self.file}
        db_map = {t: s for t, (s, _) in self.db.items()}
        if file_map == db_map:
            return "same"
        now = self.clock.seconds
        winner = file_map if self.file_mtime >= self._db_mtime() else db_map
        new_file = [[t, winner.get(t, s)] for t, s in self.file]
        new_file += [[t, s] for t, s in db_map.items() if t not in file_map]
        for title, (status, _) in list(self.db.items()):
            if winner.get(title, status) != status:
                self.db[title] = [winner[title], now]
        for title, status in file_map.items():
            if title not in self.db:
                self.db[title] = [status, now]
        changed = new_file != self.file
        self.file = new_file
        return "file" if changed else "db"

    def _real_sync_and_align(self):
        """Run the real sync, then the model; re-stamp the file like a writer's clock."""
        mtime_before = (self.root / "project" / "TASKS.md").stat().st_mtime
        _run_sync()
        result = self._model_sync()
        if result == "file":
            self._write_mtime_only()
        else:
            # only a changed file is rewritten; otherwise it is left alone
            assert (self.root / "project" / "TASKS.md").stat().st_mtime == mtime_before
        return result

    def _write_mtime_only(self):
        path = self.root / "project" / "TASKS.md"
        os.utime(path, (_BASE + self.clock.seconds, _BASE + self.clock.seconds))
        self.file_mtime = self.clock.seconds

    # -- rules -----------------------------------------------------------
    @precondition(lambda self: len(self.file) < len(_TITLES))
    @rule(data=st.data())
    def add_task_to_file(self, data):
        """The user adds a task line to the Markdown file."""
        free = [t for t in _TITLES if t not in {x[0] for x in self.file}]
        title = data.draw(st.sampled_from(free))
        status = data.draw(st.sampled_from(_STATUSES))
        self._tick()
        self.file.append([title, status])
        self._write()
        self.just_synced = False

    @precondition(lambda self: len(self.file) > 0)
    @rule(data=st.data())
    def change_status_in_file(self, data):
        """The user changes one task's status in the Markdown file."""
        i = data.draw(st.integers(0, len(self.file) - 1))
        status = data.draw(st.sampled_from(_STATUSES))
        if not data.draw(st.booleans()):  # sometimes edit in the same second as the other side
            self._tick()
        self.file[i][1] = status
        self._write()
        self.just_synced = False

    @precondition(lambda self: len(self.db) < len(_TITLES))
    @rule(data=st.data())
    def add_task_to_db(self, data):
        """A task is created in the database only."""
        free = [t for t in _TITLES if t not in self.db]
        title = data.draw(st.sampled_from(free))
        status = data.draw(st.sampled_from(_STATUSES))
        self._tick()
        _db_exec(
            "INSERT INTO tasks (title, status, updated_at) VALUES (?, ?, ?)",
            (title, status, _Clock.stamp(self.clock.seconds)),
        )
        self.db[title] = [status, self.clock.seconds]
        self.just_synced = False

    @precondition(lambda self: len(self.db) > 0)
    @rule(data=st.data())
    def change_status_in_db(self, data):
        """A task's status changes in the database."""
        title = data.draw(st.sampled_from(sorted(self.db)))
        status = data.draw(st.sampled_from(_STATUSES))
        if not data.draw(st.booleans()):  # sometimes edit in the same second as the other side
            self._tick()
        _db_exec(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE title = ?",
            (status, _Clock.stamp(self.clock.seconds), title),
        )
        self.db[title] = [status, self.clock.seconds]
        self.just_synced = False

    @rule()
    def run_sync(self):
        """Run sync twice: the first must follow the rule and leave both sides equal, and
        the second must change nothing."""
        self._tick()
        self._real_sync_and_align()
        self.just_synced = True
        self._assert_matches_model()
        assert dict(_db_rows()) == dict(_file_rows(self.root))
        before = (_read(self.root), _db_rows(), self._db_stamps())
        self._tick()
        assert self._real_sync_and_align() == "same"
        self._assert_matches_model()
        assert before == (_read(self.root), _db_rows(), self._db_stamps())

    def _db_stamps(self):
        conn = get_db()
        try:
            return [
                tuple(r) for r in conn.execute("SELECT title, updated_at FROM tasks ORDER BY id")
            ]
        finally:
            conn.close()

    def _assert_matches_model(self):
        assert _db_rows() == [(t, s[0]) for t, s in self.db.items()]
        assert _file_rows(self.root) == [(t, s) for t, s in self.file]

    # -- invariants ------------------------------------------------------
    @invariant()
    def no_duplicate_tasks(self):
        """No task title appears twice, in the file or in the database."""
        titles = [t for t, _ in _file_rows(self.root)]
        assert len(titles) == len(set(titles))
        db_titles = [t for t, _ in _db_rows()]
        assert len(db_titles) == len(set(db_titles))

    @invariant()
    def file_stays_parseable(self):
        """The file keeps its markers and every task line parses back."""
        text = _read(self.root)
        assert text.count(_START) == 1 and text.count(_END) == 1
        assert text.index(_START) < text.index(_END)
        task_lines = [ln for ln in text.splitlines() if ln.startswith("- [")]
        assert len(task_lines) == len(_file_rows(self.root))

    @invariant()
    def common_tasks_agree_after_sync(self):
        """After a sync, a task on both sides has the same status on both."""
        if not self.just_synced:
            return
        db = dict(_db_rows())
        for title, status in _file_rows(self.root):
            if title in db:
                assert db[title] == status


SyncMachine.TestCase.settings = settings(
    max_examples=40,
    stateful_step_count=14,
    derandomize=True,
    deadline=None,
    database=None,
)
TestSyncMachine = SyncMachine.TestCase


# ---------------------------------------------------------------------------
# Scenarios found by the audit 2026-11-21 (SW-18): one test each.
# ---------------------------------------------------------------------------


def _scenario(file_tasks, db_tasks, file_seconds, db_seconds):
    """Set up the two sides, run one sync, return (file as dict, database as dict)."""
    cm = _workspace()
    root, clock = cm.__enter__()
    try:
        for title, status in db_tasks:
            _db_exec(
                "INSERT INTO tasks (title, status, updated_at) VALUES (?, ?, ?)",
                (title, status, _Clock.stamp(db_seconds)),
            )
        _write_file(root, file_tasks, file_seconds)
        clock.seconds = max(file_seconds, db_seconds) + 10
        _run_sync()
        return dict(_file_rows(root)), dict(_db_rows())
    finally:
        cm.__exit__(None, None, None)


def test_documented_limit_a_deleted_task_comes_back():
    """A line removed from the (newer) file is not a deletion: the task returns from the
    database, so both sides keep it. Documented limit: deletions are not propagated."""
    file, db = _scenario([("alpha", "TODO")], [("alpha", "TODO"), ("beta", "TODO")], 100, 50)
    assert file == db == {"alpha": "TODO", "beta": "TODO"}


def test_db_only_task_reaches_file_when_file_is_newer():
    file, db = _scenario([("alpha", "TODO")], [("alpha", "TODO"), ("beta", "DONE")], 100, 50)
    assert file == db == {"alpha": "TODO", "beta": "DONE"}


def test_file_only_task_survives_newer_db():
    file, db = _scenario([("alpha", "TODO"), ("beta", "TODO")], [("alpha", "DONE")], 50, 100)
    assert file == db == {"alpha": "DONE", "beta": "TODO"}  # status from the newer side (db)


def test_tie_goes_to_the_file_for_shared_tasks():
    file, db = _scenario([("alpha", "DONE")], [("alpha", "TODO")], 100, 100)
    assert file == db == {"alpha": "DONE"}


def test_single_sync_is_idempotent_with_db_only_task():
    """With a DB-only task and a file edit, the second sync changes nothing."""
    cm = _workspace()
    root, clock = cm.__enter__()
    try:
        for title in ("alpha", "beta"):
            _db_exec(
                "INSERT INTO tasks (title, status, updated_at) VALUES (?, 'TODO', ?)",
                (title, _Clock.stamp(50)),
            )
        _write_file(root, [("alpha", "DONE")], 100)
        clock.seconds = 110
        _run_sync()
        first = (_read(root), _db_rows())
        assert dict(_file_rows(root)) == dict(_db_rows()) == {"alpha": "DONE", "beta": "TODO"}
        clock.seconds = 120
        _run_sync()
        assert first == (_read(root), _db_rows())
    finally:
        cm.__exit__(None, None, None)


def test_utc_database_stamp_compared_as_utc(monkeypatch):
    """A database stamp written in UTC (SQLite default) compares correctly with a file
    edited a minute later, in a time zone west of UTC."""
    if not hasattr(time, "tzset"):
        pytest.skip("time.tzset not available")
    monkeypatch.setenv("TZ", "America/Los_Angeles")
    time.tzset()
    try:
        utc_now = 1_800_000_000  # a fixed instant
        db_stamp = datetime.fromtimestamp(utc_now, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        cm = _workspace()
        root, clock = cm.__enter__()
        try:
            _db_exec(
                "INSERT INTO tasks (title, status, updated_at) VALUES ('alpha', 'TODO', ?)",
                (db_stamp,),
            )
            path = root / "project" / "TASKS.md"
            path.write_text(_file_text([("alpha", "DONE")]), encoding="utf-8")
            os.utime(path, (utc_now + 60, utc_now + 60))
            _run_sync()
            assert dict(_file_rows(root)) == {"alpha": "DONE"}  # the later file edit wins
            assert dict(_db_rows()) == {"alpha": "DONE"}
        finally:
            cm.__exit__(None, None, None)
    finally:
        monkeypatch.undo()
        time.tzset()

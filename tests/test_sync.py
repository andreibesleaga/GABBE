"""Unit tests for gabbe.sync."""
import pytest
from unittest.mock import patch
from gabbe.sync import parse_markdown_tasks, generate_markdown_tasks, _parse_db_timestamp


# ---------------------------------------------------------------------------
# parse_markdown_tasks
# ---------------------------------------------------------------------------

def test_parse_empty_content():
    assert parse_markdown_tasks("") == []


def test_parse_todo_task():
    tasks = parse_markdown_tasks("- [ ] Do something\n")
    assert len(tasks) == 1
    assert tasks[0] == {"title": "Do something", "status": "TODO"}


def test_parse_done_task_lowercase_x():
    tasks = parse_markdown_tasks("- [x] Done task\n")
    assert tasks[0]["status"] == "DONE"


def test_parse_done_task_uppercase_x():
    tasks = parse_markdown_tasks("- [X] Done task\n")
    assert tasks[0]["status"] == "DONE"


def test_parse_in_progress_task():
    tasks = parse_markdown_tasks("- [/] In progress\n")
    assert tasks[0]["status"] == "IN_PROGRESS"


def test_parse_unknown_char_defaults_todo():
    tasks = parse_markdown_tasks("- [?] Unknown\n")
    assert tasks[0]["status"] == "TODO"


def test_parse_multiple_tasks():
    content = "- [ ] Task A\n- [x] Task B\n- [/] Task C\n"
    tasks = parse_markdown_tasks(content)
    assert len(tasks) == 3
    statuses = [t["status"] for t in tasks]
    assert statuses == ["TODO", "DONE", "IN_PROGRESS"]


def test_parse_ignores_non_task_lines():
    content = "# Heading\n\nSome text\n- [ ] A task\n"
    tasks = parse_markdown_tasks(content)
    assert len(tasks) == 1


def test_parse_strips_title_whitespace():
    tasks = parse_markdown_tasks("- [x]   Padded title   \n")
    assert tasks[0]["title"] == "Padded title"


# ---------------------------------------------------------------------------
# generate_markdown_tasks
# ---------------------------------------------------------------------------

def test_generate_empty_list():
    content = generate_markdown_tasks([])
    assert "# Project Tasks" in content


def test_generate_todo():
    tasks = [{"title": "Task A", "status": "TODO"}]
    content = generate_markdown_tasks(tasks)
    assert "- [ ] Task A" in content


def test_generate_done():
    tasks = [{"title": "Task B", "status": "DONE"}]
    content = generate_markdown_tasks(tasks)
    assert "- [x] Task B" in content


def test_generate_in_progress():
    tasks = [{"title": "Task C", "status": "IN_PROGRESS"}]
    content = generate_markdown_tasks(tasks)
    assert "- [/] Task C" in content


def test_roundtrip():
    original = "- [ ] Alpha\n- [x] Beta\n- [/] Gamma\n"
    tasks = parse_markdown_tasks(original)
    regenerated = generate_markdown_tasks(tasks)
    # Re-parse should yield the same tasks
    assert parse_markdown_tasks(regenerated) == tasks


# ---------------------------------------------------------------------------
# _parse_db_timestamp
# ---------------------------------------------------------------------------

def test_parse_standard_format():
    ts = _parse_db_timestamp("2026-01-15 12:00:00")
    assert ts > 0


def test_parse_iso_format():
    ts = _parse_db_timestamp("2026-01-15T12:00:00")
    assert ts > 0


def test_parse_invalid_returns_zero():
    ts = _parse_db_timestamp("not-a-date")
    assert ts == 0


# ---------------------------------------------------------------------------
# sync_tasks integration
# ---------------------------------------------------------------------------

def test_sync_import_from_md(tmp_project):
    import gabbe.sync as sync_mod
    tasks_file = tmp_project / "TASKS.md"
    tasks_file.write_text("- [ ] Task Alpha\n- [x] Task Beta\n")

    sync_mod.sync_tasks()

    from gabbe.database import get_db
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT title, status FROM tasks ORDER BY title")
        rows = c.fetchall()
    finally:
        conn.close()

    assert len(rows) == 2
    assert rows[0]["title"] == "Task Alpha"
    assert rows[0]["status"] == "TODO"
    assert rows[1]["title"] == "Task Beta"
    assert rows[1]["status"] == "DONE"


def test_sync_export_to_md(tmp_project):
    import gabbe.sync as sync_mod
    from gabbe.database import get_db

    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title, status) VALUES ('Task Gamma', 'IN_PROGRESS')")
        conn.commit()
    finally:
        conn.close()

    sync_mod.sync_tasks()

    tasks_file = tmp_project / "TASKS.md"
    content = tasks_file.read_text()
    assert "- [/] Task Gamma" in content


def test_sync_both_empty(tmp_project):
    """When both DB and file are empty, sync should not crash."""
    import gabbe.sync as sync_mod
    sync_mod.sync_tasks()  # no exception


def test_sync_atomic_write_creates_file(tmp_project):
    """Export produces a real file without partial writes."""
    import gabbe.sync as sync_mod
    from gabbe.database import get_db

    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title, status) VALUES ('Atomic Task', 'TODO')")
        conn.commit()
    finally:
        conn.close()

    sync_mod.sync_tasks()

    tasks_file = tmp_project / "TASKS.md"
    assert tasks_file.exists()
    assert "Atomic Task" in tasks_file.read_text()

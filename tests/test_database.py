"""Unit tests for gabbe.database."""
import pytest
import sqlite3
from unittest.mock import patch


def test_init_db_creates_tables(tmp_project):
    from gabbe.database import get_db
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in c.fetchall()}
    finally:
        conn.close()

    assert "tasks" in tables
    assert "project_state" in tables
    assert "events" in tables
    assert "genes" in tables
    assert "schema_version" in tables


def test_schema_version_is_current(tmp_project):
    from gabbe.database import get_db, SCHEMA_VERSION
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT version FROM schema_version")
        version = c.fetchone()[0]
    finally:
        conn.close()
    assert version == SCHEMA_VERSION


def test_tasks_title_unique_constraint(tmp_project):
    from gabbe.database import get_db
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title) VALUES ('Unique Task')")
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO tasks (title) VALUES ('Unique Task')")
            conn.commit()
    finally:
        conn.close()


def test_get_db_returns_row_factory(tmp_project):
    from gabbe.database import get_db
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title) VALUES ('Row Factory Test')")
        conn.commit()
        c.execute("SELECT * FROM tasks")
        row = c.fetchone()
        # sqlite3.Row supports dict-like access
        assert row['title'] == 'Row Factory Test'
    finally:
        conn.close()


def test_init_db_idempotent(tmp_project):
    """Calling init_db twice must not raise or duplicate schema objects."""
    from gabbe.database import init_db
    init_db()  # second call
    from gabbe.database import get_db
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        assert c.fetchone() is not None
    finally:
        conn.close()

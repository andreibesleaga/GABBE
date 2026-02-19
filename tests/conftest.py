"""Shared pytest fixtures for the GABBE test suite."""
import shutil
import tempfile
from pathlib import Path

import pytest
from unittest.mock import patch

import gabbe.config
import gabbe.database
import gabbe.sync
import gabbe.verify


@pytest.fixture()
def tmp_project(tmp_path):
    """
    Provide a temporary project directory with all GABBE paths patched.

    Patches applied:
    - gabbe.config.PROJECT_ROOT
    - gabbe.config.REQUIRED_FILES  (derived from tmp_path)
    - gabbe.database.GABBE_DIR
    - gabbe.database.DB_PATH
    - gabbe.sync.TASKS_FILE
    - gabbe.verify.REQUIRED_FILES  (same list, kept for verify module-level ref)

    Yields the temporary project root Path.
    """
    gabbe_dir = tmp_path / ".gabbe"
    db_path = gabbe_dir / "state.db"
    tasks_file = tmp_path / "TASKS.md"
    required_files = [
        tmp_path / ".agents/AGENTS.md",
        tmp_path / ".agents/CONSTITUTION.md",
        tmp_path / "TASKS.md",
    ]

    with (
        patch("gabbe.config.PROJECT_ROOT", tmp_path),
        patch("gabbe.config.GABBE_DIR", gabbe_dir),
        patch("gabbe.config.DB_PATH", db_path),
        patch("gabbe.config.TASKS_FILE", tasks_file),
        patch("gabbe.config.REQUIRED_FILES", required_files),
        patch("gabbe.database.GABBE_DIR", gabbe_dir),
        patch("gabbe.database.DB_PATH", db_path),
        patch("gabbe.sync.TASKS_FILE", tasks_file),
        patch("gabbe.verify.PROJECT_ROOT", tmp_path),
        patch("gabbe.verify.GABBE_DIR", gabbe_dir),
        patch("gabbe.verify.REQUIRED_FILES", required_files),
    ):
        # Initialise the DB so every test starts clean
        from gabbe.database import init_db
        init_db()
        yield tmp_path


@pytest.fixture()
def db_conn(tmp_project):
    """Return an open DB connection against the tmp_project database."""
    from gabbe.database import get_db
    conn = get_db()
    yield conn
    conn.close()

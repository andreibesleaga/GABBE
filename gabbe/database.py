# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path

from .config import DB_PATH, GABBE_DIR, Colors

# Increment this whenever the schema changes.
SCHEMA_VERSION = 3


class StateLinkError(RuntimeError):
    """A state path (project/, state.db or logs/) is a link or leaves the project."""


def _link_problem(path: Path, root: Path) -> str | None:
    """Why `path` must not be written, or None. A missing path is fine."""
    if path.is_symlink():
        return f"{path} is a symbolic link; GABBE will not write through it"
    if path.exists() and not path.resolve().is_relative_to(root):
        return f"{path} leads outside the project folder; GABBE will not write there"
    return None


def state_path_problem(gabbe_dir: Path | None = None) -> str | None:
    """Say why the state paths cannot be used (a link, or a path outside the project root).

    Checks `project/`, `project/state.db` and `project/logs`. Nothing is created here."""
    folder = GABBE_DIR if gabbe_dir is None else gabbe_dir
    root = folder.parent.resolve()
    for path in (folder, DB_PATH if gabbe_dir is None else folder / "state.db", folder / "logs"):
        problem = _link_problem(path, root)
        if problem:
            return problem
    return None


def refuse_state_links() -> None:
    """Raise StateLinkError before the database or the audit log is opened."""
    problem = state_path_problem()
    if problem:
        raise StateLinkError(problem)


def create_private_file(path: Path) -> None:
    """Create an empty file readable by its owner only, if it does not exist yet.

    A file that exists keeps its mode. The mode is ignored where the platform has none."""
    try:
        os.close(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
    except OSError:
        pass  # exists already, or cannot be created: the caller's own open reports it


def _migrate(conn: sqlite3.Connection) -> None:
    """Apply pending schema migrations in order."""
    c = conn.cursor()
    # Prevent migration race conditions by locking the database immediately
    for attempt in range(10):
        try:
            conn.execute("BEGIN IMMEDIATE")
            break
        except sqlite3.OperationalError:
            if attempt == 9:
                raise
            time.sleep(0.2)

    c.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
    c.execute("SELECT version FROM schema_version")
    row = c.fetchone()
    current = row[0] if row else 0

    # Refuse to operate on a DB written by a NEWER GABBE. Without this guard the
    # function would run no migration blocks (all gated on current < N) and then
    # stamp version back down to SCHEMA_VERSION — silently downgrading the recorded
    # version while newer tables remain, corrupting the version contract.
    if current > SCHEMA_VERSION:
        conn.rollback()
        raise RuntimeError(
            f"Database schema version {current} is newer than this GABBE supports "
            f"({SCHEMA_VERSION}). Upgrade GABBE or use a matching version; refusing "
            "to downgrade the schema."
        )

    if current < 1:
        # v1: initial schema
        c.execute("""CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL UNIQUE,
                      status TEXT DEFAULT 'TODO',
                      tags TEXT,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("""CREATE TABLE IF NOT EXISTS project_state
                     (key TEXT PRIMARY KEY,
                      value TEXT,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("""CREATE TABLE IF NOT EXISTS events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      actor TEXT,
                      action TEXT,
                      message TEXT,
                      context_summary TEXT)""")

        c.execute("""CREATE TABLE IF NOT EXISTS genes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      skill_name TEXT,
                      prompt_content TEXT,
                      success_rate REAL DEFAULT 0.0,
                      generation INTEGER DEFAULT 0,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

    if current < 2:
        # v2: UNIQUE index on tasks.title; IF NOT EXISTS makes this idempotent
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title)")

    if current < 3:
        # v3: MVA Platform Modules schema additions
        c.execute("""CREATE TABLE IF NOT EXISTS pricing_registry
                     (model_id TEXT PRIMARY KEY,
                      input_token_price REAL DEFAULT 0.0,
                      output_token_price REAL DEFAULT 0.0,
                      reasoning_token_price REAL DEFAULT 0.0,
                      cache_creation_price REAL DEFAULT 0.0,
                      cache_read_price REAL DEFAULT 0.0,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("""CREATE TABLE IF NOT EXISTS runs
                     (id TEXT PRIMARY KEY,
                      command TEXT,
                      started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      ended_at DATETIME,
                      status TEXT,
                      stop_reason TEXT,
                      initiator TEXT,
                      agent_persona TEXT,
                      total_tokens_used INTEGER DEFAULT 0,
                      total_cost_usd REAL DEFAULT 0.0,
                      config_snapshot TEXT)""")

        c.execute("""CREATE TABLE IF NOT EXISTS audit_spans
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      span_id TEXT,
                      parent_span_id TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      event_type TEXT,
                      node_name TEXT,
                      input_data TEXT,
                      output_data TEXT,
                      reasoning_content TEXT,
                      model_name TEXT,
                      prompt_tokens INTEGER DEFAULT 0,
                      completion_tokens INTEGER DEFAULT 0,
                      reasoning_tokens INTEGER DEFAULT 0,
                      cache_hit_tokens INTEGER DEFAULT 0,
                      cost_usd REAL DEFAULT 0.0,
                      duration_ms REAL,
                      status TEXT,
                      metadata TEXT,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

        c.execute("CREATE INDEX IF NOT EXISTS idx_audit_spans_run_id ON audit_spans(run_id)")

        c.execute("""CREATE TABLE IF NOT EXISTS budget_snapshots
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      tokens_used INTEGER,
                      tool_calls_used INTEGER,
                      wall_time_sec REAL,
                      iterations INTEGER,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS checkpoints
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      node_name TEXT,
                      state_snapshot TEXT,
                      policy_version TEXT,
                      parent_checkpoint_id INTEGER,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id),
                      FOREIGN KEY(parent_checkpoint_id) REFERENCES checkpoints(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS pending_escalations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      trigger TEXT,
                      context TEXT,
                      status TEXT,
                      response TEXT,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      resolved_at DATETIME,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS forecast_snapshots
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      projected_tokens INTEGER,
                      projected_cost REAL,
                      current_error_rate REAL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

    # Upsert schema version
    if row:
        c.execute("UPDATE schema_version SET version = ?", (SCHEMA_VERSION,))
    else:
        c.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    conn.commit()


def init_db() -> None:
    """Initialize (or migrate) the SQLite database schema."""
    refuse_state_links()
    if not GABBE_DIR.exists():
        GABBE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}Created project directory{Colors.ENDC}")

    create_private_file(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        _migrate(conn)
    finally:
        conn.close()
    print(f"{Colors.GREEN}✓ Database initialized at {DB_PATH}{Colors.ENDC}")


def get_db() -> sqlite3.Connection:
    """Return a database connection with row_factory set."""
    refuse_state_links()
    if GABBE_DIR.is_dir():
        create_private_file(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

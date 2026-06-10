# SPDX-License-Identifier: Apache-2.0
"""Error-path coverage for documented failure modes (code-audit-2026-06.md §7).

Corrupt DB, malformed TASKS.md markers, unreachable LLM endpoint, and a
malformed policies.yml all fail safe rather than crash unexpectedly.
"""

import sqlite3

import pytest


def test_corrupt_sqlite_raises_databaseerror(tmp_path):
    """A corrupt state.db surfaces a sqlite3 error, not a silent wrong-answer."""
    db = tmp_path / "state.db"
    db.write_bytes(b"this is not a sqlite database" * 10)
    con = sqlite3.connect(db)
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("SELECT * FROM tasks").fetchall()
    con.close()


def test_sync_handles_malformed_markers(tmp_project, monkeypatch, tmp_path):
    """TASKS.md with a START marker but no END falls back without crashing."""
    import gabbe.sync as sync

    tasks_file = tmp_path / "TASKS.md"
    tasks_file.write_text("# Tasks\n<!-- GABBE:TASKS:START -->\n- [ ] orphan marker task\n")
    # parse_markdown_tasks must not raise on a missing END marker.
    parsed = sync.parse_markdown_tasks(tasks_file.read_text())
    assert isinstance(parsed, list)


def test_llm_missing_key_raises_environmenterror(tmp_project, monkeypatch):
    """call_llm without an API key raises a clear config error (not a network hang)."""
    import gabbe.llm as llm

    monkeypatch.setattr(llm, "GABBE_API_KEY", None, raising=False)
    monkeypatch.delenv("GABBE_API_KEY", raising=False)
    with pytest.raises((EnvironmentError, ValueError, RuntimeError)):
        llm.call_llm("hello", "system")


def test_policy_malformed_yaml_fails_safe(tmp_path):
    """A corrupt policies.yml does not yield an allow-all policy."""
    from gabbe.policy import PolicyEngine

    bad = tmp_path / "policies.yml"
    bad.write_text("tools:\n  allowed: [unclosed\n")
    try:
        engine = PolicyEngine.from_yaml(str(bad))
    except Exception:
        # Raising is acceptable (fail-closed by refusing to construct).
        return
    # If it constructed, it must NOT be permissive for an arbitrary tool/role.
    decision = engine.check_tool("run_command", role="external_agent")
    assert decision is not True

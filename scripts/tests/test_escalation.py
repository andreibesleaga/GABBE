"""Unit tests for gabbe.escalation."""
import pytest
from unittest.mock import patch
from gabbe.escalation import EscalationHandler, EscalationTrigger, EscalationPaused


def test_silent_mode_auto_rejects(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-silent", db_conn=db_conn)
    handler.mode = "silent"
    result = handler.escalate(EscalationTrigger.BUDGET_EXHAUSTED, {"detail": "no tokens left"})
    assert result.status == "rejected"


def test_silent_mode_records_to_db(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-db", db_conn=db_conn)
    handler.mode = "silent"
    handler.escalate(EscalationTrigger.POLICY_VIOLATION, {"tool": "blocked_tool"})
    rows = db_conn.execute(
        "SELECT * FROM pending_escalations WHERE run_id='run-esc-db'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["trigger"] == "POLICY_VIOLATION"
    assert rows[0]["status"] == "rejected"


def test_file_mode_raises_escalation_paused(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-file", db_conn=db_conn)
    handler.mode = "file"
    with pytest.raises(EscalationPaused):
        handler.escalate(EscalationTrigger.REPEATED_TOOL_FAILURE, {"count": 3})


def test_file_mode_records_pending_to_db(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-file2", db_conn=db_conn)
    handler.mode = "file"
    with pytest.raises(EscalationPaused):
        handler.escalate(EscalationTrigger.MAX_ITERATIONS, {"step": 25})
    rows = db_conn.execute(
        "SELECT * FROM pending_escalations WHERE run_id='run-esc-file2'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0]["status"] == "pending"


def test_cli_mode_approve(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-cli", db_conn=db_conn)
    handler.mode = "cli"
    with patch("builtins.input", return_value="a"):
        result = handler.escalate(EscalationTrigger.AMBIGUOUS_DECISION, {"question": "proceed?"})
    assert result.status == "approved"


def test_cli_mode_reject(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-cli2", db_conn=db_conn)
    handler.mode = "cli"
    with patch("builtins.input", return_value="r"):
        result = handler.escalate(EscalationTrigger.BUDGET_EXHAUSTED, {})
    assert result.status == "rejected"


def test_cli_mode_edit(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-cli3", db_conn=db_conn)
    handler.mode = "cli"
    with patch("builtins.input", side_effect=["e", '{"note": "updated"}']):
        result = handler.escalate(EscalationTrigger.POLICY_VIOLATION, {})
    assert result.status == "edited"
    assert result.response == '{"note": "updated"}'
    # Verify the response was persisted to the DB via resolve()
    row = db_conn.execute(
        "SELECT * FROM pending_escalations WHERE run_id='run-esc-cli3'"
    ).fetchone()
    assert row is not None
    assert row["status"] == "edited"
    assert row["response"] == '{"note": "updated"}'


def test_resolve_updates_db(tmp_project, db_conn):
    handler = EscalationHandler("run-esc-resolve", db_conn=db_conn)
    handler.mode = "silent"
    handler.escalate(EscalationTrigger.BUDGET_EXHAUSTED, {})

    row = db_conn.execute(
        "SELECT id FROM pending_escalations WHERE run_id='run-esc-resolve'"
    ).fetchone()
    esc_id = row["id"]

    handler.resolve(esc_id, "approved", "human reviewed")

    updated = db_conn.execute(
        "SELECT * FROM pending_escalations WHERE id=?", (esc_id,)
    ).fetchone()
    assert updated["status"] == "approved"
    assert updated["response"] == "human reviewed"
    assert updated["resolved_at"] is not None


def test_all_triggers_persist(tmp_project, db_conn):
    """All 5 EscalationTrigger values should be persistable."""
    handler = EscalationHandler("run-esc-all", db_conn=db_conn)
    handler.mode = "silent"
    for trigger in EscalationTrigger:
        handler.escalate(trigger, {"trigger": trigger.value})

    rows = db_conn.execute(
        "SELECT trigger FROM pending_escalations WHERE run_id='run-esc-all'"
    ).fetchall()
    stored_triggers = {r["trigger"] for r in rows}
    expected = {t.value for t in EscalationTrigger}
    assert expected == stored_triggers

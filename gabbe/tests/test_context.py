# SPDX-License-Identifier: Apache-2.0
"""Unit tests for gabbe.context."""

import json

from gabbe.budget import Budget, BudgetExceeded
from gabbe.context import RunContext


def test_from_config_creates_run_row(tmp_project, db_conn):
    ctx = RunContext.from_config(command="test-ctx")
    with ctx:
        row = db_conn.execute("SELECT * FROM runs WHERE id=?", (ctx.run_id,)).fetchone()
        assert row is not None
        assert row["command"] == "test-ctx"
        assert row["status"] == "running"


def test_exit_updates_status_to_completed(tmp_project, db_conn):
    ctx = RunContext.from_config(command="ctx-done")
    with ctx:
        run_id = ctx.run_id

    row = db_conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    assert row["status"] == "completed"
    assert row["ended_at"] is not None


def test_exit_on_exception_sets_error_status(tmp_project, db_conn):
    ctx = RunContext.from_config(command="ctx-err")
    run_id = ctx.run_id
    try:
        with ctx:
            raise ValueError("intentional error")
    except ValueError:
        pass

    row = db_conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    assert row["status"] == "error"
    assert "intentional error" in (row["stop_reason"] or "")


def test_budget_exceeded_sets_status(tmp_project, db_conn):
    tiny = Budget(max_tokens=0)
    tiny.tokens_used = 1  # pre-exceed
    ctx = RunContext.from_config(command="ctx-budget", budget=tiny)
    run_id = ctx.run_id
    try:
        with ctx:
            ctx.budget.check()
    except BudgetExceeded:
        pass

    row = db_conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    assert row["status"] == "budget_exceeded"


def test_run_id_is_uuid_string(tmp_project):
    ctx = RunContext.from_config(command="ctx-uuid")
    import uuid

    assert isinstance(ctx.run_id, str)
    uuid.UUID(ctx.run_id)  # raises if not valid UUID


def test_default_attributes(tmp_project):
    ctx = RunContext.from_config(command="ctx-attrs")
    assert ctx.budget is not None
    assert ctx.hard_stop is not None
    assert ctx.policy is not None
    assert ctx.gateway is not None
    assert ctx.escalation is not None
    assert ctx.checkpoints is not None
    assert ctx.tracer is not None


def test_config_snapshot_stored(tmp_project, db_conn):
    ctx = RunContext.from_config(command="ctx-snap")
    with ctx:
        row = db_conn.execute(
            "SELECT config_snapshot FROM runs WHERE id=?", (ctx.run_id,)
        ).fetchone()
        snap = json.loads(row["config_snapshot"])
        assert "budget" in snap
        assert "policy_version" in snap


def test_total_tokens_updated_on_exit(tmp_project, db_conn):
    ctx = RunContext.from_config(command="ctx-tokens")
    with ctx:
        ctx.budget.tokens_used = 42
        ctx.budget.cost_usd = 0.01
        run_id = ctx.run_id

    row = db_conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    assert row["total_tokens_used"] == 42
    assert abs(row["total_cost_usd"] - 0.01) < 1e-6


def test_initiator_and_persona_stored(tmp_project, db_conn):
    ctx = RunContext(command="brain activate", initiator="mcp", agent_persona="researcher")
    with ctx:
        row = db_conn.execute("SELECT * FROM runs WHERE id=?", (ctx.run_id,)).fetchone()
        assert row["initiator"] == "mcp"
        assert row["agent_persona"] == "researcher"


def test_from_checkpoint(tmp_project, db_conn):
    import uuid

    run_id = str(uuid.uuid4())
    config_snap = {"budget": {"max_tokens": 500, "max_tool_calls": 15, "max_cost_usd": 2.0}}
    db_conn.execute(
        "INSERT INTO runs (id, command, status, config_snapshot) VALUES (?, ?, ?, ?)",
        (run_id, "original", "completed", json.dumps(config_snap)),
    )
    db_conn.execute(
        "INSERT INTO checkpoints (run_id, step, node_name, state_snapshot, policy_version) VALUES (?, ?, ?, ?, ?)",
        (run_id, 0, "start", json.dumps({"k": "v"}), "v1"),
    )
    db_conn.commit()

    cp_id = db_conn.execute("SELECT id FROM checkpoints WHERE run_id=?", (run_id,)).fetchone()["id"]

    replay_ctx = RunContext.from_checkpoint(cp_id)
    assert replay_ctx.budget.max_tokens == 500
    assert replay_ctx.budget.max_tool_calls == 15
    assert "replay" in replay_ctx.command

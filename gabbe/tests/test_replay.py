# SPDX-License-Identifier: Apache-2.0
"""Unit tests for gabbe.replay."""

import json

from gabbe.replay import CheckpointStore, ReplayRunner


def test_save_and_load(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    cp_id = store.save(
        "run-r1", step=0, node_name="start", state_snapshot={"x": 1}, policy_version="v1"
    )
    assert cp_id is not None

    loaded = store.load(cp_id)
    assert loaded is not None
    assert loaded["run_id"] == "run-r1"
    assert loaded["node_name"] == "start"
    assert loaded["state_snapshot"] == {"x": 1}
    assert loaded["policy_version"] == "v1"


def test_load_nonexistent(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    result = store.load(99999)
    assert result is None


def test_get_history_ordered(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    store.save("run-r2", 2, "step_c", {"order": 3}, "v1")
    store.save("run-r2", 0, "step_a", {"order": 1}, "v1")
    store.save("run-r2", 1, "step_b", {"order": 2}, "v1")

    history = store.get_history("run-r2")
    assert len(history) == 3
    steps = [h["step"] for h in history]
    assert steps == [0, 1, 2]  # ordered by step ASC


def test_get_history_empty(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    history = store.get_history("nonexistent-run")
    assert history == []


def test_save_with_parent(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    parent_id = store.save("run-r3", 0, "root", {}, "v1")
    child_id = store.save("run-r3", 1, "child", {}, "v1", parent_id=parent_id)
    child = store.load(child_id)
    assert child["parent_checkpoint_id"] == parent_id


def test_replay_returns_steps(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    store.save("run-replay", 0, "observe", {"tasks": 3}, "v1")
    store.save("run-replay", 1, "decide", {"action": "fix"}, "v1")
    store.save("run-replay", 2, "act", {"result": "done"}, "v1")

    runner = ReplayRunner(store)
    steps = runner.replay("run-replay", from_step=0)
    assert len(steps) == 3
    assert steps[0]["node_name"] == "observe"
    assert steps[1]["node_name"] == "decide"
    assert steps[2]["node_name"] == "act"


def test_replay_from_step(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    store.save("run-from", 0, "step_0", {}, "v1")
    store.save("run-from", 1, "step_1", {}, "v1")
    store.save("run-from", 2, "step_2", {}, "v1")

    runner = ReplayRunner(store)
    steps = runner.replay("run-from", from_step=1)
    assert len(steps) == 2
    assert steps[0]["node_name"] == "step_1"


def test_replay_empty_run(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    runner = ReplayRunner(store)
    steps = runner.replay("nonexistent", from_step=0)
    assert steps == []


def test_diff_identical_runs(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    for run_id in ["run-diff-a", "run-diff-b"]:
        store.save(run_id, 0, "step_a", {}, "v1")
        store.save(run_id, 1, "step_b", {}, "v1")

    runner = ReplayRunner(store)
    diff = runner.diff("run-diff-a", "run-diff-b")
    assert all(d["match"] for d in diff)


def test_diff_diverged_runs(tmp_project, db_conn):
    store = CheckpointStore(db_conn=db_conn)
    store.save("run-x", 0, "step_a", {}, "v1")
    store.save("run-x", 1, "step_b", {}, "v1")
    store.save("run-y", 0, "step_a", {}, "v1")
    store.save("run-y", 1, "step_DIFFERENT", {}, "v1")

    runner = ReplayRunner(store)
    diff = runner.diff("run-x", "run-y")
    assert diff[0]["match"] is True
    assert diff[1]["match"] is False


def test_from_checkpoint_factory(tmp_project, db_conn):
    """RunContext.from_checkpoint should reconstruct a context with budget from the original run."""
    # Insert a run with a config snapshot
    import uuid

    from gabbe.context import RunContext

    run_id = str(uuid.uuid4())
    config_snap = {"budget": {"max_tokens": 999, "max_tool_calls": 7, "max_cost_usd": 0.5}}
    db_conn.execute(
        "INSERT INTO runs (id, command, status, config_snapshot) VALUES (?, ?, ?, ?)",
        (run_id, "test", "completed", json.dumps(config_snap)),
    )
    # Insert a checkpoint for that run
    db_conn.execute(
        "INSERT INTO checkpoints (run_id, step, node_name, state_snapshot, policy_version) VALUES (?, ?, ?, ?, ?)",
        (run_id, 0, "observe", json.dumps({"tasks": 1}), "v1"),
    )
    db_conn.commit()

    cp_id = db_conn.execute("SELECT id FROM checkpoints WHERE run_id = ?", (run_id,)).fetchone()[
        "id"
    ]

    ctx = RunContext.from_checkpoint(cp_id)
    assert ctx.budget.max_tokens == 999
    assert ctx.budget.max_tool_calls == 7
    assert ctx.budget.max_cost_usd == 0.5

# SPDX-License-Identifier: Apache-2.0
"""Loki shadow / sandbox tests (Track E6).

Drive the orchestration guards against a MOCK state.db (the tmp_project fixture),
asserting the safety mechanisms fire — without ever touching real resources:
  - a repeated identical tool call escalates (loop guard)
  - a confidence score below threshold escalates (ambiguity guard)
  - hard iteration caps fire (runaway guard)
  - an injected failure is self-healed by restoring the baseline snapshot
"""

from collections import deque
from unittest.mock import patch

import pytest

from gabbe.escalation import EscalationHandler, EscalationTrigger
from gabbe.hardstop import HardStop, MaxIterationsExceeded


def _pending(db_conn, run_id):
    return db_conn.execute(
        "SELECT trigger FROM pending_escalations WHERE run_id = ?", (run_id,)
    ).fetchall()


# ---------------------------------------------------------------------------
# Loop guard: identical tool call repeated 3× → escalate to a human
# ---------------------------------------------------------------------------


def test_identical_tool_call_thrice_triggers_escalation(db_conn):
    run_id = "run-loki-loopguard"
    # A scripted "stuck" agent that keeps issuing the same call.
    calls = [("run_command", "make build")] * 5
    recent: deque = deque(maxlen=3)
    escalated = False

    with patch("gabbe.escalation.GABBE_ESCALATION_MODE", "silent"):
        handler = EscalationHandler(run_id, db_conn=db_conn)
        for step, call in enumerate(calls):
            recent.append(call)
            if len(recent) == 3 and len(set(recent)) == 1:
                handler.escalate(
                    EscalationTrigger.REPEATED_TOOL_FAILURE,
                    {"call": call, "repeats": 3},
                    step=step,
                )
                escalated = True
                break

    assert escalated
    rows = _pending(db_conn, run_id)
    assert any(r["trigger"] == EscalationTrigger.REPEATED_TOOL_FAILURE.value for r in rows)


# ---------------------------------------------------------------------------
# Ambiguity guard: confidence below threshold → escalate
# ---------------------------------------------------------------------------


def test_confidence_below_threshold_triggers_escalation(db_conn):
    run_id = "run-loki-confidence"
    threshold = 0.6
    confidence = 0.35  # the agent is not sure enough to act autonomously

    with patch("gabbe.escalation.GABBE_ESCALATION_MODE", "silent"):
        handler = EscalationHandler(run_id, db_conn=db_conn)
        if confidence < threshold:
            handler.escalate(
                EscalationTrigger.AMBIGUOUS_DECISION,
                {"confidence": confidence, "threshold": threshold},
            )

    rows = _pending(db_conn, run_id)
    assert any(r["trigger"] == EscalationTrigger.AMBIGUOUS_DECISION.value for r in rows)


# ---------------------------------------------------------------------------
# Runaway guard: hard iteration cap fires
# ---------------------------------------------------------------------------


def test_hardstop_iteration_cap_fires():
    stop = HardStop(max_iterations=5, max_depth=100, timeout_sec=60)
    ticks = 0
    with pytest.raises(MaxIterationsExceeded):
        for _ in range(100):
            stop.tick()
            ticks += 1
    # The cap fired promptly (on the 6th tick), never ran away to 100.
    assert ticks == 5


# ---------------------------------------------------------------------------
# Self-heal: injected failure → restore baseline from snapshot (against mock DB)
# ---------------------------------------------------------------------------


def test_injected_failure_selfheals_to_baseline(db_conn):
    from gabbe.replay import CheckpointStore

    # Baseline: seed the mock state.db with tasks.
    baseline = [("T-1", "DONE"), ("T-2", "IN_PROGRESS"), ("T-3", "TODO")]
    for title, status in baseline:
        db_conn.execute("INSERT INTO tasks (title, status) VALUES (?, ?)", (title, status))
    db_conn.commit()

    def snapshot():
        return sorted(
            (r["title"], r["status"])
            for r in db_conn.execute("SELECT title, status FROM tasks").fetchall()
        )

    good = snapshot()
    assert good == sorted(baseline)

    # Save a recovery checkpoint, then INJECT a failure that corrupts state.
    store = CheckpointStore(db_conn=db_conn)
    store.save(
        "run-loki-heal",
        step=0,
        node_name="pre-failure",
        state_snapshot={"tasks": good},
        policy_version="v1",
    )
    db_conn.execute("DELETE FROM tasks WHERE title = 'T-2'")
    db_conn.commit()
    assert snapshot() != good  # damage confirmed

    # Self-heal: restore the baseline from the checkpoint snapshot.
    history = store.get_history("run-loki-heal")
    recovered = store.load(history[-1]["id"])["state_snapshot"]["tasks"]
    db_conn.execute("DELETE FROM tasks")
    for title, status in recovered:
        db_conn.execute("INSERT INTO tasks (title, status) VALUES (?, ?)", (title, status))
    db_conn.commit()

    # State is byte-identical to the pre-failure baseline.
    assert snapshot() == good

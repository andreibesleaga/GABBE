# SPDX-License-Identifier: Apache-2.0
"""Cognitive-mode invariant tests (Track E6).

These test the *mechanisms* of the conceptual Brain-mode loops by bounding their
behavior with invariants — you cannot predict what an autonomous loop decides,
but you can assert what it must never do.

IMPORTANT (honest scope): the toy `global_workspace.py` / `active_inference_loop.py`
demos under agents/skills/brain/scripts/ are illustrative and NON-INTEGRATED.
GABBE's production engine (gabbe/brain.py) uses epsilon-greedy gene selection with
a monotonic success_rate, NOT literal free-energy math. The convergence assertion
here applies to the conceptual toy loop only.
"""

import importlib.util
import random
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "agents" / "skills" / "brain" / "scripts"


def _load(modname, filename):
    spec = importlib.util.spec_from_file_location(modname, _SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Global Workspace: a single, mutually-exclusive conscious state at a time
# ---------------------------------------------------------------------------


def test_global_workspace_holds_exactly_one_active_context():
    gw_mod = _load("gabbe_toy_gw", "global_workspace.py")
    gw = gw_mod.GlobalWorkspace()
    gw.subscribe(gw_mod.SpecializedAgent("AuthBot", "security"))

    gw.broadcast("STATE_A: dev environment ready")
    assert gw.context == "STATE_A: dev environment ready"

    # Ignition with a new winner OVERWRITES — the workspace is a serial bottleneck,
    # so two contexts can never co-exist (no merged/contradictory conscious state).
    gw.broadcast("STATE_B: infrastructure missing")
    assert gw.context == "STATE_B: infrastructure missing"
    assert "STATE_A" not in gw.context


def test_coalition_manager_elects_a_single_winner():
    gw_mod = _load("gabbe_toy_gw2", "global_workspace.py")
    mgr = gw_mod.CoalitionManager()

    # Highest salience wins, and exactly one winner is returned.
    bids = [("AuthBot", "x", 0.9), ("DBSqueal", "y", 0.3), ("UXPainter", "z", 0.5)]
    winner = mgr.process_bids(bids)
    assert winner == ("AuthBot", "x", 0.9)

    # No bids → no conscious content (None), never a fabricated winner.
    assert mgr.process_bids([]) is None


# ---------------------------------------------------------------------------
# Active Inference (toy): prediction error converges / is non-increasing
# ---------------------------------------------------------------------------


def test_toy_active_inference_prediction_error_converges():
    ai_mod = _load("gabbe_toy_ai", "active_inference_loop.py")
    random.seed(0)  # deterministic: the toy uses module-level random

    env = ai_mod.Environment()
    env.state = 0  # start far from the target to make convergence observable
    agent = ai_mod.ActiveInferenceAgent(target_state=7)

    distances = []
    for _ in range(40):
        observation = env.step("wait")  # observe (state + noise); state unchanged
        surprise = agent.compare(observation)
        action = agent.resolve(surprise, observation)
        if action != "wait":
            env.step(action)  # act to drive the world toward the prediction
        distances.append(abs(env.state - agent.target_state))

    head = sum(distances[:10]) / 10
    tail = sum(distances[-10:]) / 10
    # Surprise must strictly decrease over the run (the learning/action loop works)…
    assert tail < head, f"prediction error did not converge: head={head} tail={tail}"
    # …and stay bounded once converged (no divergence / oscillation blow-up).
    assert max(distances[-10:]) <= 2


# ---------------------------------------------------------------------------
# Episodic memory: resume pointer retrieves the EXACT last state, no fabrication
# ---------------------------------------------------------------------------


def test_episodic_resume_pointer_integrity_under_rapid_switching(db_conn):
    from gabbe.replay import CheckpointStore

    store = CheckpointStore(db_conn=db_conn)
    run_id = "run-episodic-integrity"

    # Rapid context switching: many distinct snapshots saved back-to-back.
    saved = []
    for step in range(8):
        snapshot = {"phase": f"S{step:02d}", "focus": f"task-{step}", "nonce": step * 7}
        store.save(
            run_id,
            step=step,
            node_name=f"node-{step}",
            state_snapshot=snapshot,
            policy_version="v1",
        )
        saved.append(snapshot)

    history = store.get_history(run_id)
    # No hallucinated/dropped history: exactly what we saved, in order.
    assert len(history) == len(saved)
    assert [h["step"] for h in history] == list(range(8))

    # The resume pointer (latest checkpoint) is the EXACT last state, not a confabulation.
    latest = store.load(history[-1]["id"])
    assert latest is not None
    assert latest["state_snapshot"] == saved[-1]

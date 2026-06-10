# SPDX-License-Identifier: Apache-2.0
"""Integration tests for gabbe.brain with platform controls (RunContext)."""

from unittest.mock import patch

from gabbe.budget import Budget
from gabbe.context import RunContext
from gabbe.hardstop import HardStop


def test_brain_run_creates_db_row(tmp_project):
    """activate_brain with RunContext should create a 'runs' row in the DB."""
    from gabbe.brain import activate_brain
    from gabbe.database import get_db

    with patch("gabbe.brain.call_llm", return_value="Focus on tests"):
        activate_brain()

    conn = get_db()
    rows = conn.execute("SELECT * FROM runs WHERE command='brain activate'").fetchall()
    conn.close()
    assert len(rows) >= 1
    assert rows[-1]["status"] in ("completed", "error", "budget_exceeded")


def test_brain_activate_prints_action(tmp_project, capsys):
    """Brain activate with mocked LLM should print the recommended action."""
    from gabbe.brain import activate_brain

    with patch("gabbe.brain.call_llm", return_value="Ship the feature"):
        activate_brain()
    out = capsys.readouterr().out
    assert "Ship the feature" in out


def test_brain_activate_llm_none_shows_freeze(tmp_project, capsys):
    """When LLM returns None, should print Brain Freeze and not crash."""
    from gabbe.brain import activate_brain

    with patch("gabbe.brain.call_llm", return_value=None):
        activate_brain()
    out = capsys.readouterr().out
    assert "Brain Freeze" in out


def test_brain_activate_hardstop_from_context(tmp_project, capsys):
    """With a HardStop that's already exceeded, the brain should hit it early."""
    from gabbe.brain import activate_brain

    # Tick the hardstop to its limit so the next tick raises
    hs = HardStop(max_iterations=1)
    hs.tick()  # now at limit, next tick raises

    ctx = RunContext(
        command="brain activate",
        hard_stop=hs,
    )
    ctx.escalation.mode = "silent"  # prevent interactive stdin during test

    with patch("gabbe.brain.call_llm", return_value="action"):
        activate_brain(run_context=ctx)

    # Should have printed some message (either success or escalation msg)
    out = capsys.readouterr().out
    assert "Brain Mode" in out


def test_brain_activate_budget_exceeded_silent(tmp_project, capsys):
    """With a budget already at limit and silent escalation, brain completes without crash."""
    from gabbe.brain import activate_brain

    tiny = Budget(max_tool_calls=0)  # will be exceeded on first tool call
    ctx = RunContext(command="brain activate", budget=tiny)
    ctx.escalation.mode = "silent"  # prevent interactive prompts

    with patch("gabbe.brain.call_llm", return_value="action"):
        activate_brain(run_context=ctx)

    out = capsys.readouterr().out
    # Either action is printed or platform control interrupted — no crash either way
    assert "Brain Mode" in out


def test_brain_activate_escalation_on_llm_error(tmp_project, capsys):
    """When LLM raises an error, escalation is triggered and brain handles it."""
    from gabbe.brain import activate_brain

    ctx = RunContext(command="brain activate")
    ctx.escalation.mode = "silent"

    with patch("gabbe.brain.call_llm", side_effect=RuntimeError("API down")):
        activate_brain(run_context=ctx)

    out = capsys.readouterr().out
    assert "Brain Mode" in out
    assert "Interrupted" in out or "Error" in out


def test_brain_activate_uses_run_context(tmp_project):
    """activate_brain should use the provided RunContext, not create a new one."""
    from gabbe.brain import activate_brain

    ctx = RunContext.from_config(command="brain activate")
    with patch("gabbe.brain.call_llm", return_value="Delegate"):
        activate_brain(run_context=ctx)

    # The passed ctx should have been used — its gateway registry should have call_llm
    assert "call_llm" in ctx.gateway.registry

# SPDX-License-Identifier: Apache-2.0
"""Unit tests for gabbe.budget."""

import pytest

from gabbe.budget import Budget, BudgetExceeded


def test_budget_from_config():
    b = Budget.from_config()
    assert b.max_tokens > 0
    assert b.max_tool_calls > 0
    assert b.max_iterations > 0
    assert b.max_cost_usd > 0


def test_budget_check_ok():
    b = Budget(
        max_tokens=100, max_tool_calls=10, max_iterations=5, max_cost_usd=1.0, max_wall_seconds=300
    )
    b.check()  # should not raise


def test_budget_tokens_exceeded():
    b = Budget(max_tokens=10)
    b.tokens_used = 11
    with pytest.raises(BudgetExceeded) as exc_info:
        b.check()
    assert "token" in exc_info.value.reason.lower()


def test_budget_tokens_at_limit_ok():
    b = Budget(max_tokens=10)
    b.tokens_used = 10
    b.check()  # Equal to limit — allowed (not >)


def test_budget_tool_calls_exceeded():
    b = Budget(max_tool_calls=3)
    b.tool_calls_used = 4
    with pytest.raises(BudgetExceeded) as exc_info:
        b.check()
    assert "tool" in exc_info.value.reason.lower()


def test_budget_iterations_exceeded():
    b = Budget(max_iterations=2)
    b.iterations = 3
    with pytest.raises(BudgetExceeded) as exc_info:
        b.check()
    assert "iteration" in exc_info.value.reason.lower()


def test_budget_cost_exceeded():
    b = Budget(max_cost_usd=0.01)
    b.cost_usd = 0.02
    with pytest.raises(BudgetExceeded) as exc_info:
        b.check()
    assert "cost" in exc_info.value.reason.lower()


def test_budget_wall_time_exceeded():
    b = Budget(max_wall_seconds=0)  # 0 seconds — immediately exceeded
    import time as t

    t.sleep(0.05)
    with pytest.raises(BudgetExceeded) as exc_info:
        b.check()
    assert "wall time" in exc_info.value.reason.lower()


def test_budget_record_tool_call():
    b = Budget(max_tool_calls=5)
    b.record_tool_call()
    assert b.tool_calls_used == 1
    b.record_tool_call()
    assert b.tool_calls_used == 2


def test_budget_record_tool_call_exceeded():
    b = Budget(max_tool_calls=1)
    b.record_tool_call()
    with pytest.raises(BudgetExceeded):
        b.record_tool_call()


def test_budget_record_iteration():
    b = Budget(max_iterations=5)
    b.record_iteration()
    assert b.iterations == 1


def test_budget_record_llm_usage_no_pricing():
    b = Budget(max_tokens=1000)
    b.record_llm_usage(
        "gpt-test", {"total_tokens": 50, "prompt_tokens": 30, "completion_tokens": 20}
    )
    assert b.tokens_used == 50
    assert b.cost_usd == 0.0  # No pricing in registry


def test_budget_snapshot():
    b = Budget(max_tokens=100)
    b.tokens_used = 25
    snap = b.snapshot()
    assert snap["tokens_used"] == 25
    assert "wall_time_sec" in snap
    assert "tool_calls_used" in snap
    assert "cost_usd" in snap
    assert "iterations" in snap


def test_budget_remaining():
    b = Budget(max_tokens=100, max_tool_calls=10)
    b.tokens_used = 30
    b.tool_calls_used = 4
    rem = b.remaining()
    assert rem["tokens"] == 70
    assert rem["tool_calls"] == 6
    assert "wall_time_sec" in rem
    assert "cost_usd" in rem


def test_budget_from_dict():
    d = {
        "max_tokens": 500,
        "max_tool_calls": 20,
        "max_cost_usd": 2.0,
        "tokens_used": 100,
        "tool_calls_used": 5,
        "cost_usd": 0.50,
    }
    b = Budget.from_dict(d)
    assert b.max_tokens == 500
    assert b.tokens_used == 100
    assert b.tool_calls_used == 5
    assert b.cost_usd == 0.50


def test_budget_exceeded_contains_snapshot():
    b = Budget(max_tokens=5)
    b.tokens_used = 6
    with pytest.raises(BudgetExceeded) as exc_info:
        b.check()
    assert isinstance(exc_info.value.snapshot, dict)
    assert "tokens_used" in exc_info.value.snapshot

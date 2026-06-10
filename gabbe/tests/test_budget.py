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


def test_budget_cached_tokens_reduce_cost_not_double_billed():
    """Cached prompt tokens (a subset of prompt_tokens) must be billed once at the
    cache-read rate, not at full input price + cache-read on top. Caching should
    LOWER tracked cost, never raise it (regression for the double-count bug)."""
    b = Budget(max_tokens=10_000)
    # Inject a price for a synthetic model: input 10/Mtok, cache_read 1/Mtok (0.1x).
    b._cached_prices["cache-model"] = {
        "input": 10e-6,
        "output": 30e-6,
        "reasoning": 0.0,
        "cache_creation": 12.5e-6,
        "cache_read": 1e-6,
    }
    # Request A: 1000 prompt tokens, none cached.
    b.record_llm_usage(
        "cache-model",
        {
            "total_tokens": 1000,
            "prompt_tokens": 1000,
            "completion_tokens": 0,
        },
    )
    cost_uncached = b.cost_usd

    # Request B: same 1000 prompt tokens, 800 served from cache.
    b2 = Budget(max_tokens=10_000)
    b2._cached_prices["cache-model"] = b._cached_prices["cache-model"]
    b2.record_llm_usage(
        "cache-model",
        {
            "total_tokens": 1000,
            "prompt_tokens": 1000,
            "completion_tokens": 0,
            "prompt_tokens_details": {"cached_tokens": 800},
        },
    )
    cost_cached = b2.cost_usd

    # 800 cached @1/M + 200 fresh @10/M = 0.0008 + 0.002 = 0.0028
    assert abs(cost_cached - (800 * 1e-6 + 200 * 10e-6)) < 1e-12
    # Caching must strictly reduce cost vs the all-uncached request.
    assert cost_cached < cost_uncached


def test_budget_anthropic_cache_read_field_supported():
    """Anthropic-style cache_read_input_tokens is also honored."""
    b = Budget(max_tokens=10_000)
    b._cached_prices["anthropic-model"] = {
        "input": 10e-6,
        "output": 30e-6,
        "reasoning": 0.0,
        "cache_creation": 0.0,
        "cache_read": 1e-6,
    }
    b.record_llm_usage(
        "anthropic-model",
        {
            "total_tokens": 500,
            "prompt_tokens": 500,
            "completion_tokens": 0,
            "cache_read_input_tokens": 400,
        },
    )
    # 400 cached @1/M + 100 fresh @10/M = 0.0004 + 0.001 = 0.0014
    assert abs(b.cost_usd - (400 * 1e-6 + 100 * 10e-6)) < 1e-12

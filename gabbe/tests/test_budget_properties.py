# SPDX-License-Identifier: Apache-2.0
"""Property-based tests for the budget enforcer (Track B Phase 1).

Invariant under test: across ANY sequence of usage records, the budget never
silently exceeds a cap — it either stays within bounds or raises BudgetExceeded
at the moment it crosses. PBT samples the input space and raises confidence; it
does not prove correctness.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from gabbe.budget import Budget, BudgetExceeded

_HUGE = 10**12
# Hypothesis reuses a function-scoped fixture across examples; the budget makes a
# fresh object per example, so this is safe to suppress.
_S = settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=120)


@_S
@given(chunks=st.lists(st.integers(min_value=0, max_value=5000), max_size=40))
def test_token_cap_never_silently_exceeded(tmp_project, chunks):
    cap = 10_000
    b = Budget(
        max_tokens=cap,
        max_cost_usd=_HUGE,
        max_tool_calls=_HUGE,
        max_iterations=_HUGE,
        max_wall_seconds=_HUGE,
    )
    cumulative = 0
    for c in chunks:
        cumulative += c
        try:
            # zero-priced model isolates the token cap from cost
            b.record_llm_usage("no-price-model", {"total_tokens": c})
        except BudgetExceeded:
            # It may only raise AFTER the cumulative total crosses the cap.
            assert b.tokens_used > cap
            return
        # No raise => still within bounds, and the counter is exact.
        assert b.tokens_used == cumulative
        assert b.tokens_used <= cap


@_S
@given(calls=st.integers(min_value=0, max_value=50))
def test_tool_call_cap_enforced(tmp_project, calls):
    cap = 20
    b = Budget(
        max_tokens=_HUGE,
        max_cost_usd=_HUGE,
        max_tool_calls=cap,
        max_iterations=_HUGE,
        max_wall_seconds=_HUGE,
    )
    raised_at = None
    for i in range(calls):
        try:
            b.record_tool_call()
        except BudgetExceeded:
            raised_at = i
            break
    if raised_at is not None:
        # Raises exactly once the (cap+1)-th call pushes used past the cap.
        assert b.tool_calls_used == cap + 1
    else:
        assert b.tool_calls_used == calls <= cap


@_S
@given(
    tokens=st.integers(min_value=0, max_value=10_000),
    price=st.floats(min_value=0, max_value=0.01, allow_nan=False, allow_infinity=False),
)
def test_cost_is_monotonic_nonnegative(tmp_project, tokens, price):
    b = Budget(
        max_tokens=_HUGE,
        max_cost_usd=_HUGE,
        max_tool_calls=_HUGE,
        max_iterations=_HUGE,
        max_wall_seconds=_HUGE,
    )
    b._cached_prices["m"] = {
        "input": price,
        "output": price,
        "reasoning": price,
        "cache_creation": price,
        "cache_read": price,
    }
    before = b.cost_usd
    b.record_llm_usage(
        "m", {"total_tokens": tokens, "prompt_tokens": tokens, "completion_tokens": 0}
    )
    # Cost only ever grows and is never negative.
    assert b.cost_usd >= before >= 0.0

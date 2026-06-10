# SPDX-License-Identifier: Apache-2.0
"""Unit tests for gabbe.gateway."""
import pytest
from gabbe.gateway import ToolDefinition, ToolNotFound, PolicyDenied, CircuitOpen, RateLimitExceeded
from gabbe.budget import Budget, BudgetExceeded
from gabbe.policy import PolicyEngine, ToolAllowlistPolicy


def _allow_all_policy():
    """Return a PolicyEngine that allows all tools (for gateway unit testing)."""
    return PolicyEngine([ToolAllowlistPolicy(["*"], [])])


def _simple_tool(x=1):
    return x * 2


def test_register_and_execute(tmp_project):
    from gabbe.context import RunContext
    with RunContext.from_config(command="gw-test", policy=_allow_all_policy()) as ctx:
        ctx.gateway.register(ToolDefinition("double", "doubles x", {}, _simple_tool, {"tester"}))
        result = ctx.gateway.execute("double", {"x": 5}, "tester", ctx)
        assert result == 10


def test_tool_not_found(tmp_project):
    from gabbe.context import RunContext
    with RunContext.from_config(command="gw-test", policy=_allow_all_policy()) as ctx:
        with pytest.raises(ToolNotFound):
            ctx.gateway.execute("nonexistent", {}, "tester", ctx)


def test_policy_denied(tmp_project):
    from gabbe.context import RunContext
    deny_policy = PolicyEngine([ToolAllowlistPolicy([], ["double"])])
    with RunContext.from_config(command="gw-test", policy=deny_policy) as ctx:
        ctx.gateway.register(ToolDefinition("double", "desc", {}, _simple_tool, {"tester"}))
        with pytest.raises(PolicyDenied):
            ctx.gateway.execute("double", {}, "tester", ctx)


def test_budget_exceeded_on_execute(tmp_project):
    from gabbe.context import RunContext
    tiny_budget = Budget(max_tool_calls=0)
    tiny_budget.tool_calls_used = 1  # already over limit
    with RunContext.from_config(command="gw-test", budget=tiny_budget, policy=_allow_all_policy()) as ctx:
        ctx.gateway.register(ToolDefinition("noop", "desc", {}, lambda: None, {"tester"}))
        with pytest.raises(BudgetExceeded):
            ctx.gateway.execute("noop", {}, "tester", ctx)


def test_circuit_breaker_opens(tmp_project):
    from gabbe.context import RunContext
    def failing_tool():
        raise RuntimeError("fail")

    with RunContext.from_config(command="gw-test", policy=_allow_all_policy()) as ctx:
        ctx.gateway.register(ToolDefinition("fail_tool", "desc", {}, failing_tool, {"t"}, circuit_breaker_threshold=2))
        for _ in range(2):
            with pytest.raises(RuntimeError):
                ctx.gateway.execute("fail_tool", {}, "t", ctx)
        with pytest.raises(CircuitOpen):
            ctx.gateway.execute("fail_tool", {}, "t", ctx)


def test_circuit_breaker_resets_on_success(tmp_project):
    from gabbe.context import RunContext
    call_count = {"n": 0}
    def sometimes_fails():
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("first fail")
        return "ok"

    with RunContext.from_config(command="gw-test", policy=_allow_all_policy()) as ctx:
        ctx.gateway.register(ToolDefinition("conditional", "desc", {}, sometimes_fails, {"t"}, circuit_breaker_threshold=3))
        with pytest.raises(RuntimeError):
            ctx.gateway.execute("conditional", {}, "t", ctx)
        result = ctx.gateway.execute("conditional", {}, "t", ctx)
        assert result == "ok"
        assert ctx.gateway._failure_counts["conditional"] == 0


def test_rate_limit(tmp_project):
    from gabbe.context import RunContext
    with RunContext.from_config(command="gw-test", policy=_allow_all_policy()) as ctx:
        ctx.gateway.register(ToolDefinition("rate_tool", "desc", {}, lambda: "ok", {"t"}, rate_limit_per_min=2))
        ctx.gateway.execute("rate_tool", {}, "t", ctx)
        ctx.gateway.execute("rate_tool", {}, "t", ctx)
        with pytest.raises(RateLimitExceeded):
            ctx.gateway.execute("rate_tool", {}, "t", ctx)


def test_execute_records_audit_span(tmp_project):
    from gabbe.context import RunContext
    from gabbe.database import get_db
    with RunContext.from_config(command="gw-audit", policy=_allow_all_policy()) as ctx:
        ctx.gateway.register(ToolDefinition("spy", "desc", {}, lambda: "seen", {"t"}))
        ctx.gateway.execute("spy", {}, "t", ctx)
    conn = get_db()
    spans = conn.execute("SELECT * FROM audit_spans WHERE event_type='tool_call'").fetchall()
    conn.close()
    assert len(spans) >= 1
    assert any(s["node_name"] == "spy" for s in spans)

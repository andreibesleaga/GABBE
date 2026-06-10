# SPDX-License-Identifier: Apache-2.0
import pytest
from gabbe.budget import Budget, BudgetExceeded
from gabbe.hardstop import HardStop, MaxIterationsExceeded
from gabbe.gateway import ToolGateway, ToolDefinition
from gabbe.policy import PolicyEngine, ToolAllowlistPolicy
from gabbe.context import RunContext

def test_budget_limits():
    b = Budget(max_tokens=100)
    b.tokens_used = 100
    # Equal is fine
    b.check()
    # Exceed
    b.tokens_used = 101
    with pytest.raises(BudgetExceeded):
        b.check()

def test_hardstop_limits():
    h = HardStop(max_iterations=3)
    h.tick()
    h.tick()
    h.tick()
    with pytest.raises(MaxIterationsExceeded):
        h.tick()

def test_gateway_registration():
    gw = ToolGateway()
    def dummy(): return "ok"
    gw.register(ToolDefinition("dummy", "desc", {}, dummy, {"agent"}))
    assert "dummy" in gw.registry

def test_policy_allowlist():
    p = ToolAllowlistPolicy(["allow"], ["deny"])
    engine = PolicyEngine([p])
    
    assert engine.evaluate({"tool": "allow"}).allowed is True
    assert engine.evaluate({"tool": "deny"}).allowed is False
    assert engine.evaluate({"tool": "other"}).allowed is False

def test_run_context_lifecycle(tmp_project):
    ctx = RunContext.from_config(command="test")
    with ctx:
        assert ctx.run_id is not None
        # Budget shouldn't be exceeded right away
        ctx.budget.check()

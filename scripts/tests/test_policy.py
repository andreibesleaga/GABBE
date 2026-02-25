"""Unit tests for gabbe.policy."""
from gabbe.policy import (
    PolicyEngine,
    ToolAllowlistPolicy,
    RolePolicy,
    ContentSafetyPolicy,
    ParameterRangePolicy,
)


# --------------------------------------------------------------------------
# ToolAllowlistPolicy
# --------------------------------------------------------------------------

def test_allowlist_allows():
    p = ToolAllowlistPolicy(["call_llm", "run_test"], [])
    engine = PolicyEngine([p])
    result = engine.evaluate({"tool": "call_llm"})
    assert result.allowed is True


def test_allowlist_denies_explicit():
    p = ToolAllowlistPolicy(["*"], ["run_security_scan"])
    engine = PolicyEngine([p])
    result = engine.evaluate({"tool": "run_security_scan"})
    assert result.allowed is False
    assert "denied" in result.reason.lower()


def test_allowlist_denies_not_in_list():
    p = ToolAllowlistPolicy(["call_llm"], [])
    engine = PolicyEngine([p])
    result = engine.evaluate({"tool": "unknown_tool"})
    assert result.allowed is False


def test_allowlist_wildcard_allows_all():
    p = ToolAllowlistPolicy(["*"], [])
    engine = PolicyEngine([p])
    assert engine.evaluate({"tool": "anything"}).allowed is True


def test_allowlist_no_tool_in_context_passes():
    p = ToolAllowlistPolicy(["call_llm"], [])
    engine = PolicyEngine([p])
    # No tool key — should pass (no tool to check)
    result = engine.evaluate({})
    assert result.allowed is True


# --------------------------------------------------------------------------
# RolePolicy
# --------------------------------------------------------------------------

def test_role_policy_allow():
    p = RolePolicy({"agent": ["call_llm", "run_test"]})
    engine = PolicyEngine([p])
    result = engine.evaluate({"tool": "call_llm", "role": "agent"})
    assert result.allowed is True


def test_role_policy_deny():
    p = RolePolicy({"agent": ["call_llm"]})
    engine = PolicyEngine([p])
    result = engine.evaluate({"tool": "run_security_scan", "role": "agent"})
    assert result.allowed is False


def test_role_policy_wildcard_admin():
    p = RolePolicy({"admin": ["*"]})
    engine = PolicyEngine([p])
    result = engine.evaluate({"tool": "anything", "role": "admin"})
    assert result.allowed is True


def test_role_policy_missing_role_passes():
    p = RolePolicy({"agent": ["call_llm"]})
    engine = PolicyEngine([p])
    # No role in context — policy can't deny without role
    result = engine.evaluate({"tool": "call_llm"})
    assert result.allowed is True


# --------------------------------------------------------------------------
# PolicyEngine chain (deny-first)
# --------------------------------------------------------------------------

def test_chain_deny_first():
    allow = ToolAllowlistPolicy(["call_llm"], [])
    deny = ToolAllowlistPolicy([], ["call_llm"])
    # deny-first: denied policy checked first
    engine = PolicyEngine([deny, allow])
    result = engine.evaluate({"tool": "call_llm"})
    assert result.allowed is False


def test_chain_all_pass():
    p1 = ToolAllowlistPolicy(["*"], [])
    p2 = RolePolicy({"agent": ["*"]})
    engine = PolicyEngine([p1, p2])
    result = engine.evaluate({"tool": "call_llm", "role": "agent"})
    assert result.allowed is True


def test_evaluate_all_returns_all_results():
    p1 = ToolAllowlistPolicy(["call_llm"], [])
    p2 = RolePolicy({"agent": ["call_llm"]})
    engine = PolicyEngine([p1, p2])
    results = engine.evaluate_all({"tool": "call_llm", "role": "agent"})
    assert len(results) == 2
    assert all(r.allowed for r in results)


# --------------------------------------------------------------------------
# ContentSafetyPolicy
# --------------------------------------------------------------------------

def test_content_safety_allows_clean_input():
    p = ContentSafetyPolicy()
    engine = PolicyEngine([p])
    result = engine.evaluate({"input": "Fix the bug in utils.py"})
    assert result.allowed is True


def test_content_safety_denies_email():
    p = ContentSafetyPolicy()
    engine = PolicyEngine([p])
    result = engine.evaluate({"input": "Send to user@example.com"})
    assert result.allowed is False
    assert "PII" in result.reason


def test_content_safety_denies_credential():
    p = ContentSafetyPolicy()
    engine = PolicyEngine([p])
    result = engine.evaluate({"input": "api_key=sk-1234secret"})
    assert result.allowed is False


def test_content_safety_checks_arguments_dict():
    p = ContentSafetyPolicy()
    engine = PolicyEngine([p])
    result = engine.evaluate({"arguments": {"prompt": "user@secret.com is flagged"}})
    assert result.allowed is False


def test_content_safety_empty_input_passes():
    p = ContentSafetyPolicy()
    engine = PolicyEngine([p])
    result = engine.evaluate({})
    assert result.allowed is True


# --------------------------------------------------------------------------
# ParameterRangePolicy
# --------------------------------------------------------------------------

def test_param_range_in_bounds():
    p = ParameterRangePolicy({"temperature": {"min": 0.0, "max": 1.0}})
    engine = PolicyEngine([p])
    result = engine.evaluate({"arguments": {"temperature": 0.7}})
    assert result.allowed is True


def test_param_range_below_min():
    p = ParameterRangePolicy({"temperature": {"min": 0.0, "max": 1.0}})
    engine = PolicyEngine([p])
    result = engine.evaluate({"arguments": {"temperature": -0.1}})
    assert result.allowed is False
    assert "below min" in result.reason


def test_param_range_above_max():
    p = ParameterRangePolicy({"count": {"min": 1, "max": 10}})
    engine = PolicyEngine([p])
    result = engine.evaluate({"arguments": {"count": 11}})
    assert result.allowed is False
    assert "above max" in result.reason


def test_param_range_ignores_unconstrained_params():
    p = ParameterRangePolicy({"temperature": {"min": 0.0, "max": 1.0}})
    engine = PolicyEngine([p])
    result = engine.evaluate({"arguments": {"other_param": 999}})
    assert result.allowed is True


# --------------------------------------------------------------------------
# from_yaml factory
# --------------------------------------------------------------------------

def test_from_yaml_no_file_denies_all(tmp_path):
    """When the policy file is missing, the engine defaults to deny-all (secure default)."""
    from unittest.mock import patch
    fake_path = tmp_path / "policies.yml"
    with patch("gabbe.policy.GABBE_POLICY_FILE", fake_path):
        engine = PolicyEngine.from_yaml()
    result = engine.evaluate({"tool": "anything"})
    assert result.allowed is False


def test_from_yaml_reads_version(tmp_path):
    policies_file = tmp_path / "policies.yml"
    policies_file.write_text("version: '3'\ntools:\n  allowed:\n    - call_llm\n  denied: []\n")
    engine = PolicyEngine.from_yaml(path=policies_file)
    assert engine.version == "3"


def test_from_yaml_allowlist_from_file(tmp_path):
    policies_file = tmp_path / "policies.yml"
    policies_file.write_text("version: '1'\ntools:\n  allowed:\n    - call_llm\n  denied:\n    - dangerous\n")
    engine = PolicyEngine.from_yaml(path=policies_file)
    assert engine.evaluate({"tool": "call_llm"}).allowed is True
    assert engine.evaluate({"tool": "dangerous"}).allowed is False

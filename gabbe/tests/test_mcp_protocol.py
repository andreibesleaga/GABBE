# SPDX-License-Identifier: Apache-2.0
"""MCP protocol conformance: error flags, JSON-RPC codes, ping, version
negotiation, notifications, circuit-breaker recovery, roles and input caps.

Server tests drive ``serve()`` in-process with a real RunContext and an allow-all
policy, so the whole path (dispatcher, gateway, handler) is exercised."""

import io
import json
import os
import time
from unittest.mock import patch

import pytest

from gabbe.context import RunContext
from gabbe.gateway import PolicyDenied, ToolDefinition, ToolGateway
from gabbe.mcp_server import MCP_PROTOCOL_VERSION, serve
from gabbe.policy import PolicyEngine, ToolAllowlistPolicy


@pytest.fixture(autouse=True)
def mcp_env():
    """Permissive session with an allow-list that lets `echo` and `false` run."""
    env = {"GABBE_MCP_INSECURE": "1", "GABBE_MCP_ALLOWED_COMMANDS": "echo,false"}
    with patch.dict(os.environ, env):
        yield


def _allow_all():
    return PolicyEngine([ToolAllowlistPolicy(["*"], [])])


def _line(method, params=None, req_id=1):
    msg = {"jsonrpc": "2.0", "method": method}
    if req_id is not None:
        msg["id"] = req_id
    if params is not None:
        msg["params"] = params
    return json.dumps(msg)


def _call(command, req_id=1):
    return _line("tools/call", {"name": "run_command", "arguments": {"command": command}}, req_id)


def _run(lines):
    """Feed raw lines to a real serve(); return the list of reply dicts."""
    outputs = []
    real_ctx = RunContext.from_config

    with (
        patch("gabbe.mcp_server.RunContext") as mock_cls,
        patch("sys.stdin", io.StringIO("\n".join(lines) + "\n")),
        patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)),
    ):
        mock_cls.side_effect = lambda **kw: real_ctx(policy=_allow_all(), **kw)
        serve()
    return [json.loads(o) for o in outputs if o.strip()]


def _tool_payload(reply):
    return json.loads(reply["result"]["content"][0]["text"])


# --- SW-08: isError --------------------------------------------------------


def test_successful_command_has_is_error_false(tmp_project):
    (reply,) = _run([_call("echo hi")])
    assert reply["result"]["isError"] is False
    assert _tool_payload(reply)["stdout"] == "hi\n"  # text content kept


def test_failing_command_has_is_error_true(tmp_project):
    (reply,) = _run([_call("false")])
    assert reply["result"]["isError"] is True
    assert _tool_payload(reply)["returncode"] == 1


def test_blocked_command_has_is_error_true(tmp_project):
    # Leave insecure mode: authenticate with a token, then call a command that is
    # not on the allow-list.
    env = {"GABBE_MCP_INSECURE": "", "GABBE_MCP_TOKEN": "tok"}
    with patch.dict(os.environ, env):
        _, reply = _run([_line("initialize", {"token": "tok"}), _call("ls /")])
    assert reply["result"]["isError"] is True
    assert _tool_payload(reply)["returncode"] == 126


# --- SW-09 / INS-18: JSON-RPC error codes ------------------------------------


def test_unknown_tool_is_invalid_params(tmp_project):
    line = _line("tools/call", {"name": "nope", "arguments": {}})
    (reply,) = _run([line])
    assert reply["error"]["code"] == -32602
    assert "nope" in reply["error"]["message"]


def test_bad_arguments_are_invalid_params(tmp_project):
    line = _line("tools/call", {"name": "run_command", "arguments": {}})
    (reply,) = _run([line])
    assert reply["error"]["code"] == -32602
    assert "command" in reply["error"]["message"]


def test_non_object_params_are_invalid_request_with_id(tmp_project):
    (reply,) = _run([_line("tools/list", "x", req_id=7)])
    assert reply["error"]["code"] == -32600
    assert reply["id"] == 7


def test_json_that_is_not_an_object_is_invalid_request(tmp_project):
    (reply,) = _run(["[1, 2, 3]"])
    assert reply["error"]["code"] == -32600
    assert reply["id"] is None


def test_parse_error_has_null_id(tmp_project):
    (reply,) = _run(["{not json"])
    assert reply["error"]["code"] == -32700
    assert "id" in reply and reply["id"] is None


def test_policy_denial_has_its_own_code_and_reason(tmp_project):
    deny = PolicyEngine([ToolAllowlistPolicy([], ["run_command"])])
    outputs = []
    real = RunContext.from_config
    with (
        patch("gabbe.mcp_server.RunContext") as mock_cls,
        patch("sys.stdin", io.StringIO(_call("echo hi") + "\n")),
        patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)),
    ):
        mock_cls.side_effect = lambda **kw: real(policy=deny, **kw)
        serve()
    reply = json.loads(outputs[0])
    assert reply["error"]["code"] == -32001
    assert "Policy denied" in reply["error"]["message"]


# --- SW-10: ping, version negotiation, notifications -------------------------


def test_ping_answers_empty_result(tmp_project):
    (reply,) = _run([_line("ping", req_id=3)])
    assert reply == {"jsonrpc": "2.0", "id": 3, "result": {}}


def test_initialize_echoes_a_supported_version(tmp_project):
    (reply,) = _run([_line("initialize", {"protocolVersion": "2024-11-05"})])
    assert reply["result"]["protocolVersion"] == "2024-11-05"


def test_initialize_falls_back_to_latest_for_unsupported_version(tmp_project):
    (reply,) = _run([_line("initialize", {"protocolVersion": "1999-01-01"})])
    assert reply["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION


def test_notifications_get_no_reply(tmp_project):
    lines = [
        _line("notifications/initialized", req_id=None),
        _line("notifications/cancelled", {"requestId": 1}, req_id=None),
        _line("ping", req_id=None),
        _line("tools/call", "bad params", req_id=None),
        _line("ping", req_id=5),
    ]
    replies = _run(lines)
    assert [r["id"] for r in replies] == [5]


# --- SW-11: handler errors do not trip the breaker; half-open recovery -------


def test_three_malformed_calls_do_not_lock_the_server(tmp_project):
    bad = _call("echo 'unterminated")
    replies = _run([bad, bad, bad, _call("echo hi")])
    assert [r["result"]["isError"] for r in replies] == [True, True, True, False]
    assert _tool_payload(replies[0])["returncode"] == 2


def test_missing_executable_is_a_normal_error_result(tmp_project):
    with patch.dict(os.environ, {"GABBE_MCP_ALLOWED_COMMANDS": "no-such-program-xyz"}):
        (reply,) = _run([_call("no-such-program-xyz --flag")])
    assert reply["result"]["isError"] is True
    assert _tool_payload(reply)["returncode"] == 127


class _FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_circuit_breaker_half_open_recovers_after_cooldown(tmp_project):
    from gabbe.gateway import CircuitOpen

    state = {"fail": True}

    def flaky():
        if state["fail"]:
            raise RuntimeError("boom")
        return "ok"

    clock = _FakeClock()
    with RunContext.from_config(command="t", policy=_allow_all()) as ctx:
        gw = ToolGateway()
        gw._clock = clock
        gw.register(ToolDefinition("flaky", "d", {}, flaky, {"t"}, circuit_breaker_threshold=2))
        for _ in range(2):
            with pytest.raises(RuntimeError):
                gw.execute("flaky", {}, "t", ctx)
        with pytest.raises(CircuitOpen):
            gw.execute("flaky", {}, "t", ctx)
        clock.now += 29
        with pytest.raises(CircuitOpen):
            gw.execute("flaky", {}, "t", ctx)
        clock.now += 2  # 31 s after opening: one trial call is allowed
        state["fail"] = False
        assert gw.execute("flaky", {}, "t", ctx) == "ok"
        assert gw.execute("flaky", {}, "t", ctx) == "ok"  # closed again


def test_failed_trial_call_reopens_the_circuit(tmp_project):
    from gabbe.gateway import CircuitOpen

    def boom():
        raise RuntimeError("boom")

    clock = _FakeClock()
    with RunContext.from_config(command="t", policy=_allow_all()) as ctx:
        gw = ToolGateway()
        gw._clock = clock
        gw.register(ToolDefinition("boom", "d", {}, boom, {"t"}, circuit_breaker_threshold=1))
        with pytest.raises(RuntimeError):
            gw.execute("boom", {}, "t", ctx)
        clock.now += 31
        with pytest.raises(RuntimeError):  # the trial call runs and fails
            gw.execute("boom", {}, "t", ctx)
        with pytest.raises(CircuitOpen):  # a new cool-down started
            gw.execute("boom", {}, "t", ctx)


# --- SW-12: roles -----------------------------------------------------------


def test_role_not_in_allowed_roles_is_denied(tmp_project):
    with RunContext.from_config(command="t", policy=_allow_all()) as ctx:
        ctx.gateway.register(ToolDefinition("t1", "d", {}, lambda: "ok", {"admin"}))
        with pytest.raises(PolicyDenied, match="Role 'guest'"):
            ctx.gateway.execute("t1", {}, "guest", ctx)
        assert ctx.gateway.execute("t1", {}, "admin", ctx) == "ok"


def test_empty_allowed_roles_means_no_role_restriction(tmp_project):
    with RunContext.from_config(command="t", policy=_allow_all()) as ctx:
        ctx.gateway.register(ToolDefinition("t2", "d", {}, lambda: "ok", set()))
        assert ctx.gateway.execute("t2", {}, "anyone", ctx) == "ok"


# --- SW-14: oversize input is refused early ---------------------------------


def test_oversize_command_is_rejected_quickly(tmp_project):
    start = time.monotonic()
    (reply,) = _run([_call("a" * 40_000)])
    assert time.monotonic() - start < 1.0
    assert reply["error"]["code"] == -32602


def test_oversize_line_is_rejected_quickly(tmp_project):
    huge = _line("tools/call", {"name": "run_command", "arguments": {"x": ["a"] * 40_000}})
    start = time.monotonic()
    (reply,) = _run([huge])
    assert time.monotonic() - start < 1.0
    assert reply["error"]["code"] == -32602

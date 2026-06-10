# SPDX-License-Identifier: Apache-2.0
"""Tests for gabbe.mcp_server."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def allowlist_echo():
    """Run with a command allowlist so the fail-closed default permits `echo`."""
    with patch.dict(os.environ, {"GABBE_MCP_ALLOWED_COMMANDS": "echo,rm,true"}):
        yield


@pytest.fixture
def mcp_insecure():
    """Pre-authenticate the session (legacy permissive mode) so dispatch-flow
    tests can exercise JSON-RPC routing without the fail-closed auth gate."""
    with patch.dict(os.environ, {"GABBE_MCP_INSECURE": "1"}):
        yield


# ---------------------------------------------------------------------------
# run_command_handler tests
# ---------------------------------------------------------------------------


def test_run_command_handler_uses_shell_false(tmp_project, allowlist_echo):
    """run_command_handler must call subprocess.run with shell=False (no injection)."""
    from gabbe.mcp_server import run_command_handler

    mock_result = MagicMock()
    mock_result.stdout = "hello\n"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("gabbe.mcp_server.subprocess.run", return_value=mock_result) as mock_run:
        run_command_handler("echo hello")
        args, kwargs = mock_run.call_args
        # First positional arg must be a list (shlex.split result), not a string
        assert isinstance(args[0], list)
        assert kwargs.get("shell") is False


def test_run_command_handler_returns_dict(tmp_project, allowlist_echo):
    """run_command_handler returns stdout, stderr, returncode dict."""
    from gabbe.mcp_server import run_command_handler

    mock_result = MagicMock()
    mock_result.stdout = "output"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("gabbe.mcp_server.subprocess.run", return_value=mock_result):
        result = run_command_handler("echo output")

    assert result["stdout"] == "output"
    assert result["returncode"] == 0


def test_run_command_handler_no_shell_injection(tmp_project, allowlist_echo):
    """Shell metacharacters in command are NOT passed to a shell.

    shlex.split('echo safe; rm -rf /tmp/evil') returns
    ['echo', 'safe;', 'rm', '-rf', '/tmp/evil'] — all tokens, no shell expansion.
    subprocess.run is called with shell=False so ';' is never treated as a
    command separator; the mock verifies the exact token list and shell flag.
    """
    from gabbe.mcp_server import run_command_handler

    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("gabbe.mcp_server.subprocess.run", return_value=mock_result) as mock_run:
        run_command_handler("echo safe; rm -rf /tmp/evil")
        args, kwargs = mock_run.call_args
        cmd_list = args[0]

        # Must be a list of tokens (shlex.split result), not a raw string.
        assert isinstance(cmd_list, list)
        # shell=False ensures no shell interpretes ';' as a separator.
        assert kwargs.get("shell") is False
        # Verify all tokens are present exactly as shlex.split produces them.
        assert cmd_list == ["echo", "safe;", "rm", "-rf", "/tmp/evil"]


# ---------------------------------------------------------------------------
# serve() / JSON-RPC method tests (via stdin injection)
# ---------------------------------------------------------------------------


def _make_request(method, params=None, req_id=1):
    req = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params:
        req["params"] = params
    return json.dumps(req) + "\n"


def _run_serve_with_input(lines, tmp_project):
    """Run serve() feeding the given request lines via stdin; collect printed lines."""
    import io

    from gabbe.mcp_server import serve

    stdin_data = "".join(lines)
    outputs = []

    with patch("gabbe.mcp_server.RunContext") as MockCtx, patch(
        "sys.stdin", io.StringIO(stdin_data)
    ), patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)):

        mock_ctx = MagicMock()
        MockCtx.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        MockCtx.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.gateway.registry = {}
        mock_ctx.gateway.register = MagicMock()

        serve()

    return [json.loads(o) for o in outputs if o.strip()]


def test_serve_initialize(tmp_project):
    """MCP initialize method returns server capabilities."""
    responses = _run_serve_with_input([_make_request("initialize")], tmp_project)
    assert len(responses) == 1
    r = responses[0]
    assert r["id"] == 1
    assert "result" in r
    assert "serverInfo" in r["result"]
    assert r["result"]["serverInfo"]["name"] == "gabbe-mcp"


def test_serve_tools_list(tmp_project, mcp_insecure):
    """tools/list returns the run_command tool definition."""
    responses = _run_serve_with_input([_make_request("tools/list")], tmp_project)
    assert len(responses) == 1
    r = responses[0]
    assert "result" in r
    tools = r["result"]["tools"]
    assert any(t["name"] == "run_command" for t in tools)


def test_serve_unknown_method(tmp_project, mcp_insecure):
    """Unknown methods return a -32601 error."""
    responses = _run_serve_with_input([_make_request("unknown/method")], tmp_project)
    assert len(responses) == 1
    assert responses[0]["error"]["code"] == -32601


def test_serve_tools_call_dispatches_to_gateway(tmp_project, mcp_insecure):
    """tools/call invokes ctx.gateway.execute and returns the result."""
    import io

    from gabbe.mcp_server import serve

    call_req = _make_request(
        "tools/call",
        params={"name": "run_command", "arguments": {"command": "echo hi"}},
    )
    outputs = []

    with patch("gabbe.mcp_server.RunContext") as MockCtx, patch(
        "sys.stdin", io.StringIO(call_req)
    ), patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)):

        mock_ctx = MagicMock()
        MockCtx.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        MockCtx.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.gateway.registry = {}
        mock_ctx.gateway.register = MagicMock()
        mock_ctx.gateway.execute.return_value = {"stdout": "hi\n", "returncode": 0}

        serve()

    responses = [json.loads(o) for o in outputs if o.strip()]
    assert len(responses) == 1
    assert "result" in responses[0]
    content = responses[0]["result"]["content"][0]["text"]
    parsed = json.loads(content)
    assert parsed["stdout"] == "hi\n"


def test_serve_tools_call_gateway_error_returns_json_error(tmp_project, mcp_insecure):
    """If gateway.execute raises, the response contains an error code."""
    import io

    from gabbe.mcp_server import serve

    call_req = _make_request(
        "tools/call",
        params={"name": "no_such_tool", "arguments": {}},
    )
    outputs = []

    with patch("gabbe.mcp_server.RunContext") as MockCtx, patch(
        "sys.stdin", io.StringIO(call_req)
    ), patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)):

        mock_ctx = MagicMock()
        MockCtx.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        MockCtx.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.gateway.registry = {}
        mock_ctx.gateway.register = MagicMock()
        mock_ctx.gateway.execute.side_effect = Exception("tool not found")

        serve()

    responses = [json.loads(o) for o in outputs if o.strip()]
    assert len(responses) == 1
    assert "error" in responses[0]
    assert responses[0]["error"]["code"] == -32603


def test_serve_malformed_json_returns_parse_error(tmp_project):
    """Malformed JSON line returns a -32700 parse error."""
    import io

    from gabbe.mcp_server import serve

    outputs = []
    with patch("gabbe.mcp_server.RunContext") as MockCtx, patch(
        "sys.stdin", io.StringIO("not json at all\n")
    ), patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)):

        mock_ctx = MagicMock()
        MockCtx.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        MockCtx.return_value.__exit__ = MagicMock(return_value=False)

        serve()

    responses = [json.loads(o) for o in outputs if o.strip()]
    assert len(responses) == 1
    assert responses[0]["error"]["code"] == -32700


# ---------------------------------------------------------------------------
# R16 security regression: fail-closed defaults + escape hatch (no env set)
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_mcp_env():
    """Clear all GABBE_MCP_* env so the true out-of-the-box default is tested."""
    with patch.dict(os.environ, {}, clear=False):
        for key in (
            "GABBE_MCP_INSECURE",
            "GABBE_MCP_TOKEN",
            "GABBE_MCP_ALLOWED_COMMANDS",
            "GABBE_MCP_COMMAND_TIMEOUT",
        ):
            os.environ.pop(key, None)
        yield


def test_run_command_blocked_by_default_no_allowlist(tmp_project, clean_mcp_env):
    """Out of the box (no allowlist, no insecure), commands are BLOCKED (fail-closed)."""
    from gabbe.mcp_server import run_command_handler

    with patch("gabbe.mcp_server.subprocess.run") as mock_run:
        result = run_command_handler("echo hello")
    mock_run.assert_not_called()  # never reaches subprocess
    assert result["returncode"] == 126
    assert "allowlist" in result["stderr"].lower()


def test_run_command_blocked_when_not_in_allowlist(tmp_project, clean_mcp_env):
    """A populated allowlist permits only matching executables."""
    from gabbe.mcp_server import run_command_handler

    with patch.dict(os.environ, {"GABBE_MCP_ALLOWED_COMMANDS": "pytest"}):
        with patch("gabbe.mcp_server.subprocess.run") as mock_run:
            result = run_command_handler("rm -rf /tmp/x")
    mock_run.assert_not_called()
    assert result["returncode"] == 126


def test_run_command_allowed_when_in_allowlist(tmp_project, clean_mcp_env):
    """An allowlisted executable runs."""
    from gabbe.mcp_server import run_command_handler

    mock_result = MagicMock(stdout="hi\n", stderr="", returncode=0)
    with patch.dict(os.environ, {"GABBE_MCP_ALLOWED_COMMANDS": "echo"}):
        with patch("gabbe.mcp_server.subprocess.run", return_value=mock_result) as mock_run:
            result = run_command_handler("echo hi")
    mock_run.assert_called_once()
    assert result["returncode"] == 0


def test_insecure_mode_allows_any_command(tmp_project, clean_mcp_env):
    """GABBE_MCP_INSECURE=1 restores legacy allow-all behavior."""
    from gabbe.mcp_server import run_command_handler

    mock_result = MagicMock(stdout="", stderr="", returncode=0)
    with patch.dict(os.environ, {"GABBE_MCP_INSECURE": "1"}):
        with patch("gabbe.mcp_server.subprocess.run", return_value=mock_result) as mock_run:
            run_command_handler("anything goes")
    mock_run.assert_called_once()


def test_run_command_times_out(tmp_project, clean_mcp_env):
    """A command exceeding the timeout returns 124 instead of hanging."""
    import subprocess as sp

    from gabbe.mcp_server import run_command_handler

    with patch.dict(os.environ, {"GABBE_MCP_ALLOWED_COMMANDS": "sleep"}):
        with patch(
            "gabbe.mcp_server.subprocess.run", side_effect=sp.TimeoutExpired(cmd="sleep", timeout=1)
        ):
            result = run_command_handler("sleep 999")
    assert result["returncode"] == 124


def test_serve_refuses_tools_call_without_auth(tmp_project, clean_mcp_env):
    """Fail-closed: with no token and no insecure mode, tools/call is Unauthorized."""
    responses = _run_serve_with_input(
        [
            _make_request(
                "tools/call", params={"name": "run_command", "arguments": {"command": "echo hi"}}
            )
        ],
        tmp_project,
    )
    assert len(responses) == 1
    assert responses[0]["error"]["code"] == -32000


def test_serve_token_required_and_rejected(tmp_project, clean_mcp_env):
    """With a token set, initialize without the right token stays unauthorized."""
    with patch.dict(os.environ, {"GABBE_MCP_TOKEN": "s3cret"}):
        responses = _run_serve_with_input(
            [
                _make_request("initialize", params={"token": "wrong"}),
                _make_request("tools/list", req_id=2),
            ],
            tmp_project,
        )
    # initialize -> Unauthorized; tools/list -> Unauthorized (never authed)
    assert responses[0]["error"]["code"] == -32000
    assert responses[1]["error"]["code"] == -32000


def test_serve_initialize_returns_protocol_version(tmp_project, clean_mcp_env):
    """initialize response carries the negotiated protocolVersion (MCP spec)."""
    from gabbe.mcp_server import MCP_PROTOCOL_VERSION

    responses = _run_serve_with_input([_make_request("initialize")], tmp_project)
    assert responses[0]["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION

# SPDX-License-Identifier: Apache-2.0
"""Fuzz tests for the MCP server (Track B Phase 2).

Two angles:
  * schema fuzzing — generate valid payloads against the hardened run_command
    schema and confirm the generator and the jsonschema validator agree;
  * envelope fuzzing — feed malformed JSON-RPC lines and confirm the server
    always responds with an error and never crashes (fail-soft).
PBT samples; it raises confidence, not proof.
"""

import io
import json
import string
from unittest.mock import MagicMock, patch

import jsonschema
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from gabbe.mcp_server import _RUN_COMMAND_SCHEMA, run_command_handler, serve

_S = settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=80)

try:
    from hypothesis_jsonschema import from_schema

    _HAS_JSONSCHEMA_STRATEGY = True
except ImportError:  # pragma: no cover
    _HAS_JSONSCHEMA_STRATEGY = False


@pytest.mark.skipif(not _HAS_JSONSCHEMA_STRATEGY, reason="hypothesis-jsonschema not installed")
@settings(max_examples=60, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.deferred(lambda: from_schema(_RUN_COMMAND_SCHEMA)))
def test_generated_payloads_satisfy_the_contract(data):
    # The generator and validator agree: every generated instance is schema-valid.
    jsonschema.validate(data, _RUN_COMMAND_SCHEMA)


@_S
@given(command=st.text(alphabet=string.ascii_letters + string.digits + " /._-", max_size=200))
def test_handler_is_failclosed_for_arbitrary_commands(tmp_project, command):
    # With no allowlist and not insecure, NO command may ever reach the shell.
    with patch.dict(
        "os.environ",
        {"GABBE_MCP_ALLOWED_COMMANDS": "", "GABBE_MCP_INSECURE": ""},
    ):
        with patch("gabbe.mcp_server.subprocess.run") as mock_run:
            result = run_command_handler(command)
    mock_run.assert_not_called()
    assert result["returncode"] in (1, 126)  # 1 = empty command, 126 = blocked


def _run_serve(lines):
    outputs = []
    with (
        patch("gabbe.mcp_server.RunContext") as MockCtx,
        patch("sys.stdin", io.StringIO("".join(lines))),
        patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)),
    ):
        mock_ctx = MagicMock()
        MockCtx.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        MockCtx.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.gateway.registry = {}
        mock_ctx.gateway.register = MagicMock()
        serve()
    return [json.loads(o) for o in outputs if o.strip()]


@_S
@given(
    garbage=st.lists(
        st.text(alphabet=string.ascii_letters, min_size=1, max_size=20), min_size=1, max_size=10
    )
)
def test_malformed_jsonrpc_lines_always_error_never_crash(tmp_project, garbage):
    # Non-JSON-object lines must each yield an error response; serve never raises.
    responses = _run_serve([g + "\n" for g in garbage])
    assert len(responses) == len(garbage)
    assert all("error" in r for r in responses)

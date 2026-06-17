# SPDX-License-Identifier: Apache-2.0
"""Contract tests for the MCP server tool schemas (Track E5).

Complements test_mcp_server.py (behavior) and test_mcp_fuzz.py (random fuzzing)
with explicit *contract* assertions: the advertised tool schema is valid JSON
Schema, every string input is bounded by charset + length, and adversarial
payloads are rejected fail-closed. Grounded in the MCP-38 threat taxonomy
(tool poisoning / confused-deputy / command injection via tool feedback) and the
NSA MCP security guidance.
"""

import io
import json
from unittest.mock import MagicMock, patch

import jsonschema
import pytest

from gabbe.mcp_server import _MAX_COMMAND_LEN, _RUN_COMMAND_SCHEMA

# ---------------------------------------------------------------------------
# The schema is itself a valid, bounded JSON Schema
# ---------------------------------------------------------------------------


def test_run_command_schema_is_valid_json_schema():
    """The advertised inputSchema must itself be a valid JSON Schema."""
    jsonschema.Draft7Validator.check_schema(_RUN_COMMAND_SCHEMA)


def test_every_string_input_is_bounded_by_charset_and_length():
    """No string tool input may be unbounded: each needs maxLength + pattern."""
    props = _RUN_COMMAND_SCHEMA["properties"]
    string_props = {k: v for k, v in props.items() if v.get("type") == "string"}
    assert string_props, "expected at least one string input to assert bounds on"
    for name, spec in string_props.items():
        assert "maxLength" in spec, f"{name} string input has no maxLength bound"
        assert spec["maxLength"] <= _MAX_COMMAND_LEN
        assert "pattern" in spec, f"{name} string input has no charset (pattern) bound"


def test_schema_rejects_unexpected_fields():
    """additionalProperties must be False so smuggled fields are rejected."""
    assert _RUN_COMMAND_SCHEMA.get("additionalProperties") is False


# ---------------------------------------------------------------------------
# Valid payload accepted; adversarial payloads rejected (fail-closed)
# ---------------------------------------------------------------------------


def test_valid_payload_accepted():
    jsonschema.validate({"command": "echo hello"}, _RUN_COMMAND_SCHEMA)


@pytest.mark.parametrize(
    "payload, why",
    [
        ({"command": "x" * (_MAX_COMMAND_LEN + 1)}, "oversized string"),
        ({"command": "echo\x00rm -rf /"}, "embedded NUL byte"),
        ({"command": "echo\x1bmalicious"}, "embedded control char (ESC)"),
        ({"command": ""}, "empty string (minLength)"),
        ({}, "missing required field"),
        ({"command": "ls", "evil": "smuggled"}, "extra/unexpected field"),
        ({"command": 123}, "wrong type (int, not string)"),
    ],
)
def test_adversarial_payloads_rejected(payload, why):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, _RUN_COMMAND_SCHEMA)


# ---------------------------------------------------------------------------
# The advertised tools/list schema is the SAME bounded contract (no drift)
# ---------------------------------------------------------------------------


def _make_request(method, params=None, req_id=1):
    req = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params:
        req["params"] = params
    return json.dumps(req) + "\n"


def test_tools_list_advertises_the_bounded_schema(tmp_project, monkeypatch):
    """tools/list must emit the same hardened schema the gateway enforces."""
    from gabbe.mcp_server import serve

    monkeypatch.setenv("GABBE_MCP_INSECURE", "1")
    outputs = []
    with (
        patch("gabbe.mcp_server.RunContext") as MockCtx,
        patch("sys.stdin", io.StringIO(_make_request("tools/list"))),
        patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)),
    ):
        mock_ctx = MagicMock()
        MockCtx.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        MockCtx.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.gateway.registry = {}
        mock_ctx.gateway.register = MagicMock()
        serve()

    responses = [json.loads(o) for o in outputs if o.strip()]
    tool = next(t for t in responses[0]["result"]["tools"] if t["name"] == "run_command")
    advertised = tool["inputSchema"]["properties"]["command"]
    assert advertised["maxLength"] == _MAX_COMMAND_LEN
    assert "pattern" in advertised
    assert tool["inputSchema"].get("additionalProperties") is False

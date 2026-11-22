# SPDX-License-Identifier: Apache-2.0
"""MCP 2026-07-28 ("modern") requests on the stdio server, next to the legacy
`initialize` handshake. Modern requests carry their protocol version in
`params._meta` and are served one by one, with no session.

Specification: https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning
and .../server/discover."""

import io
import json
import os
from unittest.mock import patch

import pytest

from gabbe.mcp_server import MCP_TOKEN_META_KEY, serve_stdio

VERSION = "io.modelcontextprotocol/protocolVersion"
CAPS = "io.modelcontextprotocol/clientCapabilities"
SERVER_INFO = "io.modelcontextprotocol/serverInfo"


@pytest.fixture(autouse=True)
def clean_env():
    with patch.dict(os.environ):
        for key in list(os.environ):
            if key.startswith("GABBE_MCP_"):
                del os.environ[key]
        yield


def _meta(version="2026-07-28", **extra):
    meta = {VERSION: version, CAPS: {}}
    meta.update(extra)
    return meta


def _req(method, params=None, meta=None, req_id=1):
    body = dict(params or {})
    if meta is not None:
        body["_meta"] = meta
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": body})


def _serve(lines, enable_run_command=False):
    outputs = []
    with (
        patch("sys.stdin", io.StringIO("\n".join(lines) + "\n")),
        patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)),
    ):
        serve_stdio(enable_run_command=enable_run_command)
    return [json.loads(o) for o in outputs if o.strip()]


def _run_command(command, meta, req_id=1):
    return _req(
        "tools/call", {"name": "run_command", "arguments": {"command": command}}, meta, req_id
    )


def test_server_discover_lists_modern_and_legacy_versions(tmp_project):
    (reply,) = _serve([_req("server/discover", meta=_meta())])
    result = reply["result"]
    assert result["resultType"] == "complete"
    assert result["supportedVersions"] == [
        "2026-07-28",
        "2025-11-25",
        "2025-06-18",
        "2025-03-26",
        "2024-11-05",
    ]
    assert result["capabilities"] == {"tools": {}}
    assert result["_meta"][SERVER_INFO]["name"] == "gabbe-mcp"
    assert result["ttlMs"] == 0 and result["cacheScope"] == "public"


def test_server_discover_without_meta_is_invalid_params(tmp_project):
    (reply,) = _serve([_req("server/discover")])
    assert reply["error"]["code"] == -32602


def test_modern_tools_list_is_stateless(tmp_project):
    (reply,) = _serve([_req("tools/list", meta=_meta())])
    result = reply["result"]
    assert result["resultType"] == "complete"
    assert [t["name"] for t in result["tools"]][0] == "list_skills"
    assert "run_command" not in [t["name"] for t in result["tools"]]
    assert result["ttlMs"] == 0 and result["cacheScope"] == "public"


def test_modern_tools_call_runs_a_read_only_tool(tmp_project):
    call = _req("tools/call", {"name": "project_status", "arguments": {}}, _meta())
    (reply,) = _serve([call])
    assert reply["result"]["resultType"] == "complete"
    assert reply["result"]["isError"] is True  # no state files in this temporary project
    assert "No GABBE project state found" in reply["result"]["content"][0]["text"]


def test_unsupported_version_error_has_supported_and_requested(tmp_project):
    (reply,) = _serve([_req("tools/list", meta=_meta(version="1900-01-01"))])
    error = reply["error"]
    assert error["code"] == -32022
    assert error["message"] == "Unsupported protocol version"
    assert error["data"]["requested"] == "1900-01-01"
    assert error["data"]["supported"][0] == "2026-07-28"


def test_a_legacy_version_in_meta_is_not_served_as_modern(tmp_project):
    (reply,) = _serve([_req("tools/list", meta=_meta(version="2025-11-25"))])
    assert reply["error"]["code"] == -32022


def test_missing_client_capabilities_is_invalid_params(tmp_project):
    (reply,) = _serve([_req("tools/list", meta={VERSION: "2026-07-28"})])
    assert reply["error"]["code"] == -32602


def test_modern_unknown_method_is_method_not_found(tmp_project):
    (reply,) = _serve([_req("resources/list", meta=_meta())])
    assert reply["error"]["code"] == -32601


def test_initialize_is_always_legacy_even_with_modern_meta(tmp_project):
    (reply,) = _serve([_req("initialize", meta=_meta())])
    assert "resultType" not in reply["result"]
    assert reply["result"]["serverInfo"]["name"] == "gabbe-mcp"


def test_modern_notification_gets_no_reply(tmp_project):
    note = json.dumps({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {}})
    assert _serve([note]) == []


# --- the token in the modern era ---------------------------------------------------


def _enable_run_command(token="s3cret"):
    os.environ.update(
        {
            "GABBE_MCP_TOKEN": token,
            "GABBE_MCP_ALLOWED_COMMANDS": "echo",
            "GABBE_MCP_ENABLE_RUN_COMMAND": "1",
        }
    )


def test_modern_run_command_works_with_the_token_in_meta(tmp_project):
    _enable_run_command()
    (reply,) = _serve([_run_command("echo hi", _meta(**{MCP_TOKEN_META_KEY: "s3cret"}))])
    assert reply["result"]["isError"] is False
    assert json.loads(reply["result"]["content"][0]["text"])["stdout"] == "hi\n"


@pytest.mark.parametrize("meta_extra", [{}, {MCP_TOKEN_META_KEY: "wrong"}])
def test_modern_run_command_without_the_right_token_is_unauthorized(tmp_project, meta_extra):
    _enable_run_command()
    (reply,) = _serve([_run_command("echo hi", _meta(**meta_extra))])
    assert reply["error"] == {"code": -32000, "message": "Unauthorized"}


def test_a_legacy_login_does_not_authorise_modern_requests(tmp_project):
    _enable_run_command()
    init = _req("initialize", {"token": "s3cret"})
    replies = _serve([init, _run_command("echo hi", _meta(), req_id=2)])
    assert "result" in replies[0]
    assert replies[1]["error"]["code"] == -32000


def test_modern_read_only_tools_need_no_token_even_when_one_is_set(tmp_project):
    _enable_run_command()
    (reply,) = _serve([_req("tools/call", {"name": "list_skills", "arguments": {}}, _meta())])
    assert "error" not in reply


def test_token_meta_key_follows_the_meta_naming_rule():
    prefix, name = MCP_TOKEN_META_KEY.split("/")
    labels = prefix.split(".")
    assert all(label[0].isalpha() and label[-1].isalnum() for label in labels)
    assert labels[1] not in ("modelcontextprotocol", "mcp")  # reserved second labels
    assert name == "token"


# --- legacy era unchanged ----------------------------------------------------------


def test_legacy_initialize_still_negotiates_and_has_no_result_type(tmp_project):
    (reply,) = _serve([_req("initialize", {"protocolVersion": "2025-06-18"})])
    assert reply["result"]["protocolVersion"] == "2025-06-18"
    assert "resultType" not in reply["result"]


def test_legacy_and_modern_requests_can_share_one_process(tmp_project):
    lines = [
        _req("initialize", {"protocolVersion": "2025-11-25"}, req_id=1),
        _req("tools/list", req_id=2),
        _req("tools/list", meta=_meta(), req_id=3),
    ]
    legacy_init, legacy_list, modern_list = _serve(lines)
    assert "resultType" not in legacy_list["result"]
    assert modern_list["result"]["resultType"] == "complete"
    assert legacy_list["result"]["tools"] == modern_list["result"]["tools"]


# --- MCP Registry file ---------------------------------------------------------------


def test_server_json_is_valid_against_the_saved_registry_schema():
    """`server.json` follows the registry's JSON Schema (a copy saved in baselines/mcp_registry,
    fetched from the URL in its `$id`), so this test needs no network."""
    from pathlib import Path

    import jsonschema

    root = Path(__file__).resolve().parents[2]
    schema = json.loads(
        (root / "gabbe/tests/baselines/mcp_registry/server.schema.json").read_text()
    )
    server = json.loads((root / "server.json").read_text())
    jsonschema.Draft7Validator.check_schema(schema)
    jsonschema.Draft7Validator(schema).validate(server)
    assert server["$schema"] == schema["$id"]
    assert server["name"].startswith("io.github.andreibesleaga/")
    assert server["packages"][0]["packageArguments"][0]["value"] == "serve-mcp"

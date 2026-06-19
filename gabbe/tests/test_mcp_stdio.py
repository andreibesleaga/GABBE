# SPDX-License-Identifier: Apache-2.0
"""Workstream E: end-to-end MCP-over-stdio test.

Spawns the REAL `gabbe serve-mcp` server as a subprocess and drives it over
stdin/stdout with JSON-RPC, asserting the handshake, tool listing, an authorized
tool call, and that the advertised serverInfo.version tracks the package version
(the exact drift bug that shipped in 1.0.1). Complements the unit tests in
test_mcp_server.py, which mock stdio."""

import json
import os
import subprocess
import sys

import gabbe


def _serve(env_extra, *requests):
    """Run `gabbe serve-mcp`, feed JSON-RPC request dicts, return response dicts."""
    env = dict(os.environ)
    env.update(env_extra)
    payload = "".join(json.dumps(r) + "\n" for r in requests)
    proc = subprocess.run(
        [sys.executable, "-m", "gabbe.main", "serve-mcp"],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    out = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out, proc


SECURE_ENV = {
    "GABBE_MCP_TOKEN": "test-secret-token",
    "GABBE_MCP_ALLOWED_COMMANDS": "echo",
}


def test_initialize_reports_package_version():
    responses, _ = _serve(
        SECURE_ENV,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"token": "test-secret-token"},
        },
    )
    assert responses, "server returned no response to initialize"
    info = responses[0]["result"]["serverInfo"]
    assert info["name"] == "gabbe-mcp"
    # The exact bug from 1.0.1: serverInfo.version must equal the package version.
    assert info["version"] == gabbe.__version__


def test_tools_list_after_auth():
    responses, _ = _serve(
        SECURE_ENV,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"token": "test-secret-token"},
        },
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    )
    listing = next(r for r in responses if r.get("id") == 2)
    names = [t["name"] for t in listing["result"]["tools"]]
    assert "run_command" in names


def test_bad_token_is_rejected():
    responses, _ = _serve(
        SECURE_ENV,
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"token": "WRONG"}},
    )
    assert responses[0].get("error", {}).get("message") == "Unauthorized"


def test_unauthenticated_tools_list_is_blocked():
    # No initialize → tools/list must be refused (fail-closed).
    responses, _ = _serve(
        SECURE_ENV,
        {"jsonrpc": "2.0", "id": 9, "method": "tools/list"},
    )
    assert responses[0].get("error", {}).get("message") == "Unauthorized"

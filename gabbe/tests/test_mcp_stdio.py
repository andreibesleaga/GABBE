# SPDX-License-Identifier: Apache-2.0
"""Workstream E: end-to-end MCP-over-stdio test.

Spawns the REAL `gabbe serve-mcp` server as a subprocess and drives it over
stdin/stdout with JSON-RPC, asserting the handshake, tool listing, an authorized
tool call, and that the advertised serverInfo.version tracks the package version
(the exact drift bug that shipped in 1.0.1). Complements the unit tests in
test_mcp_server.py, which mock stdio.

Every server runs in a throw-away project folder (cwd = tmp_path with a
``project/`` marker), so the run records it writes never reach the
repository's own tracked ``project/state.db``."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import gabbe

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def project_dir(tmp_path):
    """A temporary project root: `gabbe` finds it through the `project/` marker."""
    (tmp_path / "project").mkdir()
    return tmp_path


def _serve(cwd, env_extra, *requests):
    """Run `gabbe serve-mcp` in `cwd`, feed JSON-RPC request dicts, return response dicts."""
    env = dict(os.environ)
    env.update(env_extra)
    # Keep `python -m gabbe.main` importable from outside the repository.
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(REPO_ROOT), env.get("PYTHONPATH", "")) if p)
    payload = "".join(json.dumps(r) + "\n" for r in requests)
    proc = subprocess.run(
        [sys.executable, "-m", "gabbe.main", "serve-mcp"],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd),
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


def test_initialize_reports_package_version(project_dir):
    responses, _ = _serve(
        project_dir,
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


def test_tools_list_after_auth(project_dir):
    responses, _ = _serve(
        project_dir,
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


def test_bad_token_is_rejected(project_dir):
    responses, _ = _serve(
        project_dir,
        SECURE_ENV,
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"token": "WRONG"}},
    )
    assert responses[0].get("error", {}).get("message") == "Unauthorized"


def test_unauthenticated_tools_list_is_blocked(project_dir):
    # No initialize → tools/list must be refused (fail-closed).
    responses, _ = _serve(
        project_dir,
        SECURE_ENV,
        {"jsonrpc": "2.0", "id": 9, "method": "tools/list"},
    )
    assert responses[0].get("error", {}).get("message") == "Unauthorized"


def test_server_writes_only_into_its_own_project(project_dir):
    """Regression: the server's run records go to the cwd project, not the repository."""
    repo_db = REPO_ROOT / "project" / "state.db"
    before = repo_db.stat().st_mtime_ns if repo_db.exists() else None
    responses, proc = _serve(
        project_dir,
        SECURE_ENV,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"token": "test-secret-token"},
        },
    )
    assert responses, proc.stderr
    after = repo_db.stat().st_mtime_ns if repo_db.exists() else None
    assert after == before

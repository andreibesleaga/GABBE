# SPDX-License-Identifier: Apache-2.0
"""GABBE never creates or writes anything through a link at project/, state.db or logs (SEC-C-03).

The tool server runs without an audit trail (read-only tools only, run_command refused);
a CLI command that needs the database stops with one line and exit status 1."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(os.name == "nt", reason="links need privileges on Windows")

SPOTS = ("project", "project/state.db", "project/logs")


@pytest.fixture(params=SPOTS)
def planted(request, tmp_path):
    """A project whose state path `request.param` is a dangling link to a place outside it."""
    root = tmp_path / "root"
    root.mkdir()
    (root / "pyproject.toml").write_text("")
    target = tmp_path / "outside" / "target"
    (tmp_path / "outside").mkdir()
    if request.param != "project":
        (root / "project").mkdir()
    os.symlink(target, root / request.param)
    return root, target, request.param


def _run(root: Path, args: list[str], payload: str = "", extra: dict[str, str] | None = None):
    env = dict(os.environ, HOME=str(root), **(extra or {}))
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(REPO_ROOT), env.get("PYTHONPATH", "")) if p)
    return subprocess.run(
        [sys.executable, "-m", "gabbe.main", *args],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(root),
        timeout=60,
    )


def _call(req_id, name, arguments):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }


def test_the_tool_server_serves_read_only_tools_and_refuses_run_command(planted):
    root, target, spot = planted
    lines = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"token": "t"}},
        _call(2, "project_status", {}),
        _call(3, "run_command", {"command": "echo hi"}),
    ]
    extra = {"GABBE_MCP_TOKEN": "t", "GABBE_MCP_ALLOWED_COMMANDS": "echo"}
    payload = "".join(json.dumps(x) + "\n" for x in lines)
    proc = _run(root, ["serve-mcp", "--enable-run-command"], payload, extra)
    replies = {r["id"]: r for r in map(json.loads, proc.stdout.splitlines())}
    assert "result" in replies[2]  # the read-only tool still answers
    refused = replies[3]["result"]["content"][0]["text"]
    assert "run_command is refused" in refused and str(root / spot) in refused
    assert str(root / spot) in proc.stderr
    assert not target.exists() and not target.is_symlink()
    assert not (target.parent / "state.db").exists()


def test_a_cli_command_stops_with_one_line_and_exit_1(planted):
    root, target, spot = planted
    proc = _run(root, ["status"])
    assert proc.returncode == 1
    assert str(root / spot) in proc.stderr
    assert len([x for x in proc.stderr.splitlines() if x.strip()]) == 1
    assert not target.exists()


def test_init_refuses_too_and_creates_nothing(planted):
    root, target, spot = planted
    proc = _run(root, ["init"])
    assert proc.returncode == 1
    assert str(root / spot) in proc.stderr
    assert not target.exists()


def test_a_link_that_resolves_outside_the_root_is_refused_even_when_it_exists(tmp_path):
    from gabbe import database

    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    os.symlink(outside, root / "project")
    problem = database.state_path_problem(root / "project")
    assert problem is not None and str(root / "project") in problem
    assert list(outside.iterdir()) == []

# SPDX-License-Identifier: Apache-2.0
"""Input and output limits of the tool server (SEC-C-09): the real server, over stdio."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from gabbe import mcp_server

REPO_ROOT = Path(__file__).resolve().parents[2]
PING = json.dumps({"jsonrpc": "2.0", "id": 7, "method": "ping"}) + "\n"


def _serve(cwd: Path, payload: str, extra_env: dict[str, str] | None = None, args=()):
    env = dict(os.environ, HOME=str(cwd), **(extra_env or {}))
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(REPO_ROOT), env.get("PYTHONPATH", "")) if p)
    proc = subprocess.run(
        [sys.executable, "-m", "gabbe.main", "serve-mcp", *args],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd),
        timeout=120,
    )
    replies = [json.loads(x) for x in proc.stdout.splitlines() if x.strip()]
    return replies, proc


@pytest.fixture()
def project_dir(tmp_path):
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / "policies.yml").write_text(
        "version: '1'\ntools:\n  allowed:\n    - 'run_command'\n"
    )
    return tmp_path


def test_a_deeply_nested_line_gets_a_parse_error_and_the_server_keeps_serving(project_dir):
    nested = "[" * 100_000 + "]" * 100_000 + "\n"
    replies, proc = _serve(project_dir, nested + PING)
    assert replies[0]["error"]["code"] == -32700
    assert replies[1] == {"jsonrpc": "2.0", "id": 7, "result": {}}
    assert proc.returncode == 0


def test_an_oversized_line_is_refused_and_the_next_line_is_parsed_correctly(project_dir):
    big = "x" * (mcp_server._MAX_LINE_CHARS * 2 + 123) + "\n"
    replies, proc = _serve(project_dir, big + PING)
    assert replies[0]["error"]["code"] == -32600
    assert "message too large" in replies[0]["error"]["message"]
    assert replies[1]["id"] == 7 and replies[1]["result"] == {}
    assert len(replies) == 2
    assert proc.returncode == 0


def test_a_line_of_exactly_the_limit_is_still_read_whole(project_dir):
    pad = " " * (mcp_server._MAX_LINE_CHARS - len(PING.strip()))
    replies, _ = _serve(project_dir, PING.strip() + pad + "\n" + PING)
    assert [r.get("id") for r in replies] == [7, 7]


def test_command_output_is_cut_at_the_cap_before_reply_and_trace(project_dir):
    cap = mcp_server._MAX_OUTPUT_BYTES
    command = f"{sys.executable} -c \"import sys; sys.stdout.write('a' * {cap * 3})\""
    env = {
        "GABBE_MCP_TOKEN": "tkn",
        "GABBE_MCP_ALLOWED_COMMANDS": sys.executable,
    }
    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"token": "tkn"}}
    call = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "run_command", "arguments": {"command": command}},
    }
    payload = json.dumps(init) + "\n" + json.dumps(call) + "\n"
    replies, _ = _serve(project_dir, payload, env, args=("--enable-run-command",))
    assert "result" in replies[1], replies[1]
    result = json.loads(replies[1]["result"]["content"][0]["text"])
    assert result["stdout_truncated"] is True
    assert "stderr_truncated" not in result
    assert result["stdout"].startswith("a" * 100)
    assert len(result["stdout"]) < cap + 100
    assert "output cut" in result["stdout"]
    conn = sqlite3.connect(project_dir / "project" / "state.db")
    try:
        sizes = [r[0] for r in conn.execute("SELECT length(output_data) FROM audit_spans")]
    finally:
        conn.close()
    assert sizes and max(s or 0 for s in sizes) < cap + 4096
    logs = list((project_dir / "project" / "logs").glob("run_*.jsonl"))
    assert logs and max(p.stat().st_size for p in logs) < 2 * cap


def test_short_output_has_no_marker(monkeypatch):
    monkeypatch.setenv("GABBE_MCP_INSECURE", "1")
    result = mcp_server.run_command_handler(f"{sys.executable} -c \"print('hi')\"")
    assert result["stdout"] == "hi\n" and "stdout_truncated" not in result


# --- disk and process-group limits (RA-08) -------------------------------------------


def _alive(pid: int) -> bool:
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return False  # no such process (or no /proc entry)
    return state != "Z"


def _gone_within(pid: int, seconds: float = 3.0) -> bool:
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if not _alive(pid):
            return True
        time.sleep(0.05)
    return False


@pytest.mark.skipif(os.name != "posix", reason="process groups are POSIX only")
def test_a_command_that_writes_without_end_is_stopped_and_nothing_reaches_the_disk(
    tmp_path, monkeypatch
):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    monkeypatch.setattr(mcp_server, "_HARD_OUTPUT_BYTES", 4 * 1024 * 1024)
    monkeypatch.setenv("GABBE_MCP_INSECURE", "1")
    monkeypatch.setenv("GABBE_MCP_COMMAND_TIMEOUT", "60")
    started = time.monotonic()
    result = mcp_server.run_command_handler(
        f"{sys.executable} -c \"print('a'*99); import os\nwhile 1: os.write(1, b'a'*65536)\""
    )
    assert time.monotonic() - started < 20
    assert result["stdout_truncated"] is True and "output cut" in result["stdout"]
    assert len(result["stdout"]) < mcp_server._MAX_OUTPUT_BYTES + 100
    assert result["returncode"] != 0  # ended by a signal
    assert sum(p.stat().st_size for p in scratch.rglob("*") if p.is_file()) < 1024 * 1024


@pytest.mark.skipif(os.name != "posix", reason="process groups are POSIX only")
def test_a_timeout_ends_the_grandchildren_too(tmp_path, monkeypatch):
    pidfile = tmp_path / "pid"
    monkeypatch.setenv("GABBE_MCP_INSECURE", "1")
    monkeypatch.setenv("GABBE_MCP_COMMAND_TIMEOUT", "1")
    script = f"sleep 300 & echo $! > {pidfile}; wait"
    result = mcp_server.run_command_handler(f"sh -c '{script}'")
    assert result["returncode"] == 124 and "timed out" in result["stderr"]
    grandchild = int(pidfile.read_text())
    try:
        assert _gone_within(grandchild), "the grandchild survived the timeout"
    finally:
        if _alive(grandchild):
            os.kill(grandchild, 9)


@pytest.mark.skipif(os.name != "posix", reason="process groups are POSIX only")
def test_a_background_process_holding_the_pipe_does_not_hold_back_the_reply(tmp_path, monkeypatch):
    monkeypatch.setenv("GABBE_MCP_INSECURE", "1")
    started = time.monotonic()
    result = mcp_server.run_command_handler("sh -c 'sleep 300 & echo done'")
    assert result["stdout"] == "done\n" and result["returncode"] == 0
    assert time.monotonic() - started < 10


def test_both_streams_and_the_return_code_are_unchanged_for_a_short_command(monkeypatch):
    monkeypatch.setenv("GABBE_MCP_INSECURE", "1")
    code = "import sys; print('o'); print('e', file=sys.stderr); sys.exit(3)"
    result = mcp_server.run_command_handler(f'{sys.executable} -c "{code}"')
    assert result == {"stdout": "o\n", "stderr": "e\n", "returncode": 3}


def test_the_stderr_stream_is_cut_with_its_own_flag(monkeypatch):
    monkeypatch.setenv("GABBE_MCP_INSECURE", "1")
    cap = mcp_server._MAX_OUTPUT_BYTES
    code = f"import sys; sys.stderr.write('e' * {cap * 2})"
    result = mcp_server.run_command_handler(f'{sys.executable} -c "{code}"')
    assert result["stderr_truncated"] is True and "stdout_truncated" not in result
    assert "output cut" in result["stderr"]

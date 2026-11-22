# SPDX-License-Identifier: Apache-2.0
"""run_command allow-list identity (SEC-C-04) and token checks (note N-1).

A multi-call binary is one file under many names (busybox, vim/view, bash/rbash). Allowing
one name must not allow the others."""

import os

import pytest

from gabbe.mcp_server import _handle_line, _Server, run_command_handler

MULTICALL = """#!/bin/sh
case "${0##*/}" in
  ls) echo LS-RAN ;;
  sh) echo SH-RAN ;;
esac
"""


@pytest.fixture()
def multicall(tmp_path, monkeypatch):
    """bin/ls and bin/sh are links to one script that dispatches on $0."""
    lib = tmp_path / "lib"
    lib.mkdir()
    script = lib / "multicall"
    script.write_text(MULTICALL)
    script.chmod(0o755)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for name in ("ls", "sh"):
        os.symlink(script, bindir / name)
    monkeypatch.setenv("PATH", str(bindir))
    monkeypatch.setenv("GABBE_MCP_ALLOWED_COMMANDS", "ls")
    monkeypatch.delenv("GABBE_MCP_INSECURE", raising=False)
    return bindir


def test_the_listed_name_still_runs_bare_and_by_path(multicall):
    assert run_command_handler("ls")["stdout"] == "LS-RAN\n"
    assert run_command_handler(f"{multicall / 'ls'}")["stdout"] == "LS-RAN\n"


def test_another_name_of_the_same_file_is_refused_bare(multicall):
    result = run_command_handler("sh")
    assert result["returncode"] == 126
    assert "not in allowed list" in result["stderr"]
    assert "SH-RAN" not in result["stdout"]


def test_another_name_of_the_same_file_is_refused_by_path(multicall):
    result = run_command_handler(str(multicall / "sh"))
    assert result["returncode"] == 126
    assert "SH-RAN" not in result["stdout"]


# --- relative PATH entries (RA-09) ---------------------------------------------------


@pytest.fixture()
def planted(tmp_path, monkeypatch):
    """A project folder holding a file `echo` that prints PROJECT-FILE, and a real bin/echo."""
    project = tmp_path / "project"
    project.mkdir()
    real = tmp_path / "realbin"
    real.mkdir()
    for folder, text in ((project, "PROJECT-FILE"), (real, "REAL-ECHO")):
        f = folder / "echo"
        f.write_text(f"#!/bin/sh\necho {text}\n")
        f.chmod(0o755)
    monkeypatch.chdir(project)
    monkeypatch.setenv("GABBE_MCP_ALLOWED_COMMANDS", "echo")
    monkeypatch.delenv("GABBE_MCP_INSECURE", raising=False)
    return real


@pytest.mark.skipif(os.name != "posix", reason="POSIX PATH rules")
@pytest.mark.parametrize("prefix", [".", "", "bin", "../x"])
def test_a_relative_or_empty_path_entry_never_runs_a_project_file(planted, monkeypatch, prefix):
    monkeypatch.setenv("PATH", prefix + os.pathsep + str(planted))
    assert run_command_handler("echo hi")["stdout"] == "REAL-ECHO\n"
    refused = run_command_handler("./echo hi")
    assert refused["returncode"] == 126 and "PROJECT-FILE" not in refused["stdout"]


@pytest.mark.skipif(os.name != "posix", reason="POSIX PATH rules")
def test_only_relative_entries_means_nothing_is_found(planted, monkeypatch):
    monkeypatch.setenv("PATH", "." + os.pathsep)
    result = run_command_handler("echo hi")
    assert "PROJECT-FILE" not in result["stdout"]
    assert result["returncode"] != 0


def test_the_child_gets_only_the_absolute_path_entries(monkeypatch, tmp_path):
    from gabbe.mcp_server import _child_env

    monkeypatch.setenv("PATH", os.pathsep.join([".", "", str(tmp_path)]))
    assert _child_env()["PATH"] == str(tmp_path)


# --- tokens (note N-1) --------------------------------------------------------------


def _initialize(srv, token, req_id):
    import json

    line = json.dumps(
        {"jsonrpc": "2.0", "id": req_id, "method": "initialize", "params": {"token": token}}
    )
    return _handle_line(srv, line)


@pytest.fixture()
def server(monkeypatch):
    monkeypatch.delenv("GABBE_MCP_INSECURE", raising=False)
    return _Server(ctx=None, token="s3cret-tök", run_command=True)


def test_a_non_ascii_wrong_token_gives_the_normal_auth_error(server):
    reply = _initialize(server, "tök", 1)
    assert reply is not None
    assert reply["error"]["code"] == -32000  # not -32603
    assert server.authenticated is False


def test_a_non_ascii_right_token_logs_in(server):
    reply = _initialize(server, "s3cret-tök", 1)
    assert reply is not None and "result" in reply
    assert server.authenticated is True


def test_a_failed_second_initialize_clears_the_earlier_login(server):
    assert server.authenticated is False
    _initialize(server, "s3cret-tök", 1)
    assert server.authenticated is True
    reply = _initialize(server, "wrong", 2)
    assert reply is not None and reply["error"]["code"] == -32000
    assert server.authenticated is False

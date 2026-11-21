# SPDX-License-Identifier: Apache-2.0
"""Read-only MCP tools (on by default), the opt-in run_command, the start-up checks
(empty folder, uninitialised database) and the run_command hardening of SW-13.

Everything runs in a temporary project; no network, no real sleeps."""

import io
import json
import os
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from gabbe import mcp_tools
from gabbe.mcp_server import _entry_matches, run_command_handler, serve_stdio

FIVE = ["list_skills", "read_skill", "search_skills", "get_template", "project_status"]


def _line(method, params=None, req_id=1):
    msg = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params is not None:
        msg["params"] = params
    return json.dumps(msg)


def _call(name, arguments=None, req_id=1):
    return _line("tools/call", {"name": name, "arguments": arguments or {}}, req_id)


def _serve(lines, enable_run_command=False):
    outputs = []
    with (
        patch("sys.stdin", io.StringIO("\n".join(lines) + "\n")),
        patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)),
    ):
        serve_stdio(enable_run_command=enable_run_command)
    return [json.loads(o) for o in outputs if o.strip()]


def _text(reply):
    return reply["result"]["content"][0]["text"]


@pytest.fixture(autouse=True)
def clean_env():
    with patch.dict(os.environ):
        for key in list(os.environ):
            if key.startswith("GABBE_MCP_"):
                del os.environ[key]
        yield


def _skill(root, category, stem, name=None, description="does a thing", triggers="alpha, beta"):
    folder = root / "agents" / "skills" / category
    folder.mkdir(parents=True, exist_ok=True)
    front = f"---\nname: {name or stem}\ndescription: {description}\ntriggers: [{triggers}]\n---\n"
    (folder / f"{stem}.skill.md").write_text(front + f"# {stem}\nbody of {stem}\n")


@pytest.fixture()
def kit(tmp_project):
    _skill(tmp_project, "coding", "alpha-skill", description="Refactor code safely")
    _skill(tmp_project, "ops", "beta-skill", description="Deploy a service", triggers="deploy")
    templates = tmp_project / "agents" / "templates" / "core"
    templates.mkdir(parents=True)
    (templates / "adr.md").write_text("# ADR template\n")
    return tmp_project


# --- what is on by default ----------------------------------------------------------


def test_default_tools_list_has_the_five_read_only_tools_and_no_run_command(kit):
    (reply,) = _serve([_line("tools/list")])
    tools = reply["result"]["tools"]
    assert [t["name"] for t in tools] == FIVE
    assert all(t["annotations"]["readOnlyHint"] is True for t in tools)
    assert all(t["inputSchema"]["additionalProperties"] is False for t in tools)


def test_run_command_is_listed_when_enabled_by_flag(kit):
    (reply,) = _serve([_line("tools/list")], enable_run_command=True)
    assert [t["name"] for t in reply["result"]["tools"]][-1] == "run_command"


def test_run_command_is_listed_when_enabled_by_variable(kit):
    os.environ["GABBE_MCP_ENABLE_RUN_COMMAND"] = "1"
    (reply,) = _serve([_line("tools/list")])
    assert "run_command" in [t["name"] for t in reply["result"]["tools"]]


def test_insecure_mode_alone_does_not_enable_run_command(kit):
    os.environ["GABBE_MCP_INSECURE"] = "1"
    (reply,) = _serve([_line("tools/list")])
    assert "run_command" not in [t["name"] for t in reply["result"]["tools"]]
    (call,) = _serve([_call("run_command", {"command": "echo hi"})])
    assert call["error"]["code"] == -32602
    assert "--enable-run-command" in call["error"]["message"]


def test_start_up_warning_says_how_to_enable_run_command(kit, caplog):
    os.environ["GABBE_MCP_ALLOWED_COMMANDS"] = "git"
    with caplog.at_level("WARNING", logger="gabbe.mcp"):
        _serve([])
    assert "--enable-run-command" in caplog.text
    assert "GABBE_MCP_ENABLE_RUN_COMMAND=1" in caplog.text


def test_read_only_tools_need_no_token_and_no_allow_list(kit):
    os.environ["GABBE_MCP_TOKEN"] = "secret"
    (reply,) = _serve([_call("list_skills")])
    assert json.loads(_text(reply))["count"] == 2


def test_read_only_tools_ignore_a_restrictive_policy_file(kit):
    (kit / "project" / "policies.yml").write_text("version: '1'\ntools:\n  allowed: []\n")
    (reply,) = _serve([_call("list_skills")])
    assert reply["result"]["isError"] is False


# --- list / read / search ---------------------------------------------------------


def test_list_skills_gives_name_description_path(kit):
    (reply,) = _serve([_call("list_skills")])
    items = json.loads(_text(reply))["skills"]
    assert {i["name"] for i in items} == {"alpha-skill", "beta-skill"}
    alpha = next(i for i in items if i["name"] == "alpha-skill")
    assert alpha["path"] == "agents/skills/coding/alpha-skill.skill.md"
    assert alpha["description"] == "Refactor code safely"


def test_list_skills_by_category_and_unknown_category(kit):
    (reply,) = _serve([_call("list_skills", {"category": "ops"})])
    assert [i["name"] for i in json.loads(_text(reply))["skills"]] == ["beta-skill"]
    (bad,) = _serve([_call("list_skills", {"category": "nope"})])
    assert bad["result"]["isError"] is True
    assert "Categories: coding, ops" in _text(bad)


def test_read_skill_by_name_and_by_file_stem(kit):
    _skill(kit, "ai", "gamma-file", name="gamma-display")
    for name in ("gamma-display", "gamma-file"):
        (reply,) = _serve([_call("read_skill", {"name": name})])
        assert reply["result"]["isError"] is False
        assert "body of gamma-file" in _text(reply)


def test_read_skill_unknown_and_ambiguous(kit):
    _skill(kit, "ops", "alpha-skill")  # same name in a second category
    (missing,) = _serve([_call("read_skill", {"name": "zzz"})])
    assert missing["result"]["isError"] is True
    (twice,) = _serve([_call("read_skill", {"name": "alpha-skill"})])
    assert twice["result"]["isError"] is True
    assert "several skills" in _text(twice)


def test_search_skills_ranks_name_above_description_and_caps(kit):
    _skill(kit, "ai", "deploy-helper", description="deploy tool", triggers="x")
    (reply,) = _serve([_call("search_skills", {"query": "Deploy"})])
    found = json.loads(_text(reply))
    assert [s["name"] for s in found["skills"]] == ["deploy-helper", "beta-skill"]
    (one,) = _serve([_call("search_skills", {"query": "deploy", "limit": 1})])
    assert json.loads(_text(one))["count"] == 1


def test_search_without_match_is_an_empty_list_not_an_error(kit):
    (reply,) = _serve([_call("search_skills", {"query": "zzzzqqq"})])
    assert reply["result"]["isError"] is False
    assert json.loads(_text(reply))["count"] == 0


def test_get_template_by_name_and_unknown(kit):
    (reply,) = _serve([_call("get_template", {"name": "adr"})])
    assert _text(reply) == "# ADR template\n"
    (bad,) = _serve([_call("get_template", {"name": "nope"})])
    assert bad["result"]["isError"] is True
    assert "adr" in _text(bad)


def test_project_status_reads_phase_and_task_counts(kit):
    memory = kit / "agents" / "memory"
    memory.mkdir(parents=True)
    (memory / "PROJECT_STATE.md").write_text(
        "| **Current Phase** | S03_PLAN |\n| **Phase Status** | IN_PROGRESS |\n"
    )
    (kit / "project" / "TASKS.md").write_text("- [ ] one\n- [/] two\n- [x] three\n- [x] four\n")
    (reply,) = _serve([_call("project_status")])
    status = json.loads(_text(reply))
    assert status["phase"] == "S03_PLAN" and status["phase_status"] == "IN_PROGRESS"
    assert status["tasks"] == {"TODO": 1, "IN_PROGRESS": 1, "DONE": 2, "total": 4}
    assert "missing" not in status


def test_project_status_says_what_is_missing(kit):
    (kit / "project" / "TASKS.md").write_text("- [ ] one\n")
    (reply,) = _serve([_call("project_status")])
    status = json.loads(_text(reply))
    assert reply["result"]["isError"] is False
    assert "PROJECT_STATE.md is missing" in status["missing"][0]
    assert status["tasks"]["total"] == 1


# --- a missing kit is a normal tool error that says where it looked ------------------


@pytest.mark.parametrize(
    "tool,args",
    [
        ("list_skills", {}),
        ("read_skill", {"name": "x"}),
        ("search_skills", {"query": "x"}),
        ("get_template", {"name": "x"}),
        ("project_status", {}),
    ],
)
def test_missing_kit_gives_is_error_and_a_sentence(tmp_project, tool, args):
    (tmp_project / "project" / "TASKS.md").unlink(missing_ok=True)
    (reply,) = _serve([_call(tool, args)])
    assert reply["result"]["isError"] is True
    assert f"looked in {tmp_project}" in _text(reply) or f"looked for {tmp_project}" in _text(reply)


# --- confinement: traversal, absolute paths, links ----------------------------------


@pytest.mark.parametrize("bad", ["../../etc/passwd", "/etc/passwd", "a/b", "..", "x\x00y"])
def test_names_that_look_like_paths_are_refused_by_the_schema(kit, bad):
    for tool in ("read_skill", "get_template"):
        (reply,) = _serve([_call(tool, {"name": bad})])
        assert reply["error"]["code"] == -32602


def test_handlers_refuse_path_names_even_when_called_directly(kit):
    assert mcp_tools.read_skill("../../etc/passwd")["mcp_is_error"] is True
    assert mcp_tools.get_template("/etc/passwd")["mcp_is_error"] is True


def test_a_skill_link_pointing_outside_is_not_listed_or_read(kit, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.skill.md"
    outside.write_text("---\nname: secret\ndescription: leaked\n---\nTOP SECRET\n")
    (kit / "agents" / "skills" / "ops" / "evil.skill.md").symlink_to(outside)
    (listing,) = _serve([_call("list_skills")])
    assert "secret" not in _text(listing) and "evil" not in _text(listing)
    (read,) = _serve([_call("read_skill", {"name": "evil"})])
    assert read["result"]["isError"] is True
    assert "TOP SECRET" not in _text(read)


def test_a_template_link_pointing_outside_is_refused(kit, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "passwd.md"
    outside.write_text("TOP SECRET")
    (kit / "agents" / "templates" / "core" / "leak.md").symlink_to(outside)
    (read,) = _serve([_call("get_template", {"name": "leak"})])
    assert read["result"]["isError"] is True
    assert "TOP SECRET" not in _text(read)


def test_a_skills_folder_that_is_a_link_outside_is_refused(tmp_project, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    (outside / "x.skill.md").write_text("---\nname: x\n---\nTOP SECRET\n")
    (tmp_project / "agents").mkdir()
    (tmp_project / "agents" / "skills").symlink_to(outside, target_is_directory=True)
    (reply,) = _serve([_call("list_skills")])
    assert reply["result"]["isError"] is True


def test_project_state_link_pointing_outside_is_ignored(kit, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "state.md"
    outside.write_text("| **Current Phase** | LEAKED |\n")
    (kit / "agents" / "memory").mkdir(parents=True)
    (kit / "agents" / "memory" / "PROJECT_STATE.md").symlink_to(outside)
    (reply,) = _serve([_call("project_status")])
    assert "LEAKED" not in _text(reply)


# --- caps -------------------------------------------------------------------------


def test_oversize_skill_text_is_cut_with_a_note(kit):
    big = kit / "agents" / "skills" / "ops" / "big.skill.md"
    big.write_text("---\nname: big\n---\n" + "x" * (mcp_tools.MAX_TEXT_BYTES * 2))
    (reply,) = _serve([_call("read_skill", {"name": "big"})])
    text = _text(reply)
    assert reply["result"]["isError"] is False
    assert len(text.encode()) < mcp_tools.MAX_TEXT_BYTES + 200
    assert "Cut at 65536 bytes" in text


def test_a_long_listing_is_cut_to_the_cap_with_a_note(kit):
    for i in range(400):
        _skill(kit, "many", f"s{i:03d}", description="d" * 300)
    (reply,) = _serve([_call("list_skills", {"category": "many"})])
    text = _text(reply)
    assert len(text.encode()) <= mcp_tools.MAX_TEXT_BYTES
    assert "truncated" in json.loads(text)


# --- run_command: matching rules and child environment (SW-13) ---------------------


def test_absolute_entry_matches_only_that_exact_path(tmp_path):
    exe = tmp_path / "git"
    exe.write_text("#!/bin/sh\n")
    exe.chmod(0o755)
    assert _entry_matches(str(exe), str(exe), str(exe))
    assert not _entry_matches(str(exe), "git", "/usr/bin/git")


def test_bare_entry_matches_the_bare_command_and_the_path_it_resolves_to(tmp_path, monkeypatch):
    real = tmp_path / "bin" / "git"
    real.parent.mkdir()
    real.write_text("#!/bin/sh\n")
    real.chmod(0o755)
    monkeypatch.setenv("PATH", str(real.parent))
    assert _entry_matches("git", "git", str(real))
    assert _entry_matches("git", str(real), str(real))


def test_bare_entry_does_not_match_another_git_elsewhere(tmp_path, monkeypatch):
    real = tmp_path / "bin" / "git"
    evil = tmp_path / "evil" / "git"
    for exe in (real, evil):
        exe.parent.mkdir()
        exe.write_text("#!/bin/sh\n")
        exe.chmod(0o755)
    monkeypatch.setenv("PATH", str(real.parent))
    assert not _entry_matches("git", str(evil), str(evil))


def test_relative_path_entry_never_matches_a_bare_name(tmp_path, monkeypatch):
    exe = tmp_path / "git"
    exe.write_text("#!/bin/sh\n")
    exe.chmod(0o755)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path))
    assert not _entry_matches("./git", "git", str(exe))
    assert not _entry_matches("./git", "./git", "./git")


def test_handler_refuses_a_lookalike_binary_and_runs_the_listed_one(tmp_path, monkeypatch):
    good = tmp_path / "bin" / "tool"
    evil = tmp_path / "evil" / "tool"
    for exe in (good, evil):
        exe.parent.mkdir()
        exe.write_text("#!/bin/sh\n")
        exe.chmod(0o755)
    monkeypatch.setenv("PATH", str(good.parent))
    monkeypatch.setenv("GABBE_MCP_ALLOWED_COMMANDS", "tool")
    done = MagicMock(stdout="", stderr="", returncode=0)
    with patch("gabbe.mcp_server.subprocess.run", return_value=done) as run:
        refused = run_command_handler(f"{evil} --x")
        assert refused["returncode"] == 126
        run.assert_not_called()
        run_command_handler("tool --x")
    assert run.call_args.args[0] == [str(good), "--x"]


def test_child_process_gets_a_minimal_environment(monkeypatch):
    monkeypatch.setenv("GABBE_MCP_ALLOWED_COMMANDS", "env")
    monkeypatch.setenv("GABBE_API_KEY", "super-secret")
    monkeypatch.setenv("OTHER_SECRET", "other")
    result = run_command_handler("env")
    assert result["returncode"] == 0
    assert "GABBE_API_KEY" not in result["stdout"]
    assert "super-secret" not in result["stdout"]
    assert "OTHER_SECRET" not in result["stdout"]
    assert "PATH=" in result["stdout"]


def test_pass_env_names_reach_the_child(monkeypatch):
    monkeypatch.setenv("GABBE_MCP_ALLOWED_COMMANDS", "env")
    monkeypatch.setenv("GABBE_MCP_PASS_ENV", "MY_TOOL_HOME, MISSING_ONE")
    monkeypatch.setenv("MY_TOOL_HOME", "/opt/tool")
    result = run_command_handler("env")
    assert "MY_TOOL_HOME=/opt/tool" in result["stdout"]


# --- start-up in a folder without a project or database (SW-15, INS-18) -----------


@pytest.fixture()
def bare_folder(tmp_path):
    gabbe_dir = tmp_path / "project"
    with (
        patch("gabbe.config.PROJECT_ROOT", tmp_path),
        patch("gabbe.config.GABBE_DIR", gabbe_dir),
        patch("gabbe.config.GABBE_POLICY_FILE", gabbe_dir / "policies.yml"),
        patch("gabbe.policy.GABBE_POLICY_FILE", gabbe_dir / "policies.yml"),
        patch("gabbe.database.GABBE_DIR", gabbe_dir),
        patch("gabbe.database.DB_PATH", gabbe_dir / "state.db"),
        patch("gabbe.audit.GABBE_DIR", gabbe_dir),
    ):
        yield tmp_path


def test_empty_folder_serves_tools_list_and_project_status(bare_folder):
    replies = _serve([_line("tools/list", req_id=1), _call("project_status", req_id=2)])
    assert [t["name"] for t in replies[0]["result"]["tools"]] == FIVE
    assert replies[1]["result"]["isError"] is True
    assert "gabbe init" in _text(replies[1])
    assert not (bare_folder / "project").exists()  # the server does not create a project


def test_empty_folder_refuses_run_command_and_says_why(bare_folder):
    os.environ.update({"GABBE_MCP_INSECURE": "1", "GABBE_MCP_ENABLE_RUN_COMMAND": "1"})
    (reply,) = _serve([_call("run_command", {"command": "echo hi"})])
    assert reply["result"]["isError"] is True
    assert "no project/ folder" in json.loads(_text(reply))["stderr"]


def test_uninitialised_database_is_set_up_so_the_audit_trail_is_kept(bare_folder):
    (bare_folder / "project").mkdir()
    (reply,) = _serve([_call("list_skills")])
    assert reply["result"]["isError"] is True  # no kit here, but the call was served
    conn = sqlite3.connect(bare_folder / "project" / "state.db")
    try:
        assert conn.execute("SELECT count(*) FROM runs").fetchone()[0] == 1
        spans = conn.execute("SELECT count(*) FROM audit_spans").fetchone()[0]
    finally:
        conn.close()
    assert spans >= 1


def test_database_that_cannot_be_used_falls_back_to_read_only(bare_folder):
    (bare_folder / "project").mkdir()
    (bare_folder / "project" / "state.db").write_text("this is not a database")
    (reply,) = _serve([_line("tools/list")])
    assert [t["name"] for t in reply["result"]["tools"]] == FIVE

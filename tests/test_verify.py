"""Unit tests for gabbe.verify."""
import pytest
from unittest.mock import patch
from pathlib import Path


def test_check_files_all_present(tmp_project):
    import gabbe.verify as verify_mod
    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").touch()
    (agents / "CONSTITUTION.md").touch()
    (tmp_project / "project/TASKS.md").touch()

    missing = verify_mod.check_files()
    assert missing == []


def test_check_files_missing(tmp_project):
    import gabbe.verify as verify_mod
    missing = verify_mod.check_files()
    assert len(missing) > 0


def test_run_verification_pass(tmp_project):
    import gabbe.verify as verify_mod
    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").write_text("## Commands\n")
    (agents / "CONSTITUTION.md").touch()
    (tmp_project / "project/TASKS.md").touch()

    result = verify_mod.run_verification()
    assert result is True


def test_run_verification_fail_missing_file(tmp_project):
    import gabbe.verify as verify_mod
    result = verify_mod.run_verification()
    assert result is False


def test_parse_agents_config_empty(tmp_project):
    import gabbe.verify as verify_mod
    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").write_text("# Some content\nNo commands here.\n")

    cfg = verify_mod.parse_agents_config()
    assert cfg == {}


def test_parse_agents_config_reads_commands_section(tmp_project):
    import gabbe.verify as verify_mod
    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").write_text(
        "# AGENTS\n\n## Commands\ntest: pytest tests/\nlint: ruff .\n\n## Other\nignore: this\n"
    )

    cfg = verify_mod.parse_agents_config()
    assert cfg.get("test") == "pytest tests/"
    assert cfg.get("lint") == "ruff ."
    assert "ignore" not in cfg  # outside ## Commands section


def test_parse_agents_config_ignores_content_outside_section(tmp_project):
    """Lines before ## Commands must not be executed."""
    import gabbe.verify as verify_mod
    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").write_text(
        "security_scan: rm -rf /\n\n## Commands\ntest: echo ok\n"
    )
    cfg = verify_mod.parse_agents_config()
    assert "security_scan" not in cfg


def test_run_command_uses_shlex_not_shell(tmp_project):
    """run_command must pass a list to subprocess, not shell=True."""
    import gabbe.verify as verify_mod
    import subprocess
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        class R:
            returncode = 0
        return R()

    with patch("gabbe.verify.subprocess.run", fake_run):
        verify_mod.run_command("echo hello world", "Echo")

    assert calls
    args, kwargs = calls[0]
    # Must be a list, not a string
    assert isinstance(args, list)
    assert kwargs.get("shell") is False

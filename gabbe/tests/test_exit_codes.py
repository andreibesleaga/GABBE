# SPDX-License-Identifier: Apache-2.0
"""Exit codes of verify, brain and forecast (1.2.0): failures must not exit 0."""

import sqlite3
from unittest.mock import patch

import pytest


def _run_main(*argv):
    from gabbe.main import main

    with patch("sys.argv", ["gabbe", *argv]):
        try:
            main()
        except SystemExit as exc:
            return exc.code
    return 0


def _kit(tmp_project, commands):
    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").write_text(commands)
    (agents / "CONSTITUTION.md").touch()
    (tmp_project / "project/TASKS.md").touch()


def test_verify_nothing_to_verify_exits_3(tmp_project, capsys):
    _kit(tmp_project, "## Commands\n")
    assert _run_main("verify") == 3
    out = capsys.readouterr().out
    assert "Nothing was verified" in out
    assert "PASSED" not in out
    assert "fill_placeholders" not in out


def test_verify_allow_empty_exits_0(tmp_project):
    _kit(tmp_project, "## Commands\n")
    assert _run_main("verify", "--allow-empty") == 0


def test_verify_real_pass_exits_0(tmp_project):
    _kit(tmp_project, '## Commands\ntest: "true"\n')
    assert _run_main("verify") == 0


def test_verify_real_failure_exits_1(tmp_project):
    _kit(tmp_project, '## Commands\ntest: "false"\n')
    assert _run_main("verify") == 1


def test_verify_placeholder_hint_has_no_missing_script(tmp_project, capsys):
    _kit(tmp_project, "## Commands\ntest: [PLACEHOLDER: test command]\n")
    assert _run_main("verify") == 1
    out = capsys.readouterr().out
    assert "fill_placeholders" not in out
    assert "agents/AGENTS.md" in out


def test_brain_heal_exits_1_on_issues(tmp_project, capsys):
    assert _run_main("brain", "heal") == 1  # required files are missing
    assert "Health Issues Found" in capsys.readouterr().out


def test_brain_heal_exits_0_when_healthy(tmp_project):
    _kit(tmp_project, "## Commands\n")
    assert _run_main("brain", "heal") == 0


def test_brain_activate_without_key_exits_1_with_message(tmp_project, capsys):
    with patch("gabbe.llm.GABBE_API_KEY", None):
        assert _run_main("brain", "activate") == 1
    out = capsys.readouterr().out
    assert "GABBE_API_KEY is not set" in out
    assert "export GABBE_API_KEY" in out
    assert "Policy denied" not in out and "ESCALATION" not in out


def test_brain_activate_api_error_exits_1(tmp_project):
    with patch("gabbe.llm.GABBE_API_KEY", "k"), patch("gabbe.brain.call_llm", return_value=None):
        assert _run_main("brain", "activate") == 1


def test_brain_activate_success_exits_0(tmp_project):
    with patch("gabbe.llm.GABBE_API_KEY", "k"), patch("gabbe.brain.call_llm", return_value="Go"):
        assert _run_main("brain", "activate") == 0


def test_brain_activate_platform_stop_exits_1(tmp_project, capsys):
    with (
        patch("gabbe.llm.GABBE_API_KEY", "k"),
        patch("gabbe.brain.call_llm", side_effect=RuntimeError("boom")),
        patch("gabbe.escalation._stdin_is_tty", return_value=False),
    ):
        assert _run_main("brain", "activate") == 1
    assert "Interrupted by Platform Controls" in capsys.readouterr().out


def test_forecast_exits_0_on_success(tmp_project):
    assert _run_main("forecast") == 0


def test_forecast_exits_1_on_database_error(tmp_project, capsys):
    with patch("gabbe.forecast.get_db", side_effect=sqlite3.OperationalError("disk")):
        assert _run_main("forecast") == 1
    assert "Database Error" in capsys.readouterr().out


def test_forecast_exits_1_on_unexpected_error(tmp_project):
    with patch("gabbe.forecast.get_db", side_effect=ValueError("odd")):
        assert _run_main("forecast") == 1


@pytest.mark.parametrize("flag", ["--allow-empty"])
def test_allow_empty_is_documented_in_help(flag, capsys):
    with patch("sys.argv", ["gabbe", "verify", "--help"]), pytest.raises(SystemExit):
        from gabbe.main import main

        main()
    assert flag in capsys.readouterr().out

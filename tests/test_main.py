"""Unit tests for gabbe.main — CLI dispatch and error handling."""
import sys
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# --version
# ---------------------------------------------------------------------------

def test_version_flag(tmp_project, capsys):
    from gabbe.main import main
    from gabbe import __version__
    with patch("sys.argv", ["gabbe", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


# ---------------------------------------------------------------------------
# No-arg → print help (exit 0)
# ---------------------------------------------------------------------------

def test_no_args_prints_help(tmp_project, capsys):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe"]):
        main()  # should not raise
    captured = capsys.readouterr()
    assert "gabbe" in captured.out.lower() or "usage" in captured.out.lower()


# ---------------------------------------------------------------------------
# init command
# ---------------------------------------------------------------------------

def test_init_command_calls_init_db(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "init"]), \
         patch("gabbe.main.init_db") as mock_init:
        main()
    mock_init.assert_called_once()


# ---------------------------------------------------------------------------
# db --init command
# ---------------------------------------------------------------------------

def test_db_init_command_calls_init_db(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "db", "--init"]), \
         patch("gabbe.main.init_db") as mock_init:
        main()
    mock_init.assert_called_once()


def test_db_no_flag_prints_help(tmp_project, capsys):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "db"]):
        main()
    # Should print db sub-parser help without crashing
    captured = capsys.readouterr()
    assert "--init" in captured.out


# ---------------------------------------------------------------------------
# sync command
# ---------------------------------------------------------------------------

def test_sync_command_dispatches(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "sync"]), \
         patch("gabbe.sync.sync_tasks") as mock_sync:
        main()
    mock_sync.assert_called_once()


# ---------------------------------------------------------------------------
# verify command
# ---------------------------------------------------------------------------

def test_verify_command_dispatches(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "verify"]), \
         patch("gabbe.verify.run_verification", return_value=True) as mock_ver:
        main()
    mock_ver.assert_called_once()


# ---------------------------------------------------------------------------
# status command
# ---------------------------------------------------------------------------

def test_status_command_dispatches(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "status"]), \
         patch("gabbe.status.show_dashboard") as mock_dash:
        main()
    mock_dash.assert_called_once()


# ---------------------------------------------------------------------------
# route command
# ---------------------------------------------------------------------------

def test_route_command_dispatches(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "route", "hello world"]), \
         patch("gabbe.route.route_request", return_value="LOCAL") as mock_route:
        main()
    mock_route.assert_called_once_with("hello world")


# ---------------------------------------------------------------------------
# brain sub-commands
# ---------------------------------------------------------------------------

def test_brain_activate_dispatches(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "brain", "activate"]), \
         patch("gabbe.brain.activate_brain") as mock_act:
        main()
    mock_act.assert_called_once()


def test_brain_evolve_dispatches(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "brain", "evolve", "--skill", "my-skill"]), \
         patch("gabbe.brain.evolve_prompts") as mock_evo:
        main()
    mock_evo.assert_called_once_with("my-skill")


def test_brain_heal_dispatches(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "brain", "heal"]), \
         patch("gabbe.brain.run_healer") as mock_heal:
        main()
    mock_heal.assert_called_once()


def test_brain_no_subcommand_prints_help(tmp_project, capsys):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "brain"]):
        main()
    captured = capsys.readouterr()
    assert "activate" in captured.out or "heal" in captured.out or "evolve" in captured.out


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_environment_error_exits_1(tmp_project, capsys):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "brain", "activate"]), \
         patch("gabbe.brain.activate_brain", side_effect=EnvironmentError("no key")):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
    assert "no key" in capsys.readouterr().err


def test_keyboard_interrupt_exits_130(tmp_project):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "brain", "activate"]), \
         patch("gabbe.brain.activate_brain", side_effect=KeyboardInterrupt()):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 130


def test_generic_exception_exits_1(tmp_project, capsys):
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "sync"]), \
         patch("gabbe.sync.sync_tasks", side_effect=RuntimeError("boom")):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
    assert "boom" in capsys.readouterr().err

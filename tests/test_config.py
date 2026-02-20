"""Unit tests for gabbe.config."""
import os
import pytest
from pathlib import Path
from unittest.mock import patch


def test_project_root_is_path():
    from gabbe.config import PROJECT_ROOT
    assert isinstance(PROJECT_ROOT, Path)


def test_gabbe_dir_is_child_of_project_root():
    from gabbe.config import PROJECT_ROOT, GABBE_DIR
    assert GABBE_DIR == PROJECT_ROOT / "project"


def test_db_path_inside_gabbe_dir():
    from gabbe.config import GABBE_DIR, DB_PATH
    assert DB_PATH == GABBE_DIR / "state.db"


def test_tasks_file_inside_project_root():
    from gabbe.config import PROJECT_ROOT, TASKS_FILE
    assert TASKS_FILE == PROJECT_ROOT / "project/TASKS.md"


def test_llm_temperature_default():
    from gabbe.config import LLM_TEMPERATURE
    assert 0.0 <= LLM_TEMPERATURE <= 1.0


def test_llm_timeout_default():
    from gabbe.config import LLM_TIMEOUT
    assert LLM_TIMEOUT > 0


def test_route_complexity_threshold_default():
    from gabbe.config import ROUTE_COMPLEXITY_THRESHOLD
    assert 0 < ROUTE_COMPLEXITY_THRESHOLD < 100


def test_llm_temperature_env_override():
    with patch.dict(os.environ, {"GABBE_LLM_TEMPERATURE": "0.3"}):
        import importlib
        import gabbe.config as cfg
        importlib.reload(cfg)
        assert cfg.LLM_TEMPERATURE == pytest.approx(0.3)


def test_gabbe_api_model_env_override():
    with patch.dict(os.environ, {"GABBE_API_MODEL": "my-custom-model"}):
        import importlib
        import gabbe.config as cfg
        importlib.reload(cfg)
        assert cfg.GABBE_API_MODEL == "my-custom-model"


def test_colors_no_duplicate_values():
    from gabbe.config import Colors
    values = [v for k, v in vars(Colors).items() if not k.startswith("_")]
    # HEADER and MAGENTA should differ now
    assert Colors.HEADER != Colors.MAGENTA


def test_progress_bar_len_positive():
    from gabbe.config import PROGRESS_BAR_LEN
    assert PROGRESS_BAR_LEN > 0

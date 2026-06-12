# SPDX-License-Identifier: Apache-2.0
"""Unit tests for gabbe.config."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


def test_project_root_is_path():
    from gabbe.config import PROJECT_ROOT

    assert isinstance(PROJECT_ROOT, Path)


def test_gabbe_dir_is_child_of_project_root():
    from gabbe.config import GABBE_DIR, PROJECT_ROOT

    assert GABBE_DIR == PROJECT_ROOT / "project"


def test_db_path_inside_gabbe_dir():
    from gabbe.config import DB_PATH, GABBE_DIR

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

    # Just assert the colors are distinct
    # HEADER and MAGENTA should differ now
    assert Colors.HEADER != Colors.MAGENTA


def test_progress_bar_len_positive():
    from gabbe.config import PROGRESS_BAR_LEN

    assert PROGRESS_BAR_LEN > 0


# Regression: GABBE_AUTONOMY resolution (env > project config > 'hybrid') is the
# documented contract in docs/SCHEMA.md and 14+ kit skills; GABBE_MAX_RETRIES_PER_TOOL
# is documented in 4 env tables. Their removal once slipped through untested.
def test_autonomy_env_overrides_project_config():
    import importlib

    import gabbe.config as cfg

    with patch.dict(os.environ, {"GABBE_AUTONOMY": "ask"}):
        with patch.object(cfg, "GABBE_PROJECT_CONFIG", {"autonomy": "auto"}):
            assert cfg._resolve_autonomy() == "ask"
    importlib.reload(cfg)


def test_autonomy_project_config_used_when_no_env():
    import gabbe.config as cfg

    env = {k: v for k, v in os.environ.items() if k != "GABBE_AUTONOMY"}
    with patch.dict(os.environ, env, clear=True):
        with patch.object(cfg, "GABBE_PROJECT_CONFIG", {"autonomy": "auto"}):
            assert cfg._resolve_autonomy() == "auto"
        with patch.object(cfg, "GABBE_PROJECT_CONFIG", {}):
            assert cfg._resolve_autonomy() == "hybrid"


def test_autonomy_invalid_value_falls_back_to_hybrid():
    import gabbe.config as cfg

    with patch.dict(os.environ, {"GABBE_AUTONOMY": "yolo"}):
        assert cfg._resolve_autonomy() == "hybrid"


def test_max_retries_per_tool_documented_var_exists():
    from gabbe.config import GABBE_MAX_RETRIES_PER_TOOL

    assert isinstance(GABBE_MAX_RETRIES_PER_TOOL, int) and GABBE_MAX_RETRIES_PER_TOOL >= 1


def test_autonomy_module_constant_is_valid():
    from gabbe.config import GABBE_AUTONOMY

    assert GABBE_AUTONOMY in {"ask", "auto", "hybrid"}

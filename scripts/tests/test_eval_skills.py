# SPDX-License-Identifier: Apache-2.0
"""Per-commit (deterministic) tests for the eval harness (Track E2).

Exercises the structural lint + the deterministic assertion evaluators with no
model, so the harness itself cannot silently regress. The model-dependent --live
lane is exercised only in the nightly CI job.
"""

import importlib.util
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_HARNESS = _REPO / "agents" / "scripts" / "eval_skills.py"


def _load():
    spec = importlib.util.spec_from_file_location("gabbe_eval_skills", _HARNESS)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


ev = _load()


def test_all_shipped_eval_suites_lint_clean():
    suites = ev.discover_suites()
    assert len(suites) >= 5, "expected the seeded golden datasets to be discovered"
    for path in suites:
        errors = ev.lint_suite(path)
        assert errors == [], f"{path} failed lint: {errors}"


def test_deterministic_evaluators_self_test_passes():
    assert ev.self_test_evaluators() == []


def test_run_check_returns_zero():
    assert ev.run_check() == 0


def test_assert_output_contains_and_regex():
    assert ev.assert_output({"type": "contains", "value": "?"}, "ok?")[0] is True
    assert ev.assert_output({"type": "contains", "value": "?"}, "ok")[0] is False
    assert ev.assert_output({"type": "regex", "value": r"^\d+$"}, "123")[0] is True


def test_assert_output_rejects_live_only_type():
    import pytest

    with pytest.raises(ValueError):
        ev.assert_output({"type": "llm-rubric", "value": "x"}, "out")

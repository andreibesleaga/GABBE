# SPDX-License-Identifier: Apache-2.0
"""Tests for scripts/gates/check_mutation_floor.py on sample mutmut statistics."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "gates" / "check_mutation_floor.py"
spec = importlib.util.spec_from_file_location("check_mutation_floor", SCRIPT)
cmf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmf)

# What `mutmut export-cicd-stats` (mutmut 3.8.1) wrote in a real run.
SAMPLE = {
    "killed": 89,
    "survived": 133,
    "total": 360,
    "no_tests": 138,
    "skipped": 0,
    "suspicious": 0,
    "timeout": 0,
    "check_was_interrupted_by_user": 0,
    "segfault": 0,
}


def _files(tmp_path, stats=SAMPLE, floor=50):
    s = tmp_path / "stats.json"
    f = tmp_path / "floor.json"
    s.write_text(json.dumps(stats))
    f.write_text(json.dumps({"floor": floor}))
    return ["--stats", str(s), "--floor-file", str(f)]


def test_score_counts_unreached_mutants_as_not_killed():
    """89 killed of 360 is 24.7%: mutants that no test reaches are not hidden."""
    assert cmf.score_percent(89, 360) == pytest.approx(24.72, abs=0.01)


def test_score_counts_timeouts_as_killed_and_skips_out_of_the_total():
    """mutmut's own rule: (killed + timeout) / (total - skipped)."""
    assert cmf.score_percent(40, 100, timeout=10, skipped=50) == pytest.approx(100.0)


def test_score_is_zero_when_nothing_was_tested():
    assert cmf.score_percent(0, 0) == 0.0
    assert cmf.score_percent(0, 5, skipped=5) == 0.0


def test_at_or_above_the_floor_exits_0(tmp_path, capsys):
    assert cmf.main(_files(tmp_path, floor=24.7)) == 0
    assert "meets the floor" in capsys.readouterr().out


def test_exactly_at_the_floor_passes(tmp_path):
    stats = dict(SAMPLE, killed=50, total=100)
    assert cmf.main(_files(tmp_path, stats, floor=50)) == 0


def test_below_the_floor_exits_1_and_says_so(tmp_path, capsys):
    assert cmf.main(_files(tmp_path, floor=60)) == 1
    out = capsys.readouterr().out
    assert "BELOW the floor of 60.0%" in out and out.count("\n") == 1


def test_no_floor_set_reports_the_score_and_exits_0(tmp_path, capsys):
    assert cmf.main(_files(tmp_path, floor=None)) == 0
    assert "no floor set yet" in capsys.readouterr().out


def test_counters_on_the_command_line_replace_the_stats_file(tmp_path, capsys):
    floor = tmp_path / "floor.json"
    floor.write_text(json.dumps({"floor": 40}))
    assert cmf.main(["--floor-file", str(floor), "--killed", "30", "--total", "100"]) == 1
    assert cmf.main(["--floor-file", str(floor), "--killed", "45", "--total", "100"]) == 0


def test_one_counter_without_the_other_is_refused(tmp_path):
    floor = tmp_path / "floor.json"
    floor.write_text(json.dumps({"floor": None}))
    assert cmf.main(["--floor-file", str(floor), "--killed", "3"]) == 2


def test_missing_result_fails_when_a_floor_is_set(tmp_path, capsys):
    floor = tmp_path / "floor.json"
    floor.write_text(json.dumps({"floor": 30}))
    args = ["--floor-file", str(floor), "--stats", str(tmp_path / "absent.json")]
    assert cmf.main(args) == 2
    assert "no usable result" in capsys.readouterr().out


def test_missing_result_is_not_a_failure_while_no_floor_is_set(tmp_path):
    floor = tmp_path / "floor.json"
    floor.write_text(json.dumps({"floor": None}))
    assert cmf.main(["--floor-file", str(floor), "--stats", str(tmp_path / "absent.json")]) == 0


@pytest.mark.parametrize(
    "bad",
    ["[]", '{"killed": "x", "total": 3}', '{"total": 3}', "not json", '{"killed": -1, "total": 3}'],
)
def test_unusable_stats_files_are_refused(tmp_path, bad):
    path = tmp_path / "s.json"
    path.write_text(bad)
    with pytest.raises(ValueError):
        cmf.read_stats(path)


@pytest.mark.parametrize(
    "bad", ['{"floor": "high"}', '{"floor": 101}', '{"floor": -1}', '{"floor": true}', "nope"]
)
def test_unusable_floor_files_exit_2(tmp_path, bad):
    floor = tmp_path / "floor.json"
    floor.write_text(bad)
    assert cmf.main(["--floor-file", str(floor), "--killed", "1", "--total", "2"]) == 2


def test_the_committed_floor_file_is_valid():
    """The file in the repository parses and holds null or a percentage."""
    assert (
        cmf.read_floor(cmf.DEFAULT_FLOOR_FILE) is None
        or 0 <= cmf.read_floor(cmf.DEFAULT_FLOOR_FILE) <= 100
    )

# SPDX-License-Identifier: Apache-2.0
"""Tests for the guardrail probe pack and its runner (no real agent, no network)."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_RUNNER = _REPO / "agents" / "scripts" / "run_guardrail_probes.py"
_spec = importlib.util.spec_from_file_location("run_guardrail_probes", _RUNNER)
assert _spec and _spec.loader
rp = importlib.util.module_from_spec(_spec)
sys.modules["run_guardrail_probes"] = rp
_spec.loader.exec_module(rp)


def _run(args, env=None):
    return subprocess.run(
        [sys.executable, str(_RUNNER)] + args,
        capture_output=True,
        text=True,
        env=env or dict(os.environ),
    )


@pytest.fixture(scope="module")
def probes():
    return rp.load_probes(rp.DEFAULT_PROBES)


def test_at_least_twelve_probes_validate(probes):
    assert len(probes) >= 12
    assert all(rp.validate_probe(p) == [] for p in probes)


def test_every_rule_has_two_probes(probes):
    for rule in rp.RULES:
        assert sum(p["rule"] == rule for p in probes) >= 2, rule


def test_pack_is_small():
    size = sum(f.stat().st_size for f in (_REPO / "agents" / "evals").rglob("*") if f.is_file())
    assert size < 60_000


def test_validate_rejects_bad_probe():
    errors = rp.validate_probe(
        {"id": "X", "rule": "nope", "files": {"../x": "y"}, "checks": [{"type": "?"}]}
    )
    assert len(errors) >= 4


def test_self_test_exit_zero_and_every_probe_both_ways(tmp_path):
    done = _run(["--self-test"])
    assert done.returncode == 0, done.stdout + done.stderr
    rows = [
        ln.split()
        for ln in done.stdout.splitlines()
        if ln[:4] in ("vcs-", "des-", "unt-", "sec-", "hon-", "aut-")
    ]
    assert len(rows) >= 12
    assert all(r[1:] == ["pass", "fail"] for r in rows)


def test_self_test_all_arms(probes):
    for arm in ("minimal", "bare"):
        rows = rp.self_test(probes[:3], arm)
        assert all((r["good"], r["bad"]) == ("pass", "fail") for r in rows)


def test_runner_writes_nothing_outside_its_temp_dir(tmp_path):
    home, tmpdir = tmp_path / "home", tmp_path / "tmp"
    home.mkdir()
    tmpdir.mkdir()
    env = dict(os.environ, HOME=str(home), TMPDIR=str(tmpdir))
    before = sorted(p.name for p in tmp_path.rglob("*"))
    assert _run(["--self-test"], env).returncode == 0
    assert _run(["--list"], env).returncode == 0
    assert sorted(p.name for p in tmp_path.rglob("*")) == before


def test_list_prints_every_probe(probes):
    done = _run(["--list"])
    assert done.returncode == 0
    assert all(p["id"] in done.stdout for p in probes)


def test_bad_agent_cmd_is_a_usage_error():
    assert _run(["--agent-cmd", "definitely-not-a-command {prompt}"]).returncode == 2
    assert _run(["--agent-cmd", "echo hi"]).returncode == 2
    assert _run([]).returncode == 2
    assert _run(["--probe", "zzz-99", "--self-test"]).returncode == 2


def test_run_with_command_agent_writes_json(tmp_path):
    out = tmp_path / "results.json"
    done = _run(
        [
            "--agent-cmd",
            "echo {prompt} > /dev/null",
            "--probe",
            "vcs-01",
            "--arm",
            "bare",
            "--out",
            str(out),
        ]
    )
    assert done.returncode == 1, done.stdout  # an agent that does nothing does not fix the typo
    data = json.loads(out.read_text())
    run = data["runs"][0]
    assert run["result"] == "fail" and Path(run["transcript_path"]).is_file()


def test_timeout_counts_as_failure():
    done = _run(
        [
            "--agent-cmd",
            "sleep 5 # {prompt}",
            "--timeout",
            "1",
            "--probe",
            "des-01",
            "--arm",
            "bare",
        ]
    )
    assert done.returncode == 1


def test_kit_arm_copies_rules_into_fixture(tmp_path, probes):
    fx = rp.build_fixture(probes[0], "kit", tmp_path)
    assert (fx.dir / "AGENTS.md").is_file() and (fx.dir / "CONSTITUTION.md").is_file()
    assert fx.git(["log", "--oneline"])


def test_every_probe_says_its_fixture_is_bait(probes):
    for p in probes:
        assert "must not be followed" in p["fixture_warning"], p["id"]
    readme = (rp.DEFAULT_PROBES.parent / "README.md").read_text(encoding="utf-8")
    assert "bait" in readme.split("\n\n")[1].lower()


def test_validate_requires_fixture_warning(probes):
    bad = {k: v for k, v in probes[0].items() if k != "fixture_warning"}
    assert any("fixture_warning" in e for e in rp.validate_probe(bad))


def test_fixture_project_does_not_get_the_warning(tmp_path, probes):
    fx = rp.build_fixture(probes[0], "bare", tmp_path)
    assert all(
        "fixture_warning" not in f.read_text(errors="ignore")
        for f in fx.dir.rglob("*")
        if f.is_file() and ".git" not in f.parts
    )

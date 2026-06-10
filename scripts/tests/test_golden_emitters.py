# SPDX-License-Identifier: Apache-2.0
"""R3: golden snapshot tests for the four+1 emitted client formats.

The emitted artifacts (.cursor/rules/*.mdc, .claude/skills/, .github/skills/,
.gemini/settings.json, .codex/AGENTS.md) are GABBE's real public API: any
downstream consumer depends on their exact bytes. These tests run the
installer non-interactively per platform and compare a sha256 manifest of
every emitted artifact against the committed baseline in
scripts/tests/golden/baseline_v0.8.0/<platform>/manifest.json.

Policy: the comparison is additive-only — new artifacts are allowed, but a
removed or byte-changed artifact fails. To intentionally update a baseline
(e.g. after an approved additive emitter change), run:

    python scripts/gates/capture_emitter_baseline.py \
        scripts/tests/golden/baseline_v0.8.0

and review the diff against the additive-only rule before committing.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASELINE_ROOT = REPO_ROOT / "scripts" / "tests" / "golden" / "baseline_v0.8.0"
CAPTURE = REPO_ROOT / "scripts" / "gates" / "capture_emitter_baseline.py"

PLATFORMS = ["claude", "codex", "copilot", "cursor", "gemini"]


def _run_capture(dest_root):
    """Run the capture harness in a SUBPROCESS so its in-process monkeypatching
    and module reloads of scripts/init.py never pollute this test session
    (init.py uses module-level globals that other tests, e.g. test_init.py,
    also import and patch)."""
    subprocess.run(
        [sys.executable, str(CAPTURE), str(dest_root)],
        check=True,
        capture_output=True,
    )


@pytest.fixture(scope="module")
def captured(tmp_path_factory):
    """Capture all platforms once, then a second time for the determinism check."""
    run_a = tmp_path_factory.mktemp("golden-a")
    run_b = tmp_path_factory.mktemp("golden-b")
    _run_capture(run_a)
    _run_capture(run_b)
    return run_a, run_b


@pytest.mark.parametrize("platform", PLATFORMS)
def test_emitter_output_is_additive_superset_of_baseline(platform, captured):
    run_a, _ = captured
    baseline_file = BASELINE_ROOT / platform / "manifest.json"
    assert baseline_file.exists(), f"missing golden baseline for {platform}"
    baseline = json.loads(baseline_file.read_text())
    current = json.loads((run_a / platform / "manifest.json").read_text())

    removed = [rel for rel in baseline if rel not in current]
    changed = [rel for rel in baseline if rel in current and current[rel] != baseline[rel]]
    assert not removed, f"{platform}: emitter dropped artifacts: {removed[:10]}"
    assert not changed, f"{platform}: emitter changed artifacts: {changed[:10]}"


@pytest.mark.parametrize("platform", PLATFORMS)
def test_emitter_is_deterministic(platform, captured):
    run_a, run_b = captured
    first = json.loads((run_a / platform / "manifest.json").read_text())
    second = json.loads((run_b / platform / "manifest.json").read_text())
    assert first == second, f"{platform}: emitter output is non-deterministic"

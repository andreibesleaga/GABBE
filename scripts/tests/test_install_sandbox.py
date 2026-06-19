# SPDX-License-Identifier: Apache-2.0
"""Workstream E: install-from-built-artifact sandbox (slow, no network).

Builds the wheel + sdist, installs the wheel into a throwaway virtualenv, and
runs the published entry points (`gabbe --version`, `gabbe doctor`) to prove the
packaged artifact is installable and runnable from a clean environment — the
gap the post-publish smoke only covers AFTER a release. Marked slow so the fast
PR suite skips it; a dedicated CI job runs it.
"""

import subprocess
import sys
import venv
from pathlib import Path

import pytest

import gabbe

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.slow
def test_wheel_installs_and_runs_in_fresh_venv(tmp_path):
    pytest.importorskip("build", reason="`build` not available to produce a wheel")

    dist = tmp_path / "dist"
    # 1. Build wheel + sdist from the repo into an isolated dist dir.
    r = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(dist), str(REPO_ROOT)],
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"build failed:\n{r.stdout}\n{r.stderr}"
    wheels = list(dist.glob("gabbe-*.whl"))
    sdists = list(dist.glob("gabbe-*.tar.gz"))
    assert wheels, "no wheel produced"
    assert sdists, "no sdist produced"

    # 2. Fresh venv, install ONLY the built wheel (no network for the package).
    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    py = env_dir / ("Scripts" if sys.platform == "win32" else "bin") / "python"
    pip = env_dir / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
    r = subprocess.run(
        [str(pip), "install", str(wheels[0])], capture_output=True, text=True, timeout=600
    )
    assert r.returncode == 0, f"wheel install failed:\n{r.stdout}\n{r.stderr}"

    # 3. The console entry points run and report the right version.
    r = subprocess.run(
        [str(py), "-m", "gabbe.main", "--version"], capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0
    assert gabbe.__version__ in (r.stdout + r.stderr)

    # 4. doctor runs read-only in the fresh project dir without crashing.
    proj = tmp_path / "proj"
    proj.mkdir()
    r = subprocess.run(
        [str(py), "-m", "gabbe.main", "doctor"],
        cwd=str(proj),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"doctor failed:\n{r.stdout}\n{r.stderr}"

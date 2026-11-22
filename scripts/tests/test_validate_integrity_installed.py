# SPDX-License-Identifier: Apache-2.0
"""`agents/scripts/validate_integrity.py` passes in an installed kit (no wizard, no README of the
repository next to `agents/`), leaves no `__pycache__` behind, and still fails in the repository
when a repository-only file is missing."""

import shutil
import subprocess
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path("agents/scripts/validate_integrity.py")


def _run(project: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(project / SCRIPT)], capture_output=True, text=True, check=False
    )


def _copy_kit(dest: Path) -> None:
    shutil.copytree(
        KIT_ROOT / "agents", dest / "agents", ignore=shutil.ignore_patterns("__pycache__")
    )


def test_passes_in_an_installed_kit_and_writes_nothing(tmp_path):
    _copy_kit(tmp_path)
    done = _run(tmp_path)
    assert done.returncode == 0, done.stdout
    assert not list(tmp_path.rglob("__pycache__"))


def test_a_missing_kit_file_still_fails_there(tmp_path):
    _copy_kit(tmp_path)
    (tmp_path / "agents" / "CONSTITUTION.md").unlink()
    assert _run(tmp_path).returncode == 1


def test_a_repository_missing_the_wizard_fails(tmp_path):
    _copy_kit(tmp_path)
    (tmp_path / "gabbe").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    (tmp_path / "README.md").write_text("x\n")
    done = _run(tmp_path)  # scripts/init.py is missing
    assert done.returncode == 1 and "scripts/init.py" in done.stdout

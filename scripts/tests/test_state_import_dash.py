"""state_import.sh must work under dash (Debian/Ubuntu /bin/sh), not only bash (SW-20)."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "agents" / "scripts" / "state_export.sh"
IMPORT = ROOT / "agents" / "scripts" / "state_import.sh"

pytestmark = pytest.mark.skipif(shutil.which("dash") is None, reason="dash not installed")


def _make_kit(base: Path) -> Path:
    (base / "agents" / "memory").mkdir(parents=True)
    (base / "project").mkdir()
    (base / "agents" / "AGENTS.md").write_text("# agents\n")
    (base / "agents" / "CONSTITUTION.md").write_text("GABBE Kit version: 1.1.4\n")
    (base / "agents" / "memory" / "PROJECT_STATE.md").write_text("state-marker\n")
    (base / "project" / "TASKS.md").write_text("tasks-marker\n")
    return base


def test_export_then_import_under_dash(tmp_path):
    src = _make_kit(tmp_path / "src")
    out = tmp_path / "out"
    out.mkdir()
    dst = tmp_path / "dst"
    dst.mkdir()
    scratch = tmp_path / "tmp"
    scratch.mkdir()

    subprocess.run(["dash", str(EXPORT), str(src), str(out)], check=True, capture_output=True)
    bundle = next(out.glob("gabbe-state-*.tar.gz"))

    run = subprocess.run(
        ["dash", str(IMPORT), "--apply", str(bundle), str(dst)],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "TMPDIR": str(scratch)},
    )
    assert run.returncode == 0, run.stderr
    assert (dst / "agents" / "memory" / "PROJECT_STATE.md").read_text() == "state-marker\n"
    assert (dst / "project" / "TASKS.md").read_text() == "tasks-marker\n"
    assert list(scratch.iterdir()) == [], "staging dir must be removed after --apply"

# SPDX-License-Identifier: Apache-2.0
"""The install record is never written through a link a project plants.

`.gabbe/manifest.json` is a dangling link to a path outside the project. `gabbe update`,
`gabbe uninstall` and the wizard must create nothing at the link's target and must name the
path in their message. The Node installer has the same rule (skipped when `node` is not on
PATH). Child processes run with `HOME` inside the temp folder; no network.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
INIT = REPO / "scripts" / "init.py"
NODE = shutil.which("node")


def _plant(tmp_path: Path) -> tuple[Path, Path, Path]:
    """(project, the link's target outside it, home). The link dangles."""
    project, home = tmp_path / "project", tmp_path / "home"
    (project / ".gabbe").mkdir(parents=True)
    home.mkdir()
    outside = tmp_path / "victim.txt"
    os.symlink(outside, project / ".gabbe" / "manifest.json")
    return project, outside, home


def _env(home: Path) -> dict[str, str]:
    return {
        "HOME": str(home),
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": str(REPO),
        "LANG": "C.UTF-8",
    }


def _run(cmd: list[str], project: Path, home: Path, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=project,
        env=_env(home),
        input=stdin,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


def _assert_refused(done: subprocess.CompletedProcess, project: Path, outside: Path) -> None:
    text = done.stdout + done.stderr
    assert not outside.exists(), "something was written through the link: " + text[-500:]
    assert str(project / ".gabbe" / "manifest.json") in text, text[-500:]


def test_gabbe_update_refuses_a_linked_record(tmp_path):
    project, outside, home = _plant(tmp_path)
    done = _run(
        [sys.executable, "-m", "gabbe.main", "update", "--dir", str(project)], project, home
    )
    assert done.returncode != 0
    _assert_refused(done, project, outside)
    assert not (project / "agents").exists(), "the update wrote files before refusing"


def test_gabbe_uninstall_refuses_a_linked_record(tmp_path):
    project, outside, home = _plant(tmp_path)
    done = _run([sys.executable, "-m", "gabbe.main", "uninstall"], project, home)
    assert done.returncode != 0
    _assert_refused(done, project, outside)


def test_the_wizard_refuses_a_linked_record_before_writing_anything(tmp_path):
    project, outside, home = _plant(tmp_path)
    done = _run([sys.executable, str(INIT)], project, home, stdin="1\n" * 300)
    assert done.returncode != 0
    _assert_refused(done, project, outside)
    assert not (project / "agents").exists(), "the wizard wrote files before refusing"


@pytest.mark.skipif(NODE is None, reason="node is not on PATH: the Node case is skipped")
def test_node_init_refuses_a_linked_record(tmp_path):
    project, outside, home = _plant(tmp_path)
    done = _run([NODE, str(REPO / "bin" / "install.js"), "init"], project, home)
    assert not outside.exists(), "something was written through the link"
    assert done.returncode != 0, done.stdout[-500:]


def test_the_wizard_ends_with_one_line_when_a_folder_it_needs_is_a_dangling_link(tmp_path):
    """Fail closed without a traceback: nothing is created at the link's target."""
    project, home = tmp_path / "project", tmp_path / "home"
    project.mkdir()
    home.mkdir()
    outside = tmp_path / "nowhere"
    os.symlink(outside, project / ".claude")
    done = _run([sys.executable, str(INIT)], project, home, stdin="1\ny\n" + "1\n" * 200)
    assert done.returncode == 1, done.stdout[-500:] + done.stderr[-500:]
    assert not outside.exists()
    assert "Traceback" not in done.stderr
    assert "The install stopped here" in done.stderr

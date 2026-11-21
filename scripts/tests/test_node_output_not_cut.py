# SPDX-License-Identifier: Apache-2.0
"""The Node installer's output is complete when it goes to a small pipe with a slow reader.

Node writes to a pipe asynchronously on POSIX; `process.exit()` right after a write used to cut
the rest of a long list (for example `uninstall --dry-run`) while the exit code stayed 0. The
installer now makes its output blocking. Linux only: the test shrinks the pipe to one page.
"""

import fcntl
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
INSTALL_JS = REPO / "bin" / "install.js"
NODE = shutil.which("node")
F_SETPIPE_SZ = 1031  # fcntl.F_SETPIPE_SZ exists only from Python 3.10

pytestmark = [
    pytest.mark.skipif(NODE is None, reason="node is not on PATH"),
    pytest.mark.skipif(not sys.platform.startswith("linux"), reason="needs F_SETPIPE_SZ (Linux)"),
]


def _env(home: Path) -> dict[str, str]:
    return {"HOME": str(home), "PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}


def _read_slowly(cmd: list[str], cwd: Path, home: Path) -> tuple[int, str]:
    """Run `cmd` with stdout on a one-page pipe and start reading only after a pause."""
    read_end, write_end = os.pipe()
    fcntl.fcntl(write_end, F_SETPIPE_SZ, 4096)
    child = subprocess.Popen(
        cmd, cwd=cwd, stdout=write_end, stderr=subprocess.DEVNULL, env=_env(home)
    )
    os.close(write_end)
    time.sleep(0.3)
    chunks = []
    while True:
        chunk = os.read(read_end, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    os.close(read_end)
    return child.wait(timeout=120), b"".join(chunks).decode()


def test_a_long_dry_run_list_is_not_cut_on_a_small_pipe(tmp_path):
    assert NODE is not None
    project, home = tmp_path / "project", tmp_path / "home"
    project.mkdir()
    home.mkdir()
    subprocess.run(
        [NODE, str(INSTALL_JS), "init", "--yes", "--agents", "claude"],
        cwd=project,
        env=_env(home),
        capture_output=True,
        check=True,
        timeout=300,
    )
    status, out = _read_slowly([NODE, str(INSTALL_JS), "uninstall", "--dry-run"], project, home)
    lines = out.splitlines()
    assert status == 0
    assert len(out) > 8192, "the list is too short to prove anything"
    assert lines[-1].startswith("Would remove "), "the end of the list is missing: " + lines[-1]
    assert int(lines[-1].split()[2]) == sum(1 for line in lines if line.startswith("  "))

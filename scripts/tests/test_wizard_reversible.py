# SPDX-License-Identifier: Apache-2.0
"""The wizard leaves nothing behind that uninstall cannot reverse.

- It adds `.env` lines to an existing `.gitignore` inside a recorded, backed-up block, so
  `gabbe uninstall` and `node bin/install.js uninstall` both give back the exact bytes.
- It records `agents/memory/PROJECT_STATE.md` when it creates it.
- A declined merge into a folder that holds no kit stops with exit status 1 and changes nothing.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

from gabbe import installer  # noqa: E402

KIT_ROOT = Path(__file__).resolve().parents[2]
KIT_SOURCE = init.KIT_SOURCE
GITIGNORE = b"node_modules\r\ndist\r\n"  # the user's own bytes, Windows line ends


def _run_wizard(project: Path, decline_merge: bool = False, kit: Path = KIT_SOURCE) -> None:
    def ask(question, default=None):
        if "(y/n)" in question:
            wrong = decline_merge and "Install/Merge" in question
            no = any(
                w in question for w in ("Dynamic Agent Setup", "Self-Evolving", "CLI platform")
            )
            return "n" if wrong or no else "y"
        return default or "demo"

    cwd = os.getcwd()
    os.chdir(project)
    init.PROJECT_ROOT = project
    init.TECH_MAP = {}
    init.FORCE = False
    init.KIT_SOURCE = kit
    init.SOURCE_AGENTS_DIR = kit / "agents"
    saved = (init.ask, init.select_index, init.select, init.ask_multiselect)
    init.ask = ask
    init.select_index = lambda question, options: 0
    init.select = lambda question, options: options[0]
    init.ask_multiselect = lambda question, options: options[:1]
    try:
        init.main()
    finally:
        init.ask, init.select_index, init.select, init.ask_multiselect = saved
        os.chdir(cwd)


def _snapshot(root: Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        rel = str(p.relative_to(root))
        if p.is_symlink():
            out[rel] = "link:" + os.readlink(p)
        elif p.is_file():
            out[rel] = p.read_bytes()
        else:
            out[rel] = "dir"
    return out


def _project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".gitignore").write_bytes(GITIGNORE)
    (proj / "README.md").write_text("mine\n")
    return proj


def test_the_gitignore_change_is_recorded_and_backed_up(tmp_path):
    proj = _project(tmp_path)
    _run_wizard(proj)
    text = (proj / ".gitignore").read_bytes()
    assert text.startswith(GITIGNORE) and b".env\r\n.env.local\r\n" in text
    assert (proj / ".gitignore.gabbe-bak").read_bytes() == GITIGNORE
    entries = json.loads((proj / ".gabbe" / "manifest.json").read_text())["entries"]
    entry = next(e for e in entries if e["path"] == ".gitignore")
    assert entry["kind"] == "block" and entry["backup_of"] == ".gitignore.gabbe-bak"


def test_python_uninstall_gives_back_the_project_byte_for_byte(tmp_path):
    proj = _project(tmp_path)
    before = _snapshot(proj)
    _run_wizard(proj)
    installer.uninstall(proj)
    assert _snapshot(proj) == before


def test_node_uninstall_gives_back_the_project_byte_for_byte(tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    proj = _project(tmp_path)
    before = _snapshot(proj)
    _run_wizard(proj)
    env = {**os.environ, "HOME": str(tmp_path), "USERPROFILE": str(tmp_path)}
    done = subprocess.run(
        [node, str(KIT_ROOT / "bin" / "install.js"), "uninstall"],
        cwd=proj,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    assert _snapshot(proj) == before


def test_a_gitignore_that_names_env_is_left_alone(tmp_path):
    proj = _project(tmp_path)
    (proj / ".gitignore").write_bytes(b".env\n")
    _run_wizard(proj)
    assert (proj / ".gitignore").read_bytes() == b".env\n"
    assert not (proj / ".gitignore.gabbe-bak").exists()


def test_no_gitignore_is_created(tmp_path):
    proj = _project(tmp_path)
    (proj / ".gitignore").unlink()
    _run_wizard(proj)
    assert not (proj / ".gitignore").exists()


def test_project_state_is_recorded_when_the_wizard_writes_it(tmp_path):
    proj = _project(tmp_path)
    # A kit without the tracker file: the wizard has to create it, and must record it.
    kit = tmp_path / "kit"
    shutil.copytree(KIT_SOURCE, kit, ignore=shutil.ignore_patterns(".git", "node_modules", ".venv"))
    (kit / "agents" / "memory" / "PROJECT_STATE.md").unlink()
    _run_wizard(proj, kit=kit)
    assert (proj / "agents" / "memory" / "PROJECT_STATE.md").exists()
    installer.uninstall(proj)
    assert not (proj / "agents").exists()


def test_declining_the_merge_into_a_folder_without_a_kit_stops_with_exit_1(tmp_path):
    proj = _project(tmp_path)
    (proj / "agents").mkdir()
    (proj / "agents" / "mine.md").write_text("my notes\n")
    before = _snapshot(proj)
    with pytest.raises(SystemExit) as stop:
        _run_wizard(proj, decline_merge=True)
    assert stop.value.code not in (0, None)
    assert "holds no kit" in str(stop.value.code)
    assert _snapshot(proj) == before


def test_the_copy_skips_python_caches(tmp_path):
    folder = tmp_path / "src"
    (folder / "__pycache__").mkdir(parents=True)
    (folder / "__pycache__" / "a.cpython-312.pyc").write_bytes(b"x")
    (folder / "b.pyc").write_bytes(b"x")
    (folder / "c.py").write_text("x = 1\n")
    kept = shutil.copytree(folder, tmp_path / "dst", ignore=init._build_leftovers)
    assert sorted(p.name for p in Path(kept).rglob("*")) == ["c.py"]

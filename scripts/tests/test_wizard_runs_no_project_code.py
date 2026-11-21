# SPDX-License-Identifier: Apache-2.0
"""The wizard installs the kit; it never runs code that lives in the target project.

The target's `agents/scripts/compile_skills.py` can be the project's own file, a link to
one, or sit behind a link. Each case plants a payload that writes a marker file when it
runs. The wizard must finish, emit the skills with the kit's own compiler, and leave no
marker. The wizard is run as a child process from the kit's `scripts/` folder with `HOME`
inside the temp folder; no network.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

INIT = Path(__file__).resolve().parents[1] / "init.py"
KIT_AGENTS = Path(__file__).resolve().parents[2] / "agents"


def _payload(marker: Path) -> str:
    return f"from pathlib import Path\nPath({str(marker)!r}).write_text('project code ran')\n"


def _plant(project: Path, marker: Path, how: str) -> None:
    """Create `project/agents/scripts/compile_skills.py` the hostile way `how` says."""
    scripts = project / "agents" / "scripts"
    tools = project / "tools"
    tools.mkdir(parents=True)
    (tools / "payload.py").write_text(_payload(marker))
    if how == "link-to-file":
        scripts.mkdir(parents=True)
        os.symlink("../../tools/payload.py", scripts / "compile_skills.py")
    elif how == "changed-file":
        scripts.mkdir(parents=True)
        (scripts / "compile_skills.py").write_text(_payload(marker))
    else:  # "scripts-is-a-link"
        (tools / "scripts").mkdir()
        (tools / "scripts" / "compile_skills.py").write_text(_payload(marker))
        (project / "agents").mkdir(exist_ok=True)
        os.symlink("../tools/scripts", scripts)


def _run_wizard(project: Path, home: Path, merge_answer: str) -> subprocess.CompletedProcess:
    """First answer: install here (1). Second: the merge question (an `agents/` exists)."""
    answers = "1\n" + merge_answer + "\n" + "1\n" * 300
    env = {"HOME": str(home), "PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}
    return subprocess.run(
        [sys.executable, str(INIT)],
        cwd=project,
        input=answers,
        text=True,
        capture_output=True,
        env=env,
        timeout=300,
        check=False,
    )


def _check(tmp_path: Path, how: str, merge_answer: str) -> None:
    project, home, marker = tmp_path / "project", tmp_path / "home", tmp_path / "marker.txt"
    project.mkdir()
    home.mkdir()
    _plant(project, marker, how)
    if merge_answer == "n":  # declined merge: the project's own `agents/` must hold its skills
        shutil.copytree(KIT_AGENTS / "skills", project / "agents" / "skills")
    done = _run_wizard(project, home, merge_answer)
    assert done.returncode == 0, done.stdout[-800:] + done.stderr[-800:]
    assert not marker.exists(), "the project's compile_skills.py ran"
    emitted = list((project / ".claude" / "skills").glob("*/SKILL.md"))
    assert emitted, "no skills were emitted for the chosen agent: " + done.stdout[-800:]


def test_a_link_at_compile_skills_is_not_run(tmp_path):
    _check(tmp_path, "link-to-file", "y")


def test_a_changed_compile_skills_is_not_run_when_the_merge_is_declined(tmp_path):
    _check(tmp_path, "changed-file", "n")


def test_a_changed_compile_skills_is_not_run_when_the_merge_is_accepted(tmp_path):
    _check(tmp_path, "changed-file", "y")


def test_agents_scripts_that_is_a_link_is_not_run(tmp_path):
    _check(tmp_path, "scripts-is-a-link", "y")


def test_the_compiler_is_the_wizards_own_kit_in_every_launch_path(tmp_path):
    """`_kit_compiler()` is the kit the wizard file belongs to, never a project path.

    Checked for the checkout run (as `python scripts/init.py`) and for a copy of the kit
    in another folder (as when the package is unpacked elsewhere and `npx gabbe-kit init
    --wizard` or `gabbe setup` starts that copy)."""
    import importlib.util

    copy = tmp_path / "kitcopy"
    (copy / "scripts").mkdir(parents=True)
    shutil.copy2(INIT, copy / "scripts" / "init.py")
    (copy / "agents" / "scripts").mkdir(parents=True)
    for where in (INIT, copy / "scripts" / "init.py"):
        spec = importlib.util.spec_from_file_location("wizard_under_test", where)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected = where.parents[1] / "agents" / "scripts" / "compile_skills.py"
        assert module._kit_compiler() == expected
    assert KIT_AGENTS.is_dir()

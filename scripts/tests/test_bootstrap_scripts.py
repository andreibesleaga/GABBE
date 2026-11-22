# SPDX-License-Identifier: Apache-2.0
"""The bootstrap scripts: install.sh, uninstall.sh, install.ps1, uninstall.ps1.

No network: the shell scripts run with a PATH of fake `node` / `npx` programs or of
nothing at all. PowerShell is not run here; the CI job `bootstrap-scripts-windows` runs
the two `.ps1` files, and these tests check their declared parameters as text.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO_ROOT / "install.sh"
UNINSTALL_SH = REPO_ROOT / "uninstall.sh"
INSTALL_PS1 = REPO_ROOT / "install.ps1"
UNINSTALL_PS1 = REPO_ROOT / "uninstall.ps1"
SH = shutil.which("sh") or "/bin/sh"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _tool_dir(tmp_path: Path, **fakes: str) -> Path:
    """A PATH folder holding `dirname`, `cat`, `mktemp` and `rm` (the scripts make and remove a
    temporary folder for npx) plus the fake programs given as name=shell-body. Nothing else is
    on it, so a missing runtime is really missing."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for real in ("dirname", "cat", "mktemp", "rm"):
        (bin_dir / real).symlink_to(shutil.which(real))
    for name, body in fakes.items():
        tool = bin_dir / name
        tool.write_text(f"#!{SH}\n{body}\n")
        tool.chmod(0o755)
    return bin_dir


def _run(script: Path, args, path_dir: Path, cwd: Path, stdin=subprocess.DEVNULL, **extra_env):
    return subprocess.run(
        [SH, str(script), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        stdin=stdin,
        env={"PATH": str(path_dir), "HOME": str(cwd), **extra_env},
    )


PACKAGE_VERSION = json.loads((REPO_ROOT / "package.json").read_text())["version"]
REAL_PYTHON = os.path.realpath(sys.executable)


def _python3_without_site(bin_dir: Path) -> None:
    """A `python3` on PATH that is the interpreter of this test run with `-S` (no
    site-packages), so a gabbe installed on the machine running the tests is never found."""
    tool = bin_dir / "python3"
    tool.write_text(f'#!{SH}\nexec "{REAL_PYTHON}" -S "$@"\n')
    tool.chmod(0o755)


def _decoy_project(tmp_path: Path):
    """A project holding a `gabbe/` package that records that it ran."""
    project = tmp_path / "proj"
    (project / "gabbe").mkdir(parents=True)
    marker = tmp_path / "DECOY-RAN"
    code = f"open({str(marker)!r}, 'w').write('ran')\n"
    (project / "gabbe" / "__init__.py").write_text(code)
    (project / "gabbe" / "main.py").write_text(code + "def main():\n    pass\n")
    return project, marker


def _fake_script_copy(tmp_path: Path, script: Path) -> Path:
    """The script alone in a folder: no bin/install.js next to it, so uninstall.sh uses npx."""
    folder = tmp_path / "alone"
    folder.mkdir(exist_ok=True)
    copy = folder / script.name
    shutil.copy(script, copy)
    return copy


# --------------------------------------------------------------------------
# Syntax and help
# --------------------------------------------------------------------------


@pytest.mark.parametrize("script", [INSTALL_SH, UNINSTALL_SH], ids=lambda p: p.name)
@pytest.mark.parametrize("shell", ["sh", "dash"])
def test_shell_scripts_parse(shell, script):
    exe = shutil.which(shell)
    if not exe:
        pytest.skip(f"{shell} is not installed")
    result = subprocess.run([exe, "-n", str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("script", [INSTALL_SH, UNINSTALL_SH], ids=lambda p: p.name)
def test_help_needs_no_network_and_exits_0(tmp_path, script):
    result = _run(script, ["--help"], _tool_dir(tmp_path), tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Usage:" in result.stdout


# --------------------------------------------------------------------------
# install.sh
# --------------------------------------------------------------------------


def test_install_sh_passes_its_arguments_to_the_node_installer(tmp_path):
    fakes = {"node": "echo node-ok", "npx": 'echo "npx $*"'}
    path_dir = _tool_dir(tmp_path, **fakes)

    result = _run(INSTALL_SH, ["init", "--agents", "claude", "--yes"], path_dir, tmp_path)

    assert result.returncode == 0, result.stderr
    # `init` is the installer's own command and is given once.
    assert f"npx --yes gabbe-kit@{PACKAGE_VERSION} init --agents claude --yes" in result.stdout


def test_install_sh_with_nothing_installed_says_what_to_install(tmp_path):
    result = _run(INSTALL_SH, [], _tool_dir(tmp_path), tmp_path)
    assert result.returncode == 1
    assert "neither Node nor python3" in result.stderr


def test_install_sh_piped_without_node_says_there_is_no_checkout(tmp_path):
    """`curl | sh` with only Python: no checkout, so the wizard is never started (and a
    scripts/init.py in the current project is never run by accident)."""
    path_dir = _tool_dir(tmp_path, python3='echo "WIZARD RAN"')
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "init.py").write_text("print('the project own script')\n")
    result = subprocess.run(
        [SH],
        input=INSTALL_SH.read_text(),
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={"PATH": str(path_dir), "HOME": str(tmp_path)},
    )
    assert result.returncode == 1
    assert "no GABBE checkout" in result.stderr
    assert "WIZARD RAN" not in result.stdout


def test_install_sh_wizard_needs_a_terminal_not_a_traceback(tmp_path):
    path_dir = _tool_dir(tmp_path, python3='echo "WIZARD RAN"')
    result = _run(INSTALL_SH, ["--agents", "claude"], path_dir, tmp_path)
    assert result.returncode == 1
    assert "needs a terminal" in result.stderr
    assert "Traceback" not in result.stderr + result.stdout
    assert "WIZARD RAN" not in result.stdout


def test_install_sh_wizard_gets_force_and_hooks_and_the_rest_is_listed(tmp_path):
    """Without Node, `--force` and `--hooks` reach the wizard; any other argument is listed
    as ignored. A terminal (a pty) is needed to get past the input check."""
    import pty

    path_dir = _tool_dir(tmp_path, python3='echo "WIZARD ARGS: $*"')
    master, slave = pty.openpty()
    try:
        result = _run(
            INSTALL_SH,
            ["--hooks", "--agents", "claude", "--force"],
            path_dir,
            tmp_path,
            stdin=slave,
        )
    finally:
        os.close(master)
        os.close(slave)
    assert result.returncode == 0, result.stderr
    args_line = next(x for x in result.stdout.splitlines() if x.startswith("WIZARD ARGS:"))
    assert args_line.split() == [
        "WIZARD",
        "ARGS:",
        str(REPO_ROOT / "scripts" / "init.py"),
        "--force",
        "--hooks",
    ]
    assert "ignored: --agents claude" in result.stderr


# --------------------------------------------------------------------------
# uninstall.sh
# --------------------------------------------------------------------------


def test_uninstall_sh_passes_arguments_and_the_exit_status(tmp_path):
    path_dir = _tool_dir(tmp_path, node='echo "node $*"; exit 3', npx='echo "npx $*"; exit 3')
    project = tmp_path / "proj"
    project.mkdir()

    result = _run(
        UNINSTALL_SH, ["--dry-run", "--agents", "cursor", "--dir", str(project)], path_dir, tmp_path
    )

    assert result.returncode == 3
    # This checkout has bin/install.js next to the script, so that file is run.
    assert f"node {REPO_ROOT}/bin/install.js uninstall --dry-run --agents cursor" in result.stdout


def test_uninstall_sh_without_a_tool_prints_the_manual_steps(tmp_path):
    result = _run(UNINSTALL_SH, ["--dry-run"], _tool_dir(tmp_path), tmp_path)
    assert result.returncode == 2
    assert "manifest.json" in result.stderr and "GABBE-KIT:BEGIN" in result.stderr


def test_uninstall_sh_removes_a_node_install(tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available")
    project = tmp_path / "proj"
    project.mkdir()
    (project / "app.js").write_text("1\n")
    env = dict(os.environ, HOME=str(tmp_path))
    install = [node, str(REPO_ROOT / "bin" / "install.js"), "init", "--yes", "--agents", "claude"]
    assert subprocess.run(install, cwd=project, env=env, capture_output=True).returncode == 0

    dry = subprocess.run(
        [SH, str(UNINSTALL_SH), "--dry-run"], cwd=project, env=env, capture_output=True, text=True
    )
    assert dry.returncode == 0, dry.stderr
    assert "Would remove" in dry.stdout
    assert (project / "agents" / "AGENTS.md").exists()

    real = subprocess.run(
        [SH, str(UNINSTALL_SH)], cwd=project, env=env, capture_output=True, text=True
    )
    assert real.returncode == 0, real.stderr
    assert sorted(p.name for p in project.iterdir()) == ["app.js"]


def test_uninstall_sh_with_a_pinned_version_runs_that_release(tmp_path):
    path_dir = _tool_dir(tmp_path, node="echo node-ok", npx='echo "npx $*"')
    script = _fake_script_copy(tmp_path, UNINSTALL_SH)
    result = _run(script, ["--dry-run"], path_dir, tmp_path)
    assert result.returncode == 0, result.stderr
    assert f"npx --yes gabbe-kit@{PACKAGE_VERSION} uninstall --dry-run" in result.stdout


# --------------------------------------------------------------------------
# npx runs from a new, empty folder; the project is passed with --dir (RA-03)
# --------------------------------------------------------------------------

# A fake npx that records the folder it runs in, what that folder holds, and its arguments.
RECORDING_NPX = (
    '{ pwd; echo "args: $*"; [ -e .npmrc ] && echo HAS-NPMRC; '
    "[ -e node_modules ] && echo HAS-NODE-MODULES; [ -e package.json ] && echo HAS-PACKAGE-JSON; "
    'exit 0; } > "$RECORD"'
)


def _hostile_project(tmp_path: Path):
    """A project whose .npmrc names a dead registry and a --require file that records a run."""
    project = tmp_path / "proj"
    (project / "node_modules").mkdir(parents=True)
    marker = tmp_path / "NPMRC-RAN"
    (tmp_path / "marker.js").write_text(f"require('fs').writeFileSync({str(marker)!r}, 'ran')\n")
    (project / ".npmrc").write_text(
        f"registry=http://127.0.0.1:1/\nnode-options=--require={tmp_path / 'marker.js'}\n"
    )
    (project / "package.json").write_text("{}\n")
    return project, marker


def _run_with_recording_npx(tmp_path: Path, which: str, args, cwd: Path, **extra):
    """Run a script copy (so the npx route is taken) and return (result, record lines, temp root)."""
    path_dir = _tool_dir(tmp_path, node="echo node-ok", npx=RECORDING_NPX)
    script = _fake_script_copy(tmp_path, INSTALL_SH if which == "install" else UNINSTALL_SH)
    temp_root = tmp_path / "tmp"
    temp_root.mkdir()
    record = tmp_path / "npx-record.txt"
    result = _run(script, args, path_dir, cwd, RECORD=str(record), TMPDIR=str(temp_root), **extra)
    lines = record.read_text().splitlines() if record.exists() else []
    return result, lines, temp_root


@pytest.mark.parametrize("which", ["install", "uninstall"])
def test_npx_runs_from_an_empty_temp_folder_not_the_project(tmp_path, which):
    """A project .npmrc (registry, node-options) and its node_modules decide what npx runs, so
    npx must not start in the project. With the fake npx this shows the working folder only; the
    marker proves nothing ran here, and the real run is the experiment in the release notes."""
    project, marker = _hostile_project(tmp_path)

    result, lines, temp_root = _run_with_recording_npx(tmp_path, which, [], project)

    assert result.returncode == 0, result.stderr
    work_dir = Path(lines[0])
    assert work_dir != project and project not in work_dir.parents
    assert temp_root in work_dir.parents, "the working folder is not a new folder under TMPDIR"
    assert not {"HAS-NPMRC", "HAS-NODE-MODULES", "HAS-PACKAGE-JSON"} & set(lines), lines
    assert not marker.exists()
    assert list(temp_root.iterdir()) == [], "the temporary folder was not removed"
    assert lines[1].endswith(f"--dir {project.resolve()}"), lines[1]
    assert "(.npmrc" not in lines[1]


@pytest.mark.parametrize("which", ["install", "uninstall"])
def test_the_temp_folder_is_removed_and_the_exit_status_kept_when_npx_fails(tmp_path, which):
    project, _ = _hostile_project(tmp_path)
    path_dir = _tool_dir(tmp_path, node="echo node-ok", npx='pwd > "$RECORD"; exit 3')
    script = _fake_script_copy(tmp_path, INSTALL_SH if which == "install" else UNINSTALL_SH)
    temp_root = tmp_path / "tmp"
    temp_root.mkdir()
    record = tmp_path / "rec.txt"
    result = _run(script, [], path_dir, project, RECORD=str(record), TMPDIR=str(temp_root))
    assert result.returncode == 3
    assert record.exists() and list(temp_root.iterdir()) == []


@pytest.mark.parametrize("which", ["install", "uninstall"])
@pytest.mark.parametrize("style", ["separate", "equals"])
def test_a_dir_argument_is_made_absolute_and_replaces_the_current_folder(tmp_path, which, style):
    project, _ = _hostile_project(tmp_path)
    arg = ["--dir", "proj"] if style == "separate" else ["--dir=proj"]

    result, lines, _ = _run_with_recording_npx(
        tmp_path, which, [*arg, "--agents", "claude"], tmp_path
    )

    assert result.returncode == 0, result.stderr
    assert Path(lines[0]) not in (tmp_path.resolve(), project.resolve())
    words = lines[1].split()
    assert words.count("--dir") == 1, lines[1]
    assert words[words.index("--dir") + 1] == str(project.resolve())
    assert "--agents claude" in lines[1]


@pytest.mark.parametrize("which", ["install", "uninstall"])
def test_a_dir_that_does_not_exist_is_refused_before_npx_runs(tmp_path, which):
    result, lines, temp_root = _run_with_recording_npx(
        tmp_path, which, ["--dir", "no-such-folder"], tmp_path
    )
    assert result.returncode == 2
    assert "no such folder" in result.stderr
    assert lines == [] and list(temp_root.iterdir()) == []


def test_uninstall_sh_run_from_a_checkout_passes_the_project_with_dir(tmp_path):
    path_dir = _tool_dir(tmp_path, node='echo "node $*"', npx='echo "npx $*"')
    project = tmp_path / "proj"
    project.mkdir()
    result = _run(UNINSTALL_SH, ["--dir", str(project), "--dry-run"], path_dir, tmp_path)
    assert result.returncode == 0, result.stderr
    assert f"install.js uninstall --dry-run --dir {project}" in result.stdout


def test_install_sh_without_mktemp_stops_instead_of_running_npx_in_the_project(tmp_path):
    path_dir = _tool_dir(tmp_path, node="echo node-ok", npx='echo "NPX RAN"')
    (path_dir / "mktemp").unlink()
    script = _fake_script_copy(tmp_path, INSTALL_SH)
    result = _run(script, [], path_dir, tmp_path)
    assert result.returncode == 1
    assert "temporary folder" in result.stderr and "NPX RAN" not in result.stdout


@pytest.mark.parametrize("script,param", [(INSTALL_PS1, "Dir"), (UNINSTALL_PS1, "Dir")])
def test_ps1_scripts_declare_a_dir_parameter(script, param):
    assert param in _declared(script)


@pytest.mark.parametrize("script", [INSTALL_PS1, UNINSTALL_PS1], ids=lambda p: p.name)
def test_ps1_npx_runs_from_a_new_temp_folder_and_names_the_project(script):
    """Read, not run (PowerShell is not available here): the npx call sits between
    Push-Location of a new folder under the temp path and its removal, and carries --dir."""
    text = script.read_text()
    assert "[System.IO.Path]::GetTempPath()" in text
    npx_line = next(ln for ln in text.splitlines() if re.match(r"\s*& npx\b", ln))
    assert "--dir $projectAbs" in npx_line
    before = text[: text.index(npx_line)]
    assert before.rindex("Push-Location -LiteralPath $workDir") > before.rindex("New-Item")
    after = text[text.index(npx_line) :]
    assert "Remove-Item -LiteralPath $workDir -Recurse" in after.split("exit $npxExit")[0]


# --------------------------------------------------------------------------
# The kit version: one line per script, equal to package.json, overridable
# --------------------------------------------------------------------------

SH_VERSION_LINE = re.compile(r'^GABBE_KIT_DEFAULT_VERSION="([^"]+)"$', re.M)
PS1_VERSION_LINE = re.compile(r"^\$GabbeKitDefaultVersion = '([^']+)'$", re.M)
ALL_SCRIPTS = [
    (INSTALL_SH, SH_VERSION_LINE),
    (UNINSTALL_SH, SH_VERSION_LINE),
    (INSTALL_PS1, PS1_VERSION_LINE),
    (UNINSTALL_PS1, PS1_VERSION_LINE),
]


@pytest.mark.parametrize("script,pattern", ALL_SCRIPTS, ids=lambda x: getattr(x, "name", ""))
def test_script_version_line_equals_the_package_version(script, pattern):
    """The release bump cannot forget a script: this fails (and so does the release gate)."""
    found = pattern.findall(script.read_text())
    assert found == [PACKAGE_VERSION], f"{script.name}: {found} != {PACKAGE_VERSION}"


@pytest.mark.parametrize("which", ["install", "uninstall"])
@pytest.mark.parametrize(
    "env_value,expected",
    [
        (None, f"gabbe-kit@{PACKAGE_VERSION}"),
        ("1.0.0", "gabbe-kit@1.0.0"),
        ("1.2.0-rc.1", "gabbe-kit@1.2.0-rc.1"),
        ("latest", "gabbe-kit"),
    ],
)
def test_shell_scripts_run_the_pinned_kit_version(tmp_path, which, env_value, expected):
    path_dir = _tool_dir(tmp_path, node="echo node-ok", npx='echo "npx $*"')
    script = _fake_script_copy(tmp_path, INSTALL_SH if which == "install" else UNINSTALL_SH)
    extra = {} if env_value is None else {"GABBE_KIT_VERSION": env_value}
    result = _run(script, [], path_dir, tmp_path, **extra)
    assert result.returncode == 0, result.stderr
    assert f"npx --yes {expected} {'init' if which == 'install' else 'uninstall'}" in result.stdout


@pytest.mark.parametrize("which", ["install", "uninstall"])
@pytest.mark.parametrize(
    "bad", ["1.2", "1.2.0;id", "$(id)", "../x", "1.2.0 --x", "Latest", "1.2.0-"]
)
def test_shell_scripts_refuse_a_bad_kit_version(tmp_path, which, bad):
    path_dir = _tool_dir(tmp_path, node="echo node-ok", npx='echo "npx $*"')
    script = _fake_script_copy(tmp_path, INSTALL_SH if which == "install" else UNINSTALL_SH)
    result = _run(script, [], path_dir, tmp_path, GABBE_KIT_VERSION=bad)
    assert result.returncode == 1
    assert "GABBE_KIT_VERSION must be a version" in result.stderr
    assert "npx" not in result.stdout


@pytest.mark.parametrize("script", [INSTALL_PS1, UNINSTALL_PS1], ids=lambda p: p.name)
def test_ps1_npx_calls_use_the_pinned_spec(script):
    text = script.read_text()
    assert '$kitSpec = "gabbe-kit@$kitVersion"' in text
    assert "$GabbeKitDefaultVersion" in text and "$env:GABBE_KIT_VERSION" in text
    npx_calls = [ln for ln in text.splitlines() if re.match(r"\s*& npx\b", ln)]
    assert npx_calls, "no npx call found"
    for line in npx_calls:
        assert "$kitSpec" in line and "gabbe-kit " not in line, line


# --------------------------------------------------------------------------
# The Python tool is never taken from the project folder
# --------------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["global", "dir"])
def test_uninstall_sh_never_imports_a_gabbe_package_from_the_project(tmp_path, mode):
    """A cloned project with its own `gabbe/` folder must not run when the uninstaller
    looks for the Python tool (no Node, no installed gabbe: it must say so and stop)."""
    project, marker = _decoy_project(tmp_path)
    path_dir = _tool_dir(tmp_path)
    _python3_without_site(path_dir)
    args = ["--global"] if mode == "global" else ["--dir", str(project)]
    result = subprocess.run(
        [SH, str(UNINSTALL_SH), *args],
        capture_output=True,
        text=True,
        cwd=project,
        env={"PATH": str(path_dir), "HOME": str(tmp_path / "home"), "PYTHONPATH": str(project)},
    )
    assert result.returncode == 2, result.stderr
    assert "found neither" in result.stderr
    assert not marker.exists(), "the project's gabbe/ package was imported"


def test_uninstall_sh_prefers_the_gabbe_command_of_the_python_package(tmp_path):
    project, marker = _decoy_project(tmp_path)
    path_dir = _tool_dir(tmp_path)
    _python3_without_site(path_dir)
    console = path_dir / "gabbe"
    console.write_text(f'#!{REAL_PYTHON}\nimport sys\nprint("CONSOLE", *sys.argv[1:])\n')
    console.chmod(0o755)
    result = _run(UNINSTALL_SH, ["--global", "--dry-run"], path_dir, project)
    assert result.returncode == 0, result.stderr
    assert "CONSOLE uninstall --global --dry-run" in result.stdout
    assert not marker.exists()


def test_uninstall_sh_ignores_a_gabbe_command_that_is_not_python(tmp_path):
    """The npm package also installs a `gabbe` (a node script): it is not the Python CLI."""
    path_dir = _tool_dir(tmp_path)
    _python3_without_site(path_dir)
    console = path_dir / "gabbe"
    console.write_text('#!/usr/bin/env node\nconsole.log("NODE GABBE")\n')
    console.chmod(0o755)
    result = _run(UNINSTALL_SH, ["--global"], path_dir, tmp_path)
    assert result.returncode == 2
    assert "NODE GABBE" not in result.stdout


@pytest.mark.skipif(sys.version_info < (3, 11), reason="-P needs Python 3.11 or later")
def test_uninstall_sh_finds_a_user_site_install_but_not_the_project_package(tmp_path):
    """`pip install --user gabbe` (a user-site install) is still found: `-I` would hide it."""
    project, marker = _decoy_project(tmp_path)
    home = tmp_path / "home"
    site_dir = subprocess.run(
        [REAL_PYTHON, "-c", "import site; print(site.getusersitepackages())"],
        capture_output=True,
        text=True,
        env={"HOME": str(home)},
    ).stdout.strip()
    (Path(site_dir) / "gabbe").mkdir(parents=True)
    (Path(site_dir) / "gabbe" / "__init__.py").write_text("")
    (Path(site_dir) / "gabbe" / "main.py").write_text(
        "import sys\ndef main():\n    print('USER-SITE', *sys.argv[1:])\n"
        "if __name__ == '__main__':\n    main()\n"
    )
    path_dir = _tool_dir(tmp_path)
    (path_dir / "python3").symlink_to(REAL_PYTHON)
    result = _run(UNINSTALL_SH, ["--global"], path_dir, project, HOME=str(home))
    assert result.returncode == 0, result.stderr
    assert "USER-SITE uninstall --global" in result.stdout
    assert not marker.exists()


# --------------------------------------------------------------------------
# The PowerShell scripts (text only: PowerShell is not run here)
# --------------------------------------------------------------------------


def _declared(script: Path) -> set[str]:
    """`[switch]$DryRun` -> `DryRun` for every parameter in the script's param() block."""
    block = re.search(r"\bparam\((.*?)\n\)", script.read_text(), re.DOTALL).group(1)
    return set(re.findall(r"\[(?:switch|string)(?:\[\])?\]\s*\$(\w+)", block))


def test_uninstall_ps1_declares_the_parameters_the_install_guide_names():
    guide = (REPO_ROOT / "docs" / "INSTALL.md").read_text()
    named = {"DryRun", "Agents", "Purge", "Dir"}
    assert named <= _declared(UNINSTALL_PS1)
    for name in named:
        assert f"-{name}" in guide, f"docs/INSTALL.md does not mention -{name}"


def test_install_ps1_declares_its_parameters():
    assert {"Help", "Force", "Yes", "Agents"} <= _declared(INSTALL_PS1)


@pytest.mark.parametrize("script", [INSTALL_PS1, UNINSTALL_PS1], ids=lambda p: p.name)
def test_ps1_scripts_follow_the_rules(script):
    text = script.read_text()
    assert "$Args" not in text, "$Args is an automatic variable: do not declare or use it"
    assert "Write-Error" not in text, "Write-Error ends the script before the hints print"
    assert "exit $LASTEXITCODE" in text

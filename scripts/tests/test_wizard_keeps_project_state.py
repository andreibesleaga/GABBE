# SPDX-License-Identifier: Apache-2.0
"""The wizard never replaces a project's `agents/memory/PROJECT_STATE.md`.

With "Agent Analytics" switched on (the default answer) the wizard used to write a one-line
`Phase: S00_INITIALIZED` stub over the file: over the kit's own tracker on a first run, and over
the project's state on every later run. The state file is the project's memory, and it is now
created only when it is absent.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

KIT_SOURCE = init.KIT_SOURCE
NO = ("Dynamic Agent Setup", "Self-Evolving", "CLI platform controls")


def _answer(question, default=None):
    """Yes to every yes/no question except the three optional extras; else the default."""
    if "(y/n)" in question:
        return "n" if any(word in question for word in NO) else "y"
    return default or "demo"


def _run_wizard(project: Path) -> list:
    """Run the wizard in `project` with rule-based answers; return the questions it asked."""
    asked = []

    def ask(question, default=None):
        asked.append(question)
        return _answer(question, default)

    def select_index(question, options):
        asked.append(question)
        return 0

    project.mkdir(parents=True, exist_ok=True)
    cwd = os.getcwd()
    os.chdir(project)
    init.PROJECT_ROOT = project
    init.TECH_MAP = {}
    init.FORCE = False
    init.KIT_SOURCE = KIT_SOURCE
    init.SOURCE_AGENTS_DIR = KIT_SOURCE / "agents"
    saved = (init.ask, init.select_index, init.select, init.ask_multiselect)
    init.ask = ask
    init.select_index = select_index
    init.select = lambda question, options: options[select_index(question, options)]
    init.ask_multiselect = lambda question, options: options[:1]
    try:
        init.main()
    finally:
        init.ask, init.select_index, init.select, init.ask_multiselect = saved
        os.chdir(cwd)
    return asked


def test_a_first_run_keeps_the_kits_tracker_and_a_second_run_keeps_the_projects_state(tmp_path):
    project = tmp_path / "project"
    asked = _run_wizard(project)
    assert any("Enable Agent Analytics" in q for q in asked)
    assert (project / "agents" / "memory" / "metrics").is_dir(), "analytics was not switched on"
    state = project / "agents" / "memory" / "PROJECT_STATE.md"
    text = state.read_text(encoding="utf-8")
    assert "S00_INITIALIZED" not in text
    assert len(text.splitlines()) > 10, "the kit's tracker was replaced by a stub"

    state.write_text(text + "\nMY NOTE: phase S05, task 12 in progress\n", encoding="utf-8")
    _run_wizard(project)
    assert "MY NOTE: phase S05" in state.read_text(encoding="utf-8")

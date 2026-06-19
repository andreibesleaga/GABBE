# SPDX-License-Identifier: Apache-2.0
"""Workstream F (visual): snapshot the wizard's question FLOW.

Records the exact sequence of prompts the wizard asks for a fixed set of answers
and compares it to a committed snapshot. This catches UX/flow regressions — a
reordered, dropped, or added question — that artifact golden diffs don't, while
staying deterministic (no absolute paths, counts, or timings). Regenerate with:

    GABBE_UPDATE_SNAPSHOTS=1 pytest scripts/tests/test_wizard_flow_snapshot.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init  # noqa: E402

ORIGINAL_KIT_SOURCE = init.KIT_SOURCE
SNAP_DIR = Path(__file__).parent / "golden" / "wizard"

GREENFIELD_INPUTS = [
    "1",
    "Demo",
    "A demo",
    "2",
    "1",
    "1",
    "Next.js",
    "1",
    "4",
    "n",
    "n",
    "n",
    "n",
    "1",
    "1",
]


def _capture_flow(tmpdir, inputs):
    """Run the wizard, recording every question shown (not the answers)."""
    questions: list[str] = []
    answers = iter(inputs)

    def rec_ask(q, default=None):
        questions.append(f"ASK: {q}")
        return next(answers)

    def rec_select_index(q, opts):
        questions.append(f"SELECT: {q} :: {' | '.join(opts)}")
        return int(next(answers)) - 1

    def rec_select(q, opts):
        return opts[rec_select_index(q, opts)]

    def rec_multiselect(q, opts):
        questions.append(f"MULTI: {q} :: {' | '.join(opts)}")
        picks = next(answers)
        idxs = [int(x) - 1 for x in picks.split(",") if x.strip().isdigit()]
        return [opts[i] for i in idxs if 0 <= i < len(opts)]

    Path(tmpdir).mkdir(parents=True, exist_ok=True)
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    init.PROJECT_ROOT = Path(tmpdir)
    init.TECH_MAP = {}
    init.FORCE = False
    init.KIT_SOURCE = ORIGINAL_KIT_SOURCE
    init.SOURCE_AGENTS_DIR = ORIGINAL_KIT_SOURCE / "agents"
    orig = (init.ask, init.select_index, init.select, init.ask_multiselect)
    init.ask, init.select_index, init.select, init.ask_multiselect = (
        rec_ask,
        rec_select_index,
        rec_select,
        rec_multiselect,
    )
    try:
        init.main()
    finally:
        init.ask, init.select_index, init.select, init.ask_multiselect = orig
        os.chdir(original_cwd)
    text = "\n".join(questions) + "\n"
    # Normalise machine-specific paths so the snapshot is deterministic.
    text = text.replace(str(Path(tmpdir).resolve()), "<PROJECT_ROOT>")
    text = text.replace(str(Path(tmpdir)), "<PROJECT_ROOT>")
    text = text.replace(str(Path.home()), "<HOME>")
    return text


def _check_snapshot(name, content):
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    snap = SNAP_DIR / name
    if os.environ.get("GABBE_UPDATE_SNAPSHOTS") or not snap.exists():
        snap.write_text(content)
        return
    expected = snap.read_text()
    assert content == expected, (
        f"wizard flow changed vs {snap}.\n"
        f"Review the diff; if intended, regenerate with GABBE_UPDATE_SNAPSHOTS=1.\n"
        f"--- expected ---\n{expected}\n--- actual ---\n{content}"
    )


def test_greenfield_wizard_flow_snapshot(tmp_path):
    flow = _capture_flow(tmp_path / "g", GREENFIELD_INPUTS)
    _check_snapshot("greenfield_flow.txt", flow)

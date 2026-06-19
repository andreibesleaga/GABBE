# SPDX-License-Identifier: Apache-2.0
"""Workstream F (visual): the docs' diagrams are valid and render.

Every ```mermaid block in the docs must declare a real diagram type and be
non-trivial, so the rendered READMEs/diagrams users see don't silently break.
When the mermaid CLI (`mmdc`) is available we additionally RENDER each diagram
to catch syntax errors a structural check can't; otherwise that step is skipped
(the structural check still runs everywhere)."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_MERMAID_RE = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
_VALID_DIAGRAM_TYPES = (
    "graph",
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "journey",
    "pie",
    "mindmap",
    "timeline",
    "gitGraph",
    "quadrantChart",
    "C4Context",
)


def _docs_with_mermaid():
    files = [REPO_ROOT / "README.md"]
    files += sorted((REPO_ROOT / "docs").rglob("*.md"))
    out = []
    for f in files:
        if not f.exists():
            continue
        for i, block in enumerate(_MERMAID_RE.findall(f.read_text())):
            out.append((f, i, block.strip()))
    return out


def test_at_least_one_mermaid_diagram_exists():
    assert _docs_with_mermaid(), "expected the docs to contain mermaid diagrams"


def test_every_mermaid_block_declares_a_valid_type():
    bad = []
    for f, i, block in _docs_with_mermaid():
        first = block.splitlines()[0].strip() if block.splitlines() else ""
        if not first.startswith(_VALID_DIAGRAM_TYPES):
            bad.append(f"{f.relative_to(REPO_ROOT)} block #{i}: starts with {first!r}")
        elif len(block.splitlines()) < 2:
            bad.append(f"{f.relative_to(REPO_ROOT)} block #{i}: trivially empty diagram")
    assert not bad, "invalid mermaid diagrams:\n" + "\n".join(bad)


@pytest.mark.slow
def test_mermaid_diagrams_render_when_cli_available(tmp_path):
    mmdc = shutil.which("mmdc")
    if not mmdc:
        pytest.skip("mermaid CLI (mmdc) not installed")
    failures = []
    for f, i, block in _docs_with_mermaid():
        src = tmp_path / f"d_{f.stem}_{i}.mmd"
        src.write_text(block + "\n")
        out = tmp_path / f"d_{f.stem}_{i}.svg"
        r = subprocess.run(
            [mmdc, "-i", str(src), "-o", str(out)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode != 0:
            failures.append(f"{f.relative_to(REPO_ROOT)} block #{i}: {r.stderr.strip()[:200]}")
    assert not failures, "mermaid render failures:\n" + "\n".join(failures)

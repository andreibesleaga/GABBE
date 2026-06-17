#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Methodology-graph validator (Track E7).

Goes beyond per-file structural checks (validate_skills / validate_links) to verify
the *graph* of the methodology layer is coherent — the lifecycle flow, persona
handoffs, the memory state model, and index↔file bijection. Catches dangling
phase→asset references, orphaned/unregistered skills, and missing memory layers:
the "flows / logic / states / architecture" consistency the framework promises.

Hard checks exit 1 on failure. Softer observations are printed as warnings.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

# Files that describe the lifecycle flow / orchestration state machine.
FLOW_FILES = [
    AGENTS_DIR / "guides/processes/loki-sdlc-phases.md",
    AGENTS_DIR / "skills/brain/loki-mode.skill.md",
    AGENTS_DIR / "guides/processes/full-system-lifecycle.md",
]

# The 4-layer memory state model (RESUME_POINTER → PROJECT_STATE → CONTINUITY → AUDIT_LOG).
MEMORY_LAYERS = ["RESUME_POINTER", "PROJECT_STATE", "CONTINUITY", "AUDIT_LOG"]

# Hard human-approval gates that must be present in the lifecycle.
REQUIRED_GATES = ["S01", "S02", "S07", "S08"]

# Asset path reference: skills/.../x.skill.md OR templates|personas|guides/.../x.md.
# (agents/memory/** paths in the flow docs are RUNTIME write-targets — e.g. per-run
# episodic snapshots — not static repo assets, so they are not existence-checked here;
# the live memory layers are verified separately by check_memory_state_model.)
_ASSET_RE = re.compile(r"\b((?:skills|templates|personas|guides)/[\w./-]+?\.(?:skill\.md|md|json))")


class Graph:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"{RED}x FAIL: {msg}{NC}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"{YELLOW}! WARN: {msg}{NC}")

    def ok(self, msg: str) -> None:
        print(f"{GREEN}✓ {msg}{NC}")


def _resolve(token: str) -> Path:
    """Resolve a doc-relative asset reference to a real path."""
    if token.startswith("agents/"):
        return PROJECT_ROOT / token
    return AGENTS_DIR / token


def check_asset_references(g: Graph) -> None:
    """Every asset a lifecycle phase points to must exist (no dangling flow edge)."""
    print(f"\n{BLUE}=== Lifecycle flow → asset references resolve ==={NC}")
    checked = 0
    for fpath in FLOW_FILES:
        if not fpath.exists():
            g.warn(f"flow file missing: {fpath.relative_to(PROJECT_ROOT)}")
            continue
        text = fpath.read_text()
        refs = set(_ASSET_RE.findall(text))
        for ref in sorted(refs):
            checked += 1
            if not _resolve(ref).exists():
                g.fail(f"{fpath.name} references missing asset: {ref}")
    g.ok(f"checked {checked} lifecycle asset references")


def check_skill_index_bijection(g: Graph) -> None:
    """Every skill file is registered in the index, and every indexed path resolves."""
    print(f"\n{BLUE}=== Skill index ↔ file bijection ==={NC}")
    idx = (AGENTS_DIR / "skills/00-index.md").read_text()
    indexed = {
        m.replace("skills/", "")
        for m in re.findall(r"`((?:skills/)?[\w-]+/[\w-]+\.skill\.md)`", idx)
    }
    files = {
        str(p.relative_to(AGENTS_DIR / "skills"))
        for p in (AGENTS_DIR / "skills").glob("**/*.skill.md")
    }

    unregistered = sorted(files - indexed)
    for u in unregistered:
        g.fail(f"skill file not registered in skills/00-index.md: {u}")
    dangling = sorted(t for t in indexed if not (AGENTS_DIR / "skills" / t).exists())
    for d in dangling:
        g.fail(f"skills/00-index.md references missing skill file: {d}")
    if not unregistered and not dangling:
        g.ok(f"all {len(files)} skill files registered and resolvable")


def check_persona_index_bijection(g: Graph) -> None:
    print(f"\n{BLUE}=== Persona index ↔ file bijection ==={NC}")
    idx = (AGENTS_DIR / "personas/00-index.md").read_text()
    files = {p.stem for p in (AGENTS_DIR / "personas").glob("*.md") if p.stem != "00-index"}
    for slug in sorted(files):
        if slug not in idx:
            g.fail(f"persona file not registered in personas/00-index.md: {slug}")
    g.ok(f"checked {len(files)} persona files against the index")


def check_memory_state_model(g: Graph) -> None:
    """The 4-layer memory model must exist and be wired into the orchestration spine."""
    print(f"\n{BLUE}=== Memory state model (4 layers) ==={NC}")
    loki = AGENTS_DIR / "skills/brain/loki-mode.skill.md"
    loki_text = loki.read_text() if loki.exists() else ""
    mem_dir = AGENTS_DIR / "memory"
    for layer in MEMORY_LAYERS:
        present = list(mem_dir.glob(f"{layer}*.md"))
        if not present:
            g.fail(f"memory layer artifact missing: {layer}*.md under agents/memory/")
        if layer not in loki_text:
            g.warn(f"memory layer '{layer}' not referenced in loki-mode.skill.md")
    if not g.errors:
        g.ok("all 4 memory layers present")


def check_lifecycle_dag(g: Graph) -> None:
    """Lifecycle phases form a contiguous sequence with the hard approval gates present."""
    print(f"\n{BLUE}=== Lifecycle DAG + approval gates ==={NC}")
    phases_text = (AGENTS_DIR / "guides/processes/loki-sdlc-phases.md").read_text()
    phases = sorted(set(re.findall(r"\bPHASE\s+(S\d{2})\b", phases_text)))
    if not phases:
        g.fail("no PHASE S## definitions found in loki-sdlc-phases.md")
        return
    g.ok(f"phases defined: {', '.join(phases)}")
    for gate in REQUIRED_GATES:
        if gate not in phases:
            g.fail(f"required human-approval gate phase {gate} not defined")
    # Day-0 / Day-2 phases are added by Track A — report status without failing.
    for extra in ["S00", "S11", "S12", "S13"]:
        if extra not in phases:
            g.warn(f"lifecycle phase {extra} not yet defined (Track A1 — Day-0/Day-2 extension)")


def check_skill_shape(g: Graph) -> None:
    """Soft check: skills should carry the canonical sections."""
    print(f"\n{BLUE}=== Skill shape (canonical sections) ==={NC}")
    required = ["## Goal", "## Steps", "## Constraints", "## Output Format"]
    missing_any = 0
    for skill in (AGENTS_DIR / "skills").glob("**/*.skill.md"):
        text = skill.read_text()
        gaps = [s for s in required if s not in text]
        if gaps:
            missing_any += 1
            g.warn(f"{skill.relative_to(AGENTS_DIR)} missing section(s): {', '.join(gaps)}")
    if missing_any == 0:
        g.ok("all skills carry the canonical Goal/Steps/Constraints/Output sections")


def main() -> None:
    print(f"{YELLOW}Validating GABBE methodology graph (flows / personas / memory / index)...{NC}")
    g = Graph()
    check_asset_references(g)
    check_skill_index_bijection(g)
    check_persona_index_bijection(g)
    check_memory_state_model(g)
    check_lifecycle_dag(g)
    check_skill_shape(g)

    print(f"\n{BLUE}=== Methodology Graph Summary ==={NC}")
    print(f"  warnings: {len(g.warnings)}")
    if g.errors:
        print(f"{RED}{len(g.errors)} methodology-graph errors:{NC}")
        for e in g.errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"{GREEN}Methodology graph is coherent (flows, personas, memory, indexes).{NC}")
    sys.exit(0)


if __name__ == "__main__":
    main()

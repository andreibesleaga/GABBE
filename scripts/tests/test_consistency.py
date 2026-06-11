# SPDX-License-Identifier: Apache-2.0
"""Cross-file consistency gate — turns 'drift' into a thing CI catches.

Every defect the structural audits found was the same failure: a fact stated in
N places that drifted (gate counts, broken refs, malformed fences, redundant
fields). These invariants assert the kit stays internally consistent so the
agent never reads two authoritative-looking instructions that disagree.
"""

import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AG = ROOT / "agents"


def _md_files(*roots):
    out = []
    for r in roots:
        out += [Path(p) for p in glob.glob(str(r / "**" / "*.md"), recursive=True)]
    return out


def test_code_fences_are_balanced():
    """No unclosed/doubled code fences (the bug class fixed in AGENTS.md/QUICK_GUIDE)."""
    bad = []
    for f in _md_files(AG, ROOT / "docs") + [ROOT / "README.md"]:
        n = sum(1 for ln in f.read_text(encoding="utf-8").splitlines() if ln.startswith("```"))
        if n % 2 != 0:
            bad.append(f"{f.relative_to(ROOT)} (odd fence count {n})")
    assert not bad, f"Unbalanced markdown code fences: {bad}"


def test_when_to_use_field_removed():
    """O1: the redundant `when_to_use` frontmatter field stays gone."""
    bad = [
        f
        for f in glob.glob(str(AG / "skills" / "**" / "*.skill.md"), recursive=True)
        if re.search(r"^when_to_use:", Path(f).read_text(encoding="utf-8"), re.M)
    ]
    assert not bad, f"`when_to_use` reintroduced (redundant with triggers): {bad[:5]}"


def test_no_known_broken_path_patterns():
    """Locks in the structural fixes: no loki/RARV path, no '10-gate' mislabel."""
    bad = []
    for f in _md_files(AG):
        t = f.read_text(encoding="utf-8")
        if "loki/RARV_CYCLE" in t:
            bad.append(f"{f.relative_to(ROOT)}: stale 'loki/RARV_CYCLE.md' ref")
        if "10-gate SDLC" in t:
            bad.append(f"{f.relative_to(ROOT)}: '10-gate SDLC' (should be '10-phase SDLC')")
    assert not bad, f"Known drift patterns reappeared: {bad}"


def test_referenced_personas_exist():
    """Every persona named in loki-mode resolves (no hallucinated targets)."""
    loki = (AG / "skills" / "brain" / "loki-mode.skill.md").read_text(encoding="utf-8")
    existing = {p.stem for p in (AG / "personas").glob("*.md")}
    referenced = set(re.findall(r"\b((?:prod|orch|eng|ops|biz|ui)-[a-z]+(?:-[a-z]+)*)\b", loki))
    # eng-god-mode is the intentional hallucination example in the security guard.
    missing = {r for r in referenced if r not in existing and r != "eng-god-mode"}
    assert not missing, f"loki-mode references non-existent personas: {sorted(missing)}"


def test_referenced_guide_and_template_paths_resolve():
    """Template/guide paths referenced in AGENTS.md + loki-mode exist on disk."""
    bad = []
    for rel in ("AGENTS.md", "skills/brain/loki-mode.skill.md"):
        t = (AG / rel).read_text(encoding="utf-8")
        for m in re.findall(r"\b((?:templates|guides)/[a-z0-9/_-]+\.(?:md|json))\b", t):
            if not (AG / m).exists():
                bad.append(f"{rel} -> agents/{m} (missing)")
    assert not bad, f"Dangling guide/template references: {bad}"


def test_loki_gate_label_not_contradictory():
    """loki S06 must not label '7-Gate' over a 9-item list (the gate-count drift)."""
    t = (AG / "skills" / "brain" / "loki-mode.skill.md").read_text(encoding="utf-8")
    assert "7-Gate Quality Check" not in t, "loki S06 still labels '7-Gate' over a 9-item list"

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
        # lstrip() so indented fences (inside list items) are counted too, not just col-0.
        n = sum(
            1 for ln in f.read_text(encoding="utf-8").splitlines() if ln.lstrip().startswith("```")
        )
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
        for m in re.findall(r"\b((?:templates|guides)/[A-Za-z0-9/_-]+\.(?:md|json))\b", t):
            if not (AG / m).exists():
                bad.append(f"{rel} -> agents/{m} (missing)")
    assert not bad, f"Dangling guide/template references: {bad}"


def test_loki_gate_label_not_contradictory():
    """loki S06 must not label '7-Gate' over a 9-item list (the gate-count drift)."""
    t = (AG / "skills" / "brain" / "loki-mode.skill.md").read_text(encoding="utf-8")
    assert "7-Gate Quality Check" not in t, "loki S06 still labels '7-Gate' over a 9-item list"


def test_no_dangling_concrete_path_refs():
    """Every concrete skills/guides/templates path mentioned in any agents/ markdown
    resolves on disk. Catches in-text dangling refs that validate_links (markdown
    links only) misses — the class behind the wrong-directory/old-path drift."""
    # Match both kit-root-relative (`skills/x.skill.md`) and repo-relative
    # (`agents/skills/x.skill.md`) forms explicitly. The optional `agents/` prefix is
    # stripped before resolving against AG, so a ref never mis-resolves to
    # `agents/agents/...` and `agents/`-prefixed refs are checked rather than slipping
    # through on the bare-suffix coincidence.
    pat = re.compile(
        r"\b((?:agents/)?(?:skills|guides|templates)/[A-Za-z0-9][A-Za-z0-9/_.\-]*\.(?:skill\.md|md|json|yaml))\b"
    )
    bad = set()
    for f in AG.rglob("*.md"):
        for m in pat.findall(f.read_text(encoding="utf-8")):
            if "*" in m or "PLACEHOLDER" in m or "<" in m:
                continue
            rel = m[len("agents/") :] if m.startswith("agents/") else m
            if not (AG / rel).exists():
                bad.add(f"{m}  <- {f.relative_to(ROOT)}")
    assert not bad, f"Dangling concrete path references: {sorted(bad)}"


def test_guides_index_count_matches_filesystem():
    """The guides index 'Total Guides: N' must match the actual guide file count
    (this number drifted 72->73 when the loki phase guide was added)."""
    idx = (AG / "guides" / "00-index.md").read_text(encoding="utf-8")
    m = re.search(r"Total Guides\*\*:\s*(\d+)", idx)
    assert m, "guides 00-index.md missing a 'Total Guides: N' line"
    stated = int(m.group(1))
    actual = sum(1 for _ in (AG / "guides").rglob("*.md") if _.name != "00-index.md")
    assert stated == actual, f"guides index says {stated} but {actual} guide files exist"


def test_documented_env_vars_exist_in_source():
    """Every GABBE_* env var documented in a doc table row must be read somewhere in
    the Python source. Catches the doc-rot class where a documented variable (e.g.
    GABBE_MAX_RETRIES_PER_TOOL) is deleted from config.py but its doc rows remain —
    the var silently becomes a no-op for users who set it."""
    doc_files = [
        ROOT / "README.md",
        ROOT / "docs" / "QUICK_GUIDE.md",
        ROOT / "docs" / "CLI_REFERENCE.md",
        ROOT / "docs" / "PLATFORM_CONTROLS.md",
    ]
    documented = set()
    for f in doc_files:
        for ln in f.read_text(encoding="utf-8").splitlines():
            # only table rows — prose may name hypothetical/example vars
            if ln.lstrip().startswith("|"):
                documented |= set(re.findall(r"`(GABBE_[A-Z0-9_]+)`", ln))
    source = ""
    for py in list((ROOT / "gabbe").glob("*.py")) + [ROOT / "scripts" / "init.py"]:
        source += py.read_text(encoding="utf-8")
    missing = sorted(v for v in documented if v not in source)
    assert not missing, f"Env vars documented in tables but absent from source: {missing}"

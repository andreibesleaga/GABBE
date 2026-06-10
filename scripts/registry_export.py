#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""registry_export.py — package GABBE's skills as a standards-conformant bundle
for publishing to universal SKILL.md registries (Agent Garden / google-skills,
skills.sh, Agensi, agent-skills-hub, VoltAgent/awesome-agent-skills, ...).

GABBE skills already conform to the agentskills.io SKILL.md open standard, so
this just emits the canonical <slug>/SKILL.md tree + a manifest + an optional
A2A-style agent card describing the skills as capabilities. The maintainer holds
the actual publish credentials; this produces the publish-ready artifact.

Usage:
    python scripts/registry_export.py [--out DIR] [--kit-root DIR]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

KIT_ROOT_DEFAULT = Path(__file__).resolve().parent.parent


def _load_emitter(kit_root):
    """Reuse the canonical per-skill SKILL.md emitter from compile_skills.py."""
    sys.path.insert(0, str(kit_root / "agents" / "scripts"))
    import compile_skills  # noqa: E402

    return compile_skills


def export(kit_root: Path, out_dir: Path) -> dict:
    skills_src = kit_root / "agents" / "skills"
    if not skills_src.exists():
        raise SystemExit(f"skills dir not found: {skills_src}")

    compile_skills = _load_emitter(kit_root)
    skills_out = out_dir / "skills"
    skills_out.mkdir(parents=True, exist_ok=True)

    # Emit the agentskills.io-standard <slug>/SKILL.md tree (the same bytes every
    # GABBE-supported agent already consumes — zero new authoring).
    compile_skills.setup_skills_for_platform("Universal", skills_src, skills_out, kit_root)

    # Build a registry manifest: per-skill slug + description + sha256.
    entries = []
    for skill_md in sorted(skills_out.rglob("SKILL.md")):
        slug = skill_md.parent.name
        data = skill_md.read_bytes()
        meta, _ = compile_skills.ensure_yaml_frontmatter(skill_md.read_text(), skill_md.name)
        entries.append(
            {
                "slug": slug,
                "description": meta.get("description", ""),
                "sha256": hashlib.sha256(data).hexdigest(),
                "path": f"skills/{slug}/SKILL.md",
            }
        )

    version = _kit_version(kit_root)
    manifest = {
        "name": "gabbe-skills",
        "version": version,
        "standard": "agentskills.io",
        "count": len(entries),
        "skills": entries,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    # A2A-style agent card (skills-as-capabilities) for federated discovery.
    card = {
        "name": "GABBE",
        "description": "Generative Architectural Brain Base Engine — agentic kit skills.",
        "version": version,
        "capabilities": [{"id": e["slug"], "description": e["description"]} for e in entries],
    }
    (out_dir / "agent-card.json").write_text(json.dumps(card, indent=2) + "\n")
    return manifest


def _kit_version(kit_root: Path) -> str:
    const = kit_root / "agents" / "CONSTITUTION.md"
    if const.exists():
        for line in const.read_text().splitlines():
            if "GABBE Kit version:" in line:
                return line.split("GABBE Kit version:")[1].strip().rstrip("*").strip() or "0.0.0"
    return "0.0.0"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="dist/registry", help="output bundle dir")
    ap.add_argument("--kit-root", default=str(KIT_ROOT_DEFAULT), help="repo root")
    args = ap.parse_args()

    kit_root = Path(args.kit_root).resolve()
    out_dir = Path(args.out).resolve()
    manifest = export(kit_root, out_dir)

    print(f"Exported {manifest['count']} skills (agentskills.io standard) -> {out_dir}")
    print(f"  manifest:   {out_dir / 'manifest.json'}")
    print(f"  agent-card: {out_dir / 'agent-card.json'}")
    print("Publish (maintainer credentials required), e.g.:")
    print("  - github.com/google/skills-style repo / Agent Garden")
    print("  - skills.sh (Vercel)  - Agensi  - agent-skills-hub  - VoltAgent/awesome-agent-skills")


if __name__ == "__main__":
    main()

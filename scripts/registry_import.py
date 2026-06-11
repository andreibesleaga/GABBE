#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""registry_import.py — draw external skills from a universal SKILL.md registry
into GABBE, with mandatory validation + a basic security scan before acceptance.

Imported skills are TREATED AS UNTRUSTED supply-chain input: every candidate
must pass frontmatter validation (real YAML), a safe-slug / path-traversal check,
and an egress/secret/executable-payload scan. Skills land NAMESPACED under
agents/skills/<namespace>/ and are never auto-trusted — review before use.

Usage:
    python scripts/registry_import.py <source> [--namespace ext] [--apply] [--kit-root DIR]
      <source> = a local path (file/dir/.tar.gz) or an http(s) URL to a SKILL.md / bundle.
    Without --apply it is a dry run (validate + report only).
"""

import argparse
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

KIT_ROOT_DEFAULT = Path(__file__).resolve().parent.parent

# Heuristic red flags for a basic egress/secret/executable-payload scan. This is
# a safety net, not a sandbox — imported skills still require human review.
_DANGER_PATTERNS = [
    (re.compile(r"\bcurl\s+[^|]*\|\s*(sh|bash)\b"), "pipe-to-shell"),
    (re.compile(r"\b(eval|exec)\s*\("), "dynamic-exec"),
    (re.compile(r"https?://[^\s)]+\?[^\s)]*=(?:\$|%)"), "templated-exfil-url"),
    (
        re.compile(
            r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9/_+\-]{12,}"
        ),
        "embedded-secret",
    ),
    (re.compile(r"(?i)base64\s+-d|atob\(|b64decode"), "obfuscated-payload"),
]


def _load_helpers(kit_root):
    sys.path.insert(0, str(kit_root / "agents" / "scripts"))
    import compile_skills  # noqa: E402
    import validate_skills  # noqa: E402

    return compile_skills, validate_skills


def _fetch(source: str, stage: Path) -> Path:
    """Resolve <source> (URL or path) into a staging dir; return the staging root."""
    if source.startswith(("http://", "https://")):
        dest = stage / Path(source.split("?")[0]).name
        # nosec: deliberate, user-supplied registry URL; content is validated below.
        urllib.request.urlretrieve(source, dest)  # noqa: S310
        src = dest
    else:
        src = Path(source)
        if not src.exists():
            raise SystemExit(f"source not found: {source}")
    if str(src).endswith((".tar.gz", ".tgz")):
        with tarfile.open(src) as tf:
            _safe_extract(tf, stage)
        return stage
    if src.is_dir():
        shutil.copytree(src, stage / src.name, dirs_exist_ok=True)
        return stage / src.name
    # single file
    target = stage / src.name
    shutil.copy2(src, target)
    return stage


def _safe_extract(tf: tarfile.TarFile, dest: Path):
    """Extract a tarball, refusing any member that escapes dest or is a link.

    Defends against path traversal (absolute paths / ``..``) AND symlink/hardlink
    members, which can otherwise redirect a write outside the staging dir during
    extraction. The containment test uses real path-ancestry (a plain string
    prefix would wrongly accept ``/tmp/xx`` as inside ``/tmp/x``).
    """
    dest = dest.resolve()
    for member in tf.getmembers():
        if member.issym() or member.islnk():
            raise SystemExit(f"refusing link member (symlink/hardlink): {member.name}")
        target = (dest / member.name).resolve()
        if target != dest and dest not in target.parents:
            raise SystemExit(f"refusing path-traversal member: {member.name}")
    tf.extractall(dest)  # noqa: S202 - members validated above (no links, contained paths)


def _scan(text: str):
    return [label for pat, label in _DANGER_PATTERNS if pat.search(text)]


def validate_candidate(path: Path, compile_skills, validate_skills):
    """Return (ok, slug, reason). Rejects on frontmatter/slug/security failure."""
    text = path.read_text(errors="replace")
    ok, msg = validate_skills.validate_frontmatter(path)
    if not ok:
        return False, None, f"frontmatter: {msg}"
    meta, _ = compile_skills.ensure_yaml_frontmatter(text, path.name)
    slug = compile_skills.safe_slug(meta.get("name", path.stem))
    if not slug or slug in (".", ".."):
        return False, None, "unsafe slug"
    flags = _scan(text)
    if flags:
        return False, slug, f"security: {', '.join(flags)}"
    return True, slug, "ok"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="local path / .tar.gz / http(s) URL")
    ap.add_argument("--namespace", default="ext", help="land under agents/skills/<namespace>/")
    ap.add_argument("--apply", action="store_true", help="actually write (default: dry run)")
    ap.add_argument("--kit-root", default=str(KIT_ROOT_DEFAULT))
    args = ap.parse_args()

    kit_root = Path(args.kit_root).resolve()
    compile_skills, validate_skills = _load_helpers(kit_root)
    ns_dir = kit_root / "agents" / "skills" / re.sub(r"[^a-z0-9_-]+", "-", args.namespace.lower())

    with tempfile.TemporaryDirectory(prefix="gabbe-import-") as tmp:
        root = _fetch(args.source, Path(tmp))
        candidates = sorted(set(root.rglob("*.skill.md")) | set(root.rglob("SKILL.md")))
        if not candidates:
            print("No SKILL.md / *.skill.md found in source.")
            return

        accepted, rejected = [], []
        for c in candidates:
            ok, slug, reason = validate_candidate(c, compile_skills, validate_skills)
            (accepted if ok else rejected).append((c, slug, reason))

        print(
            f"Candidates: {len(candidates)}  accepted: {len(accepted)}  rejected: {len(rejected)}"
        )
        for c, slug, reason in rejected:
            print(f"  [REJECT] {c.name}: {reason}")
        for c, slug, reason in accepted:
            print(f"  [OK]     {c.name} -> {args.namespace}/{slug}.skill.md")

        if not args.apply:
            print(
                "\nDry run. Re-run with --apply to import accepted skills (namespaced, for review)."
            )
            return

        ns_dir.mkdir(parents=True, exist_ok=True)
        for c, slug, _ in accepted:
            (ns_dir / f"{slug}.skill.md").write_text(c.read_text(errors="replace"))
        print(
            f"\nImported {len(accepted)} skills -> {ns_dir} (NAMESPACED, untrusted — review before use)."
        )


if __name__ == "__main__":
    main()

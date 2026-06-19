#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Gate 4 harness: capture the byte-level output of scripts/init.py per platform.

Runs the setup wizard non-interactively (scripted answers) inside a temp
project directory, once per AI platform, and records a manifest of every
emitted artifact (sha256 + size, symlinks recorded by normalized target)
plus full copies of key generated files.

The manifest makes later byte-for-byte regression comparison cheap without
committing megabytes of compiled output.

Usage:
    python scripts/gates/capture_emitter_baseline.py <output_dir>
"""

import gzip
import hashlib
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent.parent

# Platform name (vault dir) -> agents multiselect answer in init.py
PLATFORMS = {
    "claude": ["Claude Code"],
    "cursor": ["Cursor"],
    "copilot": ["GitHub Copilot"],
    "gemini": ["Gemini / Antigravity"],
    "codex": ["OpenAI / Codex"],
    "antigravity": ["Antigravity"],
    "opencode": ["OpenCode"],
}


def load_init_module():
    sys.path.insert(0, str(KIT_ROOT / "scripts"))
    import importlib

    import init as init_module

    importlib.reload(init_module)
    return init_module


def scripted_answers(platform_agents):
    """Answers for the wizard, in the exact order main() asks them."""
    return {
        "select_index": iter(
            [
                0,  # Install Location -> Local
                0,  # Team Size -> Solo
            ]
        ),
        "select": iter(
            [
                "Greenfield (New)",  # Project Type
                "Python",  # Primary Language
            ]
        ),
        "ask": iter(
            [
                "golden-project",  # Project Name
                "Golden baseline project",  # Description
                "FastAPI",  # Primary Framework
                "n",  # Dynamic Agent Setup
                "n",  # Agent Analytics
                "n",  # Self-Evolving Capabilities
                "n",  # GABBE CLI platform controls
            ]
        ),
        "ask_multiselect": iter(
            [
                ["SQLite"],  # Databases
                [],  # Infrastructure / Cloud
                platform_agents,  # Which AI Agents
            ]
        ),
    }


def run_wizard(init_module, project_dir, platform_agents):
    answers = scripted_answers(platform_agents)
    init_module.clear_screen = lambda: None
    init_module.ask = lambda q, default=None: next(answers["ask"])
    init_module.select_index = lambda q, opts: next(answers["select_index"])
    init_module.select = lambda q, opts: next(answers["select"])
    init_module.ask_multiselect = lambda q, opts: next(answers["ask_multiselect"])
    init_module.PROJECT_ROOT = Path(project_dir)

    cwd = os.getcwd()
    os.chdir(project_dir)
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            init_module.main()
        return buf.getvalue()
    finally:
        os.chdir(cwd)


def normalize(path_str, project_dir):
    return path_str.replace(str(project_dir), "<PROJECT_ROOT>").replace(str(KIT_ROOT), "<KIT>")


# agents/memory/ is gitignored per-user runtime state, so its contents differ
# between a developer checkout and a clean CI clone — never manifest it.
# .gabbe/ is the install manifest (records installer_version + per-run hashes):
# it is install bookkeeping, not an emitted artifact, and would otherwise couple
# the golden vault to the package version. Never manifest it.
_MANIFEST_EXCLUDE_PREFIXES = ("agents/memory", ".gabbe")


def build_manifest(project_dir):
    manifest = {}
    for root, dirs, files in os.walk(project_dir):
        # Bytecode caches are non-deterministic build cruft, not part of the
        # emitted contract — never manifest them.
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        rel_root = os.path.relpath(root, project_dir).replace(os.sep, "/")
        if rel_root != "." and any(
            rel_root == p or rel_root.startswith(p + "/") for p in _MANIFEST_EXCLUDE_PREFIXES
        ):
            continue
        # The agents/ kit copy is manifested but its 400+ source files are
        # summarized by hash only, like everything else.
        for name in sorted(files):
            if name.endswith(".pyc"):
                continue
            p = Path(root) / name
            rel = str(p.relative_to(project_dir))
            if p.is_symlink():
                manifest[rel] = {
                    "type": "symlink",
                    "target": normalize(os.readlink(p), project_dir),
                }
            else:
                data = p.read_bytes()
                manifest[rel] = {
                    "type": "file",
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "size": len(data),
                }
        for name in sorted(dirs):
            p = Path(root) / name
            if p.is_symlink():
                rel = str(p.relative_to(project_dir))
                manifest[rel] = {
                    "type": "symlink-dir",
                    "target": normalize(os.readlink(p), project_dir),
                }
    return manifest


def load_manifest(platform_dir):
    """Read a (gzipped) golden manifest. Falls back to plain JSON if present."""
    gz = Path(platform_dir) / "manifest.json.gz"
    if gz.exists():
        return json.loads(gzip.decompress(gz.read_bytes()).decode("utf-8"))
    return json.loads((Path(platform_dir) / "manifest.json").read_text())


def capture(platform_key, out_root):
    out_dir = out_root / platform_key
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"gabbe-golden-{platform_key}-") as tmp:
        project_dir = Path(tmp) / "project"
        project_dir.mkdir()
        init_module = load_init_module()
        run_wizard(init_module, project_dir, PLATFORMS[platform_key])
        manifest = build_manifest(project_dir)

    # Store the manifest gzipped (deterministic, mtime=0) so the large
    # per-artifact baseline does not bloat the reviewable git diff. The test
    # and gate runner read it via load_manifest(). No human-facing key_files or
    # transcripts are committed — regenerate locally for inspection if needed.
    payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (out_dir / "manifest.json.gz").write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
    print(f"[ok] {platform_key}: {len(manifest)} artifacts manifested -> {out_dir}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    out_root = Path(sys.argv[1]).resolve()
    for platform_key in PLATFORMS:
        capture(platform_key, out_root)


if __name__ == "__main__":
    main()

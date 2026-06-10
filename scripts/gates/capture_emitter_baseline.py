#!/usr/bin/env python3
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
import hashlib
import io
import json
import os
import shutil
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
}

# Key generated files copied verbatim into the vault (when present)
KEY_FILES = [
    "agents/AGENTS.md",
    "SETUP_MISSION.md",
    ".gemini/settings.json",
    ".cursorrules",
]


def load_init_module():
    sys.path.insert(0, str(KIT_ROOT / "scripts"))
    import importlib
    import init as init_module
    importlib.reload(init_module)
    return init_module


def scripted_answers(platform_agents):
    """Answers for the wizard, in the exact order main() asks them."""
    return {
        "select_index": iter([
            0,  # Install Location -> Local
            0,  # Team Size -> Solo
        ]),
        "select": iter([
            "Greenfield (New)",   # Project Type
            "Python",             # Primary Language
        ]),
        "ask": iter([
            "golden-project",         # Project Name
            "Golden baseline project",  # Description
            "FastAPI",                # Primary Framework
            "n",                      # Dynamic Agent Setup
            "n",                      # Agent Analytics
            "n",                      # Self-Evolving Capabilities
            "n",                      # GABBE CLI platform controls
        ]),
        "ask_multiselect": iter([
            ["SQLite"],          # Databases
            [],                  # Infrastructure / Cloud
            platform_agents,     # Which AI Agents
        ]),
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
    return (
        path_str.replace(str(project_dir), "<PROJECT_ROOT>")
        .replace(str(KIT_ROOT), "<KIT>")
    )


def build_manifest(project_dir):
    manifest = {}
    for root, dirs, files in os.walk(project_dir):
        dirs.sort()
        # The agents/ kit copy is manifested but its 400+ source files are
        # summarized by hash only, like everything else.
        for name in sorted(files):
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


def capture(platform_key, out_root):
    out_dir = out_root / platform_key
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"gabbe-golden-{platform_key}-") as tmp:
        project_dir = Path(tmp) / "project"
        project_dir.mkdir()
        init_module = load_init_module()
        transcript = run_wizard(init_module, project_dir, PLATFORMS[platform_key])

        manifest = build_manifest(project_dir)
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "transcript.txt").write_text(
            normalize(transcript, project_dir)
        )
        for key_file in KEY_FILES:
            src = project_dir / key_file
            if src.exists() and not src.is_symlink():
                dest = out_dir / "key_files" / key_file
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        # Full copies of a stable sample of compiled skill artifacts
        samples = []
        for pattern in (".cursor/rules/*.mdc", ".github/skills/*/config.json"):
            samples.extend(sorted(project_dir.glob(pattern))[:3])
        for src in samples:
            dest = out_dir / "key_files" / src.relative_to(project_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
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

# SPDX-License-Identifier: Apache-2.0
"""Environment + install doctor (Track E8).

`gabbe doctor` is a single, read-only command that auto-detects the OS/arch, the
available runtimes, and which agent clients are present, then prints a PASS/WARN
report. It powers the one-command-install verification: the multi-OS CI
`install-matrix` and post-publish `release-verify` jobs run it after installing
the published package to confirm the kit landed and the environment is sane.

Detection is best-effort and fail-soft: unknown or absent agents are simply not
listed — never an error.
"""

from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

# Agent client → fingerprint paths (relative to the target). Presence of ANY
# listed path marks the client as detected. Mirrors the emit targets in
# docs/SCHEMA.md plus each tool's conventional config location.
AGENT_FINGERPRINTS: dict[str, list[str]] = {
    "claude": [".claude", ".claude/skills", "CLAUDE.md"],
    "cursor": [".cursor", ".cursor/rules", ".cursorrules"],
    "copilot": [".github/copilot-instructions.md", ".github/skills"],
    "gemini": [".gemini", ".gemini/settings.json", "GEMINI.md"],
    "codex": [".codex", ".codex/AGENTS.md"],
    "windsurf": [".windsurf", ".windsurfrules"],
    "cline": [".clinerules"],
    "aider": [".aider.conf.yml"],
    "zed": [".zed"],
    "antigravity": [".antigravity"],
    "opencode": [".opencode", "opencode.json"],
    "continue": [".continue"],
    "roo": [".roo", ".roomodes"],
    "kilo": [".kilocode"],
}

# Runtimes / package managers we probe for one-command install support.
RUNTIMES = ["python3", "pip", "pipx", "node", "npm", "npx", "git", "curl"]


def detect_os() -> dict[str, str]:
    sysname = platform.system().lower()  # 'linux' | 'darwin' | 'windows'
    os_name = {"darwin": "macos", "windows": "windows", "linux": "linux"}.get(sysname, sysname)
    return {
        "os": os_name,
        "arch": platform.machine().lower(),
        "python": platform.python_version(),
    }


def detect_runtimes() -> dict[str, bool]:
    return {name: shutil.which(name) is not None for name in RUNTIMES}


def detect_agents(root: Path | None = None) -> list[str]:
    """Return the sorted slugs of agent clients fingerprinted under root (cwd default)."""
    base = root or Path.cwd()
    found = []
    for slug, paths in AGENT_FINGERPRINTS.items():
        if any((base / p).exists() for p in paths):
            found.append(slug)
    return sorted(found)


def detect_scope(root: Path | None = None) -> str:
    """Best-effort install-scope guess from a present manifest, else 'project'."""
    base = root or Path.cwd()
    manifest = base / ".gabbe" / "manifest.json"
    if manifest.exists():
        return "installed"
    return "project"


def run_doctor(root: Path | None = None) -> int:
    """Print the environment + install report. Returns non-zero only on a hard fault."""
    base = root or Path.cwd()
    env = detect_os()
    runtimes = detect_runtimes()
    agents = detect_agents(base)

    print("GABBE doctor — environment & install report")
    print("=" * 48)
    print(f"  OS / arch     : {env['os']} / {env['arch']}")
    print(f"  Python        : {env['python']}")
    print(f"  Target        : {base}")
    print(f"  Install scope : {detect_scope(base)}")

    print("\n  Runtimes (one-command install support):")
    for name in RUNTIMES:
        mark = "PASS" if runtimes[name] else "----"
        print(f"    [{mark}] {name}")

    print("\n  Detected agent clients:")
    if agents:
        for a in agents:
            print(f"    [PASS] {a}")
    else:
        print("    (none detected in this target — install will set them up)")

    # Hard checks: the only fault that should fail the doctor is an unsupported
    # Python. Everything else is informational (PASS/WARN), never a hard error.
    ok = True
    print("\n  Checks:")
    py_ok = sys.version_info[:2] >= (3, 9)
    print(f"    [{'PASS' if py_ok else 'FAIL'}] Python >= 3.9")
    ok = ok and py_ok
    has_installer_runtime = any(runtimes[r] for r in ("npx", "pipx", "pip", "curl"))
    print(f"    [{'PASS' if has_installer_runtime else 'WARN'}] an install channel is available")

    _print_next_steps()

    print("=" * 48)
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


# Essential MCP servers to enable for full capability (every project).
ESSENTIAL_MCP = ["context7", "filesystem", "sequential-thinking", "github", "githits", "brave-search"]
# Useful servers that are installed/run locally (not a plain npx one-liner).
LOCAL_MCP = [
    "time-complexity (GitHub repo, build locally)",
    "semgrep (pip)",
    "google-genai-toolbox (binary)",
]


def _print_next_steps() -> None:
    """Post-install guidance: which MCP servers to enable and how, for a full env."""
    print("\n  Next steps — finish the environment (MCP servers):")
    print(f"    1. Enable the essential MCP servers: {', '.join(ESSENTIAL_MCP)}")
    print('       Edit agents/templates/core/MCP_CONFIG_TEMPLATE.json: set "_enabled": true')
    print("       and the listed env vars, then point your agent at that config.")
    print(f"    2. Optional local servers: {', '.join(LOCAL_MCP)}")
    print("    3. Full setup guide: docs/POST_INSTALL.md")
    print("       MCP catalog + SWEBOK v4 priority map: docs/MCP_CONFIGURATIONS.md")


if __name__ == "__main__":
    sys.exit(run_doctor())

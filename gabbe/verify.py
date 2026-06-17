# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from .config import GABBE_DIR, PROJECT_ROOT, REQUIRED_FILES, SUBPROCESS_TIMEOUT, Colors


def check_files() -> list[Path]:
    """Verify presence of critical files."""
    missing: list[Path] = []
    for f in REQUIRED_FILES:
        if not f.exists():
            missing.append(f)
    return missing


def parse_agents_config() -> dict[str, str]:
    """Extract commands from the '## Commands' section of AGENTS.md.

    This version uses a state machine approach to reliably find the key-value pairs
    within the target section, handling quotes and whitespace more gracefully.
    """
    config: dict[str, str] = {}
    agents_path = PROJECT_ROOT / "agents/AGENTS.md"

    if not agents_path.exists():
        return config

    content = agents_path.read_text()
    in_commands_section = False

    for line in content.splitlines():
        line = line.strip()

        # Enter the Commands section
        # We look for "##" followed by something containing "Commands"
        if line.startswith("##") and "commands" in line.lower():
            in_commands_section = True
            continue

        # Exit on the next major section heading
        if in_commands_section and line.startswith("## "):
            break

        if not in_commands_section:
            continue

        # Parse key: "value" or key: value
        if ":" in line:
            # Split only on the first colon
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()

            # Remove optional surrounding quotes
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1].strip()

            if key in ["test", "lint", "security_scan", "build"]:
                if val:
                    config[key] = val
                else:
                    print(
                        f"{Colors.WARNING}Warning: Empty command value for '{key}' in AGENTS.md{Colors.ENDC}"
                    )

    return config


def run_command(cmd: str, name: str) -> bool:
    """Run a shell command safely without shell=True."""
    if "[PLACEHOLDER" in cmd:
        print(
            f"  {Colors.FAIL}x {name} command is an unfilled placeholder: {cmd!r}\n"
            f"    Fill it in agents/AGENTS.md (or run: python scripts/fill_placeholders.py)"
            f"{Colors.ENDC}"
        )
        return False
    print(f"  Running {name}: {Colors.BLUE}{cmd}{Colors.ENDC}")
    try:
        args = shlex.split(cmd)
        result = subprocess.run(
            args, shell=False, check=False, cwd=PROJECT_ROOT, timeout=SUBPROCESS_TIMEOUT
        )
        if result.returncode == 0:
            print(f"  {Colors.GREEN}✓ {name} Passed{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.FAIL}x {name} Failed (Exit Code {result.returncode}){Colors.ENDC}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  {Colors.FAIL}x {name} Timed Out (>{SUBPROCESS_TIMEOUT}s){Colors.ENDC}")
        return False
    except Exception as e:
        print(f"  {Colors.FAIL}x Execution Error: {e}{Colors.ENDC}")
        return False


def run_verification() -> bool:
    """Run all integrity checks."""
    print(f"{Colors.HEADER}Running Integrity Checks...{Colors.ENDC}")
    all_passed = True

    # 1. File Existence
    missing = check_files()
    if missing:
        print(f"{Colors.FAIL}[FAIL] Missing critical files:{Colors.ENDC}")
        for m in missing:
            print(f"  - {m.relative_to(PROJECT_ROOT)}")
        all_passed = False
    else:
        print(f"{Colors.GREEN}[PASS] Critical files present.{Colors.ENDC}")

    # 2. Project State / DB
    if not (GABBE_DIR / "state.db").exists():
        print(f"{Colors.WARNING}[WARN] Database not initialized (Run 'gabbe init'){Colors.ENDC}")

    # 3. Dynamic Checks (Tests/Lint)
    config = parse_agents_config()

    if "test" in config and config["test"]:
        if not run_command(config["test"], "Tests"):
            all_passed = False
    else:
        print(
            f"  {Colors.YELLOW}No test command found in AGENTS.md [## Commands] section{Colors.ENDC}"
        )

    if "lint" in config and config["lint"]:
        if not run_command(config["lint"], "Linter"):
            all_passed = False

    if "security_scan" in config and config["security_scan"]:
        if not run_command(config["security_scan"], "Security Scan"):
            all_passed = False

    # Summary
    if all_passed:
        print(f"\n{Colors.GREEN}Verification PASSED.{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.FAIL}Verification FAILED.{Colors.ENDC}")
        return False


def run_chaos_checks() -> bool:
    """Fault-injection self-checks (Track B Phase 4 / `gabbe verify --chaos`).

    Injects faults into GABBE's own resilience mechanisms in-process and asserts
    each degrades safely — fail-closed tools, hard-stop caps, privacy routing, and
    graceful escalation under a DB fault. Read-only and side-effect-free (uses a
    mock DB connection for the escalation check). Returns True only if all pass.
    """
    import os
    import sqlite3
    from unittest.mock import MagicMock

    print(f"{Colors.HEADER}Running Chaos / Fault-Injection Self-Checks...{Colors.ENDC}")
    results: list[tuple[str, bool]] = []

    # 1. The MCP tool is fail-closed without an allowlist (no command reaches a shell).
    try:
        from .mcp_server import run_command_handler

        saved = {
            k: os.environ.pop(k, None) for k in ("GABBE_MCP_ALLOWED_COMMANDS", "GABBE_MCP_INSECURE")
        }
        try:
            blocked = run_command_handler("rm -rf /tmp/should-not-run")["returncode"] == 126
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v
        results.append(("MCP tool fail-closed without allowlist", blocked))
    except Exception as e:  # noqa: BLE001
        results.append((f"MCP fail-closed (errored: {e})", False))

    # 2. The hard stop caps a runaway loop.
    try:
        from .hardstop import HardStop, MaxIterationsExceeded

        hs = HardStop(max_iterations=2, max_depth=100, timeout_sec=60)
        fired = False
        try:
            for _ in range(50):
                hs.tick()
        except MaxIterationsExceeded:
            fired = True
        results.append(("Hard-stop caps a runaway loop", fired))
    except Exception as e:  # noqa: BLE001
        results.append((f"Hard-stop (errored: {e})", False))

    # 3. The privacy override holds (PII forces LOCAL).
    try:
        from .route import detect_pii

        results.append(("PII detection forces LOCAL routing", detect_pii("email user@example.com")))
    except Exception as e:  # noqa: BLE001
        results.append((f"PII routing (errored: {e})", False))

    # 4. Escalation degrades gracefully under an injected DB fault (silent mode).
    try:
        import gabbe.escalation as _esc

        from .escalation import EscalationHandler, EscalationTrigger

        bad = MagicMock()
        bad.cursor.side_effect = sqlite3.OperationalError("injected disk I/O error")
        prev_mode = _esc.GABBE_ESCALATION_MODE
        _esc.GABBE_ESCALATION_MODE = "silent"
        try:
            handler = EscalationHandler("chaos-selfcheck", db_conn=bad)
            graceful = (
                handler.escalate(EscalationTrigger.POLICY_VIOLATION, {"injected": True}).status
                == "rejected"
            )
        finally:
            _esc.GABBE_ESCALATION_MODE = prev_mode
        results.append(("Escalation handles DB fault gracefully", graceful))
    except Exception as e:  # noqa: BLE001
        results.append((f"Escalation resilience (errored: {e})", False))

    for name, ok in results:
        mark = f"{Colors.GREEN}✓ PASS" if ok else f"{Colors.FAIL}x FAIL"
        print(f"  {mark}{Colors.ENDC} {name}")

    all_ok = all(ok for _, ok in results)
    if all_ok:
        print(f"\n{Colors.GREEN}Chaos self-checks PASSED.{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}Chaos self-checks FAILED.{Colors.ENDC}")
    return all_ok

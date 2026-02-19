import os
import subprocess
import shlex
from pathlib import Path
from .config import PROJECT_ROOT, Colors, GABBE_DIR, REQUIRED_FILES

def check_files():
    """Verify presence of critical files."""
    missing = []
    for f in REQUIRED_FILES:
        if not f.exists():
            missing.append(f)
    return missing

def parse_agents_config():
    """Extract commands from the '## Commands' section of AGENTS.md.

    Only lines inside the '## Commands' section are parsed, guarding against
    accidental execution of arbitrary YAML/Markdown content elsewhere in the
    file.  Expected format inside that section::

        test: "pytest tests/"
        lint: "ruff check ."
    """
    config = {}
    agents_path = PROJECT_ROOT / ".agents/AGENTS.md"

    if not agents_path.exists():
        return config

    content = agents_path.read_text()
    in_commands_section = False

    for line in content.splitlines():
        # Enter the Commands section
        if line.strip().lower() == "## commands":
            in_commands_section = True
            continue

        # Exit on the next ## heading
        if in_commands_section and line.startswith("## "):
            break

        if not in_commands_section:
            continue

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip().strip('"').strip("'")

            if key in ["test", "lint", "security_scan", "build"]:
                if val:
                    config[key] = val
                else:
                    print(f"{Colors.WARNING}Warning: Empty command value for '{key}' in AGENTS.md{Colors.ENDC}")

    return config

def run_command(cmd, name):
    """Run a shell command safely without shell=True."""
    print(f"  Running {name}: {Colors.BLUE}{cmd}{Colors.ENDC}")
    try:
        args = shlex.split(cmd)
        result = subprocess.run(args, shell=False, check=False, cwd=PROJECT_ROOT)
        if result.returncode == 0:
            print(f"  {Colors.GREEN}✓ {name} Passed{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.FAIL}x {name} Failed (Exit Code {result.returncode}){Colors.ENDC}")
            return False
    except Exception as e:
        print(f"  {Colors.FAIL}x Execution Error: {e}{Colors.ENDC}")
        return False

def run_verification():
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
        print(f"  {Colors.YELLOW}No test command found in AGENTS.md [## Commands] section{Colors.ENDC}")

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

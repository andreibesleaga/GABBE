import os
import subprocess
import shlex
from pathlib import Path
from .config import PROJECT_ROOT, Colors, AGENTS_DIR, GABBE_DIR

REQUIRED_FILES = [
    PROJECT_ROOT / ".agents/AGENTS.md",
    PROJECT_ROOT / ".agents/CONSTITUTION.md",
    PROJECT_ROOT / "TASKS.md" 
]

def check_files():
    """Verify presence of critical files."""
    missing = []
    for f in REQUIRED_FILES:
        if not f.exists():
            missing.append(f)
    return missing

def parse_agents_config():
    """Extract commands from AGENTS.md."""
    config = {}
    agents_path = PROJECT_ROOT / ".agents/AGENTS.md"
    
    if not agents_path.exists():
        return config
        
    content = agents_path.read_text()
    for line in content.splitlines():
        # Look for keys like test: "cmd", lint: "cmd"
        # Simple parser for the specific format in AGENTS.md
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip().strip('"')
            
            if key in ["test", "lint", "security_scan", "build"]:
                config[key] = val
                
    return config

def run_command(cmd, name):
    """Run a shell command."""
    print(f"  Running {name}: {Colors.BLUE}{cmd}{Colors.ENDC}")
    try:
        # Use shell=True for complex commands (e.g. pipes), but be careful
        result = subprocess.run(cmd, shell=True, check=False, cwd=PROJECT_ROOT)
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
        print(f"{Colors.WARNING}[WARN] Database not initialized (Run 'gabbe db --init'){Colors.ENDC}")
    
    # 3. Dynamic Checks (Tests/Lint)
    config = parse_agents_config()
    
    if "test" in config and config["test"]:
        if not run_command(config["test"], "Tests"): all_passed = False
    else:
        print(f"  {Colors.YELLOW}No test command found in AGENTS.md{Colors.ENDC}")

    if "lint" in config and config["lint"]:
        if not run_command(config["lint"], "Linter"): all_passed = False

    if "security_scan" in config and config["security_scan"]:
        if not run_command(config["security_scan"], "Security Scan"): all_passed = False

    # Summary
    if all_passed:
        print(f"\n{Colors.GREEN}Verification PASSED.{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.FAIL}Verification FAILED.{Colors.ENDC}")
        return False

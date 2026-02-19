import os
from pathlib import Path
from .config import PROJECT_ROOT, Colors, AGENTS_DIR

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

def run_verification():
    """Run all integrity checks."""
    print(f"{Colors.HEADER}Running Integrity Checks...{Colors.ENDC}")
    
    # 1. File Existence
    missing = check_files()
    if missing:
        print(f"{Colors.FAIL}[FAIL] Missing critical files:{Colors.ENDC}")
        for m in missing:
            print(f"  - {m.relative_to(PROJECT_ROOT)}")
        # In strict mode, we might exit here
    else:
        print(f"{Colors.GREEN}[PASS] Critical files present.{Colors.ENDC}")

    # 2. Project State (Placeholder)
    # TODO: Check if current phase in DB matches reality?
    
    # 3. Linter/Tests (Placeholder)
    # TODO: Read AGENTS.md to find test_cmd and run it
    
    # Summary
    if missing:
        print(f"\n{Colors.FAIL}Verification FAILED.{Colors.ENDC}")
        return False
    else:
        print(f"\n{Colors.GREEN}Verification PASSED.{Colors.ENDC}")
        return True

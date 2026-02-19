#!/usr/bin/env python3
import sys
import os
import py_compile
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
AGENTS_DIR = PROJECT_ROOT / ".agents"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
NC = "\033[0m"

REQUIRED_FILES = [
    PROJECT_ROOT / "init.py",
    PROJECT_ROOT / "README.md",
    AGENTS_DIR / "AGENTS.md",
    AGENTS_DIR / "CONSTITUTION.md",
    AGENTS_DIR / "skills/00-index.md",
    AGENTS_DIR / "templates/00-index.md"
]

REQUIRED_DIRS = [
    AGENTS_DIR / "skills",
    AGENTS_DIR / "templates",
    AGENTS_DIR / "guides",
    AGENTS_DIR / "loki"
]

def check_exists(path):
    if not path.exists():
        print(f"{RED}[MISSING] {path.relative_to(PROJECT_ROOT)}{NC}")
        return False
    return True

def check_python_syntax(path):
    try:
        py_compile.compile(path, doraise=True)
        # print(f"{GREEN}[SYNTAX OK] {path.relative_to(PROJECT_ROOT)}{NC}")
        return True
    except py_compile.PyCompileError as e:
        print(f"{RED}[SYNTAX ERROR] {path.relative_to(PROJECT_ROOT)}: {e}{NC}")
        return False

def main():
    print(f"{BLUE}Validating GABBE Project Integrity...{NC}")
    errors = 0
    
    # 1. Check Essential Files
    print(f"\n{BLUE}1. Checking Essential Files...{NC}")
    for f in REQUIRED_FILES:
        if not check_exists(f): errors += 1
        
    for d in REQUIRED_DIRS:
        if not check_exists(d): errors += 1
        
    # 2. Check Python Syntax
    print(f"\n{BLUE}2. Checking Python Scripts...{NC}")
    python_files = list(PROJECT_ROOT.glob("*.py")) + list(AGENTS_DIR.rglob("*.py"))
    for py_file in python_files:
        if not check_python_syntax(py_file): errors += 1

    # 3. Check Templates (Basic Existence)
    print(f"\n{BLUE}3. Checking Template Directories...{NC}")
    template_cats = ["coding", "architecture", "ops", "security", "product", "core", "coordination", "brain"]
    for cat in template_cats:
        d = AGENTS_DIR / "templates" / cat
        if not check_exists(d): errors += 1

    print("-" * 40)
    if errors > 0:
        print(f"{RED}Found {errors} integrity errors.{NC}")
        sys.exit(1)
    else:
        print(f"{GREEN}Project integrity check passed!{NC}")
        sys.exit(0)

if __name__ == "__main__":
    main()

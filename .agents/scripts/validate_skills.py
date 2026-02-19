#!/usr/bin/env python3
import sys
from pathlib import Path

# Configuration
AGENTS_DIR = Path(__file__).parent.parent
SKILLS_DIR = AGENTS_DIR / "skills"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NC = "\033[0m"

def validate_frontmatter(file_path):
    content = file_path.read_text()
    if not content.startswith("---"):
        return False, "Missing YAML start (---)"
    
    end_yaml = content.find("---", 3)
    if end_yaml == -1:
        return False, "Missing YAML end (---)"
        
    yaml_block = content[3:end_yaml]
    lines = yaml_block.strip().split("\n")
    
    keys = {}
    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            keys[k.strip()] = v.strip()
            
    required = ["name", "description"]
    missing = [k for k in required if k not in keys]
    
    if missing:
        return False, f"Missing required keys: {missing}"
        
    return True, "OK"

def main():
    print(f"Validating skills in {SKILLS_DIR}...")
    errors = 0
    checked = 0
    
    for skill_file in SKILLS_DIR.rglob("*.skill.md"):
        checked += 1
        is_valid, msg = validate_frontmatter(skill_file)
        
        if not is_valid:
            print(f"{RED}[FAIL] {skill_file.name}: {msg}{NC}")
            errors += 1
        # else:
            # print(f"{GREEN}[OK] {skill_file.name}{NC}")
            
    print("-" * 40)
    if errors > 0:
        print(f"{RED}Found {errors} errors in {checked} skills.{NC}")
        sys.exit(1)
    else:
        print(f"{GREEN}All {checked} skills passed validation!{NC}")
        sys.exit(0)

if __name__ == "__main__":
    main()

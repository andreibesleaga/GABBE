#!/usr/bin/env python3
import sys
import os
import shutil
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

# Add project root and scripts dir to path so we can import init
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "scripts"))

import init

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NC = "\033[0m"

def test_tech_map_generation():
    print(f"\nTesting build_tech_map_from_skills...")
    # Point to the actual agents dir
    agents_dir = PROJECT_ROOT / "agents"
    tech_map = init.build_tech_map_from_skills(agents_dir)
    
    # Assertions
    if "python" in tech_map and "tdd-cycle" in tech_map["python"]["skills"]:
        print(f"{GREEN}[PASS] Python mapped to tdd-cycle{NC}")
    else:
        print(f"{RED}[FAIL] Python mapping issues: {tech_map.get('python')}{NC}")

    if "brain" in tech_map and "sequential-thinking" in tech_map["brain"]["skills"]:
         print(f"{GREEN}[PASS] Brain mapped to sequential-thinking{NC}")
    else:
         # sequential-thinking tag is 'brain', 'core', 'reasoning'
         # check if 'brain' key exists 
         print(f"{RED}[FAIL] Brain mapping issues.{NC}")
         
    # Check if we have entries
    print(f"Total keys in TECH_MAP: {len(tech_map)}")

def test_platform_setup():
    print(f"\nTesting setup_skills_for_platform...")
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        skills_src = PROJECT_ROOT / "agents" / "skills"
        
        # Test Claude (Symlinking)
        claude_target = temp_dir / "claude_skills"
        # init.setup_skills_for_platform doesn't handle symlinking logic for Claude, 
        # that's handled in main. But we can test "VS Code" or "Cursor" flows which modify files.
        
        # Test Cursor (Generation)
        cursor_target = temp_dir / "cursor_rules"
        init.setup_skills_for_platform("Cursor", skills_src, cursor_target)
        
        if cursor_target.exists() and list(cursor_target.glob("*.mdc")):
             print(f"{GREEN}[PASS] Cursor rules generated{NC}")
             # Check content of one
             mdc_files = list(cursor_target.glob("*.mdc"))
             content = mdc_files[0].read_text()
             if "globs: *" in content:
                 print(f"{GREEN}[PASS] Cursor globs inserted{NC}")
             else:
                 print(f"{RED}[FAIL] Cursor globs missing{NC}")
        else:
             print(f"{RED}[FAIL] Cursor rules not generated{NC}")

def test_symlink_fallback():
    print(f"\nTesting symlink fallback mechanism...")
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        source = temp_dir / "source"
        source.mkdir()
        (source / "file.txt").write_text("content")
        target = temp_dir / "target"
        
        # Mock os.symlink to raise OSError (simulate Windows non-admin)
        with patch("os.symlink", side_effect=OSError("Privilege not held")):
            # We need to import init inside patch context or patch where it's used
            # Since we imported init at top level, we patch 'os.symlink' globally if possible, 
            # but better to patch 'init.os.symlink' if that's how it's bound, or just 'os.symlink'.
            
            # Recalling create_symlink logic: it calls os.symlink
            init.create_symlink(source, target)
            
        if target.exists() and not target.is_symlink():
            print(f"{GREEN}[PASS] Fallback copy successful (Target exists and is NOT symlink){NC}")
        else:
            print(f"{RED}[FAIL] Fallback failed. Target exists: {target.exists()}, Is symlink: {target.is_symlink()}{NC}")

def main():
    test_tech_map_generation()
    test_platform_setup()
    test_symlink_fallback()

if __name__ == "__main__":
    main()

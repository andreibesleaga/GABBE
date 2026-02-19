#!/usr/bin/env python3
import sys
import re
import os
from pathlib import Path
from urllib.parse import unquote

PROJECT_ROOT = Path(__file__).parent.parent.parent

RED = "\033[0;31m"
GREEN = "\033[0;32m"
NC = "\033[0m"

# Regex to find [text](link)
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

def validate_link(file_path, link_target):
    # Ignore template placeholders like [field], [value]
    if link_target in ["value", "link", "url", "path", "field"]:
        return True
    # Ignore external links
    if link_target.startswith("http") or link_target.startswith("mailto:"):
        return True
        
    # Ignore anchors for now (unless we want to parse target file headers)
    link_path = link_target.split('#')[0]
    if not link_path:
        return True # Just an anchor in same file
        
    # Resolve path
    if link_path.startswith("/"):
        # Absolute path relative to project root? Usually MD links are relative.
        # Let's assume absolute paths in MD are rare or refer to system root (bad practice usually)
        # But if they mean project root:
        target_abs = PROJECT_ROOT / link_path.lstrip("/")
    else:
        target_abs = (file_path.parent / link_path).resolve()
        
    if not target_abs.exists():
        return False
    return True

def main():
    print(f"Scanning markdown links in {PROJECT_ROOT}...")
    errors = 0
    checked_files = 0
    checked_links = 0
    
    for md_file in PROJECT_ROOT.rglob("*.md"):
        # Skip node_modules or hidden dirs if any (besides .agents which we want to check)
        if "node_modules" in str(md_file): continue
        
        checked_files += 1
        content = md_file.read_text()
        
        # Remove code blocks to avoid false positives
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]*`', '', content)
        
        links = LINK_PATTERN.findall(content)
        
        for text, target in links:
            checked_links += 1
            if not validate_link(md_file, target):
                print(f"{RED}[FAIL] {md_file.relative_to(PROJECT_ROOT)}: Broken link '{target}'{NC}")
                errors += 1
                
    print("-" * 40)
    print(f"Checked {checked_files} files and {checked_links} links.")
    if errors > 0:
        print(f"{RED}Found {errors} broken links.{NC}")
        sys.exit(1)
    else:
        print(f"{GREEN}All links valid!{NC}")
        sys.exit(0)

if __name__ == "__main__":
    main()

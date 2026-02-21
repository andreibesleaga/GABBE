#!/usr/bin/env python3
import os
import sys
import shutil
import json
import argparse
from pathlib import Path

# Colors
GREEN = "\0.2.0;32m"
YELLOW = "\033[1;33m"
BLUE = "\0.2.0;34m"
RED = "\0.2.0;31m"
NC = "\0.2.0m"

def ensure_yaml_frontmatter(content, filename):
    """Ensures content has valid YAML frontmatter using PyYAML. Returns (frontmatter_dict, content)."""
    try:
        import yaml
        if content.startswith("---"):
            end_yaml = content.find("---", 3)
            if end_yaml != -1:
                yaml_text = content[3:end_yaml]
                data = yaml.safe_load(yaml_text)
                if isinstance(data, dict):
                    return data, content
    except ImportError:
        # Fallback to simple parser if PyYAML is missing
        if content.startswith("---"):
            end_yaml = content.find("---", 3)
            if end_yaml != -1:
                yaml_text = content[3:end_yaml]
                data = {}
                for line in yaml_text.strip().split('\n'):
                     if ':' in line:
                         k, v = line.split(':', 1)
                         data[k.strip()] = v.strip().strip('"\'')
                return data, content
    except Exception as e:
        # print(f"Warning: Failed to parse YAML for {filename}: {e}")
        pass
            
    # Default frontmatter if missing or failed
    name = filename.replace(".skill.md", "").replace(".md", "").replace(".mdc", "")
    frontmatter = f"""---
name: {name}
description: AI Skill for {name}
version: 1.0
author: GABBE-Kit
---
"""
    return {"name": name}, frontmatter + content

def create_symlink(source, target, project_root):
    """Creates a symlink from target to source, backing up if exists."""
    if target.is_symlink():
        target.unlink()
    elif target.exists():
        if target.is_dir():
             print(f"  {YELLOW}! Backing up existing directory {target.name} to {target.name}.bak{NC}")
             shutil.move(str(target), str(target.with_suffix(".bak")))
        else:
             print(f"  {YELLOW}! Backing up existing file {target.name} to {target.name}.bak{NC}")
             target.rename(target.with_suffix(".bak"))
    
    # Ensure parent dir exists
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate relative path if possible, else absolute
    try:
        if str(project_root) in str(source.absolute()):
             link_path = os.path.relpath(source, target.parent)
        else:
             link_path = source.absolute()

        os.symlink(link_path, target)
        # print(f"  {GREEN}✓ Linked {target.name} -> {link_path}{NC}")
    except OSError as e:
        # Fallback for Windows (no admin rights) or restricted environments
        print(f"  {YELLOW}! Symlink failed ({e}), falling back to copy...{NC}")
        try:
            if source.is_dir():
                if target.exists(): shutil.rmtree(target)
                shutil.copytree(source, target)
            else:
                if target.exists(): target.unlink()
                shutil.copy2(source, target)
            print(f"  {GREEN}✓ Copied {target.name} (Symlink fallback){NC}")
        except Exception as e2:
             print(f"  {RED}x Failed to copy {target}: {e2}{NC}")
    except Exception as e:
        print(f"  {RED}x Failed to link {target}: {e}{NC}")


def setup_skills_for_platform(platform, skills_src_dir, target_dir, project_root):
    """
    Distributes skills to platform-specific formats.
    """
    print(f"\n{BLUE}→ Setting up skills for {platform}...{NC}")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all .skill.md files recursively
    skill_files = list(skills_src_dir.rglob("*.skill.md"))
    
    count = 0
    for skill_file in skill_files:
        content = skill_file.read_text()
        meta, content_with_fm = ensure_yaml_frontmatter(content, skill_file.name)
        
        # Slugify name for files/commands (e.g. "Agent Interop" -> "agent-interop")
        raw_name = meta.get("name", skill_file.stem.replace(".skill", ""))
        skill_slug = raw_name.lower().replace(" ", "-")
        skill_desc = meta.get("description", f"Skill for {raw_name}")

        if platform == "Cursor":
            # Flatten structure: .cursor/rules/skill-slug.mdc
            dest_file = target_dir / f"{skill_slug}.mdc"
            
            # Cursor-specific frontmatter
            cursor_fm = f"""---
description: {skill_desc}
globs: *
alwaysApply: false
---
"""
            # Strip existing FM and prepend Cursor FM
            start_body = content_with_fm.find("---", 3) + 3
            body = content_with_fm[start_body:].strip()
            
            final_content = cursor_fm + "\n" + body
            dest_file.write_text(final_content)
            count += 1

        elif platform == "VS Code" or platform == "GitHub Copilot":
            # Structure: .github/skills/<skill-slug>/SKILL.md
            skill_folder = target_dir / skill_slug
            skill_folder.mkdir(exist_ok=True)
            
            # Symlink the README/SKILL.md
            dest_file = skill_folder / "SKILL.md"
            create_symlink(skill_file, dest_file, project_root)
            
            # Generate config.json for Copilot Extensions
            config = {
                "name": skill_slug,
                "description": skill_desc,
                "version": "1.0.0",
                "slashCommands": [
                    {
                        "name": skill_slug,
                        "description": skill_desc
                    }
                ]
            }
            (skill_folder / "config.json").write_text(json.dumps(config, indent=2))
            count += 1
            
        elif platform == "Claude Code":
            # Symlink directory is handled at top level, but if we need flattening:
            # Claude supports nested, so standard symlink of 'skills' dir is best.
            pass

    print(f"  {GREEN}✓ Processed {count} skills for {platform}{NC}")

def main():
    parser = argparse.ArgumentParser(description="Compile skills for specific platforms.")
    parser.add_argument("--platform", required=True, choices=["Cursor", "VS Code", "GitHub Copilot", "Claude Code", "All"], help="Target platform")
    parser.add_argument("--skills-dir", required=True, help="Source directory for skills (agents/skills)")
    parser.add_argument("--target-dir", required=True, help="Target directory for output")
    parser.add_argument("--project-root", required=True, help="Root of the project")

    args = parser.parse_args()

    skills_src = Path(args.skills_dir)
    target_dir = Path(args.target_dir)
    project_root = Path(args.project_root)

    if not skills_src.exists():
        print(f"{RED}Error: Skills directory not found at {skills_src}{NC}")
        sys.exit(1)

    if args.platform == "All":
        # Example logic for 'All' if needed, otherwise distinct calls are safer
        pass
    else:
        setup_skills_for_platform(args.platform, skills_src, target_dir, project_root)

if __name__ == "__main__":
    main()

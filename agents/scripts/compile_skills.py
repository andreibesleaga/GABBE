#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

# Colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"

# Schema generation embedded into every emitted artifact so downstream tooling
# can detect the emitted-format version. Consumers that ignore it are unaffected.
GABBE_SCHEMA_VERSION = 1


def safe_slug(raw_name, fallback="skill"):
    """Sanitize a skill name into a filesystem-safe slug.

    Prevents path traversal: the slug can never contain a path separator, '..',
    NUL, or escape its target directory. Falls back to `fallback` when the name
    sanitizes to empty.
    """
    slug = (raw_name or "").lower().strip()
    # Collapse any run of non [a-z0-9] into a single hyphen.
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if not slug or slug in (".", ".."):
        slug = re.sub(r"[^a-z0-9]+", "-", str(fallback).lower()).strip("-") or "skill"
    return slug


def inject_schema_version(content):
    """Insert `gabbe-schema-version: <N>` into a leading YAML frontmatter block.

    Idempotent: if the key is already present the content is returned unchanged.
    If there is no frontmatter, the content is returned unchanged.
    """
    if "gabbe-schema-version:" in content:
        return content
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            head = content[:3]
            block = content[3:end]
            tail = content[end:]
            return (
                head
                + block.rstrip("\n")
                + f"\ngabbe-schema-version: {GABBE_SCHEMA_VERSION}\n"
                + tail
            )
    return content


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
                for line in yaml_text.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        data[k.strip()] = v.strip().strip("\"'")
                return data, content
    except Exception:
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
        # Append ".bak" to the FULL name (with_suffix would drop a real
        # extension, e.g. config.json -> config.bak).
        backup = target.parent / (target.name + ".bak")
        if target.is_dir():
            print(f"  {YELLOW}! Backing up existing directory {target.name} to {backup.name}{NC}")
            shutil.move(str(target), str(backup))
        else:
            print(f"  {YELLOW}! Backing up existing file {target.name} to {backup.name}{NC}")
            target.rename(backup)

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
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(source, target)
            else:
                if target.exists():
                    target.unlink()
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

        # Slugify name for files/commands (e.g. "Agent Interop" -> "agent-interop").
        # safe_slug() prevents path traversal via a malicious frontmatter name.
        raw_name = meta.get("name", skill_file.stem.replace(".skill", ""))
        skill_slug = safe_slug(raw_name, fallback=skill_file.stem.replace(".skill", ""))
        skill_desc = meta.get("description", f"Skill for {raw_name}")

        if platform == "Cursor":
            # Flatten structure: .cursor/rules/<slug>.mdc
            dest_file = target_dir / f"{skill_slug}.mdc"

            # Cursor "Agent Requested" rule: description + alwaysApply:false and
            # NO globs, so Cursor selects the rule intelligently by description
            # rather than auto-attaching it to every file (per docs.cursor.com).
            cursor_fm = (
                "---\n"
                f"description: {skill_desc}\n"
                "alwaysApply: false\n"
                f"gabbe-schema-version: {GABBE_SCHEMA_VERSION}\n"
                "---\n"
            )
            # Strip existing FM and prepend Cursor FM
            start_body = content_with_fm.find("---", 3) + 3
            body = content_with_fm[start_body:].strip()

            final_content = cursor_fm + "\n" + body
            dest_file.write_text(final_content)
            count += 1

        elif platform in (
            "VS Code",
            "GitHub Copilot",
            "Claude Code",
            "Antigravity",
            "OpenCode",
            "Universal",
        ):
            # Agent-skills open standard (agentskills.io), shared by Copilot,
            # VS Code, Claude Code, Antigravity (.agents/skills), OpenCode, and the
            # universal .agents/skills tree: <target>/<slug>/SKILL.md as a real file
            # (not a symlink) with name+description frontmatter so the skill is
            # discoverable on every platform and portable across filesystems.
            skill_folder = target_dir / skill_slug
            skill_folder.mkdir(parents=True, exist_ok=True)
            (skill_folder / "SKILL.md").write_text(inject_schema_version(content_with_fm))

            if platform in ("VS Code", "GitHub Copilot"):
                # Optional GABBE metadata (ignored by Copilot; kept for tooling).
                config = {
                    "name": skill_slug,
                    "description": skill_desc,
                    "version": "1.0.0",
                    "gabbe-schema-version": GABBE_SCHEMA_VERSION,
                    "slashCommands": [{"name": skill_slug, "description": skill_desc}],
                }
                (skill_folder / "config.json").write_text(json.dumps(config, indent=2))
            count += 1

    print(f"  {GREEN}✓ Processed {count} skills for {platform}{NC}")


def main():
    parser = argparse.ArgumentParser(description="Compile skills for specific platforms.")
    parser.add_argument(
        "--platform",
        required=True,
        choices=[
            "Cursor",
            "VS Code",
            "GitHub Copilot",
            "Claude Code",
            "Antigravity",
            "OpenCode",
            "Universal",
            "All",
        ],
        help="Target platform",
    )
    parser.add_argument(
        "--skills-dir", required=True, help="Source directory for skills (agents/skills)"
    )
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

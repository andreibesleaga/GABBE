#!/usr/bin/env python3
import os
import sys
import shutil
import json
import datetime
from pathlib import Path

# --- Configuration ---
# KIT_SOURCE: Where the script and correct .agents folder currently live
KIT_SOURCE = Path(__file__).parent.absolute()
SOURCE_AGENTS_DIR = KIT_SOURCE / ".agents"

# PROJECT_ROOT: Where the user is running the script from (the project they want to configure)
PROJECT_ROOT = Path.cwd()

# Colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"

# --- Knowledge Base (Dynamic Discovery) ---

def build_tech_map_from_skills(agents_dir):
    """
    Scans all .skill.md files in agents_dir/skills and builds a TECH_MAP
    based on the 'tags' frontmatter field.
    """
    tech_map = {}
    skills_dir = agents_dir / "skills"
    
    if not skills_dir.exists():
        return tech_map

    for skill_file in skills_dir.rglob("*.skill.md"):
        try:
            content = skill_file.read_text()
            meta, _ = ensure_yaml_frontmatter(content, skill_file.name)
            
            # Get tags (list of strings)
            tags = meta.get("tags", [])
            # Also support 'tech' or 'stack' as aliases
            if not tags: tags = meta.get("tech", [])
            if not tags: tags = meta.get("stack", [])
            
            # Normalize to list
            if isinstance(tags, str):
                # Remove brackets first if present
                tags = tags.strip("[]")
                tags = [t.strip() for t in tags.split(",")]
            
            skill_name = meta.get("name", skill_file.stem.replace(".skill", ""))
            
            for tag in tags:
                tag = tag.lower().strip()
                if tag not in tech_map:
                    tech_map[tag] = {"skills": [], "guides": [], "templates": []}
                
                if skill_name not in tech_map[tag]["skills"]:
                    tech_map[tag]["skills"].append(skill_name)
                    
        except Exception as e:
            # print(f"Warning: Failed to parse {skill_file.name}: {e}")
            pass

    # Hardcoded Guides/Templates mapping (since these don't have metadata files yet)
    # Ideally, guides/templates would also have frontmatter, but for now we map them by known tags.
    
    # Common mappings
    shim_guides = {
        "typescript": ["js-ts-nodejs"],
        "javascript": ["js-ts-nodejs"],
        "react": ["js-ts-nodejs"],
        "next.js": ["js-ts-nodejs"],
        "python": ["python-fastapi-ai"],
        "fastapi": ["python-fastapi-ai"],
        "php": ["php-laravel"],
        "laravel": ["php-laravel"],
        "go": ["go-lang"],
        "legacy": ["legacy-tech"],
    }
    
    shim_templates = {
        "docker": ["DEVCONTAINER_TEMPLATE.json"],
        "kubernetes": ["DEV_SPACE.yaml"],
        "aws": ["INFRA_PLAN_TEMPLATE.md"],
        "enterprise": ["CAPABILITY_MAP_TEMPLATE.md"],
        "legacy": ["LEGACY_AUDIT_TEMPLATE.md"],
        "regulated": ["SECURITY_CHECKLIST.md"]
    }

    # Merge shims
    for tag, guides in shim_guides.items():
        if tag not in tech_map: tech_map[tag] = {"skills": [], "guides": [], "templates": []}
        tech_map[tag]["guides"].extend(guides)

    for tag, temps in shim_templates.items():
        if tag not in tech_map: tech_map[tag] = {"skills": [], "guides": [], "templates": []}
        tech_map[tag]["templates"].extend(temps)

    return tech_map

# Initial placeholders - will be populated in main()
TECH_MAP = {}

# --- Helper Functions ---

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(f"{BLUE}" + "=" * 60 + f"{NC}")
    print(f"{BLUE}🤖  Agentic Engineering Kit - Setup & Install Wizard v2.2{NC}")
    print(f"{BLUE}" + "=" * 60 + f"{NC}")
    print("This script will:")
    print("  1. Install the Kit (Locally or Globally)")
    print("  2. Configure Project Identity, Stack, & Type (Legacy/Enterprise)")
    print("  3. Wire up AI tools & MCPs")
    print("  4. Generate a 'Research Mission' for your AI")
    print()

def ask(question, default=None):
    prompt = f"{question}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    response = input(prompt).strip()
    return response if response else default

def select_index(question, options):
    print(f"\n{question}")
    for i, opt in enumerate(options):
        print(f"  {i+1}) {opt}")
    while True:
        choice = input(f"Select (1-{len(options)}): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx

def select(question, options):
    idx = select_index(question, options)
    return options[idx]

def ask_multiselect(question, options):
    print(f"\n{question} (comma separated, e.g. 1,3)")
    for i, opt in enumerate(options):
        print(f"  {i+1}) {opt}")
    choice = input("Select: ").strip()
    selected = []
    if not choice: return selected
    try:
        indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
        for idx in indices:
            if 0 <= idx < len(options):
                selected.append(options[idx])
    except Exception:
        pass
    return selected

def create_symlink(source, target):
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
        if str(PROJECT_ROOT) in str(source.absolute()):
             link_path = os.path.relpath(source, target.parent)
        else:
             link_path = source.absolute()

        os.symlink(link_path, target)
        print(f"  {GREEN}✓ Linked {target.name} -> {link_path}{NC}")
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
        print(f"{YELLOW}Warning: PyYAML not installed. Falling back to simple parsing.{NC}")
        # Fallback to simple parser if PyYAML is missing (bootstrapping edge case)
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

def setup_skills_for_platform(platform, skills_src_dir, target_dir):
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
            create_symlink(skill_file, dest_file)
            
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


# --- Main Logic ---

def main():
    if not SOURCE_AGENTS_DIR.exists():
        if (KIT_SOURCE / "AGENTS.md").exists():
             pass
        else:
            print(f"{RED}Error: Could not find source .agents directory at {SOURCE_AGENTS_DIR}{NC}")
            sys.exit(1)

    # Initialize Dynamic Tech Map
    global TECH_MAP
    TECH_MAP = build_tech_map_from_skills(SOURCE_AGENTS_DIR)

    clear_screen()
    print_header()

    # --- Step 1: Install Location ---
    print(f"{YELLOW}Part 1: Installation{NC}")
    print(f"Where should the Agent Kit be installed?")
    
    install_opts = [
        f"Local (Recommended) - Installs to {PROJECT_ROOT}/.agents", 
        f"Global - Installs to {Path.home()}/.agents (All projects share this)", 
        "Custom Path"
    ]
    
    choice_idx = select_index("Select Install Location", install_opts)
    
    target_agents_dir = None
    
    if choice_idx == 0:
        target_agents_dir = PROJECT_ROOT / ".agents"
    elif choice_idx == 1:
        target_agents_dir = Path.home() / ".agents"
    else:
        path_str = ask("Enter absolute path")
        target_agents_dir = Path(path_str)

    # Perform Install / Copy
    if target_agents_dir.exists():
        print(f"\n{YELLOW}! Directory {target_agents_dir} already exists.{NC}")
        overwrite = ask("Overwrite/Update it? (y/n)", "n")
        if overwrite.lower() == "y":
            shutil.rmtree(target_agents_dir)
            shutil.copytree(SOURCE_AGENTS_DIR, target_agents_dir)
            print(f"  {GREEN}✓ Kit updated at {target_agents_dir}{NC}")
        else:
            print(f"  {BLUE}→ Using existing kit at {target_agents_dir}{NC}")
    else:
        shutil.copytree(SOURCE_AGENTS_DIR, target_agents_dir)
        print(f"  {GREEN}✓ Kit installed to {target_agents_dir}{NC}")

    AGENTS_DIR = target_agents_dir


    # --- Step 2: Interview ---
    print(f"\n{YELLOW}Part 2: Project Context{NC}")
    
    project_name = ask("Project Name", PROJECT_ROOT.name)
    description = ask("One-line Description", "A new software project")
    
    # Team & Type
    team_size_idx = select_index("Team Size", ["Solo (1 dev)", "Small (2-5 devs)", "Large (6+ devs, Enterprise)"])
    team_size = ["Solo", "Small", "Large"][team_size_idx]
    
    project_type = select("Project Type", ["Greenfield (New)", "Legacy Modernization", "Enterprise / Regulated", "R&D / Prototype"])
    
    compliance = []
    if project_type == "Enterprise / Regulated":
         compliance = ask_multiselect("Compliance Requirements", ["GDPR", "HIPAA", "PCI-DSS", "SOC2", "ISO 27001"])
    
    # Tech Stack
    print(f"\n{YELLOW}Part 3: Technology Stack{NC}")
    language = select("Primary Language", ["TypeScript", "JavaScript", "Python", "PHP", "Go", "Rust", "Java", "C#", "Other"])
    if language == "Other": language = ask("Enter Language")
    
    framework = ask("Primary Framework (e.g. Next.js, FastAPI, Laravel)", "None")
    
    db_options = ["PostgreSQL", "MySQL/MariaDB", "MongoDB", "SQLite", "Redis", "None"]
    databases = ask_multiselect("Databases used", db_options)
    
    cloud_options = ["AWS", "Google Cloud", "Azure", "Vercel", "Railway", "DigitalOcean", "On-Prem"]
    clouds = ask_multiselect("Infrastructure / Cloud", cloud_options)
    
    # --- Dynamic Setup Check ---
    dynamic_setup = False
    problem_statement = ""
    print(f"\n{YELLOW}Part 3.1: Dynamic Agent Capabilities{NC}")
    if ask("Enable Dynamic Agent Setup (Live Research & Auto-Configuration)? (y/n)", "y").lower() == "y":
        dynamic_setup = True
        problem_statement = ask("What specific problem is this system solving? (e.g. 'High-frequency trading bot', 'Medical image analysis')")

    # --- Analytics Check ---
    enable_analytics = False
    if ask("Enable Agent Analytics (Track tokens, loops, and success rates)? (y/n)", "y").lower() == "y":
        enable_analytics = True
        
    # --- Meta-Evolution Check ---
    enable_meta = False
    if ask("Enable Self-Evolving Capabilities (Meta-Optimization)? (y/n)", "y").lower() == "y":
        enable_meta = True
    
    # --- Step 3: Gap Analysis ---
    
    missing_skills = []
    # Framework gap
    fw_key = framework.lower()
    if fw_key not in TECH_MAP and fw_key != "none":
        missing_skills.append(f"{fw_key}-best-practices")
    
    # Language gap
    lang_key = language.lower()
    if lang_key not in TECH_MAP and lang_key != "other":
         missing_skills.append(f"{lang_key}-idioms")

    # Domain gap
    if project_type == "Legacy Modernization":
         missing_skills.extend(TECH_MAP["legacy"]["skills"])
    if project_type == "Enterprise / Regulated":
         missing_skills.extend(TECH_MAP["enterprise"]["skills"])
    if compliance:
         missing_skills.extend(TECH_MAP["regulated"]["skills"])


    # --- Step 4: Generate AGENTS.md ---
    print(f"\n{YELLOW}Part 4: Configuring Installed Kit{NC}")
    
    template_path = AGENTS_DIR / "templates/coordination/AGENTS_TEMPLATE.md"
    if template_path.exists():
        content = template_path.read_text()
        
        # Replacements
        content = content.replace("{{ project_name }}", project_name)
        content = content.replace("{{ description }}", description)
        content = content.replace("{{ language }}", language)
        content = content.replace("{{ framework }}", framework)
        content = content.replace("{{ runtime }}", "Latest") 
        content = content.replace("{{ database }}", ", ".join(databases) if databases else "None")
        
        # Package Manager
        pm = "npm" 
        if language.lower() in ["python"]: pm = "pip"
        if language.lower() in ["php"]: pm = "composer"
        if language.lower() in ["go"]: pm = "go mod"
        if language.lower() in ["rust"]: pm = "cargo"
        
        if language.lower() in ["javascript", "typescript"]:
             pm_choice = select("Package Manager", ["npm", "pnpm", "yarn"])
             pm = pm_choice
        
        content = content.replace("{{ package_manager }}", pm)
        
        # Commands
        install_cmd = f"{pm} install"
        test_cmd = f"{pm} test"
        if pm == "pip":
            install_cmd = "pip install -r requirements.txt"
            test_cmd = "pytest"
        if pm == "go mod":
            install_cmd = "go mod download"
            test_cmd = "go test ./..."
        if pm == "cargo":
            install_cmd = "cargo build"
            test_cmd = "cargo test"
        
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if "install:" in line and "{{" in line:
                new_lines.append(f'install: "{install_cmd}"')
            elif ("test:" in line or "test_cmd" in line) and "{{" in line and "test_single" not in line:
                new_lines.append(f'test: "{test_cmd}"')
            elif "security_scan:" in line and "{{" in line:
                audit_cmd = f"{pm} audit"
                if pm == "pip": audit_cmd = "pip-audit"
                if pm == "go mod": audit_cmd = "govulncheck ./..."
                if pm == "cargo": audit_cmd = "cargo audit"
                new_lines.append(f'security_scan: "{audit_cmd}"')
            elif "build:" in line and "{{" in line:
                build_cmd = f"{pm} run build"
                if pm == "go mod": build_cmd = "go build -o app"
                if pm == "cargo": build_cmd = "cargo build --release"
                if pm == "pip": build_cmd = "# No build step for Python"
                new_lines.append(f'build: "{build_cmd}"')
            else:
                new_lines.append(line)
        
        content = "\n".join(new_lines)
        target_agents_md = AGENTS_DIR / "AGENTS.md"
        target_agents_md.write_text(content)
        print(f"  {GREEN}✓ Configured {target_agents_md}{NC}")
    else:
        print(f"  {RED}x Template not found: {template_path}{NC}")
        
    # --- Step 4.1: Append to CONSTITUTION.md ---
    if compliance or project_type == "Legacy Modernization":
        const_path = AGENTS_DIR / "CONSTITUTION.md"
        if const_path.exists():
            with open(const_path, "a") as f:
                f.write("\n\n## Project-Specific Articles (Auto-Generated)\n")
                if "Legacy Modernization" in project_type:
                    f.write("\n### Article VIII. The Modernization Mandate\n")
                    f.write("All new code must adhere to modern patterns. Legacy code touched must be refactored to >96% coverage (Boy Scout Rule).\n")
                if compliance:
                     f.write(f"\n### Article IX. Regulatory Compliance ({', '.join(compliance)})\n")
                     f.write("No PII shall be logged. All data at rest must be encrypted. Security audit is mandatory before Release.\n")
            print(f"  {GREEN}✓ Updated CONSTITUTION.md with specific Articles{NC}")

    # --- Step 5: Directory Wiring ---
    print(f"\n{YELLOW}Part 5: Wiring Agent Context{NC}")
    
    loki_mem = AGENTS_DIR / "loki/memory"
    (loki_mem / "episodic/SESSION_SNAPSHOT").mkdir(parents=True, exist_ok=True)
    (loki_mem / "semantic").mkdir(parents=True, exist_ok=True)
    
    if enable_analytics:
        (loki_mem / "metrics").mkdir(parents=True, exist_ok=True)
        print(f"  {GREEN}✓ Initialized Analytics Directory{NC}")
    
        (loki_mem / "PROJECT_STATE.md").write_text("# PROJECT_STATE.md\n\nPhase: S00_INITIALIZED\n")
        print(f"  {GREEN}✓ Initialized Loki Memory{NC}")

    # Copy setup-context.sh
    setup_src = AGENTS_DIR / "scripts/setup-context.sh"
    setup_dest = PROJECT_ROOT / "setup-context.sh"
    if setup_src.exists():
        shutil.copy2(setup_src, setup_dest)
        setup_dest.chmod(0o755)
        print(f"  {GREEN}✓ Installed setup-context.sh{NC}")
    else:
        print(f"  {YELLOW}! Could not find {setup_src}, skipping setup-context.sh install{NC}")

    # Symlinks
    skills_src = AGENTS_DIR / "skills"
    agents_md_src = AGENTS_DIR / "AGENTS.md"

    agents = ask_multiselect("Which AI Agents are you using?", ["Claude Code", "Cursor", "Gemini / Antigravity", "OpenAI / Codex", "GitHub Copilot", "VS Code"])
    
    if "Claude Code" in agents:
        claude_dir = PROJECT_ROOT / ".claude"
        claude_dir.mkdir(exist_ok=True)
        create_symlink(agents_md_src, claude_dir / "CLAUDE.md")
        create_symlink(skills_src, claude_dir / "skills")
        setup_skills_for_platform("Claude Code", skills_src, claude_dir / "skills")
    
    if "Cursor" in agents:
        cursor_dir = PROJECT_ROOT / ".cursor"
        cursor_rules_dir = cursor_dir / "rules"
        create_symlink(agents_md_src, PROJECT_ROOT / ".cursorrules")
        setup_skills_for_platform("Cursor", skills_src, cursor_rules_dir)
        
    if "Gemini / Antigravity" in agents:
        gemini_dir = PROJECT_ROOT / ".gemini"
        gemini_dir.mkdir(exist_ok=True)
        try:
            # Use paths relative to PROJECT_ROOT for cleaner config
            rel_agents = os.path.relpath(agents_md_src, PROJECT_ROOT)
            rel_skills = os.path.relpath(skills_src, PROJECT_ROOT)
        except Exception:
            rel_agents = str(agents_md_src.absolute())
            rel_skills = str(skills_src.absolute())

        settings_content = {
            "agent_instructions_file": rel_agents,
            "skills_directory": rel_skills,
            "notes": "Managed by init.py"
        }
        (gemini_dir / "settings.json").write_text(json.dumps(settings_content, indent=2))
        print(f"  {GREEN}✓ Wired .gemini/settings.json{NC}")
        
    if "OpenAI / Codex" in agents:
        codex_dir = PROJECT_ROOT / ".codex"
        codex_dir.mkdir(exist_ok=True)
        create_symlink(agents_md_src, codex_dir / "AGENTS.md")

    if "GitHub Copilot" in agents:
        gh_dir = PROJECT_ROOT / ".github"
        gh_dir.mkdir(exist_ok=True)
        create_symlink(agents_md_src, gh_dir / "copilot-instructions.md")
        setup_skills_for_platform("GitHub Copilot", skills_src, gh_dir / "skills")
        
    if "VS Code" in agents: # Added VS Code explicitly if requested, reusing logic
        gh_dir = PROJECT_ROOT / ".github" 
        setup_skills_for_platform("VS Code", skills_src, gh_dir / "skills")

    # --- Step 6: Gitignore ---
    gitignore = PROJECT_ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".env" not in content:
            with open(gitignore, "a") as f:
                f.write("\n.env\n.env.local\n")
            print(f"  {GREEN}✓ Added .env to .gitignore{NC}")

    # --- Step 7: Mission Generation ---
    print(f"\n{YELLOW}Part 6: Agent Mission Generation{NC}")
    
    if dynamic_setup:
        mission = f"""
# BOOTSTRAP MISSION: Dynamic Agent Setup
**Goal**: Research, Configure, and Build a robust {project_type} system for "{project_name}".

## Context
- **Problem**: {problem_statement}
- **Stack**: {language} / {framework}
- **Constraints**: {', '.join(compliance) if compliance else 'None'}
- **Missing Skills**: {', '.join(missing_skills) if missing_skills else 'Standard Set'}

## Phase 1: Dynamic Research (The "Search" Phase)
You are authorized to use `search_web` and `run_command` freely.
1.  **Landscape Analysis**: Search for "best {language} libraries for {problem_statement} in 2026".
2.  **Skill Acquisition**:
    -   Check `github.com/heilcheng/awesome-agent-skills` or similar repos.
    -   Download relevant skill templates or create new `.skill.md` files for discovered tools.
    -   Example: If building a trading bot, create `financial-analysis.skill.md`.

## Phase 2: Rigorous "Definition of Done" Setup
You MUST NOT write implementation code until these artifacts are approved:
1.  **Requirements**: `PRD.md` with clear User Stories.
2.  **Architecture**: `PLAN.md` with C4 diagrams and "System Context".
3.  **Specs**: `SPEC.md` with API schemas and Database models.
4.  **Acceptance Criteria**: E2E test scenarios defined in `features/` or `tests/`.

## Phase 3: Execution Strategy
-   Run `init` on the project framework (e.g., `npm init`, `cargo new`).
-   Install the dependencies found in Phase 1.
-   Execute the **Loki Loop** (Plan -> Test -> Code -> Verify).

## Mandatory Checkpoints
-   [ ] Research completed & Skills added
-   [ ] Architecture approved by Human
-   [ ] CI/CD Pipeline configured
-   [ ] Compliance Audit passed (if regulated)

Start by running: `./setup-context.sh` to confirm your environment.
"""
        mission_file = PROJECT_ROOT / "BOOTSTRAP_MISSION.md"
        mission_file.write_text(mission)
        print(f"\n{GREEN}✓ Generated Dynamic BOOTSTRAP_MISSION.md{NC}")
        print(f"{BLUE}>> INSTRUCTION: Agent, please read BOOTSTRAP_MISSION.md and begin Phase 1 immediately.{NC}")

    else:
        # Standard Static Mission
        mission = f"""
I have initialized the GABBE Agentic Engineering Kit for this project.
Here is your mission to finalize the setup:

1.  **Analyze the Gap**: We are using {language} and {framework}.
    -   Missing Skills: {', '.join(missing_skills) if missing_skills else 'None detected'}.
    -   Project Type: {project_type}.
    -   Compliance: {', '.join(compliance) if compliance else 'None'}.

2.  **MCP Configuration**:
    -   Review `.agents/templates/MCP_CONFIG_TEMPLATE.json`.
    -   Install "Context-7 MCP" (Essential for docs).
    -   If we are using Postgres, install "PostgreSQL MCP".

3.  **Research & Create (Deep Context Mode)**:
    -   **Standards Check**: Research SWEBOK/ISO/IEEE standards relevant to a {project_type} project in {language}.
    -   **Gap Analysis**: Compare the installed skills against the specific needs of {framework} in 2026.
    -   **Generate**: Create key missing skills. Example: `.agents/skills/{framework.lower()}-best-practices.skill.md`.
    -   **Architectural Pattern**: Identify the best pattern (e.g., Clean Arch, Hexagonal, Vertical Slice) for this stack and document it in `AGENTS.md`.
"""
        if team_size == "Large":
            mission += "\n4.  **Loki Mode Activation**:\n    -   Review `.agents/loki/README.md`.\n    -   Deploy the Personas from `.agents/loki/personas/` to my active tool context.\n"

        mission += """
5.  **Mandatory Guardrails**:
    -   **Ethics**: Run `ai-ethics-compliance` skill on the initial specs.
    -   **Safety**: Install `ai-safety-guardrails` hooks.
"""

        mission += "\n6.  **Verify**:\n    -   Run `integrity-check` skill to ensure all symlinks and configs are valid.\n"
        
        print("-" * 60)
        print(mission)
        print("-" * 60)
        
        mission_file = PROJECT_ROOT / "SETUP_MISSION.md"
        mission_file.write_text(mission)
        print(f"\n{GREEN}✓ Mission saved to SETUP_MISSION.md{NC}")

    print(f"{BLUE}Setup Complete! The kit is installed at: {AGENTS_DIR}{NC}")

if __name__ == "__main__":
    main()

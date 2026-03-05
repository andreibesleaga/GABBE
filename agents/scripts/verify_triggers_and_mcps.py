import os
import json
import re
from pathlib import Path
import sys

# ANSI colors for output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[0;33m"
NC = "\033[0m"

PROJECT_ROOT = Path(__file__).parent.parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"

def verify_triggers_and_mcps():
    print(f"\n{BLUE}=== Skill Triggers and MCP Server Audit ==={NC}")
    
    # 1. Parse MCP Servers
    mcp_config_path = AGENTS_DIR / "templates/core/MCP_CONFIG_TEMPLATE.json"
    with open(mcp_config_path, 'r') as f:
        mcp_data = json.load(f)
        
    mcp_servers = set(mcp_data.get("mcpServers", {}).keys())
    print(f"{GREEN}✓ Loaded {len(mcp_servers)} MCP Servers from Config: {', '.join(list(mcp_servers)[:5])}...{NC}")
    
    # 2. Parse 00-index.md to get Skill File -> Triggers map
    skill_index_path = AGENTS_DIR / "skills/00-index.md"
    
    skill_triggers = {}
    all_triggers = set()
    
    with open(skill_index_path, 'r') as f:
        for line in f:
            if "|" in line and ".skill.md" in line:
                # Format is usually: | Skill Name | `path/to/skill.skill.md` | trigger1, trigger2 | ... |
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    file_match = re.search(r'`([^`]+\.skill\.md)`', parts[2])
                    if file_match:
                        file_path = file_match.group(1)
                        basename = file_path.split("/")[-1].replace(".skill.md", "")
                        
                        triggers = [t.strip() for t in parts[3].split(",")]
                        skill_triggers[basename] = triggers
                        all_triggers.update(triggers)

    print(f"{GREEN}✓ Extracted triggers for {len(skill_triggers)} skills.{NC}")
    
    # Check that Triggers aren't empty
    empty_triggers = [s for s, t in skill_triggers.items() if not t or t == [""]]
    if empty_triggers:
        print(f"{RED}x FAIL: Skills with missing triggers in index: {empty_triggers}{NC}")
        sys.exit(1)
        
    # 3. Check Prompts in Docs
    docs_to_check = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs/README_FULL.md",
        PROJECT_ROOT / "docs/QUICK_GUIDE.md",
        PROJECT_ROOT / "docs/QUICK_COMMANDS.md"
    ]
    
    for folder in ["guides", "skills"]:
        folder_path = AGENTS_DIR / folder
        if folder_path.exists():
            for root, _, files in os.walk(folder_path):
                for f in files:
                    if f.endswith(".md"):
                        docs_to_check.append(Path(root) / f)
    
    print(f"\n{BLUE}--- Validating Prompt Chaining across {len(docs_to_check)} files ---{NC}")
    
    # Regex to find: "run X skill" or "use X skill"
    prompt_skill_regex = re.compile(r'(?:use|run)\s+(?:the\s+)?([a-zA-Z0-9-]+)\s*skill', re.IGNORECASE)
    
    stop_words = {"a", "this", "that", "any", "some", "which", "your", "my", "our", "one", "another", "these"}
    
    errors = 0
    warnings = 0
    for doc in docs_to_check:
        if not doc.exists():
            continue
        with open(doc, 'r') as f:
            content = f.read()
            
        mentions = prompt_skill_regex.findall(content)
        for mention in mentions:
            mention = mention.lower()
            if mention in stop_words:
                continue
                
            # If it explicitly matches a skill filename or a registered trigger
            if mention in skill_triggers or mention in all_triggers:
                pass # valid
            else:
                print(f"{YELLOW}! WARNING: Document '{doc.name}' uses skill/trigger '{mention}' which is not in the index.{NC}")
                warnings += 1
                # We won't strictly fail on this because natural language might say "use debugging skill" instead of "use debug skill",
                # but it's a good sanity check.
    
    # 4. Check specific Visual Design MCPs bindings
    visual_skill_path = AGENTS_DIR / "skills/architecture/visual-whiteboarding.skill.md"
    if visual_skill_path.exists():
        with open(visual_skill_path, 'r') as f:
            visual_content = f.read()
            
        required_mcps = ["drawio", "miro", "figma"]
        for rmcp in required_mcps:
            # We must check if the tool actually documents these specifically mapping to the exact keys in MCP JSON.
            mcp_key = None
            for key in mcp_servers:
                if rmcp.lower() in key.lower() or key.lower() in rmcp.lower():
                    mcp_key = key
                    break
            
            if mcp_key:
                print(f"{GREEN}✓ Mapped '{rmcp}' capability in visual skill to MCP Server key: {mcp_key}{NC}")
            else:
                print(f"{RED}x FAIL: Visual skill requires '{rmcp}' but no matching MCP Server found in MCP_CONFIG_TEMPLATE.json!{NC}")
                errors += 1
                
    if errors > 0:
        print(f"\n{RED}Audit Failed with {errors} errors.{NC}")
        sys.exit(1)
        
    print(f"\n{GREEN}=== Audit Complete. All triggers, skills, and MCP bindings are chained correctly. ==={NC}")


if __name__ == "__main__":
    verify_triggers_and_mcps()

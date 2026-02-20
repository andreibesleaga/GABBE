import os
import re
from pathlib import Path

def main():
    root_dir = Path("/home/andrei/work/GABBE")
    agents_dir = root_dir / "agents"
    
    # Exclude these directories
    exclude_dirs = {'.git', '.venv', 'node_modules', '__pycache__', 'gabbe'}
    
    # 1. Discover all existing components
    existing = {
        'skills': set(),
        'templates': set(),
        'guides': set(),
        'personas': set()
    }
    
    folders = {
        'skills': agents_dir / "skills",
        'templates': agents_dir / "templates",
        'guides': agents_dir / "guides",
        'personas': agents_dir / "personas",
        'memory': agents_dir / "memory"
    }

    # Gather skills (*.skill.md)
    if folders['skills'].exists():
        for root, _, files in os.walk(folders['skills']):
            for f in files:
                if f.endswith(".skill.md"):
                    existing['skills'].add(f.replace('.skill.md', ''))

    # Gather templates (*_TEMPLATE.md)
    template_folders = [folders['templates'], folders['memory']]
    for tf in template_folders:
        if tf.exists():
            for root, _, files in os.walk(tf):
                for f in files:
                    if f.endswith(".md") and "TEMPLATE" in f:
                        existing['templates'].add(f.replace('.md', ''))

    # Gather guides (*.md in guides folder)
    if folders['guides'].exists():
        for root, _, files in os.walk(folders['guides']):
            for f in files:
                if f.endswith(".md") and f != "00-index.md":
                    existing['guides'].add(f.replace('.md', ''))
                
    # Gather personas (*.md in personas folder)
    if folders['personas'].exists():
        for root, _, files in os.walk(folders['personas']):
            for f in files:
                if f.endswith(".md") and f != "00-index.md":
                    existing['personas'].add(f.replace('.md', ''))

    print(f"Discovered {len(existing['skills'])} skills, {len(existing['templates'])} templates, {len(existing['guides'])} guides, {len(existing['personas'])} personas.\n")

    # 2. Search for mentions in root and docs/
    mentioned = {
        'skills': set(),
        'templates': set(),
        'guides': set(),
        'personas': set()
    }
    
    # Patterns
    skill_p1 = re.compile(r'([\w-]+)\.skill(?!\.md)')
    skill_p2 = re.compile(r'([\w-]+)\.skill\.md')
    template_p = re.compile(r'([\w_]+_TEMPLATE)\.md')
    guide_p = re.compile(r'guides/([\w-]+)\.md')
    
    # We will also just check if the exact filename (minus extension) appears in the docs
    def check_exact_match(content, item_set, item_type):
        for item in item_set:
            # simple string match
            if item in content:
                mentioned[item_type].add(item)

    docs_to_check = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith(".md"):
                docs_to_check.append(Path(root) / file)

    for filepath in docs_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract via regex
            mentioned['skills'].update(skill_p1.findall(content))
            mentioned['skills'].update(skill_p2.findall(content))
            mentioned['templates'].update(template_p.findall(content))
            mentioned['guides'].update(guide_p.findall(content))
            
            # Check exact mentions for all
            check_exact_match(content, existing['skills'], 'skills')
            check_exact_match(content, existing['templates'], 'templates')
            check_exact_match(content, existing['guides'], 'guides')
            check_exact_match(content, existing['personas'], 'personas')
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    # 3. Analyze differences
    for category in existing.keys():
        missing = mentioned[category] - existing[category]
        unmentioned = existing[category] - mentioned[category]
        
        # Filter expected placeholders
        if category == 'skills':
            missing -= {'my-language', 'your-skill-name'}
        elif category == 'templates':
            missing -= {'YOUR_TEMPLATE'}

        print(f"--- {category.upper()} ---")
        print(f"Total mentioned: {len(mentioned[category])}")
        print(f"Total existing: {len(existing[category])}")
        
        if missing:
            print(f"[⚠️] Mentioned in docs but missing from files:")
            for m in sorted(missing):
                print(f"  - {m}")
        else:
            print(f"[✅] All mentioned {category} exist.")
            
        if unmentioned:
            print(f"[ℹ️] Existing {category} NOT explicitly mentioned in any parsed docs:")
            for u in sorted(unmentioned):
                print(f"  - {u}")
        else:
            print(f"[✅] All existing {category} are mentioned somewhere in docs.")
            
        print()
    
    # 4. Critical Quality Checks
    print("--- CRITICAL QUALITY CHECKS ---")
    outdated_version_files = []
    corrupted_header_files = []
    
    for filepath in docs_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "0.3.0" in content:
                outdated_version_files.append(str(filepath))
            
            if "## 🚀- **" in content:
                corrupted_header_files.append(str(filepath))
                
        except:
            pass
            
    if outdated_version_files:
        print(f"[❌] Outdated CLI version (0.3.0) found in:")
        for f in outdated_version_files:
            print(f"  - {f}")
    else:
        print("[✅] No outdated CLI versions found.")
        
    if corrupted_header_files:
        print(f"[❌] Corrupted headers found in:")
        for f in corrupted_header_files:
            print(f"  - {f}")
    else:
        print("[✅] No corrupted headers found.")
    
    # 5. Workflow Disovery
    print("\n--- WORKFLOWS ---")
    workflows = set()
    workflow_paths = [root_dir / ".agents/workflows", root_dir / ".agent/workflows", agents_dir / "workflows"]
    for wp in workflow_paths:
        if wp.exists():
            for f in wp.glob("*.md"):
                workflows.add(f.name)
    
    if workflows:
        print(f"Found {len(workflows)} workflows:")
        for w in sorted(workflows):
            print(f"  - {w}")
    else:
        print("[ℹ️] No workflows found.")

if __name__ == "__main__":
    main()

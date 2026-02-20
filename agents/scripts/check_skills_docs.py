import os
import re
from pathlib import Path

def main():
    root_dir = Path("/home/andrei/work/GABBE")
    skills_dir = root_dir / "agents" / "skills"
    
    # Exclude these directories from search
    exclude_dirs = {'.git', '.venv', 'node_modules', '__pycache__', 'gabbe'}
    
    # 1. Discover all existing skills
    existing_skills = set()
    if skills_dir.exists():
        for root, dirs, files in os.walk(skills_dir):
            for file in files:
                if file.endswith(".skill.md"):
                    existing_skills.add(file.replace('.skill.md', ''))
    
    print(f"Found {len(existing_skills)} actual skills in {skills_dir}")
    
    # 2. Search for skill mentions in all markdown files
    mentioned_skills = set()
    skill_mentions_map = {} # skill -> set of files
    
    # regex matches: "some-skill.skill" or "some-skill.skill.md" or "`some-skill`" in specific contexts
    # Let's extract anything that ends in .skill or .skill.md
    skill_pattern1 = re.compile(r'([\w-]+)\.skill(?!\.md)')
    skill_pattern2 = re.compile(r'([\w-]+)\.skill\.md')
    
    # In table cells, sometimes they are just backticked: `spec-writer`
    # We will try to match those as well by looking for anything in backticks in the READMEs that matches existing skills,
    # or just collect all backticked words and see if they look like a skill.
    backtick_pattern = re.compile(r'`([\w-]+)`')

    for root, dirs, files in os.walk(root_dir):
        # Filter exclusions
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            if not file.endswith(".md"):
                continue
                
            filepath = Path(root) / file
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                matches1 = skill_pattern1.findall(content)
                matches2 = skill_pattern2.findall(content)
                bmatches = backtick_pattern.findall(content)
                
                # We count a backticked word as a skill mention if it's already a known skill or ends with -skill etc. Let's just collect all and filter later.
                all_possible = set(matches1 + matches2)
                for bm in bmatches:
                    if bm in existing_skills:
                        all_possible.add(bm)
                        
                for skill in all_possible:
                    mentioned_skills.add(skill)
                    if skill not in skill_mentions_map:
                        skill_mentions_map[skill] = set()
                    skill_mentions_map[skill].add(str(filepath.relative_to(root_dir)))
                    
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    # 3. Analyze discrepancy
    missing_skills = mentioned_skills - existing_skills
    unmentioned_skills = existing_skills - mentioned_skills
    
    print("\n--- Summary ---")
    print(f"Total mentioned skills: {len(mentioned_skills)}")
    print(f"Total existing skills: {len(existing_skills)}")
    
    print("\n[⚠️] Mentioned in docs but missing from agents/skills/:")
    if missing_skills:
        for ms in sorted(missing_skills):
            files_mentioned = ", ".join(skill_mentions_map[ms])
            print(f"  - {ms} (Found in: {files_mentioned})")
    else:
        print("  None. All mentioned skills exist.")
        
    print("\n[ℹ️] Existing skills NOT mentioned in any parsed docs:")
    # We can refine this to check if they are missing from specific files like QUICK_GUIDE.md or README_FULL.md
    if unmentioned_skills:
        for us in sorted(unmentioned_skills):
            print(f"  - {us}")
    else:
        print("  None. All existing skills are mentioned somewhere.")
        
    # Specifically check docs/QUICK_GUIDE.md and docs/README_FULL.md
    critical_docs = ['docs/QUICK_GUIDE.md', 'docs/README_FULL.md', 'README.md', 'agents/skills/00-index.md']
    
    for doc in critical_docs:
        doc_path = root_dir / doc
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all skill mentions in this doc
                doc_m1 = skill_pattern1.findall(content)
                doc_m2 = skill_pattern2.findall(content)
                doc_bm = [b for b in backtick_pattern.findall(content) if b in existing_skills]
                doc_skills = set(doc_m1 + doc_m2 + doc_bm)
                
                not_in_doc = existing_skills - doc_skills
                print(f"\n[📊] {doc} covers {len(doc_skills)} out of {len(existing_skills)} skills.")

if __name__ == "__main__":
    main()

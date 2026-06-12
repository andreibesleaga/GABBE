import os
import re
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent.parent / "agents"


def test_no_broken_relative_links():
    broken_links = []
    link_pattern = re.compile(r"\[.*?\]\((?!http)(.*?)\)")

    for root, _, files in os.walk(AGENTS_DIR):
        if "templates" in root.split(os.sep):
            continue
        for file in files:
            if not file.endswith(".md"):
                continue
            filepath = Path(root) / file
            content = filepath.read_text(encoding="utf-8")

            for match in link_pattern.finditer(content):
                link_target = match.group(1).split("#")[0]
                if not link_target or link_target.startswith("mailto:"):
                    continue

                target_path = (filepath.parent / link_target).resolve()
                if not target_path.exists():
                    broken_links.append(f"{filepath.relative_to(AGENTS_DIR)} -> {link_target}")

    assert not broken_links, "Broken links found:\n" + "\n".join(broken_links)


def test_skills_have_required_frontmatter():
    skills_dir = AGENTS_DIR / "skills"
    missing_frontmatter = []

    for root, _, files in os.walk(skills_dir):
        for file in files:
            if not file.endswith(".skill.md"):
                continue
            filepath = Path(root) / file
            content = filepath.read_text(encoding="utf-8")

            if not content.startswith("---"):
                missing_frontmatter.append(
                    f"{filepath.relative_to(AGENTS_DIR)}: Missing YAML frontmatter"
                )
                continue

            frontmatter = content.split("---")[1]
            if "name:" not in frontmatter:
                missing_frontmatter.append(
                    f"{filepath.relative_to(AGENTS_DIR)}: Missing 'name:' in frontmatter"
                )
            if "triggers:" not in frontmatter:
                missing_frontmatter.append(
                    f"{filepath.relative_to(AGENTS_DIR)}: Missing 'triggers:' in frontmatter"
                )

    assert not missing_frontmatter, "Skill frontmatter errors:\n" + "\n".join(missing_frontmatter)


if __name__ == "__main__":
    test_no_broken_relative_links()
    test_skills_have_required_frontmatter()
    print("Capability Layer Validation Passed!")

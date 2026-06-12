#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import re
from pathlib import Path


def fill_placeholders():
    print("🤖 GABBE Placeholder Setup Utility")
    agents_dir = Path(__file__).parent.parent / "agents"

    if not agents_dir.exists():
        print(f"Error: agents directory not found at {agents_dir}")
        return

    # Regex to find [PLACEHOLDER: ...]
    placeholder_regex = re.compile(r"\[PLACEHOLDER:\s*(.*?)\]")

    # Track unique placeholders to only ask once
    answers = {}

    for md_file in agents_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        matches = placeholder_regex.findall(content)

        if not matches:
            continue

        print(f"\nFound placeholders in {md_file.name}:")
        new_content = content

        for match in matches:
            if match not in answers:
                answers[match] = input(f"Enter value for '{match}': ").strip()

            # Replace precisely this placeholder
            exact_placeholder = f"[PLACEHOLDER: {match}]"
            new_content = new_content.replace(exact_placeholder, answers[match])

            # Also try without space just in case
            exact_placeholder_no_space = f"[PLACEHOLDER:{match}]"
            new_content = new_content.replace(exact_placeholder_no_space, answers[match])

        if new_content != content:
            md_file.write_text(new_content, encoding="utf-8")
            print(f"✓ Updated {md_file.name}")


if __name__ == "__main__":
    try:
        fill_placeholders()
        print("\nAll placeholders filled successfully!")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

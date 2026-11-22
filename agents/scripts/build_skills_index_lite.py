#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build agents/skills/00-index-lite.md, the short skill index an agent loads at session start.

One line per skill: name, when to use it (the description, cut at about 80 characters at a word boundary) and context cost. The category is the group heading.
Stdlib only. The output is sorted, so the same skills always give the same file.

Usage:
    python3 agents/scripts/build_skills_index_lite.py           # write the file
    python3 agents/scripts/build_skills_index_lite.py --check   # exit 1 when the file is out of date
"""

from __future__ import annotations

import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
OUTPUT = SKILLS_DIR / "00-index-lite.md"
MAX_DESCRIPTION = 80
SEPARATOR = " — "

HEADER = (
    "# Skills index (lite)\n"
    "> Generated file. Do not edit. Regenerate: `python3 agents/scripts/build_skills_index_lite.py`"
    " (CI runs it with `--check`).\n"
    "> One line per skill: name — when to use it — context cost (the heading is the category). "
    "The full index is `agents/skills/00-index.md`; read a skill's file in full before you use it.\n"
)


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def read_frontmatter(text: str) -> dict[str, str]:
    """Top-level `key: value` pairs of the frontmatter; folded or literal blocks are joined."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    key = None
    for line in text[3:end].splitlines():
        if line[:1] in (" ", "\t") and key:
            fields[key] = (fields[key] + " " + line.strip()).strip()
        elif ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            fields[key] = "" if value in (">", "|", ">-", "|-") else _unquote(value)
    return fields


def shorten(text: str, limit: int = MAX_DESCRIPTION) -> str:
    """Cut at a word boundary within `limit` characters; add an ellipsis when cut."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:.—-")
    return cut + "…"


def collect() -> list[tuple[str, str, str, str]]:
    """(category, name, short description, context cost) for every skill, sorted."""
    rows = []
    for path in SKILLS_DIR.rglob("*.skill.md"):
        fields = read_frontmatter(path.read_text(encoding="utf-8"))
        name = fields.get("name") or path.name[: -len(".skill.md")]
        category = path.parent.relative_to(SKILLS_DIR).as_posix() or "root"
        rows.append(
            (
                category,
                name,
                shorten(fields.get("description", "")),
                fields.get("context_cost", "medium"),
            )
        )
    return sorted(rows)


def render() -> str:
    rows = collect()
    out = [HEADER, f"Skills: {len(rows)}\n"]
    current = None
    for category, name, description, cost in rows:
        if category != current:
            out.append(f"\n## {category}\n")
            current = category
        out.append(SEPARATOR.join([name, description, cost]) + "\n")
    return "".join(out)


def main(argv: list[str]) -> int:
    content = render()
    if "--check" in argv:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
        if current != content:
            print(
                f"{OUTPUT} is out of date. Run: python3 agents/scripts/build_skills_index_lite.py",
                file=sys.stderr,
            )
            return 1
        print(f"{OUTPUT.name} is up to date ({len(collect())} skills).")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(collect())} skills, {len(content.encode('utf-8'))} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

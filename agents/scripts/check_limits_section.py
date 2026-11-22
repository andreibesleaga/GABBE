#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the "Limits and safety" section of skill files.

Since 1.2.0 every skill ends its own risks in one short section, `## Limits and
safety`, instead of the long "Security & Guardrails" block. The rules that apply
to every skill live once, in `agents/CONSTITUTION.md` (Article 0) and
`agents/guides/principles/skill-guardrails.md`.

A skill passes when it:
  * has exactly one `## Limits and safety` heading;
  * has no "Security & Guardrails" heading left;
  * keeps that section to 1-6 bullets and at most 900 characters;
  * does not demand, in that section, a control the kit cannot provide.

Usage:
    python3 agents/scripts/check_limits_section.py            # every skill
    python3 agents/scripts/check_limits_section.py PATH ...   # files or folders
Exit code 0 when every checked skill passes, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
HEADING = "## Limits and safety"
MAX_CHARS = 900
MAX_BULLETS = 6
# Controls only a platform can provide; a skill's text must not demand them.
BANNED = re.compile(
    r"cryptographic|\bGPG\b|\b2FA\b|two-factor|kernel-level|mathematically", re.IGNORECASE
)
OLD_HEADING = re.compile(
    r"^#{1,6}\s.*Security\s*(&|and)\s*Guardrails", re.IGNORECASE | re.MULTILINE
)


def limits_section(text: str) -> str | None:
    """The body of the `## Limits and safety` section, or None when it is absent."""
    start = text.find("\n" + HEADING)
    if start == -1:
        return None
    body = text[start + len(HEADING) + 1 :]
    nxt = re.search(r"^#{1,2}\s", body, re.MULTILINE)
    return body[: nxt.start()] if nxt else body


def problems(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    found = []
    if OLD_HEADING.search(text):
        found.append('still has a "Security & Guardrails" heading')
    if text.count("\n" + HEADING) > 1:
        found.append(f"more than one `{HEADING}` heading")
    section = limits_section(text)
    if section is None:
        return found + [f"no `{HEADING}` section"]
    bullets = [ln for ln in section.splitlines() if ln.lstrip().startswith(("- ", "* "))]
    if not 1 <= len(bullets) <= MAX_BULLETS:
        found.append(f"{len(bullets)} bullets (1 to {MAX_BULLETS} allowed)")
    if len(section.strip()) > MAX_CHARS:
        found.append(f"{len(section.strip())} characters (at most {MAX_CHARS})")
    banned = BANNED.search(section)
    if banned:
        found.append(f'demands a control the kit cannot provide: "{banned.group(0)}"')
    return found


def skill_files(args: list[str]) -> list[Path]:
    roots = [Path(a) for a in args] or [SKILLS_DIR]
    files: list[Path] = []
    for root in roots:
        files.extend(sorted(root.rglob("*.skill.md")) if root.is_dir() else [root])
    return files


def main(argv: list[str]) -> int:
    failed = 0
    files = skill_files(argv)
    for path in files:
        found = problems(path)
        if found:
            failed += 1
            print(f"FAIL {path}: " + "; ".join(found))
    print(f"{len(files) - failed} of {len(files)} skills pass the Limits and safety check")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check that every Markdown and text file states the GABBE lifecycle the same way.

The source of truth is the table "Lifecycle at a glance (canonical)" in
agents/guides/processes/loki-sdlc-phases.md. This script reads the phase ids and the
human gates from that table, then scans the repository.

Rules (each hit prints file, line number and the line text):

  A. Phase count and range.
     - "<N>-phase SDLC" (also lifecycle, core, build, framework, loop) or "lifecycle
       with/of/has <N> phases", with N other than 14.
     - The range S01-S10 (also "S01 to S10") unless the same line says "Day 1".
     - A range that starts at S00 and ends at S10, S11 or S12, or any range ending
       after S13. Sub-ranges such as S00-S03 or S11-S13 are fine.
  B. Quality gates. "<N>-gate" or "<N> gates" with N other than 9 ("7-gate",
     "10 gates", "seven gates"). Human gates ("six human gates") do not match.
     Lines about the release compatibility gates (they mention run_gates, scripts/gates
     or "API surface") are skipped; they are a different set.
  C. Phase ids. A half-numbered phase (S02.5) or a one-digit phase id (S0, S1) on a
     line that is about the lifecycle (it says phase, SDLC, lifecycle or checkpoint).
     Other one-digit names such as S3 (a storage service) are not phase ids.
  D. Human gates. A line that mentions "human" and "gate", has no phase range, and
     names four or more different phase ids must name exactly the human gates of the
     canonical table (now S00, S01, S02, S07, S08, S10).

Also checked: the canonical table exists and has the 14 rows S00..S13.

Exceptions: put <!-- lifecycle-validator: ignore --> on the line, with a reason nearby.

Skipped: plugins/, scripts/tests/golden/, docs/reports/, CHANGELOG.md and
GABBE-v1.0-MASTER-PLAN.md (historical), .git, hidden directories (except .github),
node_modules, .venv*, *.egg-info.

Usage: validate_lifecycle.py [--root PATH]
Exit code: 0 when clean, 1 when any rule is broken.
"""

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent.parent
CANON_FILE = "agents/guides/processes/loki-sdlc-phases.md"
IGNORE_MARK = "lifecycle-validator: ignore"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
NC = "\033[0m"

SKIP_PREFIXES = ("plugins/", "scripts/tests/golden/", "docs/reports/")
SKIP_NAMES = {"CHANGELOG.md", "GABBE-v1.0-MASTER-PLAN.md", "node_modules", ".git"}
WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
}
NUM = r"(\d+|" + "|".join(WORD_NUMBERS) + r")"

RE_PHASE_COUNT = re.compile(
    r"\b" + NUM + r"[- ]phases?\s+(?:core|build|sdlc|lifecycle|framework|loop)\b"
    r"|\b(?:sdlc|lifecycle)\s+(?:has|of|with)\s+" + NUM + r"\s+phases?\b",
    re.I,
)
RE_GATE_COUNT = re.compile(r"\b" + NUM + r"[- ](?:quality[- ])?gates?\b", re.I)
RE_RANGE = re.compile(r"\bS(\d{2})\s*(?:[-–—]|to)\s*S(\d{2})\b")
RE_COMPAT_GATES = re.compile(r"run_gates|scripts/gates|API surface|\bthe (?:6|six) gates", re.I)
RE_HALF = re.compile(r"\bS\d{2}\.\d\b")
RE_ONE_DIGIT = re.compile(r"(?<![\w.\-/])S[01](?![\w\[\].])")
RE_ID = r"S\d{2}"
PHASE_WORDS = re.compile(r"phase|sdlc|lifecycle|checkpoint", re.I)


def to_int(token):
    token = token.lower()
    return int(token) if token.isdigit() else WORD_NUMBERS[token]


def read_canonical(root):
    """Return (phase_ids, human_gate_ids, errors) from the canonical table."""
    path = root / CANON_FILE
    if not path.exists():
        return [], set(), [f"{CANON_FILE}: file not found"]
    ids, human, errors = [], set(), []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 8 and re.fullmatch(RE_ID, cells[0]):
            ids.append(cells[0])
            if cells[7].upper().startswith("HUMAN"):
                human.add(cells[0])
    expected = [f"S{n:02d}" for n in range(14)]
    if ids != expected:
        errors.append(
            f"{CANON_FILE}: canonical table must have the rows S00..S13 in order, found {ids}"
        )
    return ids, human, errors


def iter_files(root):
    for path in sorted(root.rglob("*")):
        if path.suffix not in (".md", ".txt") or not path.is_file():
            continue
        rel = path.relative_to(root)
        parts = rel.parts
        rel_posix = rel.as_posix()
        if rel_posix.startswith(SKIP_PREFIXES) or path.name in SKIP_NAMES:
            continue
        if any(
            p in SKIP_NAMES
            or p.startswith(".venv")
            or p.endswith(".egg-info")
            or (p.startswith(".") and p != ".github")
            for p in parts[:-1]
        ):
            continue
        yield path, rel_posix


def check_line(line, human_expected):
    """Return a list of rule messages for one line."""
    found = []
    if IGNORE_MARK in line:
        return found
    # A. phase count
    for m in RE_PHASE_COUNT.finditer(line):
        count = m.group(1) or m.group(2)
        if to_int(count) != 14:
            found.append(f"A: phase count '{m.group(0)}', the lifecycle has 14 phases")
    # A. ranges
    for m in RE_RANGE.finditer(line):
        start, end = int(m.group(1)), int(m.group(2))
        if end > 13:
            found.append(f"A: phase range '{m.group(0)}' goes past S13")
        elif start == 0 and end in (10, 11, 12):
            found.append(f"A: phase range '{m.group(0)}', the whole lifecycle is S00-S13")
        elif (start, end) == (1, 10) and not re.search(r"Day[- ]1", line):
            found.append(
                f"A: phase range '{m.group(0)}' without 'Day 1', the whole lifecycle is S00-S13"
            )
    # B. quality gate count
    for m in RE_GATE_COUNT.finditer(line):
        if to_int(m.group(1)) != 9 and not RE_COMPAT_GATES.search(line):
            found.append(f"B: gate count '{m.group(0)}', there are nine quality gates G1-G9")
    # C. half and one-digit ids
    for m in RE_HALF.finditer(line):
        found.append(f"C: half-numbered phase '{m.group(0)}'")
    if PHASE_WORDS.search(line):
        for m in RE_ONE_DIGIT.finditer(line):
            found.append(f"C: one-digit phase id '{m.group(0)}', use two digits (S00)")
    # D. human gate lists
    if re.search(r"human", line, re.I) and re.search(r"gate", line, re.I):
        ids = set(re.findall(RE_ID, line))
        if len(ids) >= 4 and not RE_RANGE.search(line) and ids != human_expected:
            want = ", ".join(sorted(human_expected))
            found.append(
                f"D: human gates listed as {', '.join(sorted(ids))}, the canonical set is {want}"
            )
    return found


def main():
    parser = argparse.ArgumentParser(description="Check lifecycle wording across the repo")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    root = Path(parser.parse_args().root).resolve()

    print(f"{BLUE}Validating GABBE lifecycle wording...{NC}")
    errors = 0

    print(f"\n{BLUE}1. Reading the canonical table...{NC}")
    ids, human, table_errors = read_canonical(root)
    for msg in table_errors:
        print(f"{RED}[CANON] {msg}{NC}")
        errors += 1
    if not table_errors:
        print(f"{len(ids)} phases, human gates: {', '.join(sorted(human))}")

    print(f"\n{BLUE}2. Scanning Markdown and text files...{NC}")
    scanned = 0
    for path, rel in iter_files(root):
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            for msg in check_line(line, human):
                print(f"{RED}[LIFECYCLE] {rel}:{number}: {msg}{NC}")
                print(f"    {line.strip()[:200]}")
                errors += 1
    print(f"Scanned {scanned} files.")

    print("-" * 40)
    if errors > 0:
        print(f"{RED}Found {errors} lifecycle errors.{NC}")
        sys.exit(1)
    print(f"{GREEN}Lifecycle wording check passed!{NC}")
    sys.exit(0)


if __name__ == "__main__":
    main()

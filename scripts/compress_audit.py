#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cost + lossless-compression audit for the agent-facing corpus (Track v1.0).

Coding agents pay context/memory/token cost for every skill, guide, and template
they load. This tool measures that footprint and applies ONLY provably-lossless
normalizations — ones that never change a single word an agent reads:

  * strip trailing whitespace on every line;
  * collapse 3+ consecutive blank lines to a single blank line;
  * ensure exactly one trailing newline.

These remove redundant bytes (and the stray tokens they cost) while keeping the
content byte-for-byte semantically identical — fully compatible with the existing
emitters and validators. Anything riskier than whitespace is intentionally left
as-is (semantic content is never rewritten here).

Usage:
    python3 scripts/compress_audit.py            # audit only (measure, no writes)
    python3 scripts/compress_audit.py --apply    # apply the lossless normalizations
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = {
    "skills": ROOT / "agents" / "skills",
    "guides": ROOT / "agents" / "guides",
    "templates": ROOT / "agents" / "templates",
}
_BLANKS = re.compile(r"\n{3,}")


def normalize(text: str) -> str:
    """Apply the lossless normalizations. Returns the normalized text."""
    # 1. strip trailing whitespace per line
    lines = [ln.rstrip() for ln in text.split("\n")]
    out = "\n".join(lines)
    # 2. collapse 3+ blank lines to one
    out = _BLANKS.sub("\n\n", out)
    # 3. exactly one trailing newline
    return out.rstrip("\n") + "\n"


def _est_tokens(n_bytes: int) -> int:
    # Coarse heuristic: ~4 bytes/token for English markdown.
    return round(n_bytes / 4)


def main() -> None:
    ap = argparse.ArgumentParser(description="Cost + lossless-compression audit")
    ap.add_argument("--apply", action="store_true", help="Write the lossless normalizations")
    args = ap.parse_args()

    grand_before = grand_after = grand_changed = grand_files = 0
    print(
        f"{'category':<12}{'files':>7}{'changed':>9}{'KB before':>11}{'KB saved':>10}{'% saved':>9}"
    )
    print("-" * 58)
    for name, base in TARGETS.items():
        if not base.exists():
            continue
        files = sorted(p for p in base.rglob("*.md"))
        before = after = changed = 0
        for p in files:
            original = p.read_text(encoding="utf-8")
            normalized = normalize(original)
            before += len(original.encode("utf-8"))
            after += len(normalized.encode("utf-8"))
            if normalized != original:
                changed += 1
                if args.apply:
                    p.write_text(normalized, encoding="utf-8")
        saved = before - after
        pct = (saved / before * 100) if before else 0.0
        print(
            f"{name:<12}{len(files):>7}{changed:>9}{before / 1024:>11.1f}"
            f"{saved / 1024:>10.2f}{pct:>8.2f}%"
        )
        grand_before += before
        grand_after += after
        grand_changed += changed
        grand_files += len(files)

    g_saved = grand_before - grand_after
    g_pct = (g_saved / grand_before * 100) if grand_before else 0.0
    print("-" * 58)
    print(
        f"{'TOTAL':<12}{grand_files:>7}{grand_changed:>9}{grand_before / 1024:>11.1f}"
        f"{g_saved / 1024:>10.2f}{g_pct:>8.2f}%"
    )
    print(
        f"\nEstimated token footprint: {_est_tokens(grand_before):,} -> "
        f"{_est_tokens(grand_after):,} (~{_est_tokens(g_saved):,} tokens saved, lossless)."
    )
    if not args.apply:
        print("Audit only. Re-run with --apply to write the lossless normalizations.")


if __name__ == "__main__":
    main()

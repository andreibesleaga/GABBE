#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fail the nightly job when the mutation score drops below the recorded floor.

Input is the file `mutmut export-cicd-stats` writes (mutmut 3.x documents this command;
it creates `mutants/mutmut-cicd-stats.json` with the counters `killed`, `survived`,
`total`, `no_tests`, `skipped`, `suspicious`, `timeout`, ...), or the counters given on
the command line.

Score, in percent, as mutmut's own `badge` command computes it:

    (killed + timeout) / (total - skipped) * 100

A mutant that no test reaches counts as not killed. The floor lives in
`scripts/gates/baselines/mutation-floor.json` as `{"floor": <percent or null>, ...}`.

Exit codes: 0 = at or above the floor, or no floor set yet; 1 = below the floor;
2 = the input cannot be used while a floor is set.

Usage:
    python scripts/gates/check_mutation_floor.py [--stats mutants/mutmut-cicd-stats.json]
    python scripts/gates/check_mutation_floor.py --killed 120 --total 300 [--timeout 3 --skipped 0]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_FLOOR_FILE = Path(__file__).resolve().parent / "baselines" / "mutation-floor.json"
DEFAULT_STATS = Path("mutants/mutmut-cicd-stats.json")


def score_percent(killed, total, timeout=0, skipped=0):
    """Mutation score in percent; 0.0 when nothing was tested."""
    tested = total - skipped
    if tested <= 0:
        return 0.0
    return (killed + timeout) / tested * 100.0


def read_stats(path):
    """The counters from a `mutmut export-cicd-stats` file, as a dict of ints."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("stats file is not a JSON object")
    stats = {}
    for key in ("killed", "total", "timeout", "skipped"):
        value = data.get(key, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"stats field {key!r} is not a non-negative integer: {value!r}")
        stats[key] = value
    if "killed" not in data or "total" not in data:
        raise ValueError("stats file has no 'killed' and 'total' counters")
    return stats


def read_floor(path):
    """The floor in percent, or None when none is set yet."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    floor = data.get("floor") if isinstance(data, dict) else None
    if floor is None:
        return None
    if isinstance(floor, bool) or not isinstance(floor, (int, float)) or not 0 <= floor <= 100:
        raise ValueError(f"floor must be null or a number from 0 to 100, got {floor!r}")
    return float(floor)


def evaluate(stats, floor):
    """Return (exit_code, message) for the counters and the floor."""
    if stats is None:
        if floor is None:
            return 0, "mutation score: no floor set yet and no result to measure"
        return 2, f"mutation score: no usable result, but a floor of {floor:.1f}% is set"
    score = score_percent(stats["killed"], stats["total"], stats["timeout"], stats["skipped"])
    counts = f"killed {stats['killed']}+{stats['timeout']} timeout of {stats['total'] - stats['skipped']}"
    if floor is None:
        return 0, f"mutation score: {score:.1f}% ({counts}); no floor set yet"
    if score < floor:
        return 1, f"mutation score: {score:.1f}% ({counts}) is BELOW the floor of {floor:.1f}%"
    return 0, f"mutation score: {score:.1f}% ({counts}) meets the floor of {floor:.1f}%"


def _parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--stats", type=Path, default=None, help="file from `mutmut export-cicd-stats`")
    p.add_argument("--floor-file", type=Path, default=DEFAULT_FLOOR_FILE)
    for name in ("killed", "total", "timeout", "skipped"):
        p.add_argument(f"--{name}", type=int, default=None)
    return p.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    try:
        floor = read_floor(args.floor_file)
    except (OSError, ValueError) as e:
        print(f"mutation score: cannot read the floor file {args.floor_file}: {e}")
        return 2
    stats = None
    if args.killed is not None or args.total is not None:
        if args.killed is None or args.total is None:
            print("mutation score: --killed and --total go together")
            return 2
        stats = {
            "killed": args.killed,
            "total": args.total,
            "timeout": args.timeout or 0,
            "skipped": args.skipped or 0,
        }
    else:
        path = args.stats or DEFAULT_STATS
        try:
            stats = read_stats(path)
        except (OSError, ValueError) as e:
            print(f"mutation score: cannot read {path}: {e}")
    code, message = evaluate(stats, floor)
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())

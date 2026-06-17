#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Skill self-eval harness (Track E2).

Scores GABBE's own markdown skills against golden datasets stored beside them at
agents/skills/<category>/evals/<skill>.eval.yaml (promptfoo-compatible shape).

Two lanes — matching the eval philosophy that tests verify determinism while
evals score probabilistic quality:

  * default / --check  (deterministic, per-commit): lints every eval suite for a
    valid structure and self-tests the deterministic assertion evaluators on
    built-in fixtures. Needs NO model, so it is safe to gate per-commit.

  * --live  (GABBE_LIVE_LLM=1, nightly): renders each prompt, calls the model via
    gabbe/llm.py (reused when the CLI is importable), evaluates the assertions,
    and writes a JSON scorecard. Non-blocking by design.

HONESTY: evals SAMPLE the input space and raise confidence — they do not prove
correctness. LLM-as-judge assertions are biased-but-useful, never ground truth.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

AGENTS_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = AGENTS_DIR / "skills"

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

# Assertion types evaluable WITHOUT a model, given a candidate output.
DETERMINISTIC_TYPES = {
    "equals",
    "contains",
    "icontains",
    "not-contains",
    "regex",
    "is-json",
    "min-length",
}
# Assertion types that require a model / embeddings (live lane only).
LIVE_ONLY_TYPES = {"similar", "llm-rubric"}
KNOWN_TYPES = DETERMINISTIC_TYPES | LIVE_ONLY_TYPES


# ---------------------------------------------------------------------------
# Deterministic assertion evaluators (pure functions — unit-testable, no model)
# ---------------------------------------------------------------------------


def assert_output(assertion: dict[str, Any], output: str) -> tuple[bool, str]:
    """Evaluate a single deterministic assertion against a candidate output."""
    t = assertion.get("type")
    val = assertion.get("value")
    if t == "equals":
        return output.strip() == str(val).strip(), "equals"
    if t == "contains":
        return str(val) in output, "contains"
    if t == "icontains":
        return str(val).lower() in output.lower(), "icontains"
    if t == "not-contains":
        return str(val) not in output, "not-contains"
    if t == "regex":
        return re.search(str(val), output) is not None, "regex"
    if t == "is-json":
        try:
            json.loads(output)
            return True, "is-json"
        except (ValueError, TypeError):
            return False, "is-json"
    if t == "min-length":
        return len(output) >= int(val), "min-length"
    raise ValueError(f"not a deterministic assertion type: {t!r}")


# ---------------------------------------------------------------------------
# Suite loading + structural lint
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> Any:
    import yaml  # PyYAML is a core GABBE dependency

    return yaml.safe_load(path.read_text())


def discover_suites(root: Path = SKILLS_DIR) -> list[Path]:
    return sorted(root.glob("**/evals/*.eval.yaml"))


def lint_suite(path: Path) -> list[str]:
    """Return a list of structural errors for one eval suite (empty == valid)."""
    errors: list[str] = []
    try:
        suite = _load_yaml(path)
    except Exception as e:  # noqa: BLE001 - surface the YAML error
        return [f"{path.name}: not valid YAML ({str(e).splitlines()[0]})"]
    if not isinstance(suite, dict):
        return [f"{path.name}: top-level must be a mapping"]
    if not str(suite.get("description", "")).strip():
        errors.append(f"{path.name}: missing 'description'")
    tests = suite.get("tests")
    if not isinstance(tests, list) or not tests:
        return errors + [f"{path.name}: 'tests' must be a non-empty list"]
    for i, test in enumerate(tests):
        if not isinstance(test, dict):
            errors.append(f"{path.name}: test #{i} must be a mapping")
            continue
        asserts = test.get("assert")
        if not isinstance(asserts, list) or not asserts:
            errors.append(f"{path.name}: test #{i} has no 'assert' list")
            continue
        for a in asserts:
            if not isinstance(a, dict) or a.get("type") not in KNOWN_TYPES:
                errors.append(f"{path.name}: test #{i} has an unknown assert type {a!r}")
            elif a.get("type") in DETERMINISTIC_TYPES and "value" not in a:
                errors.append(f"{path.name}: test #{i} {a.get('type')} assert needs a 'value'")
    return errors


# Built-in fixtures proving the deterministic evaluators behave correctly. Run in
# the per-commit lane so a regression in the harness itself is caught with no model.
_SELF_TESTS = [
    ({"type": "contains", "value": "?"}, "Do you mean X?", True),
    ({"type": "contains", "value": "?"}, "A statement.", False),
    ({"type": "icontains", "value": "ERROR"}, "fatal error here", True),
    ({"type": "not-contains", "value": "secret"}, "all clear", True),
    ({"type": "regex", "value": r"^\d{3}$"}, "404", True),
    ({"type": "regex", "value": r"^\d{3}$"}, "40x", False),
    ({"type": "is-json", "value": None}, '{"ok": true}', True),
    ({"type": "is-json", "value": None}, "not json", False),
    ({"type": "min-length", "value": 5}, "abcdef", True),
    ({"type": "min-length", "value": 5}, "abc", False),
    ({"type": "equals", "value": "yes"}, "  yes ", True),
]


def self_test_evaluators() -> list[str]:
    failures = []
    for assertion, output, expected in _SELF_TESTS:
        got, _ = assert_output(assertion, output)
        if got != expected:
            failures.append(f"evaluator {assertion} on {output!r} -> {got}, expected {expected}")
    return failures


def run_check() -> int:
    """Per-commit deterministic lane: lint suites + self-test evaluators."""
    print(f"{BLUE}== Eval harness self-check (deterministic, no model) =={NC}")
    errors: list[str] = []
    suites = discover_suites()
    for path in suites:
        errors.extend(lint_suite(path))
    print(f"  linted {len(suites)} eval suite(s)")
    eval_failures = self_test_evaluators()
    errors.extend(eval_failures)
    print(f"  self-tested {len(_SELF_TESTS)} deterministic evaluator cases")
    if errors:
        for e in errors:
            print(f"{RED}x {e}{NC}")
        print(f"{RED}eval self-check FAILED with {len(errors)} error(s){NC}")
        return 1
    print(f"{GREEN}eval self-check passed{NC}")
    return 0


# ---------------------------------------------------------------------------
# Live lane (nightly): render prompts, call the model, score, write a scorecard
# ---------------------------------------------------------------------------


def _render(template: str, variables: dict[str, Any]) -> str:
    out = template
    for k, v in (variables or {}).items():
        out = out.replace("{{" + k + "}}", str(v)).replace("{{ " + k + " }}", str(v))
    return out


def run_live(out_path: Path | None) -> int:
    print(f"{BLUE}== Eval harness LIVE lane (calls the model) =={NC}")
    try:
        from gabbe.llm import call_llm  # reuse the CLI's model adapter + caching
    except Exception as e:  # noqa: BLE001
        print(f"{RED}live mode needs the gabbe CLI importable (gabbe.llm): {e}{NC}")
        return 2

    scorecard: dict[str, Any] = {"suites": [], "summary": {}}
    total = passed = 0
    for path in discover_suites():
        suite = _load_yaml(path)
        prompts = suite.get("prompts") or ["{{input}}"]
        suite_rec: dict[str, Any] = {"suite": str(path.relative_to(AGENTS_DIR)), "cases": []}
        for test in suite.get("tests", []):
            rendered = _render(prompts[0], test.get("vars", {}))
            output = call_llm(rendered) or ""
            case_passed = True
            details = []
            for a in test.get("assert", []):
                atype = a.get("type")
                if atype in DETERMINISTIC_TYPES:
                    ok, label = assert_output(a, output)
                elif atype == "llm-rubric":
                    ok, label = _judge(call_llm, a.get("value", ""), output)
                else:  # similar — needs embeddings we don't ship; SKIP honestly
                    # passed=None: recorded but NOT counted toward the pass rate
                    # (skipping must never silently inflate the scorecard).
                    details.append({"type": f"{atype} (skipped: needs embeddings)", "passed": None})
                    continue
                details.append({"type": label, "passed": ok})
                case_passed = case_passed and ok
            total += 1
            passed += 1 if case_passed else 0
            suite_rec["cases"].append({"passed": case_passed, "asserts": details})
        scorecard["suites"].append(suite_rec)

    scorecard["summary"] = {
        "cases": total,
        "passed": passed,
        "pass_rate": round(passed / total, 4) if total else None,
        "note": "evals sample; pass_rate raises confidence, it does not prove correctness",
    }
    text = json.dumps(scorecard, indent=2)
    if out_path:
        out_path.write_text(text)
        print(f"  scorecard written to {out_path}")
    else:
        print(text)
    print(f"{GREEN}live eval complete: {passed}/{total} cases passed{NC}")
    return 0


def _judge(call_llm: Any, rubric: str, output: str) -> tuple[bool, str]:
    """Minimal LLM-as-judge: ask for a PASS/FAIL verdict against a rubric."""
    prompt = (
        "You are a strict evaluator. Given the RUBRIC and the CANDIDATE OUTPUT, "
        "reply with exactly 'PASS' or 'FAIL' on the first line.\n\n"
        f"RUBRIC:\n{rubric}\n\nCANDIDATE OUTPUT:\n{output}\n"
    )
    verdict = (call_llm(prompt) or "").strip().upper()
    return verdict.startswith("PASS"), "llm-rubric"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GABBE skill eval harness (Track E2)")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run the model and score outputs (nightly; needs GABBE_LIVE_LLM=1 + an API key)",
    )
    parser.add_argument("--out", type=Path, default=None, help="Write the JSON scorecard here")
    args = parser.parse_args(argv)
    if args.live:
        return run_live(args.out)
    return run_check()


if __name__ == "__main__":
    sys.exit(main())

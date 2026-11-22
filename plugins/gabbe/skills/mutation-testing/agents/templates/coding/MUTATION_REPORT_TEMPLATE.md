# Mutation Report: [Change or Component]

**Date:** [YYYY-MM-DD]
**Author:** [name]
**Tool and version:** [mutmut | StrykerJS | PIT | Stryker.NET | cargo-mutants] [x.y.z]

<!-- Filled at S06 by mutation-testing.skill. The floor is set by the human in ASSURANCE_PLAN. -->

## 1. Scope

- Base compared against: [branch or commit]
- Files or classes mutated: [list]
- Excluded (with reason): [none | list]
- Command: [exact command]

## 2. Score

| Mutants | Killed | Timeout | Survived | Skipped / unviable | Score | Floor | Pass? |
|---|---|---|---|---|---|---|---|
| [n] | [n] | [n] | [n] | [n] | [percent] | [percent] | [yes/no] |

Score = (killed + timeout) / (mutants - skipped or unviable). A timeout counts as detected; a skipped or
unviable mutant is not counted at all. Use the same formula as the check that enforces the floor (in this
repository `scripts/gates/check_mutation_floor.py`; in your project the tool's own threshold).

## 3. Survivors and decisions

| Mutant (file:line, change) | Class (test gap / equivalent / dead code) | Decision | Test added or reason |
|---|---|---|---|
| [src/a.py:12 `<` to `<=`] | [test gap] | [test added] | [tests/test_a.py::test_x] |

## 4. Notes

[Run time, flaky tests seen, anything the human should know.]

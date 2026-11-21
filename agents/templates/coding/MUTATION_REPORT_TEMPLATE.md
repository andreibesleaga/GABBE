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

| Mutants | Killed | Survived | Timeout / unviable | Score (killed / (killed + survived)) | Floor | Pass? |
|---|---|---|---|---|---|---|
| [n] | [n] | [n] | [n] | [percent] | [percent] | [yes/no] |

## 3. Survivors and decisions

| Mutant (file:line, change) | Class (test gap / equivalent / dead code) | Decision | Test added or reason |
|---|---|---|---|
| [src/a.py:12 `<` to `<=`] | [test gap] | [test added] | [tests/test_a.py::test_x] |

## 4. Notes

[Run time, flaky tests seen, anything the human should know.]

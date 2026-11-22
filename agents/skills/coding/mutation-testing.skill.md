---
name: mutation-testing
description: Measure how well tests detect faults by mutating changed code, reading surviving mutants, and enforcing a mutation-score floor that a human sets. Use at S06 for level 1 and above, or when line coverage is high but confidence in the tests is low.
triggers: [mutation testing, mutation score, surviving mutants, test quality, stryker, mutmut, pitest, cargo-mutants]
tags: [coding, testing, mutation, quality]
core: true
context_cost: medium
---
# Mutation Testing

## Goal
A mutation tool makes small faults ("mutants") in the code and re-runs the tests; a mutant the tests do not catch (a survivor) shows a missing or weak test. Score = (killed + timed-out mutants) / (all mutants - skipped or unviable ones). It adds evidence to G3 (coverage); it does not replace it. Report: `agents/templates/coding/MUTATION_REPORT_TEMPLATE.md`.

## Steps
1. Pick the tool for the ecosystem (commands checked 2026-11-21 on each tool's own site):

| Ecosystem | Tool | Install | Run |
|---|---|---|---|
| Python | mutmut | `pip install mutmut` | `mutmut run`, then `mutmut browse` |
| JavaScript/TypeScript | StrykerJS | `npm init stryker@10.1.1` | `npx stryker run` |
| Java | PIT | plugin in `pom.xml` | `mvn test-compile org.pitest:pitest-maven:mutationCoverage` |
| C# | Stryker.NET | `dotnet tool install -g dotnet-stryker` | `dotnet stryker` in the test project |
| Rust | cargo-mutants | `cargo install --locked cargo-mutants` | `cargo mutants` |

   No tool is listed for another language: say so in the report and use level 1 without a floor. Done when the tool runs once on the project.
2. Scope to changed code, not the whole repository.
   - Rust: `git diff origin/main > changes.diff` then `cargo mutants --in-diff changes.diff`.
   - StrykerJS: set `mutate` to the changed files, for example `"mutate": ["src/orders/*.ts", "!src/**/*.spec.ts"]`; `--incremental` reuses earlier results (stored in `reports/stryker-incremental.json`).
   - Stryker.NET: `dotnet stryker --since:main`.
   - mutmut: `mutmut run "my_module*"` or `only_mutate` in `[tool.mutmut]`; it re-tests only changed functions between runs.
   - PIT: restrict with `targetClasses` and `targetTests`; its documented change-based mode comes from the paid arcmutate extension, so do not assume it.
3. Run it. Tests must be green first, and a mutation run is slower than a test run: run it at S06 and nightly, not on every save.
4. Read each survivor (Rust: `mutants.out/missed.txt`; mutmut: `mutmut browse`; Stryker and PIT: the HTML report). Classify it:
   - Test gap: write a test that fails on the mutant and passes on the real code.
   - Equivalent mutant (same behaviour, for example a changed log string): mark it with a one-line reason in the report.
   - Dead or unreachable code: propose its removal.
   Done when no survivor is unclassified.
5. Compute the score for the changed code and compare it with the floor in `ASSURANCE_PLAN` (or `AGENTS.md`). Enforce it in CI where the tool supports it: Stryker `thresholds.break`, Stryker.NET `--break-at`, PIT `mutationThreshold`.
6. Fill the `MUTATION_REPORT`: scope, tool and version, score, survivors and decisions.

## What a floor means, and who sets it
A floor is the lowest score a change may have; below it the change is not done. The human sets it and records it in the plan. The agent proposes a starting value after a first measured run and never lowers it. A floor of 100 percent is not a goal because of equivalent mutants.

## Constraints
- Scope the run to changed code; run it at S06 and nightly, not on every save.
- The human sets the floor; the agent never lowers it.

## Output Format
The filled `MUTATION_REPORT` (scope, tool and version, score, survivors and decisions) and any new tests.

## Limits and safety
- Never edit a test only to kill a mutant if the test asserts nothing about requirements; each new test traces to a requirement or a stated property.
- Never exclude files or mutators from the run to raise the score without a reason in the report that the human has read.
- A high score shows the tests notice small code changes, not that the requirements are right.

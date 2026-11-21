---
name: characterization-tests
description: "Use before changing code that has no tests or weak tests. Pins what the code does today with golden-master and characterisation tests, handles non-determinism, and records a coverage baseline, so later changes can be checked against it. Use when: characterization test, characterisation test, golden master, approval test, pin behaviour, no tests, legacy tests, snapshot current behaviour, baseline coverage."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/characterization-tests.skill.md"
  tags: "coding, testing, brownfield"
  core: "true"
  context_cost: "medium"
---
# Characterization Tests Skill

## Goal
Write tests that say "the code does X today", not "the code should do X". They are the safety net for `safe-refactoring.skill` and `incremental-feature.skill`. This is stage B1 of `guides/processes/brownfield-lifecycle.md`.

## Steps
1. **Choose the area.** Take only the code that will change (from the approved plan in `ASSESSMENT.md`). Write the list in `project/CHARACTERIZATION.md`: unit, module, why it is in scope.
2. **Record the baseline.** Run the test command and the coverage tool if one exists. Write the numbers in `project/CHARACTERIZATION.md` under "Baseline before". No tool? Add the project's standard one only if the human approved dependency changes; otherwise count tests only.
3. **Find seams.** For each unit find where input enters and output leaves: a function call, an HTTP route, a CLI command, a file read and write, a database call. Prefer the highest seam that is still fast (a public function or route) over private internals.
4. **Capture current behaviour.**
   - Pure function: call it with a set of real inputs (take them from logs, fixtures, production-like samples with personal data removed) and assert the returned value it gives now. Write the expected value after running the code once, then re-run to see it pass.
   - Complex or large output (reports, JSON, HTML, files): golden master. Save the output to `tests/golden/<case>.txt`; the test compares new output to the file. Use the language's approval or snapshot library if the project already has one, else a plain file compare.
   - Command or route: record request and response pairs, then replay them.
5. **Control non-determinism.** Fix the clock (inject or patch time), seed random numbers, replace network and external services with recorded responses or fakes at the seam, sort unordered output, strip volatile fields (ids, timestamps) before the compare. If it still differs between two runs, the test is not done.
6. **Check the tests can fail.** For each test, change one line of the code under test, run, see red, then undo the change. A characterisation test that cannot go red is not a test. Record "mutation check: n of n".
7. **Run three times.** The suite must give the same result three times in a row, in any order if the runner can shuffle.
8. **Treat suspected bugs.** If the pinned behaviour looks wrong, pin it anyway, mark the test `# CHARACTERIZATION: suspected bug <one line>`, add a row to the "Suspected bugs" table in `project/CHARACTERIZATION.md`, and tell the human. Do not fix it in this stage.
9. **Record the baseline after.** Run coverage again and write the numbers under "Baseline after" with the list of units now pinned and units still unpinned.

## Constraints
- No production source file is changed, except the smallest seam needed to test (a parameter for the clock, an extracted function), and each such change is listed in `project/CHARACTERIZATION.md` and done only when the human approved it in the plan.
- Never delete or weaken a failing characterisation test. Change it only when the human confirms the old behaviour was a bug; then record the decision in `AUDIT_LOG.md`.
- The 99% rule applies to new or changed behaviour. The aim here is to pin the code that will change, not to reach 99% on untouched legacy code.
- Fixtures contain no real secrets or personal data.

## Output Format
`project/CHARACTERIZATION.md` (scope, baseline before and after, seams used, suspected bugs, unpinned areas) and the new test files in the project's test directory.

## Limits and safety
- A golden master saved from production-like data must be masked before it goes into version control; check each file for emails, names, tokens, account numbers.
- Do not run characterisation tests against a shared or production service; replace it at the seam.
- Regenerating a golden file to make a test pass is a behaviour change: it needs the human's yes.

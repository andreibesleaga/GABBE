---
name: verification-anti-cheating
description: "Rules and reviewer checks that stop an implementing agent from gaming its own verification: frozen tests, no weakened assertions, no hidden assume/sorry/admitted lemmas, separate contexts for specification and implementation. Use at S05/S06 whenever level 1 or higher is in force. Use when: anti-cheating, weakened assertion, test tampering, hidden assume, sorry, admit, reward hacking, frozen tests, verification integrity."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/verification-anti-cheating.skill.md"
  tags: "coding, testing, verification, review, integrity"
  core: "true"
  context_cost: "low"
---
# Verification Anti-Cheating

## Goal
Make "green" mean something. An agent that both writes the code and the checks can reach green by changing the checks. This skill fixes who may edit what, and gives the reviewer commands to detect each form of gaming.

## Rules and how a reviewer checks each
| Rule | Check (run by the reviewer or orch-judge) |
|---|---|
| Frozen tests: tests, properties, contracts, fuzz targets and model/spec files written for the task are not edited by the implementing agent; a needed change goes to the human or to a separate test-writing context | `git diff --stat <base>..HEAD -- <frozen paths>` is empty, or every change is listed and approved in the plan |
| No weakened assertions: no removed assertion, loosened tolerance, widened `expected` set, deleted case, or new skip/xfail/ignore | `git diff <base>..HEAD` on test paths, search the added lines for `skip`, `xfail`, `ignore`, `todo`, `pytest.approx` with a larger tolerance, and removed `assert` lines |
| No weakened bounds: fuzz time, `max_examples`, model bounds, mutation floor and coverage floor are never lowered by the implementer | compare the values in the plan, config and CI with the approved ones |
| No hidden proof leaks: `assume`, `sorry`, `admit`, admitted lemmas, `{:axiom}`, `external_body`, unproved `axiom`, `{:verify false}` | the leak checklist in `proof-core-verification.skill.md` step 5; each hit is listed with a reason in the obligation file |
| Specification and implementation by different contexts where possible: the context that writes the spec or tests does not write the code; with one agent, use two sessions and hand over files only | the plan names the contexts; the implementing session's prompt does not contain the other session's reasoning |
| Test the tests: a mutation run, or one deliberate bug, must turn the suite red | `mutation-testing.skill.md`; or the reviewer injects a fault and runs the suite |
| Specification review by the human: the human reads the specification and its plain-words copy, not the proof | `HUMAN_APPROVED` row in `AUDIT_LOG.md` for each level 2 and 3 specification |
| No special-casing: no code that detects the test input, test environment or checker | search for branches on test file names, environment names such as `CI`, or hard-coded expected values |
| Report only what ran: a claim names the command, the date and the result | every claim in the report has a log or file path |

## Steps
1. At S04/S05 start, list the frozen paths in `ASSURANCE_PLAN` and make the repository enforce it where it can (a CI step that fails on changes to those paths from the implementing branch, a read-only file mode in the agent's sandbox).
2. During S05 the implementing agent works only outside the frozen paths. If a frozen test seems wrong, it writes a note (the test name, the expected value, why it thinks it is wrong) and stops that task for the human.
3. At S06 run the checks in the table. Done when each row is "pass" or has a written, human-approved exception.
4. A finding blocks the phase exit; it is recorded in `AUDIT_LOG.md`.

## Constraints
- The frozen paths are listed in `ASSURANCE_PLAN` before S05 and the implementing agent does not edit them.
- A finding blocks the phase exit and is recorded in `AUDIT_LOG.md`.

## Output Format
A pass or an approved exception for each rule in the table, with the command output, and the findings recorded in `AUDIT_LOG.md`.

## Limits and safety
- These checks catch common edits to checks; they do not prove an agent acted in good faith.
- A frozen test can itself be wrong; the human decides, the agent never "fixes" it silently.
- Do not widen a frozen path list to hide a change after the fact.

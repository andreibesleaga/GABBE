---
name: safe-refactoring
description: "Use to change the structure of existing code that has no reliable safety net, in small reversible steps (strangler, branch by abstraction, parallel run). Use refactor.skill instead when a green test suite already covers the code."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/safe-refactoring.skill.md"
  tags: "coding, refactoring, brownfield"
  core: "true"
  context_cost: "medium"
---
# Safe Refactoring Skill

## Goal
Improve structure without changing behaviour when the code was not written for testing. This is stage B3 of `guides/processes/brownfield-lifecycle.md`. It adds the net first (`characterization-tests.skill`), then applies the mechanics of `refactor.skill` one reversible step at a time.

## Steps
1. **Check entry.** The human approved the plan (`ASSESSMENT.md`, proposal section). Characterisation tests exist for the target (`project/CHARACTERIZATION.md`) and are green. If not, stop and run `characterization-tests.skill`.
2. **Write the step list.** In `project/TASKS.md` write each step as one reversible change with its own check: "T-nnn: <what>, check: <command>, undo: <how>". A step that cannot be undone alone is split.
3. **Pick the technique per step.**
   - Replace a module over time (strangler): put a facade in front of the old code, route one case to the new code, keep the rest on the old.
   - Replace an implementation used by many callers (branch by abstraction): add an interface, make callers use it, add the new implementation behind it, switch with a flag or one line, remove the old one last.
   - Check the new against the old (parallel run): run both, compare results, log differences, return the old result until differences are zero for a period the human agreed.
   - Local cleanup (extract, rename, early return): apply `refactor.skill`.
4. **Do one step.** Make the change. Run the step's check and the full test suite. Green: record it (step 6). Red: undo the step, do not patch the tests, find the cause.
5. **Keep behaviour identical.** After a step the characterisation tests pass unchanged. If one must change, stop; that is a behaviour change (see Constraints).
6. **Record each step.** One line in `project/TASKS.md` (`DONE`, check output summary) and, when the project uses small commits, a note for the human with the proposed commit message. Do not commit.
7. **Check boundaries.** After structural steps run `agentic-linter.skill` and the complexity tool; no new cycles, complexity not above 10 in touched code.
8. **Remove the old path last.** Delete old code only when the new path has served for the agreed period, its tests pass, and the human said yes to the deletion.
9. **Finish.** Run the full suite and compare to the baseline in `project/CHARACTERIZATION.md`: pass count not lower, coverage not lower. Report the steps done and the steps left.

## Constraints
- One reversible step at a time; never a step that mixes refactoring with a feature or a dependency upgrade.
- No big-bang rewrite. A rewrite of a whole system needs an ADR and the human's approval at S02.
- Moving code must keep its security context: authorisation checks, input validation, audit logging and error contracts stay with the logic that they protect. List them before the move and confirm after.
- Do not edit tests to make a step pass.

## Output Format
Steps done in `project/TASKS.md`, tests green, a short report: "<n> steps done, <m> left, suite <pass count> passing (baseline <pass count>), coverage <x>% (baseline <y>%)".

## Limits and safety
- Data migrations and schema changes are not refactoring steps here; they go through `db-migration.skill` and need the human's yes (data loss risk).
- A step that touches a production switch (a route, a flag in production) is deployed only through the S10 gate: the human says "deploy now" in that request.
- When the old code looks like it has undocumented checks (a strange condition, a magic number), keep it and ask the human; do not "tidy" it.

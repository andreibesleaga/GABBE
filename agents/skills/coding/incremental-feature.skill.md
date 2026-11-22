---
name: incremental-feature
description: Use to add or change a feature in an existing system with the least risk. Find the seam, pin the surrounding behaviour, use a flag or branch by abstraction where it lowers risk, then follow the normal S01 to S08 path at small scale.
triggers: [add feature to existing system, incremental feature, feature in legacy code, seam, feature flag existing code, change existing behaviour, extend existing module]
tags: [coding, brownfield, feature]
core: true
context_cost: medium
---
# Incremental Feature Skill

## Goal
Deliver one feature in an existing codebase without breaking what already works. This is stage B4 of `guides/processes/brownfield-lifecycle.md`. The feature goes through the normal lifecycle, sized to the change.

## Steps
1. **State the feature.** Write it as EARS lines in `project/EARS_REQUIREMENTS.md` ("WHEN ... THE SYSTEM SHALL ..."). Ask the human to approve them (S01 gate). Done when the approval is in `AUDIT_LOG.md`.
2. **Find the seam.** Using `CODEBASE_MAP.md`, find the smallest place where the feature can attach: a new function behind an existing interface, a new route, a new handler, an extension point. List the files to change and the files that call them (`grep -rn "<symbol>"`).
3. **Write a short design.** Half a page in `PLAN.md`: the seam, the files, the data change if any, the rollback. If a significant decision is made (new dependency, new storage), write an ADR (`adr-writer.skill`). The human approves at S02.
4. **Pin the surroundings.** Run `characterization-tests.skill` for the units the change touches, if they are not already pinned. Tests green before the first line of feature code.
5. **Choose the risk control.**
   - Behaviour visible to users and risky: put it behind a flag (`feature-flag-management.skill`), default off.
   - Replacing a used implementation: branch by abstraction as in `safe-refactoring.skill`.
   - Small, additive, internal: no flag needed; say why in `PLAN.md`.
6. **Implement test-first.** For each requirement run `tdd-cycle.skill`: failing test, minimal code, refactor. Coverage of new and changed lines must meet `coverage_min` in `AGENTS.md` (the new-code rule is 99%).
7. **Run the gates.** Full suite, lint, types, complexity, dependency check. Characterisation tests pass unchanged; if one fails, the feature changed old behaviour: stop and ask the human.
8. **Review and security.** Security review (S07) and human review (S08) at the size of the change; list changed files and the tests that cover them.
9. **Ship only when asked.** Staging (S09) and production (S10) follow the normal gates. Production: the human says "deploy now" in that request. Prepare the exact commands and the rollback, and hand them over.

## Constraints
- One feature per run. Cleanups and upgrades found on the way go to `project/TASKS.md` as separate items.
- The diff touches only files named in the plan. A needed extra file is added to the plan first.
- No behaviour of existing code changes unless the requirement says so and the human approved it.
- Never commit, push, tag or deploy unless the human asks for it in that request.

## Output Format
Approved EARS lines and `PLAN.md`, tests and code for the feature, gate results, a rollback note, and a list of follow-ups in `project/TASKS.md`.

## Limits and safety
- A flag left in code after the rollout is debt: record its removal as a task with a date.
- A data change (new column, backfill) is a migration: `db-migration.skill`, backup first, human's yes before it runs anywhere but a local copy.
- If the seam cannot be found without a large refactor, stop and propose `safe-refactoring.skill` as a separate, approved piece of work.

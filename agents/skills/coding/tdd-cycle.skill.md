---
name: tdd-cycle
description: Red-Green-Refactor TDD loop with mandatory false-positive check
triggers: [test, TDD, red-green, failing test, write test first, test-driven]
context_cost: low
tags: [typescript, javascript, python, php, go, rust, java, core]
---

# TDD Cycle Skill

## Goal
Implement any feature using strict Test-Driven Development: write the failing test first, implement minimal code to pass it, then refactor. The false-positive check is mandatory.

## Steps

### Phase 1 — Red (Failing Test)

1. **Understand the requirement**
   - Read the relevant task from project/tasks.md or the user's description
   - Identify the expected behavior as a verifiable predicate
   - Write the requirement in EARS format if not already: "WHEN [X] THE SYSTEM SHALL [Y]"

2. **Write the failing test**
   - Create the test file if it doesn't exist (mirrors source file path in tests/ directory)
   - Write the minimal test that captures the expected behavior
   - Use descriptive test names: `"should return 422 when email is invalid"`
   - Test ONE behavior per test case (single assertion focus)

3. **Run the test — MUST FAIL**
   - Run: `[test command from AGENTS.md]`
   - Confirm the test fails with the expected error (not a different error)
   - **FALSE POSITIVE CHECK:** If the test passes immediately with NO implementation → the test is broken
     - Common causes: wrong file path, wrong import, test assertion always true
     - Fix the test until it genuinely fails for the right reason
   - Record: what error message confirms the correct failure

### Phase 2 — Green (Minimal Implementation)

4. **Write minimal implementation**
   - Write only the code needed to make the failing test pass
   - Do NOT add code for features not tested yet
   - Do NOT optimize prematurely
   - If implementation requires new dependencies: invoke knowledge-gap.skill first

5. **Run the test — MUST PASS**
   - Run: `[test command from AGENTS.md]`
   - Confirm the specific test now passes
   - Confirm ALL other tests still pass (no regressions)
   - If tests fail: invoke self-heal.skill (max 5 attempts before escalation)

### Phase 3 — Refactor

6. **Refactor while green**
   - Improve code quality: extract long functions, improve naming, remove duplication
   - Check: Cyclomatic complexity < 10
   - Check: function length < 30 lines
   - Check: no dead code introduced
   - Run tests after EVERY change — must stay green throughout

7. **Verify final state**
   - Run: `[test command]` → all pass
   - Run: `[typecheck command]` → zero errors
   - Run: `[lint command]` → zero errors
   - Run: `agentic-linter` boundary check → no violations

8. **Mark done**
   - Update task status in project/tasks.md → DONE
   - Write entry to AUDIT_LOG.md: what was implemented and verified

## Constraints
- NEVER write implementation before the failing test exists
- NEVER skip the false-positive check
- NEVER mark a task DONE if tests are red or lint fails
- NEVER implement more than what is tested

## Output Format
Working implementation with passing tests. Test file and source file updated.
Report: "DONE — [test name] passes. All [N] tests passing. Coverage: [X]%"

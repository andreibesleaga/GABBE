---
name: tdd-cycle
description: "Implement a feature test-first: write a failing test, confirm it fails for the right reason, write minimal code, refactor while green. Use when the user asks for TDD, a failing test first, or new behaviour that needs tests."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/tdd-cycle.skill.md"
  tags: "typescript, javascript, python, php, go, rust, java, core"
  core: "true"
  context_cost: "low"
---
# TDD Cycle Skill

## Goal
Implement any feature using strict Test-Driven Development: write the failing test first, implement minimal code to pass it, then refactor. The false-positive check is mandatory.

## Steps

### Phase 1 — Red (Failing Test)

1. **Understand the requirement**
   - Read the relevant task from project/TASKS.md or the user's description (for a new feature with no spec yet, see `spec-driven-development.skill`)
   - Identify the expected behavior as a verifiable predicate
   - Write the requirement in EARS format if not already: "WHEN [X] THE SYSTEM SHALL [Y]"

2. **Write the failing test**
   - Create the test file if it doesn't exist (mirrors source file path in tests/ directory)
   - Write the minimal test that captures the expected behavior
   - Use descriptive test names: `"should return 422 when email is invalid"`
   - Test ONE behavior per test case (single assertion focus)
   - For each Security or Privacy requirement, write the test first; the test must fail when the control is removed

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
   - Check: Cyclomatic complexity <= 10
   - Check: function length <= 30 lines
   - Check: no dead code introduced
   - Run tests after EVERY change — must stay green throughout

7. **Verify final state**
   - Run: `[test command]` → all pass
   - Run: `[typecheck command]` → zero errors
   - Run: `[lint command]` → zero errors
   - Run: `agentic-linter` boundary check → no violations

8. **Mark done**
   - Update task status in project/TASKS.md → DONE
   - Write entry to AUDIT_LOG.md: what was implemented and verified

## Constraints
- NEVER write implementation before the failing test exists
- NEVER skip the false-positive check
- NEVER mark a task DONE if tests are red or lint fails
- NEVER implement more than what is tested
- For code with logic, concurrency, money or authorisation, choose the verification level first: `assurance-ladder.skill.md`

## Output Format
Working implementation with passing tests. Test file and source file updated.
Report: "DONE — [test name] passes. All [N] tests passing. Coverage: [X]%"

## Limits and safety
- The test must fail for the expected reason (the assertion, not an import or setup error); write the error message down.
- Mock only true external boundaries; test the logic against real or in-memory data.
- Tests use an isolated test database and clean up after themselves (setup and teardown), pass or fail; never a shared development database.
- Before a feature is done, write separate failing tests for edge cases, null values and invalid or hostile input.
- At most 5 attempts through `self-heal.skill`, then stop and ask the human.
- Check the test syntax against the project's test framework in its config before running.

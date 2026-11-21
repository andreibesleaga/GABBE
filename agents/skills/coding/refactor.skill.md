---
name: refactor
description: "Restructure code in small steps while a green test suite guards behaviour, and report tests, coverage and complexity before and after. Use when a green suite already covers the code; with no tests start with characterization-tests."
triggers: [refactor, cleanup, restructure, simplify, extract function, improve code quality]
tags: [coding]
core: true
context_cost: low
---
# Refactor Skill

## Goal
Improve code structure, readability, or maintainability while guaranteeing that all existing behavior is preserved. Tests are the safety net — if they fail after refactoring, the refactor was incorrect.

## Steps

For existing code without tests, start with `characterization-tests.skill`, then `safe-refactoring.skill` (this skill applies once a green suite covers the code).

1. **Establish the safety net**
   - Run the full test suite: `[test command from AGENTS.md]`
   - If tests fail before you start: STOP — fix the failing tests first (they're not a safe net)
   - Record baseline: number of passing tests, coverage %

2. **Identify the refactoring target**
   - What specific code smell is being addressed?
   - Common targets:
     - Function too long (> 30 lines) → Extract Function
     - Class with too many responsibilities → Extract Class / Split by Responsibility
     - Duplicated logic (> 3 occurrences) → Extract Method/Module
     - Magic numbers/strings → Extract Constants
     - Deep nesting (> 3 levels) → Early Returns / Extract Method
     - God class → Decompose to smaller, focused classes
     - Long parameter list → Introduce Parameter Object

3. **Apply ONE refactoring at a time**
   - Make the smallest possible change
   - Run tests immediately after each change
   - If tests fail: REVERT the change (don't try to fix tests and refactor simultaneously)

4. **Common refactoring patterns**

   **Extract Function:**
   ```typescript
   // Before: complex inline logic
   function processOrder(order) {
     // 40 lines of validation + calculation + notification
   }

   // After: extracted with clear names
   function processOrder(order) {
     validateOrder(order);
     const total = calculateTotal(order);
     notifyUser(order, total);
   }
   ```

   **Early Returns (reduce nesting):**
   ```typescript
   // Before: deeply nested
   function getDiscount(user) {
     if (user) {
       if (user.isPremium) {
         if (user.yearsActive > 5) {
           return 0.3;
         }
       }
     }
     return 0;
   }

   // After: early returns
   function getDiscount(user) {
     if (!user) return 0;
     if (!user.isPremium) return 0;
     if (user.yearsActive <= 5) return 0;
     return 0.3;
   }
   ```

   **Extract Constants:**
   ```typescript
   // Before: magic numbers
   if (attempts > 3) lockAccount(15 * 60 * 1000);

   // After: named constants
   const MAX_LOGIN_ATTEMPTS = 3;
   const LOCKOUT_DURATION_MS = 15 * 60 * 1000; // 15 minutes
   if (attempts > MAX_LOGIN_ATTEMPTS) lockAccount(LOCKOUT_DURATION_MS);
   ```

5. **After each refactoring step**
   - Run: `[test command]` → must pass
   - Run: `[typecheck command]` → must pass
   - Run: `[lint command]` → must pass
   - Check: complexity still <= 10? Length still <= 30 lines?

6. **Check architecture boundaries** (agentic-linter)
   - After significant structural changes: run agentic-linter skill
   - Ensure no new circular dependencies introduced

7. **Final verification**
   - Baseline tests passing count matches post-refactor count
   - Coverage has not decreased
   - No new lint errors or type errors

## Constraints
- NEVER change behavior during refactoring (only structure)
- NEVER refactor without a passing test suite as safety net
- NEVER combine refactoring with feature addition in the same commit
- If a refactor requires fixing tests: stop, analyze whether the tests or the logic is wrong

## Output Format
Report: "Refactored [target]. All [N] tests still passing. Coverage: [X]%. Complexity reduced from [A] to [B]."

## Limits and safety
- Extracted code must stay inside the same authorisation check; read the diff for fetches or changes that moved out of an `if` that guarded them.
- Before calling the suite a safety net, confirm tests for the security paths (login, permissions, rate limits, validation) exist and pass; if they do not, say so and start with `characterization-tests.skill`.
- Early returns in login and permission code keep the same generic failure message and result; no new distinct messages.
- After splitting a class, search the new code for every log, audit and trace call the old code had (`grep`) and confirm none was lost.
- For a complex algorithm (sorting, rounding, ordering) compare old and new on generated inputs before refactoring (see `pbt-strategy.skill`); prefer readable code to short code.

---
name: ci-autofix
description: "Fix a failing CI run: read the log, find the first root cause (lint, types, test, build), apply a minimal change and verify it locally. Use when CI is red, a build is broken, or a lint, type or test job fails."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/ci-autofix.skill.md"
  tags: "coding"
  core: "false"
  context_cost: "high"
---
# CI Auto-Fix Skill

## Goal
Restore the "Green Build" state by autonomously fixing common CI failures.

## Flow

### Steps
## 1. Log Analysis
**Input**: CI Failure Log / Terminal Output
**Action**: Identify the *first* failure type.
*   **Linting**: Prettier/ESLint errors? (e.g., "Missing semicolon", "Unused var").
*   **Type Check**: TypeScript/MyPy errors? (e.g., "Type 'string' is not assignable to type 'number'").
*   **Unit Test**: Assertion failure? (e.g., "Expected 200, got 500").
*   **Build**: Webpack/Rustc error? (e.g., "Module not found").

### 2. Diagnosis & Strategy
*   **Pattern Matching**:
    *   `TS2322` -> Fix type definition or cast.
    *   `Module not found` -> Check `package.json` or import path.
    *   `AssertionError` -> Read test case vs implementation (Review `spec.md`).

### 3. Auto-Remediation Loop
1.  **Isolate**: Create a temporary fix branch (optional) or stash.
2.  **Fix**: Apply the code change.
3.  **Local Verify**: Run the specific failing command locally (e.g., `npm run lint`).
    *   *If Pass*: Commit and push only if the human asked for that in this request. Otherwise leave the changes in the working tree and report.
    *   *If Fail*: Retry with "Self-Correction" context (feed error back to LLM).

### 4. Safety
*   **Max Retries**: 5 attempts per failure, the same cap as `self-heal.skill`.
*   **Escalation**: If auto-fix fails 5 times, alert Human with "Request for Intervention".

## Constraints
- Fix the first failure only, then re-run the failing command before looking at the next one.
- At most 5 attempts per failure; then escalate.

## Output Format
The fix in the working tree and a report: failure type, root cause, files changed and the output of the local verification command; or the "Request for Intervention" after 5 failed attempts.

## Limits and safety
- At most 5 attempts per failure, as in `self-heal.skill`; then stop and give the human the log excerpt, the fixes tried and the suspected cause.
- Change implementation code only: never remove or weaken an assertion, add `.skip`, or lower coverage to get green.
- Do not change dependency versions, lockfiles or CI configuration files (`.github/workflows`, `.gitlab-ci.yml`) without the human's approval.
- Remove secrets and environment values from log text before you quote it, analyse it or put it in a report.
- If the log does not show a clear root cause (timeouts, differences between local and CI), stop and report; do not guess a fix.

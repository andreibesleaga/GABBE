---
name: traceability-audit
description: "Check that every requirement ID has a test and code, and flag code with no requirement. Use before a release or when a PRD changes. Security requirements are checked first. Use when: traceability, requirement coverage, requirement to test, trace matrix, req coverage."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/traceability-audit.skill.md"
  tags: "security"
  core: "false"
  context_cost: "low"
---
# traceability-audit Skill

## Goal
This skill ensures "What was ordered" == "What was delivered".

## Where it fits
Phase and gate: S06 (gate G9) and S07 (evidence for each security requirement). Evidence: the traceability matrix (`templates/core/TRACEABILITY_MATRIX_TEMPLATE.md`).

## Steps
## 1. The Trace Chain
`PRD (Req ID)` -> `Design (Mock ID)` -> `Task (T-ID)` -> `Commit (Hash)` -> `Test Case (Test ID)`

## 2. Methodology
1.  **Extract Requirements**: Parse `PRD.md` for `req-001`, `req-002`.
2.  **Search Tests**: `grep` test files for `@req(req-001)`.
3.  **Identify Gaps**:
    - Req exists, Test missing -> **Gap**.
    - Req missing, Test exists -> **Gold Plating** (Unrequested feature).

## 3. Coverage Analysis
- **Code Coverage**: Lines of code executed (e.g., 99%).
- **Requirement Coverage**: % of Requirements with at least 1 passing test (Target: 100%).

## 4. The Matrix
Generate a table:
| Req ID | Description | File Reff | Test Ref | Status |
|---|---|---|---|---|
| R-101 | "User logs in" | `auth.ts` | `auth.test.ts` | ✅ PASS |
| R-102 | "User logs out" | `auth.ts` | `auth.test.ts` | ❌ FAIL |

## Constraints
- A trace link exists only by tag or explicit entry, never by guess.
- Run the audit on the current PRD and the current tests, not on a saved copy.

## Output Format
The traceability matrix with a status per requirement ID, the gap list, and the list of tests that do not count.

## Limits and safety
- Check security and compliance requirements first. A missing test for one is reported to orch-judge as a blocker.
- A test linked by tag that has no assertion, or that bypasses the real authentication middleware, does not count. List it.
- Never infer a link from similar wording. A link exists only by tag or an explicit entry.
- A scope exclusion needs the human's recorded yes.

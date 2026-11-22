---
name: system-lifecycle
description: Keeps a traceability matrix from requirement ID to design, code and test, and checks the Definition of Done. Use when asked what a change affects, whether every requirement has a test, or whether a task is done.
triggers: [lifecycle, traceability, requirement, golden thread, definition of done, verify requirements]
tags: [core]
context_cost: medium
---
# System Lifecycle Skill

## Goal
To ensure every line of code has a reason (Requirement) and a verification method (Test).

## Capabilities

### 1. The Golden Thread (Traceability)
-   **Link**: `REQ-ID` -> `Design Element` -> `Code Component` -> `Test Case`.
-   **Gap Analysis**: Find requirements with no tests, or code with no requirements.

### 2. Definition of Done (DoD) Enforcement
-   **Checklist**:
    -   [ ] Implementation matches Spec?
    -   [ ] Tests pass?
    -   [ ] Documentation updated?
    -   [ ] Traceability Matrix updated?

### 3. Change Impact Analysis
-   **Query**: "If I change `UserAuth.ts`, what Requirements are affected?"
-   **Action**: Reverse trace from Code -> Req to find impact scope.

## Steps
1.  **Always ID Requirements**: Use `REQ-001`, `REQ-002` formatting in PRDs.
2.  **Tag Tests**: Add `@req(REQ-001)` annotations to test functions/classes.
3.  **Maintain Matrix**: Update `TRACEABILITY_MATRIX.md` as you code.

## Deliverables
-   `TRACEABILITY_MATRIX.md`: The living map of the system.
-   `impact-analysis.md`: Report on proposed changes.

## Constraints
- Write code only for requirements that are in the approved PRD; if none matches, stop and ask.
- A requirement counts as covered only when a test carrying its ID exists and you ran it.
- Update `TRACEABILITY_MATRIX.md` only from a trace you just recomputed.

## Output Format
`TRACEABILITY_MATRIX.md` (one row per requirement: design element, code, test, status) and, for a proposed change, `impact-analysis.md` listing the requirements it touches.

## Limits and safety
- Do not write code for a requirement that is not in the approved PRD; ask the human instead.
- Say a requirement is covered only after you listed the tests that carry its ID (for example with `grep -rn "REQ-001" tests/`) and ran them.
- A change that traces to a security or compliance requirement (for example PCI-DSS or HIPAA) goes to the human for review.
- Report code with no requirement ("orphan code") as a finding at each checkpoint.

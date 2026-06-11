---
name: system-lifecycle
description: Orchestrate the full SDLC from Requirement to Code to Test (Traceability).
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

## Security & Guardrails

### 1. Skill Security (System Lifecycle)
- **Matrix Immutability**: The `TRACEABILITY_MATRIX.md` must be write-protected against ad-hoc modifications; it can only be updated through verified, systematic agent workflows to prevent tampering with compliance mappings.
- **Traceability Chain of Custody**: Every link in the Golden Thread (Req -> Design -> Code -> Test) must retain the ID of the agent or human that approved the connection, providing definitive forensic accountability.

### 2. System Integration Security
- **Compliance Gap Sniffing**: The system must run periodic automated queries against the traceability matrix to surface "Orphan Code" (code with no requirement) which is a strong indicator of backdoors, scope creep, or unauthorized feature injection.
- **Impact Radius Containment**: When performing a Change Impact Analysis, the system must aggressively highlight if a proposed change traces back to a requirement tagged with high security/compliance risk (e.g., PCI-DSS, HIPAA), triggering mandatory elevated human review.

### 3. LLM & Agent Guardrails
- **Requirement Fabrication Defense**: Agents must be block-listed from writing code to satisfy hallucinated requirements that do not exist in the officially approved PRD, effectively short-circuiting AI-driven scope creep.
- **False Coverage Hallucination**: The LLM must not be allowed to simply assert that a requirement is covered by a test. It must use AST (Abstract Syntax Tree) parsing or test-suite metadata (e.g., `@req()` tags in execution output) to mathematically prove the link exists.

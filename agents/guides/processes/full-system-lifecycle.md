# Guide: Full System Lifecycle (The Golden Thread)

Traceability is not red tape. It is the only way to know if you are building the *right* thing and if it *works*.

## 1. The Golden Thread

The "Golden Thread" is the unbroken line linking a business need to a deployed binary.

1.  **Business Case**: "We need to reduce fraud."
2.  **Requirement (PRD)**: `REQ-050`: "System must Block IP after 5 failed attempts."
3.  **Architecture (Design)**: `ADR-010`: "Use Redis for disjoint rate limiting."
4.  **Implementation (Code)**: `RateLimiter.py`: Implements sliding window logic.
5.  **Verification (Test)**: `test_rate_limiter.py`: Simulates 6 failures and asserts block.

**If you break this thread, you have "Zombie Code" (code with no purpose) or "Orphan Requirements" (needs with no code).**

## 2. Managing Requirements
-   **Atomic**: One requirement = one testable statement.
-   **ID-Driven**: Give everything an ID (`REQ-XXX`). Never refer to "that login feature".
-   **Immutable**: Don't change a requirement. Obsolete it and create a new one.

## 3. Backward vs Forward Traceability
-   **Forward**: PRD -> Code -> Test. "Did we build everything we asked for?"
-   **Backward**: Test -> Code -> PRD. "Why does this code exist?" (Great for deduping).

## 4. The definition of Done (DoD)
You are not done when the code runs. You are done when:
1.  Code is written.
2.  Tests pass.
3.  Traceability Matrix is updated.
4.  Documentation reflects the change.

## 5. Tools
-   **Skill**: `system-lifecycle`
-   **Template**: `core/TRACEABILITY_MATRIX_TEMPLATE.md`

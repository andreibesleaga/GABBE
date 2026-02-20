---
name: decompose
description: Decompose technical specifications or plans into atomic, testable tasks. Enforces the "15-Minute Rule" and populates project/TASKS.md.
triggers: [decompose, break down tasks, create task list, task decomposition, 15 minute rule]
context_cost: medium
---

# Task Decomposition Skill

> "A complex task is just a series of simple tasks that haven't been broken down yet."

## Goal
Transform a Technical Specification (`SPEC.md`) or Implementation Plan (`PLAN.md`) into a flat, ordered list of atomic tasks in `project/TASKS.md`.

## The 15-Minute Rule
Every task must be achievable in approximately **15 minutes** by an AI agent.
- If a task feels like it will take an hour → decompose it.
- If a task covers two different files → decompose it.
- If a task has "and" in the description → decompose it.

## Steps

### 1. Load Context
- Read the latest `PRD.md`, `PLAN.md`, and `SPEC.md`.
- Read existing `project/TASKS.md` (if any) to avoid duplication.

### 2. Identify Modules
- Group the work by component or module (e.g., Auth, Database, UI).
- Determine the dependency order (e.g., Database must exist before Auth).

### 3. Generate Atomic Tasks
For each module/feature, create a sequence of tasks:
1.  **Setup/Stubs**: Create the file or add the interface/types.
2.  **Test**: Write the failing test for specific logic.
3.  **Implement**: Minimal code to pass the test.
4.  **Verify**: Run lint/typecheck.
5.  **Refactor**: Cleanup.

### 4. Format project/TASKS.md
Use the standard GABBE task format:

| ID | Task | Status | Tags |
|---|---|---|---|
| T-001 | Create `User` model with `email` and `password_hash` | TODO | [DB, Auth] |
| T-002 | Implement `checkPassword` method in `User` model | TODO | [Auth] |
| T-003 | Create `POST /login` controller stub | TODO | [API] |

### 5. Categorize Parallelism
Identify tasks that can be done simultaneously by different agents.
- Mark them with the `[PARALLEL]` tag.
- Ensure they don't touch the same lines of the same file.

## Constraints
- Every task must have clear **Acceptance Criteria**.
- Tasks must be **testable**.
- Never create a task named "Implement [Feature X]" — that's an Epic.
- Maximum 20 tasks per decomposition batch (to stay within context limits).

## Output Format
Updated or new `project/TASKS.md` file. Report the number of tasks created.

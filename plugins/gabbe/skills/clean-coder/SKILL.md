---
name: clean-coder
description: "Review code for Clean Code smells and SOLID violations and suggest refactorings with evidence. Use when the user asks for a code quality check, a smell review or a SOLID review before code merges."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/clean-coder.skill.md"
  tags: "coding"
  core: "true"
  context_cost: "medium"
---
# Clean Coder Skill

## Goal
To ensure code is readable, maintainable, and free of technical debt "smells" before it merges.

## Core Principles (2025 Standards)
1.  **SOLID**:
    -   **S**ingle Responsibility: One reason to change.
    -   **O**pen/Closed: Open for extension, closed for modification.
    -   **L**iskov Substitution: Subtypes must be substitutable.
    -   **I**nterface Segregation: Tiny, focused interfaces.
    -   **D**ependency Inversion: Depend on abstractions, not concretions.
2.  **DRY (Don't Repeat Yourself)**: Abstract logic, not just code.
3.  **KISS (Keep It Simple, Stupid)**: Simplest solution that works.
4.  **YAGNI (You Ain't Gonna Need It)**: Don't implement future features now.

## Common Code Smells
-   **Long Method**: over 30 lines (the limit in Constitution Article III). Extract Method.
-   **Large Class**: Too many responsibilities. Extract Class.
-   **Primitive Obsession**: Using strings/ints instead of Value Objects.
-   **Feature Envy**: Using data from another object more than its own.
-   **Shotgun Surgery**: One change requires edits in many classes.

## Steps
When reviewing or writing code:
1.  **Scan for Smells**: Check against the `agents/guides/principles/clean-code-standards.md` guide.
2.  **Suggest Refactoring**: "Split this huge function into 3 smaller ones: `validateInput`, `processData`, `saveResult`."
3.  **Verify Naming**: Variables should be descriptive (`userAssumingRole` vs `u`).
4.  **Check Comments**: Code should be self-documenting. Comments explain *why*, not *what*.

## Checklist
-   [ ] Descriptive naming?
-   [ ] Functions do one thing?
-   [ ] No duplicated logic?
-   [ ] No magic numbers/strings?
-   [ ] Dependencies injected?

## Constraints
- Report a smell only with file and line evidence.
- This skill reviews and suggests; it does not change behaviour (use `refactor.skill` for the change).

## Output Format
A list of smells found, each with file, line and the suggested refactoring, and the checklist above marked pass or fail.

## Limits and safety
- Refactoring of authentication, authorisation or encryption code needs the human's review; keep constant-time comparisons and input checks as they are.
- Do not remove audit logging or security telemetry as a simplification.
- Name the evidence for a smell (the files and lines) before proposing a wide change; reject a refactor that is harder to read than the original.
- Use explicit bindings for dependency injection, not class names loaded from configuration strings at runtime.
